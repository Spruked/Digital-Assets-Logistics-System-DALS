"""
CANS Heartbeat API Router
Provides heartbeat monitoring and status endpoints
"""

import asyncio
import time
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from cans.core.state import CANSState

# Global state reference - set by main service
_cans_state = None

def set_cans_state(state: CANSState):
    """Set the global CANS state reference"""
    global _cans_state
    _cans_state = state

def _ensure_cans_state() -> CANSState:
    """Ensure CANS state is available"""
    if _cans_state is None:
        raise HTTPException(status_code=503, detail="CANS service not initialized")
    return _cans_state

router = APIRouter()

@router.get("/heartbeat")
async def get_heartbeat() -> Dict[str, Any]:
    """
    DALS-001 compliant CANS heartbeat endpoint.
    Must update internal state and must never return None or invalid values.
    """
    state = _ensure_cans_state()
    current_time = time.time()

    # --- REQUIRED for UCM alignment ---
    # Update internal state timestamps
    state.last_heartbeat = current_time
    state.last_seen_alive = current_time

    # Normalize all values to ensure DALS-001 compliance (zero-or-empty)
    cycle = state.current_sync_cycle or 0
    uptime = (current_time - state.start_time) if state.start_time else 0
    health = state.get_system_health_score() or 0
    monitored = len(state.module_states) or 0
    sync = state.total_sync_pulses or 0
    isolated = len(state.isolated_modules) or 0

    return {
        "module": "CANS",
        "status": "alive" if not state.is_shutting_down else "shutting_down",
        "timestamp": current_time,

        # Corrected fields
        "cycle": cycle,
        "uptime": uptime,
        "health_score": health,
        "monitored_modules": monitored,
        "sync_pulses": sync,
        "isolated_modules": isolated
    }

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get detailed CANS status - comprehensive system overview

    Returns complete status of all monitored modules and system health.
    """
    state = _ensure_cans_state()

    return {
        "service": "CANS - Cognitive Autonomous Neural Synchronizer",
        "status": "operational" if not state.is_shutting_down else "shutting_down",
        "timestamp": time.time(),
        "uptime": time.time() - state.start_time,
        "version": "1.0.0",

        "system_health": {
            "overall_score": state.get_system_health_score(),
            "total_modules": len(state.module_states),
            "operational_modules": len([m for m in state.module_states.values()
                                      if m.state.value == "operational"]),
            "isolated_modules": len(state.isolated_modules),
            "recovering_modules": len(state.recovering_modules)
        },

        "synchronization": state.get_sync_status_summary(),

        "performance": {
            "heartbeats_sent": state.total_heartbeats_sent,
            "sync_pulses": state.total_sync_pulses,
            "monitoring_cycles": state.total_monitoring_cycles,
            "failures_detected": state.total_failures_detected,
            "recoveries": state.total_recoveries
        },

        "modules": state.get_all_module_statuses()
    }

@router.get("/health")
async def get_health() -> Dict[str, Any]:
    """
    Get CANS health check - lightweight status endpoint

    Used for load balancer health checks and basic monitoring.
    """
    state = _ensure_cans_state()
    health_score = state.get_system_health_score()

    return {
        "status": "healthy" if health_score >= 50 else "degraded",
        "health_score": health_score,
        "timestamp": time.time(),
        "modules_monitored": len(state.module_states),
        "sync_cycles": state.sync_cycle_count
    }

@router.get("/modules/{module_name}/status")
async def get_module_status(module_name: str) -> Dict[str, Any]:
    """
    Get status for a specific module

    Args:
        module_name: Name of the module to check

    Returns:
        Detailed status information for the requested module
    """
    state = _ensure_cans_state()
    module = state.get_module_status(module_name)
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    return {
        "module": module.name,
        "state": module.state.value,
        "health_score": module.health_score,
        "latency": module.latency,
        "sync_status": module.sync_status.value,
        "last_heartbeat": module.last_heartbeat,
        "cycle_number": module.cycle_number,
        "consecutive_failures": module.consecutive_failures,
        "last_error": module.last_error,
        "time_since_last_heartbeat": time.time() - module.last_heartbeat
    }

@router.get("/sync/status")
async def get_sync_status() -> Dict[str, Any]:
    """
    Get current synchronization status across all modules

    Returns real-time sync information and drift detection.
    """
    state = _ensure_cans_state()

    return {
        "timestamp": time.time(),
        "current_cycle": state.current_sync_cycle,
        "sync_status": state.get_sync_status_summary(),
        "last_sync_pulse": {
            "timestamp": state.last_sync_pulse.timestamp if state.last_sync_pulse else None,
            "cycle_number": state.last_sync_pulse.cycle_number if state.last_sync_pulse else None,
            "modules_in_sync": state.last_sync_pulse.modules_in_sync if state.last_sync_pulse else 0,
            "drift_detected": state.last_sync_pulse.drift_detected if state.last_sync_pulse else False,
            "max_drift": state.last_sync_pulse.max_drift if state.last_sync_pulse else 0.0
        } if state.last_sync_pulse else None
    }