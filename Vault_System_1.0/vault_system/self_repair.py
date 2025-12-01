# self_repair.py

"""
Self-Repair Protocols - Autonomous System Healing

This module provides autonomous self-repair capabilities for the vault system,
enabling automatic detection and correction of system issues.
"""

import time
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from lifecycle_control import LifecycleController, ComponentRecord, LifecycleState, ComponentHealth
from vault_core.module_blueprints import BlueprintManager


class RepairStrategy(Enum):
    """Strategies for repairing components"""
    RESTART = "restart"           # Simple restart
    REINITIALIZE = "reinitialize" # Reinitialize with fresh state
    FAILOVER = "failover"        # Switch to backup instance
    RECONFIGURE = "reconfigure"  # Reconfigure with different settings
    REPLACE = "replace"          # Replace with new instance
    ESCALATE = "escalate"        # Escalate to human intervention


class FailurePattern(Enum):
    """Common failure patterns"""
    CRASH_LOOP = "crash_loop"        # Component crashes repeatedly
    MEMORY_LEAK = "memory_leak"      # Memory usage growing
    PERFORMANCE_DEGRADATION = "performance_degradation"  # Slowing down
    CONNECTIVITY_ISSUE = "connectivity_issue"  # Network problems
    CONFIGURATION_ERROR = "configuration_error"  # Bad configuration
    RESOURCE_EXHAUSTION = "resource_exhaustion"  # Out of resources
    CORRUPTION = "corruption"        # Data corruption
    UNKNOWN = "unknown"             # Unidentified failure


class RepairAction:
    """
    Represents a repair action taken on a component.
    """

    def __init__(self, component_name: str, strategy: RepairStrategy,
                 failure_pattern: FailurePattern, details: Dict[str, Any]):
        """
        Initialize a repair action.

        Args:
            component_name: Name of the component being repaired
            strategy: Repair strategy used
            failure_pattern: Identified failure pattern
            details: Repair action details
        """
        self.component_name = component_name
        self.strategy = strategy
        self.failure_pattern = failure_pattern
        self.details = details
        self.timestamp = datetime.now()
        self.success = None
        self.duration = None
        self.error_message = None

    def complete(self, success: bool, duration: float, error_message: Optional[str] = None):
        """
        Mark the repair action as completed.

        Args:
            success: Whether the repair was successful
            duration: Time taken for repair
            error_message: Error message if repair failed
        """
        self.success = success
        self.duration = duration
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "component_name": self.component_name,
            "strategy": self.strategy.value,
            "failure_pattern": self.failure_pattern.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "duration": self.duration,
            "error_message": self.error_message
        }


