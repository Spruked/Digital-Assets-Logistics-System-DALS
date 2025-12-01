# lifecycle_control.py

"""
Lifecycle Control - Dynamic Component Management System

This module provides comprehensive lifecycle management for vault system
components, enabling dynamic loading, suspension, resumption, and graceful
shutdown of system components.
"""

import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import logging


class LifecycleState(Enum):
    """Possible states for component lifecycle"""
    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    STARTING = "starting"
    ACTIVE = "active"
    SUSPENDING = "suspending"
    SUSPENDED = "suspended"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    RECOVERING = "recovering"


class ComponentHealth(Enum):
    """Health status of components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentRecord:
    """
    Record of a registered component with its lifecycle information.
    """

    def __init__(self, name: str, start_function: Callable,
                 stop_function: Optional[Callable] = None,
                 repair_function: Optional[Callable] = None,
                 health_check_function: Optional[Callable] = None):
        """
        Initialize a component record.

        Args:
            name: Component name
            start_function: Function to start the component
            stop_function: Optional function to stop the component
            repair_function: Optional function to repair the component
            health_check_function: Optional function to check component health
        """
        self.name = name
        self.start_function = start_function
        self.stop_function = stop_function
        self.repair_function = repair_function
        self.health_check_function = health_check_function

        # Lifecycle state
        self.state = LifecycleState.REGISTERED
        self.health = ComponentHealth.UNKNOWN

        # Timestamps
        self.registered_at: datetime = datetime.now()
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None  # type: ignore[assignment]
        self.last_health_check: Optional[datetime] = None

        # Statistics
        self.start_count = 0
        self.stop_count = 0
        self.failure_count = 0
        self.repair_count = 0

        # Health monitoring
        self.consecutive_failures = 0
        self.last_error: Optional[str] = None

    def can_start(self) -> bool:
        """Check if component can be started"""
        return self.state in [LifecycleState.REGISTERED, LifecycleState.STOPPED, LifecycleState.FAILED]

    def can_stop(self) -> bool:
        """Check if component can be stopped"""
        return self.state in [LifecycleState.ACTIVE, LifecycleState.SUSPENDED]

    def can_suspend(self) -> bool:
        """Check if component can be suspended"""
        return self.state == LifecycleState.ACTIVE

    def can_resume(self) -> bool:
        """Check if component can be resumed"""
        return self.state == LifecycleState.SUSPENDED

    def get_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": self.name,
            "state": self.state.value,
            "health": self.health.value,
            "registered_at": self.registered_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "start_count": self.start_count,
            "stop_count": self.stop_count,
            "failure_count": self.failure_count,
            "repair_count": self.repair_count,
            "consecutive_failures": self.consecutive_failures,
            "last_error": str(self.last_error) if self.last_error else None
        }


class LifecycleController:
    """
    Controller for managing component lifecycles in the vault system.

    Provides centralized control over component startup, shutdown,
    suspension, and health monitoring.
    """

    def __init__(self, health_check_interval: int = 60, max_consecutive_failures: int = 3):
        """
        Initialize the lifecycle controller.

        Args:
            health_check_interval: Health check interval in seconds
            max_consecutive_failures: Max consecutive failures before marking unhealthy
        """
        self.components: Dict[str, ComponentRecord] = {}
        self.active_components: set = set()
        self.suspended_components: set = set()

        # Configuration
        self.health_check_interval = health_check_interval
        self.max_consecutive_failures = max_consecutive_failures

        # Background processing
        self.running = False
        self.health_thread = None
        self.lock = threading.RLock()

        # Event callbacks
        self.state_change_callbacks: List[Callable] = []
        self.health_change_callbacks: List[Callable] = []
        self.failure_callbacks: List[Callable] = []

        # Logging
        self.logger = logging.getLogger("LifecycleController")

        print("🔄 Lifecycle Controller initialized")

    def register_component(self, name: str, start_function: Callable,
                          stop_function: Optional[Callable] = None,
                          repair_function: Optional[Callable] = None,
                          health_check_function: Optional[Callable] = None) -> bool:
        """
        Register a component with the lifecycle controller.

        Args:
            name: Component name
            start_function: Function to start the component
            stop_function: Optional function to stop the component
            repair_function: Optional function to repair the component
            health_check_function: Optional function to check health

        Returns:
            Registration success status
        """
        with self.lock:
            if name in self.components:
                self.logger.warning(f"Component {name} already registered")
                return False

            component = ComponentRecord(
                name=name,
                start_function=start_function,
                stop_function=stop_function,
                repair_function=repair_function,
                health_check_function=health_check_function
            )

            self.components[name] = component
            self._notify_state_change(name, LifecycleState.UNREGISTERED, LifecycleState.REGISTERED)

            self.logger.info(f"Registered component: {name}")
            return True

    def unregister_component(self, name: str) -> bool:
        """
        Unregister a component from the lifecycle controller.

        Args:
            name: Component name

        Returns:
            Unregistration success status
        """
        with self.lock:
            if name not in self.components:
                return False

            component = self.components[name]

            # Stop component if it's active
            if component.state == LifecycleState.ACTIVE:
                self.stop_component(name)

            # Remove from sets
            self.active_components.discard(name)
            self.suspended_components.discard(name)

            # Unregister
            del self.components[name]
            self._notify_state_change(name, component.state, LifecycleState.UNREGISTERED)

            self.logger.info(f"Unregistered component: {name}")
            return True

    def start_component(self, name: str) -> bool:
        """
        Start a registered component.

        Args:
            name: Component name

        Returns:
            Start success status
        """
        with self.lock:
            if name not in self.components:
                self.logger.error(f"Component {name} not registered")
                return False

            component = self.components[name]

            if not component.can_start():
                self.logger.warning(f"Cannot start component {name} in state {component.state.value}")
                return False

            try:
                component.state = LifecycleState.STARTING
                self._notify_state_change(name, LifecycleState.REGISTERED, LifecycleState.STARTING)

                # Call start function
                result = component.start_function(component)

                if result is None or result is True:
                    component.state = LifecycleState.ACTIVE
                    component.started_at = datetime.now()
                    component.start_count += 1
                    component.consecutive_failures = 0
                    component.last_error = None

                    self.active_components.add(name)
                    self.suspended_components.discard(name)

                    self._notify_state_change(name, LifecycleState.STARTING, LifecycleState.ACTIVE)
                    self.logger.info(f"Started component: {name}")
                    return True
                else:
                    raise Exception(f"Start function returned failure: {result}")

            except Exception as e:

                component.state = LifecycleState.FAILED
                component.failure_count += 1
                component.consecutive_failures += 1
                component.last_error = str(e)

                self._notify_state_change(name, LifecycleState.STARTING, LifecycleState.FAILED)
                self._notify_failure(name, e)

                self.logger.error(f"Failed to start component {name}: {e}")
                return False

    def stop_component(self, name: str, graceful: bool = True) -> bool:
        """
        Stop a component.

        Args:
            name: Component name
            graceful: Whether to perform graceful shutdown

        Returns:
            Stop success status
        """
        with self.lock:
            if name not in self.components:
                return False

            component = self.components[name]

            if not component.can_stop():
                self.logger.warning(f"Cannot stop component {name} in state {component.state.value}")
                return False

            try:
                component.state = LifecycleState.STOPPING
                self._notify_state_change(name, component.state, LifecycleState.STOPPING)

                # Call stop function if available
                if component.stop_function:
                    component.stop_function(component, graceful)

                component.state = LifecycleState.STOPPED
                component.stopped_at = datetime.now()
                component.stop_count += 1

                self.active_components.discard(name)
                self.suspended_components.discard(name)

                self._notify_state_change(name, LifecycleState.STOPPING, LifecycleState.STOPPED)
                self.logger.info(f"Stopped component: {name}")
                return True

            except Exception as e:

                component.state = LifecycleState.FAILED
                component.failure_count += 1
                component.last_error = str(e)

                self._notify_failure(name, e)

                self.logger.error(f"Error stopping component {name}: {e}")
                return False

    def suspend_component(self, name: str) -> bool:
        """
        Suspend a component temporarily.

        Args:
            name: Component name

        Returns:
            Suspension success status
        """
        with self.lock:
            if name not in self.components:
                return False

            component = self.components[name]

            if not component.can_suspend():
                self.logger.warning(f"Cannot suspend component {name} in state {component.state.value}")
                return False

            try:
                component.state = LifecycleState.SUSPENDING
                self._notify_state_change(name, LifecycleState.ACTIVE, LifecycleState.SUSPENDING)

                # For now, suspension is just a state change
                # Components can implement custom suspend logic in their stop function
                if component.stop_function:
                    component.stop_function(component, graceful=True)

                component.state = LifecycleState.SUSPENDED

                self.active_components.discard(name)
                self.suspended_components.add(name)

                self._notify_state_change(name, LifecycleState.SUSPENDING, LifecycleState.SUSPENDED)
                self.logger.info(f"Suspended component: {name}")
                return True

            except Exception as e:

                component.state = LifecycleState.FAILED
                component.last_error = str(e)

                self._notify_failure(name, e)

                self.logger.error(f"Error suspending component {name}: {e}")
                return False

    def resume_component(self, name: str) -> bool:
        """
        Resume a suspended component.

        Args:
            name: Component name

        Returns:
            Resume success status
        """
        with self.lock:
            if name not in self.components:
                return False

            component = self.components[name]

            if not component.can_resume():
                self.logger.warning(f"Cannot resume component {name} in state {component.state.value}")
                return False

            try:
                # Resume is essentially a restart for suspended components
                return self.start_component(name)

            except Exception as e:

                component.state = LifecycleState.FAILED
                component.last_error = str(e)

                self._notify_failure(name, e)

                self.logger.error(f"Error resuming component {name}: {e}")
                return False

    def repair_component(self, name: str) -> bool:
        """
        Attempt to repair a failed component.

        Args:
            name: Component name

        Returns:
            Repair success status
        """
        with self.lock:
            if name not in self.components:
                return False

            component = self.components[name]

            if component.state != LifecycleState.FAILED:
                self.logger.warning(f"Component {name} is not in failed state")
                return False

            if not component.repair_function:
                self.logger.warning(f"No repair function available for {name}")
                return False

            try:
                component.state = LifecycleState.RECOVERING
                self._notify_state_change(name, LifecycleState.FAILED, LifecycleState.RECOVERING)

                # Call repair function
                result = component.repair_function(component)

                if result:
                    component.state = LifecycleState.STOPPED
                    component.repair_count += 1
                    component.consecutive_failures = 0
                    component.last_error = None

                    self._notify_state_change(name, LifecycleState.RECOVERING, LifecycleState.STOPPED)
                    self.logger.info(f"Repaired component: {name}")
                    return True
                else:
                    component.state = LifecycleState.FAILED
                    self._notify_state_change(name, LifecycleState.RECOVERING, LifecycleState.FAILED)
                    self.logger.warning(f"Repair failed for component: {name}")
                    return False

            except Exception as e:
                component.state = LifecycleState.FAILED
                component.last_error = str(e)

                self._notify_failure(name, e)

                self.logger.error(f"Error repairing component {name}: {e}")
                return False

    def get_component_state(self, name: str) -> Optional[LifecycleState]:
        """Get the current state of a component"""
        component = self.components.get(name)
        return component.state if component else None

    def get_component_health(self, name: str) -> Optional[ComponentHealth]:
        """Get the current health of a component"""
        component = self.components.get(name)
        return component.health if component else None

    def list_components(self, state_filter: Optional[LifecycleState] = None) -> List[Dict[str, Any]]:
        """
        List all registered components.

        Args:
            state_filter: Optional state filter

        Returns:
            List of component information
        """
        components = self.components.values()

        if state_filter:
            components = [c for c in components if c.state == state_filter]

        return [component.get_info() for component in components]

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health based on component states.

        Returns:
            System health information
        """
        total_components = len(self.components)
        if total_components == 0:
            return {"overall_health": "no_components", "score": 0}

        active_count = len(self.active_components)
        suspended_count = len(self.suspended_components)
        failed_count = sum(1 for c in self.components.values() if c.state == LifecycleState.FAILED)

        # Calculate health score (0-100)
        active_score = (active_count / total_components) * 100
        failure_penalty = (failed_count / total_components) * 50  # Failed components heavily penalize score

        health_score = max(0, active_score - failure_penalty)

        # Determine overall health status
        if health_score >= 90:
            overall_health = "excellent"
        elif health_score >= 75:
            overall_health = "good"
        elif health_score >= 60:
            overall_health = "fair"
        elif health_score >= 40:
            overall_health = "poor"
        else:
            overall_health = "critical"

        return {
            "overall_health": overall_health,
            "health_score": round(health_score, 1),
            "total_components": total_components,
            "active_components": active_count,
            "suspended_components": suspended_count,
            "failed_components": failed_count,
            "healthy_percentage": round((active_count / total_components) * 100, 1) if total_components > 0 else 0
        }

    def start_all_components(self) -> Dict[str, Any]:
        """
        Start all registered components.

        Returns:
            Startup results
        """
        results = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "details": []
        }

        for name in list(self.components.keys()):
            results["attempted"] += 1
            if self.start_component(name):
                results["successful"] += 1
                results["details"].append({"name": name, "result": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"name": name, "result": "failed"})

        return results

    def stop_all_components(self, graceful: bool = True) -> Dict[str, Any]:
        """
        Stop all active components.

        Returns:
            Shutdown results
        """
        results = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "details": []
        }

        # Stop active components first
        for name in list(self.active_components):
            results["attempted"] += 1
            if self.stop_component(name, graceful):
                results["successful"] += 1
                results["details"].append({"name": name, "result": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"name": name, "result": "failed"})

        # Then stop suspended components
        for name in list(self.suspended_components):
            results["attempted"] += 1
            if self.stop_component(name, graceful):
                results["successful"] += 1
                results["details"].append({"name": name, "result": "success"})
            else:
                results["failed"] += 1
                results["details"].append({"name": name, "result": "failed"})

        return results

    def _perform_health_checks(self):
        """Perform periodic health checks on all components"""
        while self.running:
            try:
                for name, component in self.components.items():
                    if component.health_check_function and component.state == LifecycleState.ACTIVE:
                        try:
                            is_healthy = component.health_check_function(component)

                            new_health = ComponentHealth.HEALTHY if is_healthy else ComponentHealth.UNHEALTHY
                            old_health = component.health

                            if new_health != old_health:
                                component.health = new_health
                                component.last_health_check = datetime.now()

                                if new_health == ComponentHealth.UNHEALTHY:
                                    component.consecutive_failures += 1

                                    # Notify health change
                                    self._notify_health_change(name, old_health, new_health)

                                    # Auto-repair if too many consecutive failures
                                    if component.consecutive_failures >= self.max_consecutive_failures:
                                        self.logger.warning(f"Component {name} has {component.consecutive_failures} consecutive failures, attempting repair")
                                        self.repair_component(name)
                                else:
                                    component.consecutive_failures = 0

                        except Exception as e:
                            self.logger.error(f"Health check failed for {name}: {e}")
                            component.consecutive_failures += 1

                time.sleep(self.health_check_interval)

            except Exception as e:
                self.logger.error(f"Health check cycle error: {e}")
                time.sleep(10)  # Brief pause before retrying

    def start_health_monitoring(self):
        """Start the health monitoring thread"""
        if self.running:
            return

        self.running = True
        self.health_thread = threading.Thread(target=self._perform_health_checks, daemon=True)
        self.health_thread.start()

        self.logger.info("Started health monitoring")

    def stop_health_monitoring(self):
        """Stop the health monitoring thread"""
        self.running = False
        if self.health_thread:
            self.health_thread.join(timeout=5)

        self.logger.info("Stopped health monitoring")

    def add_state_change_callback(self, callback: Callable):
        """
        Add a callback for state change events.

        Args:
            callback: Function to call on state changes
        """
        self.state_change_callbacks.append(callback)

    def add_health_change_callback(self, callback: Callable):
        """
        Add a callback for health change events.

        Args:
            callback: Function to call on health changes
        """
        self.health_change_callbacks.append(callback)

    def add_failure_callback(self, callback: Callable):
        """
        Add a callback for failure events.

        Args:
            callback: Function to call on failures
        """
        self.failure_callbacks.append(callback)

    def _notify_state_change(self, component_name: str, old_state: LifecycleState, new_state: LifecycleState):
        """Notify state change callbacks"""
        for callback in self.state_change_callbacks:
            try:
                callback(component_name, old_state, new_state)
            except Exception as e:
                self.logger.error(f"State change callback error: {e}")

    def _notify_health_change(self, component_name: str, old_health: ComponentHealth, new_health: ComponentHealth):
        """Notify health change callbacks"""
        for callback in self.health_change_callbacks:
            try:
                callback(component_name, old_health, new_health)
            except Exception as e:
                self.logger.error(f"Health change callback error: {e}")

    def _notify_failure(self, component_name: str, error: Exception):
        """Notify failure callbacks"""
        for callback in self.failure_callbacks:
            try:
                callback(component_name, error)
            except Exception as e:
                self.logger.error(f"Failure callback error: {e}")

    def graceful_shutdown(self):
        """Perform graceful shutdown of all components"""
        self.logger.info("Initiating graceful shutdown")

        # Stop health monitoring
        self.stop_health_monitoring()

        # Stop all components
        shutdown_results = self.stop_all_components(graceful=True)

        self.logger.info(f"Graceful shutdown complete: {shutdown_results['successful']}/{shutdown_results['attempted']} components stopped")

        return shutdown_results