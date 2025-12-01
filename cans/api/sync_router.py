"""
CANS Synchronization API Router
Provides synchronization beacon and cycle alignment endpoints
"""

import asyncio
import time
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from cans.core.state import CANSState, SyncStatus
from cans.core.config import config

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

@router.get("/sync/pulse")
async def get_sync_pulse() -> Dict[str, Any]:
    """
    Get current synchronization pulse

    This endpoint provides the master sync pulse that all cognitive modules
    should align to for coordinated reasoning cycles.
    """
    current_time = time.time()
    state = _ensure_cans_state()

    return {
        "sync_pulse": {
            "timestamp": current_time,
            "cycle_number": state.current_sync_cycle,
            "pulse_id": f"cans_pulse_{state.current_sync_cycle}_{int(current_time)}"
        },
        "system_status": {
            "modules_in_sync": len([m for m in state.module_states.values()
                                   if m.sync_status.value == "in_sync"]),
            "total_modules": len(state.module_states),
            "drift_level": state.current_drift_level,
            "health_score": state.get_system_health_score()
        },
        "alignment_required": state.current_drift_level > config.max_cycle_drift
    }

@router.post("/sync/acknowledge")
async def acknowledge_sync_pulse(sync_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Acknowledge receipt of sync pulse from a module

    Args:
        sync_data: Synchronization data from the acknowledging module

    Returns:
        Acknowledgment confirmation
    """
    module_name = sync_data.get("module_name")
    module_cycle = sync_data.get("cycle_number", 0)
    module_timestamp = sync_data.get("timestamp", time.time())

    if not module_name:
        raise HTTPException(status_code=400, detail="module_name is required")

    state = _ensure_cans_state()
    drift_detected = False

    # Update module sync status
    if module_name in state.module_states:
        module = state.module_states[module_name]
        cycle_drift = abs(state.current_sync_cycle - module_cycle)

        if cycle_drift <= config.max_cycle_drift:
            module.sync_status = SyncStatus.IN_SYNC
            module.cycle_number = module_cycle
            drift_detected = False
        else:
            module.sync_status = SyncStatus.OUT_OF_SYNC
            drift_detected = True

        # Update drift tracking
        state.current_drift_level = max(state.current_drift_level, cycle_drift)

    return {
        "acknowledged": True,
        "module": module_name,
        "master_cycle": state.current_sync_cycle,
        "drift_detected": drift_detected,
        "timestamp": time.time()
    }

@router.get("/sync/modules")
async def get_module_sync_status() -> Dict[str, Any]:
    """
    Get synchronization status for all monitored modules
    """
    state = _ensure_cans_state()
    module_sync_info = {}

    for name, module in state.module_states.items():
        cycle_drift = abs(state.current_sync_cycle - module.cycle_number)
        module_sync_info[name] = {
            "cycle_number": module.cycle_number,
            "sync_status": module.sync_status.value,
            "cycle_drift": cycle_drift,
            "time_since_sync": time.time() - module.last_heartbeat,
            "requires_alignment": cycle_drift > config.max_cycle_drift
        }

    return {
        "master_cycle": state.current_sync_cycle,
        "timestamp": time.time(),
        "modules": module_sync_info,
        "overall_sync_health": len([m for m in module_sync_info.values()
                                   if not m["requires_alignment"]]) / len(module_sync_info) * 100
    }

@router.post("/sync/align")
async def request_alignment(alignment_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request cycle alignment for a module

    Args:
        alignment_request: Alignment request data

    Returns:
        Alignment instructions
    """
    module_name = alignment_request.get("module_name")

    if not module_name:
        raise HTTPException(status_code=400, detail="module_name is required")

    state = _ensure_cans_state()

    if module_name not in state.module_states:
        raise HTTPException(status_code=404, detail=f"Module '{module_name}' not found")

    module = state.module_states[module_name]
    current_drift = abs(state.current_sync_cycle - module.cycle_number)

    alignment_instructions = {
        "module": module_name,
        "current_cycle": module.cycle_number,
        "target_cycle": state.current_sync_cycle,
        "drift": current_drift,
        "alignment_required": current_drift > config.max_cycle_drift,
        "instructions": []
    }

    if current_drift > config.max_cycle_drift:
        alignment_instructions["instructions"] = [
            f"Reset local cycle counter to {state.current_sync_cycle}",
            "Synchronize internal clocks with CANS timestamp",
            "Flush any pending operations from drifted cycles",
            "Resume processing from aligned cycle"
        ]
        module.sync_status = SyncStatus.REALIGNING
    else:
        alignment_instructions["instructions"] = ["No alignment required - cycles are synchronized"]
        module.sync_status = SyncStatus.IN_SYNC

    return alignment_instructions

@router.get("/sync/beacon")
async def get_sync_beacon() -> Dict[str, Any]:
    """
    Get synchronization beacon broadcast

    This endpoint provides the continuous sync beacon that modules can poll
    to maintain alignment with the cognitive rhythm.
    """
    state = _ensure_cans_state()

    return {
        "beacon": {
            "id": f"cans_beacon_{state.current_sync_cycle}",
            "timestamp": time.time(),
            "cycle": state.current_sync_cycle,
            "frequency": config.sync_interval,
            "master_clock": time.time()
        },
        "system_rhythm": {
            "pulse_interval": config.heartbeat_interval,
            "sync_interval": config.sync_interval,
            "monitor_interval": config.monitor_interval,
            "cycle_check_interval": config.cycle_check_interval
        },
        "module_alignment": {
            "total_modules": len(state.module_states),
            "aligned_modules": len([m for m in state.module_states.values()
                                   if m.sync_status.value == "in_sync"]),
            "drifting_modules": len([m for m in state.module_states.values()
                                    if m.sync_status.value == "drifting"]),
            "out_of_sync_modules": len([m for m in state.module_states.values()
                                       if m.sync_status.value == "out_of_sync"])
        }
    }