class SelfRepairProtocols:
    """
    Autonomous self-repair system for vault components.
    """

    def __init__(self, blueprint_manager: BlueprintManager,
                 lifecycle_controller: LifecycleController,
                 repair_interval: int = 30):
        """
        Initialize self-repair protocols.

        Args:
            blueprint_manager: Blueprint manager instance
            lifecycle_controller: Lifecycle controller instance
            repair_interval: Health check interval in seconds
        """
        self.blueprint_manager = blueprint_manager
        self.lifecycle_controller = lifecycle_controller
        self.repair_interval = repair_interval

        # Repair history
        self.repair_history: List[RepairAction] = []
        self.max_history_size = 1000

        # Repair strategies by failure pattern
        self.repair_strategies = self._initialize_repair_strategies()

        # Background monitoring
        self.running = False
        self.monitor_thread = None

        # Repair statistics
        self.repair_stats = {
            "total_attempts": 0,
            "successful_repairs": 0,
            "failed_repairs": 0,
            "escalations": 0
        }

        print("🔧 Self-Repair Protocols initialized")

    def _initialize_repair_strategies(self) -> Dict[FailurePattern, List[RepairStrategy]]:
        """Initialize repair strategies for different failure patterns"""
        return {
            FailurePattern.CRASH_LOOP: [
                RepairStrategy.RESTART,
                RepairStrategy.REINITIALIZE,
                RepairStrategy.REPLACE,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.MEMORY_LEAK: [
                RepairStrategy.RESTART,
                RepairStrategy.REINITIALIZE,
                RepairStrategy.RECONFIGURE,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.PERFORMANCE_DEGRADATION: [
                RepairStrategy.RESTART,
                RepairStrategy.RECONFIGURE,
                RepairStrategy.REINITIALIZE,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.CONNECTIVITY_ISSUE: [
                RepairStrategy.RESTART,
                RepairStrategy.RECONFIGURE,
                RepairStrategy.FAILOVER,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.CONFIGURATION_ERROR: [
                RepairStrategy.RECONFIGURE,
                RepairStrategy.REINITIALIZE,
                RepairStrategy.REPLACE,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.RESOURCE_EXHAUSTION: [
                RepairStrategy.RESTART,
                RepairStrategy.RECONFIGURE,
                RepairStrategy.FAILOVER,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.CORRUPTION: [
                RepairStrategy.REINITIALIZE,
                RepairStrategy.REPLACE,
                RepairStrategy.ESCALATE
            ],
            FailurePattern.UNKNOWN: [
                RepairStrategy.RESTART,
                RepairStrategy.REINITIALIZE,
                RepairStrategy.RECONFIGURE,
                RepairStrategy.ESCALATE
            ]
        }

    def start_health_monitoring(self):
        """Start the health monitoring and repair thread"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_and_repair, daemon=True)
        self.monitor_thread.start()

        print("🔍 Started health monitoring and self-repair")

    def stop_health_monitoring(self):
        """Stop the health monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        print("🛑 Stopped health monitoring and self-repair")

    def _monitor_and_repair(self):
        """Main monitoring and repair loop"""
        while self.running:
            try:
                self._perform_health_checks()
                time.sleep(self.repair_interval)
            except Exception as e:
                print(f"⚠️  Self-repair monitoring error: {e}")
                time.sleep(10)  # Brief pause before retrying

    def _perform_health_checks(self):
        """Perform health checks and initiate repairs as needed"""
        health_results = self.blueprint_manager.health_check_all()

        for component_info in health_results["details"]:
            component_name = component_info["instance_id"].split('_')[0]  # Extract base name

            if not component_info["healthy"]:
                failure_pattern = self._diagnose_failure(component_name, component_info)
                self._initiate_repair(component_name, failure_pattern, component_info)

    def _diagnose_failure(self, component_name: str, component_info: Dict[str, Any]) -> FailurePattern:
        """
        Diagnose the failure pattern for a component.

        Args:
            component_name: Name of the failed component
            component_info: Health check information

        Returns:
            Identified failure pattern
        """
        errors = component_info.get("errors", 0)

        # Check recent repair history for patterns
        recent_repairs = [
            action for action in self.repair_history[-10:]  # Last 10 repairs
            if action.component_name == component_name
        ]

        # Crash loop detection
        if errors > 5 and len(recent_repairs) >= 3:
            recent_failures = sum(1 for r in recent_repairs[-3:] if not r.success)
            if recent_failures >= 2:
                return FailurePattern.CRASH_LOOP

        # Memory leak detection (would need actual memory monitoring)
        # For now, assume unknown
        return FailurePattern.UNKNOWN

    def attempt_repair(self, component_name: str, failure_pattern: 'Optional[FailurePattern]' = None,
                      context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attempt to repair a component.

        Args:
            component_name: Name of the component to repair
            failure_pattern: Known failure pattern (auto-diagnosed if None)
            context: Additional repair context

        Returns:
            Repair success status
        """
        start_time = time.time()

        # Auto-diagnose if pattern not provided
        if failure_pattern is None:
            # Get component health info
            health_results = self.blueprint_manager.health_check_all()
            component_info = next(
                (info for info in health_results["details"]
                 if info["instance_id"].startswith(component_name)),
                {"healthy": True, "errors": 0}
            )
            failure_pattern = self._diagnose_failure(component_name, component_info)

        # Get repair strategies for this pattern
        strategies = self.repair_strategies.get(failure_pattern, [RepairStrategy.ESCALATE])

        # Try each strategy in order
        for strategy in strategies:
            repair_action = RepairAction(
                component_name=component_name,
                strategy=strategy,
                failure_pattern=failure_pattern,
                details={
                    "context": context or {},
                    "strategy_attempted": strategy.value
                }
            )

            success = self._execute_repair_strategy(component_name, strategy, repair_action)

            duration = time.time() - start_time
            repair_action.complete(success, duration)

            self.repair_history.append(repair_action)

            # Maintain history size
            if len(self.repair_history) > self.max_history_size:
                self.repair_history = self.repair_history[-self.max_history_size:]

            # Update statistics
            self.repair_stats["total_attempts"] += 1
            if success:
                self.repair_stats["successful_repairs"] += 1
                return True
            else:
                self.repair_stats["failed_repairs"] += 1

        # All strategies failed
        self.repair_stats["escalations"] += 1
        return False

    def _execute_repair_strategy(self, component_name: str, strategy: RepairStrategy,
                                repair_action: RepairAction) -> bool:
        """
        Execute a specific repair strategy.

        Args:
            component_name: Component to repair
            strategy: Repair strategy to execute
            repair_action: Repair action record

        Returns:
            Strategy execution success
        """
        try:
            if strategy == RepairStrategy.RESTART:
                return self._repair_restart(component_name, repair_action)

            elif strategy == RepairStrategy.REINITIALIZE:
                return self._repair_reinitialize(component_name, repair_action)

            elif strategy == RepairStrategy.FAILOVER:
                return self._repair_failover(component_name, repair_action)

            elif strategy == RepairStrategy.RECONFIGURE:
                return self._repair_reconfigure(component_name, repair_action)

            elif strategy == RepairStrategy.REPLACE:
                return self._repair_replace(component_name, repair_action)

            elif strategy == RepairStrategy.ESCALATE:
                return self._repair_escalate(component_name, repair_action)

            else:
                print(f"⚠️  Unknown repair strategy: {strategy}")
                return False

        except Exception as e:
            print(f"❌ Repair strategy {strategy.value} failed for {component_name}: {e}")
            repair_action.error_message = str(e)
            return False

    def _repair_restart(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute restart repair strategy"""
        print(f"🔄 Attempting restart repair for {component_name}")

        # Stop the component
        if not self.lifecycle_controller.stop_component(component_name):
            return False

        # Wait a moment
        time.sleep(2)

        # Start the component
        if self.lifecycle_controller.start_component(component_name):
            repair_action.details["restart_successful"] = True
            return True

        return False

    def _repair_reinitialize(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute reinitialize repair strategy"""
        print(f"🔄 Attempting reinitialize repair for {component_name}")

        # Get the component instance
        instance = self.blueprint_manager.get_component_instance(component_name)
        if not instance:
            return False

        # Try to reinitialize if the instance supports it
        if hasattr(instance, 'reinitialize'):
            try:
                result = instance.reinitialize()
                repair_action.details["reinitialize_result"] = result
                return result is True
            except Exception as e:
                repair_action.details["reinitialize_error"] = str(e)
                return False

        # Fallback to restart
        return self._repair_restart(component_name, repair_action)

    def _repair_failover(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute failover repair strategy"""
        print(f"🔄 Attempting failover repair for {component_name}")

        # For now, this is similar to restart
        # In a real implementation, this would switch to a backup instance
        repair_action.details["failover_note"] = "failover_not_implemented_yet"
        return self._repair_restart(component_name, repair_action)

    def _repair_reconfigure(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute reconfigure repair strategy"""
        print(f"🔄 Attempting reconfigure repair for {component_name}")

        # Get the component instance
        instance = self.blueprint_manager.get_component_instance(component_name)
        if not instance:
            return False

        # Try to reconfigure if the instance supports it
        if hasattr(instance, 'reconfigure'):
            try:
                # Use default configuration
                result = instance.reconfigure({})
                repair_action.details["reconfigure_result"] = result
                return result is True
            except Exception as e:
                repair_action.details["reconfigure_error"] = str(e)
                return False

        # Fallback to restart
        return self._repair_restart(component_name, repair_action)

    def _repair_replace(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute replace repair strategy"""
        print(f"🔄 Attempting replace repair for {component_name}")

        # Destroy the current instance
        if not self.blueprint_manager.destroy_component(component_name):
            return False

        # Create a new instance
        new_instance_id = self.blueprint_manager.instantiate_component(component_name)
        if new_instance_id:
            repair_action.details["new_instance_id"] = new_instance_id
            return True

        return False

    def _repair_escalate(self, component_name: str, repair_action: RepairAction) -> bool:
        """Execute escalate repair strategy (human intervention)"""
        print(f"🚨 Escalating repair for {component_name} - requires human intervention")

        repair_action.details["escalation_reason"] = "all_automated_repairs_failed"
        repair_action.details["escalation_timestamp"] = datetime.now().isoformat()

        # In a real system, this would send alerts, create tickets, etc.
        # For now, just log the escalation
        return False  # Escalation is not considered a "successful repair"

    def _initiate_repair(self, component_name: str, failure_pattern: FailurePattern,
                        component_info: Dict[str, Any]):
        """Initiate repair for a failed component"""
        print(f"🔧 Initiating repair for {component_name} (pattern: {failure_pattern.value})")

        success = self.attempt_repair(
            component_name=component_name,
            failure_pattern=failure_pattern,
            context={
                "health_info": component_info,
                "auto_initiated": True,
                "failure_timestamp": datetime.now().isoformat()
            }
        )

        if success:
            print(f"✅ Auto-repair successful for {component_name}")
        else:
            print(f"❌ Auto-repair failed for {component_name}")

    def get_repair_history(self, component_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get repair history.

        Args:
            component_name: Optional component name filter
            limit: Maximum number of records to return

        Returns:
            List of repair action records
        """
        history = self.repair_history

        if component_name:
            history = [action for action in history if action.component_name == component_name]

        return [action.to_dict() for action in history[-limit:]]

    def get_repair_statistics(self) -> Dict[str, Any]:
        """Get repair statistics"""
        total_attempts = self.repair_stats["total_attempts"]

        return {
            "total_repair_attempts": total_attempts,
            "successful_repairs": self.repair_stats["successful_repairs"],
            "failed_repairs": self.repair_stats["failed_repairs"],
            "escalations": self.repair_stats["escalations"],
            "success_rate": round(self.repair_stats["successful_repairs"] / total_attempts * 100, 1) if total_attempts > 0 else 0,
            "escalation_rate": round(self.repair_stats["escalations"] / total_attempts * 100, 1) if total_attempts > 0 else 0,
            "recent_repairs": len([r for r in self.repair_history[-100:] if (datetime.now() - r.timestamp).days < 1])
        }

    def get_healthy_component_count(self) -> int:
        """Get count of healthy components"""
        health_results = self.blueprint_manager.health_check_all()
        return health_results["healthy"]

    def get_failed_component_count(self) -> int:
        """Get count of failed components"""
        health_results = self.blueprint_manager.health_check_all()
        return health_results["failed"]

    def analyze_repair_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze the effectiveness of repair strategies.

        Returns:
            Repair effectiveness analysis
        """
        if not self.repair_history:
            return {"status": "no_repair_history"}

        # Strategy success rates
        strategy_stats = {}
        for action in self.repair_history:
            strategy = action.strategy.value
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"attempts": 0, "successes": 0}

            strategy_stats[strategy]["attempts"] += 1
            if action.success:
                strategy_stats[strategy]["successes"] += 1

        # Calculate success rates
        for strategy, stats in strategy_stats.items():
            stats["success_rate"] = round(stats["successes"] / stats["attempts"] * 100, 1)

        # Pattern analysis
        pattern_stats = {}
        for action in self.repair_history:
            pattern = action.failure_pattern.value
            if pattern not in pattern_stats:
                pattern_stats[pattern] = {"occurrences": 0, "resolved": 0}

            pattern_stats[pattern]["occurrences"] += 1
            if action.success:
                pattern_stats[pattern]["resolved"] += 1

        # Calculate resolution rates
        for pattern, stats in pattern_stats.items():
            stats["resolution_rate"] = round(stats["resolved"] / stats["occurrences"] * 100, 1)

        return {
            "strategy_effectiveness": strategy_stats,
            "pattern_analysis": pattern_stats,
            "overall_success_rate": round(
                sum(s["successes"] for s in strategy_stats.values()) /
                sum(s["attempts"] for s in strategy_stats.values()) * 100, 1
            ) if strategy_stats else 0,
            "most_effective_strategy": max(
                strategy_stats.items(),
                key=lambda x: x[1]["success_rate"]
            )[0] if strategy_stats else None
        }

    def predictive_repair(self) -> List[Dict[str, Any]]:
        """
        Perform predictive repair analysis.

        Returns:
            List of components that may need preventive repair
        """
        predictions = []

        # Analyze repair history for patterns
        component_failures = {}
        for action in self.repair_history[-200:]:  # Last 200 repairs
            comp = action.component_name
            if comp not in component_failures:
                component_failures[comp] = []
            component_failures[comp].append(action.timestamp)

        # Predict components at risk
        for comp, failures in component_failures.items():
            if len(failures) >= 3:
                # Calculate failure frequency
                sorted_failures = sorted(failures)
                intervals = [
                    (sorted_failures[i+1] - sorted_failures[i]).days
                    for i in range(len(sorted_failures)-1)
                ]

                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    days_since_last = (datetime.now() - sorted_failures[-1]).days

                    # If we're past 80% of average interval, flag for preventive repair
                    if days_since_last > avg_interval * 0.8:
                        predictions.append({
                            "component": comp,
                            "risk_level": "high" if days_since_last > avg_interval else "medium",
                            "days_since_last_failure": days_since_last,
                            "average_failure_interval": round(avg_interval, 1),
                            "recommendation": "schedule_preventive_repair"
                        })

        return predictions