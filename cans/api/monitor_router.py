"""
CANS Monitoring API Router
Provides module monitoring, responsiveness checking, and autonomic actions
"""

import asyncio
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional

from cans.core.config import config

# Global state reference - set by main service
_cans_state = None

def set_cans_state(state):
    """Set the global CANS state reference"""
    global _cans_state
    _cans_state = state

def _ensure_cans_state():
    """Ensure CANS state is available"""
    if _cans_state is None:
        raise HTTPException(status_code=503, detail="CANS service not initialized")
    return _cans_state

router = APIRouter()

@router.get("/monitor/status")
async def get_monitoring_status() -> Dict[str, Any]:
    """
    Get overall monitoring status and autonomic actions taken
    """
    return {
        "monitoring_active": not _ensure_cans_state().is_shutting_down,
        "timestamp": time.time(),
        "monitoring_cycles": _ensure_cans_state().total_monitoring_cycles,
        "modules_monitored": len(_ensure_cans_state().module_states),

        "autonomic_actions": {
            "isolations": len(_ensure_cans_state().isolated_modules),
            "recoveries": _ensure_cans_state().total_recoveries,
            "failures_detected": _ensure_cans_state().total_failures_detected
        },

        "system_health": {
            "overall_score": _ensure_cans_state().get_system_health_score(),
            "isolated_modules": _ensure_cans_state().isolated_modules,
            "recovering_modules": _ensure_cans_state().recovering_modules,
            "failed_modules": _ensure_cans_state().failed_modules
        }
    }

@router.get("/monitor/modules")
async def get_monitored_modules() -> Dict[str, Any]:
    """
    Get list of all monitored modules with their current status
    """
    modules_info = {}

    for name, module in _ensure_cans_state().module_states.items():
        modules_info[name] = {
            "state": module.state.value,
            "health_score": module.health_score,
            "latency": module.latency,
            "last_check": module.last_heartbeat,
            "time_since_check": time.time() - module.last_heartbeat,
            "consecutive_failures": module.consecutive_failures,
            "sync_status": module.sync_status.value,
            "last_error": module.last_error
        }

    return {
        "timestamp": time.time(),
        "total_modules": len(modules_info),
        "modules": modules_info,
        "config": {
            "monitor_interval": config.monitor_interval,
            "max_latency_threshold": config.max_latency_threshold,
            "critical_modules": config.critical_modules
        }
    }

