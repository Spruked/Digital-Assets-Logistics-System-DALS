"""
Universal CANS Compatibility Router
Provides standardized sync endpoints for CANS autonomic monitoring

This router enables any module to respond to CANS heartbeat, sync, and monitor requests,
allowing the autonomic nervous system to maintain system coherence.

Endpoints:
- GET /heartbeat: Module heartbeat acknowledgment
- POST /sync: Receive CANS sync pulses and cycle updates
- GET /monitor: Module health and status reporting
"""

from fastapi import APIRouter, HTTPException
import time
import logging

logger = logging.getLogger("CANS.Sync.Router")

router = APIRouter()

# Module state tracking for CANS compatibility
MODULE_STATE = {
    "cycle": 0,
    "healthy": True,
    "last_sync": None,
    "last_heartbeat": None,
    "drift_detected": False,
    "sync_count": 0
}

@router.get("/heartbeat")
async def module_heartbeat():
    """
    CANS Heartbeat Endpoint
    Returns acknowledgment and current module state for autonomic monitoring
    """
    try:
        MODULE_STATE["last_heartbeat"] = time.time()

        return {
            "acknowledged": True,
            "timestamp": MODULE_STATE["last_heartbeat"],
            "module_cycle": MODULE_STATE["cycle"],
            "healthy": MODULE_STATE["healthy"]
        }
    except Exception as e:
        logger.error(f"Heartbeat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Heartbeat failed")

@router.post("/sync")
async def module_sync(data: dict):
    """
    CANS Sync Endpoint
    Receives sync pulses from CANS autonomic system and maintains cycle coherence
    """
    try:
        # Extract sync data from CANS
        master_cycle = data.get("master_cycle", MODULE_STATE["cycle"])
        sync_timestamp = data.get("timestamp", time.time())
        pulse_id = data.get("pulse_id", f"pulse_{int(time.time())}")

        # Update module state
        MODULE_STATE["cycle"] = master_cycle
        MODULE_STATE["last_sync"] = sync_timestamp
        MODULE_STATE["sync_count"] += 1

        # Check for drift (simple implementation)
        drift_detected = abs(time.time() - sync_timestamp) > 1.0  # 1 second tolerance
        MODULE_STATE["drift_detected"] = drift_detected

        logger.info(f"CANS sync received: cycle={master_cycle}, pulse={pulse_id}")

        return {
            "acknowledged": True,
            "module_cycle": MODULE_STATE["cycle"],
            "drift_detected": drift_detected,
            "sync_timestamp": sync_timestamp,
            "pulse_id": pulse_id
        }
    except Exception as e:
        logger.error(f"Sync endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Sync failed")

@router.get("/monitor")
async def module_monitor():
    """
    CANS Monitor Endpoint
    Provides module health and status for autonomic system monitoring
    """
    try:
        # Calculate health score based on recent activity
        current_time = time.time()
        health_score = 100.0

        # Reduce health if no recent heartbeat
        if MODULE_STATE["last_heartbeat"]:
            heartbeat_age = current_time - MODULE_STATE["last_heartbeat"]
            if heartbeat_age > 300:  # 5 minutes
                health_score -= 20
            elif heartbeat_age > 60:  # 1 minute
                health_score -= 5

        # Reduce health if no recent sync
        if MODULE_STATE["last_sync"]:
            sync_age = current_time - MODULE_STATE["last_sync"]
            if sync_age > 600:  # 10 minutes
                health_score -= 30
            elif sync_age > 120:  # 2 minutes
                health_score -= 10

        # Reduce health if drift detected
        if MODULE_STATE["drift_detected"]:
            health_score -= 15

        # Update healthy status
        MODULE_STATE["healthy"] = health_score >= 60

        return {
            "status": "operational" if MODULE_STATE["healthy"] else "degraded",
            "health_score": round(health_score, 1),
            "cycle": MODULE_STATE["cycle"],
            "last_sync": MODULE_STATE["last_sync"],
            "last_heartbeat": MODULE_STATE["last_heartbeat"],
            "drift_detected": MODULE_STATE["drift_detected"],
            "sync_count": MODULE_STATE["sync_count"],
            "timestamp": current_time
        }
    except Exception as e:
        logger.error(f"Monitor endpoint error: {e}")
        return {
            "status": "error",
            "health_score": 0.0,
            "cycle": MODULE_STATE["cycle"],
            "error": str(e),
            "timestamp": time.time()
        }

# Utility functions for module state management
def set_module_cycle(cycle: int):
    """Update module cycle counter"""
    MODULE_STATE["cycle"] = cycle

def mark_module_healthy(healthy: bool = True):
    """Mark module health status"""
    MODULE_STATE["healthy"] = healthy

def reset_drift_detection():
    """Reset drift detection flag"""
    MODULE_STATE["drift_detected"] = False