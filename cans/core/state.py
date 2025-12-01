"""
CANS State Management
Centralized state tracking for all cognitive modules and synchronization status
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class ModuleState(Enum):
    """Enumeration of possible module states"""
    UNKNOWN = "unknown"
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    FAILED = "failed"
    RECOVERING = "recovering"

class SyncStatus(Enum):
    """Enumeration of synchronization states"""
    IN_SYNC = "in_sync"
    DRIFTING = "drifting"
    OUT_OF_SYNC = "out_of_sync"
    REALIGNING = "realigning"

@dataclass
class ModuleStatus:
    """Status information for a monitored module"""
    name: str
    state: ModuleState
    last_heartbeat: float
    latency: float
    health_score: float  # 0-100
    sync_status: SyncStatus
    cycle_number: int
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    recovery_attempts: int = 0

@dataclass
class CANSSyncPulse:
    """Synchronization pulse data"""
    timestamp: float
    cycle_number: int
    modules_in_sync: int
    total_modules: int
    drift_detected: bool
    max_drift: float

@dataclass
class CANSState:
    """Global CANS state management"""

    # Core state
    is_initialized: bool = False
    is_shutting_down: bool = False
    start_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    last_seen_alive: float = field(default_factory=time.time)

    # Module tracking
    module_states: Dict[str, ModuleStatus] = field(default_factory=dict)

    # Synchronization tracking
    current_sync_cycle: int = 0
    sync_cycle_count: int = 0
    last_sync_pulse: Optional[CANSSyncPulse] = None

    # Performance metrics
    total_heartbeats_sent: int = 0
    total_sync_pulses: int = 0
    total_monitoring_cycles: int = 0
    total_failures_detected: int = 0
    total_recoveries: int = 0

    # Isolation and recovery tracking
    isolated_modules: List[str] = field(default_factory=list)
    recovering_modules: List[str] = field(default_factory=list)
    failed_modules: List[str] = field(default_factory=list)

    # Drift detection
    max_observed_drift: float = 0.0
    current_drift_level: float = 0.0

    def initialize_module(self, module_name: str, is_critical: bool = False):
        """Initialize tracking for a new module"""
        if module_name not in self.module_states:
            self.module_states[module_name] = ModuleStatus(
                name=module_name,
                state=ModuleState.UNKNOWN,
                last_heartbeat=0.0,
                latency=0.0,
                health_score=0.0,
                sync_status=SyncStatus.OUT_OF_SYNC,
                cycle_number=0
            )
            self._log_state_change(module_name, "initialized", ModuleState.UNKNOWN)

    def update_module_heartbeat(self, module_name: str, latency: float, health_score: float):
        """Update module heartbeat information"""
        if module_name in self.module_states:
            module = self.module_states[module_name]
            module.last_heartbeat = time.time()
            module.latency = latency
            module.health_score = health_score
            module.consecutive_failures = 0  # Reset failure count

            # Update state based on health
            new_state = self._determine_state_from_health(health_score)
            if new_state != module.state:
                self._log_state_change(module_name, "heartbeat_update", new_state)
                module.state = new_state

                # Handle state transitions
                if new_state == ModuleState.OPERATIONAL:
                    self._handle_module_recovery(module_name)
                elif new_state in [ModuleState.DEGRADED, ModuleState.FAILED]:
                    self._handle_module_degradation(module_name)

    def record_module_failure(self, module_name: str, error: str):
        """Record a module failure"""
        if module_name in self.module_states:
            module = self.module_states[module_name]
            module.consecutive_failures += 1
            module.last_error = error
            module.health_score = max(0, module.health_score - 20)  # Reduce health

            # Check if module should be isolated
            if module.consecutive_failures >= 3:
                self._isolate_module(module_name, f"Consecutive failures: {error}")
            else:
                module.state = ModuleState.DEGRADED
                self._log_state_change(module_name, "failure_recorded", ModuleState.DEGRADED)

            self.total_failures_detected += 1

    def record_sync_pulse(self, modules_in_sync: int, total_modules: int, drift_detected: bool, max_drift: float):
        """Record a synchronization pulse"""
        self.current_sync_cycle += 1
        self.sync_cycle_count += 1
        self.total_sync_pulses += 1

        self.last_sync_pulse = CANSSyncPulse(
            timestamp=time.time(),
            cycle_number=self.current_sync_cycle,
            modules_in_sync=modules_in_sync,
            total_modules=total_modules,
            drift_detected=drift_detected,
            max_drift=max_drift
        )

        if drift_detected:
            self.current_drift_level = max_drift
            self.max_observed_drift = max(self.max_observed_drift, max_drift)

    def get_module_status(self, module_name: str) -> Optional[ModuleStatus]:
        """Get status for a specific module"""
        return self.module_states.get(module_name)

    def get_all_module_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status summary for all modules"""
        return {
            name: {
                "state": module.state.value,
                "health_score": module.health_score,
                "latency": module.latency,
                "sync_status": module.sync_status.value,
                "last_heartbeat": module.last_heartbeat,
                "consecutive_failures": module.consecutive_failures
            }
            for name, module in self.module_states.items()
        }

    def get_system_health_score(self) -> float:
        """Calculate overall system health score"""
        if not self.module_states:
            return 0.0

        total_health = sum(module.health_score for module in self.module_states.values())
        avg_health = total_health / len(self.module_states)

        # Penalize for isolated modules
        isolation_penalty = len(self.isolated_modules) * 10
        avg_health = max(0, avg_health - isolation_penalty)

        return round(avg_health, 2)

    def _determine_state_from_health(self, health_score: float) -> ModuleState:
        """Determine module state based on health score"""
        if health_score >= 80:
            return ModuleState.OPERATIONAL
        elif health_score >= 50:
            return ModuleState.DEGRADED
        elif health_score >= 20:
            return ModuleState.ISOLATED
        else:
            return ModuleState.FAILED

    def _isolate_module(self, module_name: str, reason: str):
        """Isolate a failing module"""
        if module_name in self.module_states:
            self.module_states[module_name].state = ModuleState.ISOLATED
            if module_name not in self.isolated_modules:
                self.isolated_modules.append(module_name)
            self._log_state_change(module_name, f"isolated: {reason}", ModuleState.ISOLATED)

    def _handle_module_recovery(self, module_name: str):
        """Handle module recovery from degraded/failed state"""
        if module_name in self.isolated_modules:
            self.isolated_modules.remove(module_name)
        if module_name in self.recovering_modules:
            self.recovering_modules.remove(module_name)

        self.total_recoveries += 1
        self._log_state_change(module_name, "recovered", ModuleState.OPERATIONAL)

    def _handle_module_degradation(self, module_name: str):
        """Handle module degradation"""
        if module_name not in self.recovering_modules:
            self.recovering_modules.append(module_name)

    def _log_state_change(self, module_name: str, action: str, new_state: ModuleState):
        """Log state changes for monitoring"""
        # This would integrate with the main logging system
        print(f"CANS: Module {module_name} {action} -> {new_state.value}")

    def get_sync_status_summary(self) -> Dict[str, Any]:
        """Get synchronization status summary"""
        return {
            "current_cycle": self.current_sync_cycle,
            "total_cycles": self.sync_cycle_count,
            "modules_in_sync": len([m for m in self.module_states.values() if m.sync_status == SyncStatus.IN_SYNC]),
            "total_modules": len(self.module_states),
            "drift_level": self.current_drift_level,
            "max_drift_observed": self.max_observed_drift,
            "isolated_modules": self.isolated_modules.copy(),
            "recovering_modules": self.recovering_modules.copy()
        }