@router.post("/monitor/check/{module_name}")
async def manual_module_check(module_name: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Manually trigger a health check for a specific module

    Args:
        module_name: Name of the module to check

    Returns:
        Check initiation confirmation
    """
    if module_name not in config.monitored_modules:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' is not configured for monitoring")

    # Add background task to perform the check
    background_tasks.add_task(perform_manual_check, module_name)

    return {
        "check_initiated": True,
        "module": module_name,
        "timestamp": time.time(),
        "expected_completion": time.time() + config.monitor_timeout
    }

async def perform_manual_check(module_name: str):
    """Perform manual health check for a module"""
    # This would integrate with the ModuleMonitor service
    # For now, just log the manual check
    print(f"CANS: Manual check initiated for {module_name}")

@router.post("/monitor/isolate/{module_name}")
async def isolate_module(module_name: str, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Manually isolate a module (emergency autonomic action)

    Args:
        module_name: Name of the module to isolate
        reason: Reason for isolation

    Returns:
        Isolation confirmation
    """
    if module_name not in _ensure_cans_state().module_states:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    isolation_reason = reason or "Manual isolation requested"
    _ensure_cans_state()._isolate_module(module_name, isolation_reason)

    return {
        "isolated": True,
        "module": module_name,
        "reason": isolation_reason,
        "timestamp": time.time(),
        "action": "manual_isolation"
    }

@router.post("/monitor/recover/{module_name}")
async def recover_module(module_name: str) -> Dict[str, Any]:
    """
    Manually trigger recovery process for an isolated module

    Args:
        module_name: Name of the module to recover

    Returns:
        Recovery initiation confirmation
    """
    if module_name not in _ensure_cans_state().module_states:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    if module_name not in _ensure_cans_state().isolated_modules:
        raise HTTPException(status_code=400, detail=f"Module '{module_name}' is not currently isolated")

    # Remove from isolated list and mark as recovering
    _ensure_cans_state().isolated_modules.remove(module_name)
    _ensure_cans_state().recovering_modules.append(module_name)
    _ensure_cans_state().module_states[module_name].state = _ensure_cans_state().ModuleState.RECOVERING
    _ensure_cans_state().module_states[module_name].recovery_attempts += 1

    return {
        "recovery_initiated": True,
        "module": module_name,
        "timestamp": time.time(),
        "recovery_attempt": _ensure_cans_state().module_states[module_name].recovery_attempts
    }

@router.get("/monitor/alerts")
async def get_active_alerts() -> Dict[str, Any]:
    """
    Get all active monitoring alerts and issues
    """
    alerts = []

    current_time = time.time()

    # Check for modules with high latency
    for name, module in _ensure_cans_state().module_states.items():
        if module.latency > config.max_latency_threshold:
            alerts.append({
                "type": "high_latency",
                "severity": "warning",
                "module": name,
                "value": module.latency,
                "threshold": config.max_latency_threshold,
                "timestamp": current_time
            })

    # Check for isolated modules
    for module_name in _ensure_cans_state().isolated_modules:
        alerts.append({
            "type": "module_isolated",
            "severity": "critical",
            "module": module_name,
            "timestamp": current_time,
            "description": "Module has been isolated due to consecutive failures"
        })

    # Check for modules with consecutive failures
    for name, module in _ensure_cans_state().module_states.items():
        if module.consecutive_failures >= 2:
            alerts.append({
                "type": "consecutive_failures",
                "severity": "error",
                "module": name,
                "value": module.consecutive_failures,
                "timestamp": current_time
            })

    # Check for sync drift
    if _ensure_cans_state().current_drift_level > config.max_cycle_drift:
        alerts.append({
            "type": "sync_drift",
            "severity": "warning",
            "value": _ensure_cans_state().current_drift_level,
            "threshold": config.max_cycle_drift,
            "timestamp": current_time,
            "description": "High synchronization drift detected across modules"
        })

    return {
        "timestamp": current_time,
        "total_alerts": len(alerts),
        "alerts": alerts,
        "severity_breakdown": {
            "critical": len([a for a in alerts if a["severity"] == "critical"]),
            "error": len([a for a in alerts if a["severity"] == "error"]),
            "warning": len([a for a in alerts if a["severity"] == "warning"])
        }
    }

@router.get("/monitor/performance")
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get detailed performance metrics from monitoring
    """
    current_time = time.time()

    # Calculate average latency
    latencies = [m.latency for m in _ensure_cans_state().module_states.values() if m.latency > 0]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    # Calculate health score distribution
    health_scores = [m.health_score for m in _ensure_cans_state().module_states.values()]
    avg_health = sum(health_scores) / len(health_scores) if health_scores else 0

    return {
        "timestamp": current_time,
        "uptime": current_time - _ensure_cans_state().start_time,

        "performance_metrics": {
            "average_latency": round(avg_latency, 3),
            "average_health_score": round(avg_health, 2),
            "total_heartbeats_processed": _ensure_cans_state().total_heartbeats_sent,
            "total_monitoring_cycles": _ensure_cans_state().total_monitoring_cycles,
            "max_observed_drift": _ensure_cans_state().max_observed_drift
        },

        "module_distribution": {
            "operational": len([m for m in _ensure_cans_state().module_states.values()
                               if m.state.value == "operational"]),
            "degraded": len([m for m in _ensure_cans_state().module_states.values()
                            if m.state.value == "degraded"]),
            "isolated": len(_ensure_cans_state().isolated_modules),
            "failed": len(_ensure_cans_state().failed_modules),
            "recovering": len(_ensure_cans_state().recovering_modules)
        },

        "thresholds": {
            "max_latency_threshold": config.max_latency_threshold,
            "max_cycle_drift": config.max_cycle_drift,
            "monitor_interval": config.monitor_interval
        }
    }