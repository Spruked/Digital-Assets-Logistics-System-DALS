# dual_core_integration.py

"""
Dual-Core Integration - Hemispheric Synchronization System

This module provides dual-core integration capabilities, enabling the vault system
to operate with hemispheric synchronization similar to human brain function.
"""

import asyncio
import threading
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from vault_core.ISS_bridge import ISSConnector


class SynchronizationMode(Enum):
    """Modes for hemispheric synchronization"""
    REDUNDANT = "redundant"      # Both hemispheres maintain identical state
    MIRROR = "mirror"           # Hemispheres mirror each other's operations
    SPECIALIZED = "specialized" # Hemispheres specialize in different functions
    COMPETITIVE = "competitive" # Hemispheres compete for optimal solutions
    COLLABORATIVE = "collaborative" # Hemispheres work together on complex tasks


class Hemisphere(Enum):
    """Hemisphere identifiers"""
    LEFT = "left"
    RIGHT = "right"


@dataclass
class HemisphereMapping:
    """
    Mapping between left and right hemisphere instances.
    """
    component_name: str
    left_instance: Any
    right_instance: Any
    sync_mode: SynchronizationMode
    last_sync: Optional[datetime] = None
    sync_interval: int = 30  # seconds
    health_status: Optional[Dict[str, bool]] = None

    def __post_init__(self):
        if self.health_status is None:
            self.health_status = {Hemisphere.LEFT.value: True, Hemisphere.RIGHT.value: True}


class SynchronizationEvent:
    """
    Represents a synchronization event between hemispheres.
    """

    def __init__(self, component_name: str, event_type: str,
                 source_hemisphere: Hemisphere, data: Dict[str, Any]):
        """
        Initialize a synchronization event.

        Args:
            component_name: Name of the component being synchronized
            event_type: Type of synchronization event
            source_hemisphere: Hemisphere that initiated the event
            data: Event data
        """
        self.component_name = component_name
        self.event_type = event_type
        self.source_hemisphere = source_hemisphere
        self.data = data
        self.timestamp = datetime.now()
        self.event_id = f"sync_{int(time.time()*1000000)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "component_name": self.component_name,
            "event_type": self.event_type,
            "source_hemisphere": self.source_hemisphere.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class DualCoreIntegration:
    """
    Dual-core integration system providing hemispheric synchronization.

    This system enables the vault to operate with left/right brain-like
    processing, with different synchronization modes for different components.
    """

    def __init__(self, iss_connector: ISSConnector, lifecycle_controller):
        """
        Initialize dual-core integration.

        Args:
            iss_connector: ISS connector for inter-system communication
            lifecycle_controller: Lifecycle controller for component management
        """
        self.iss_connector = iss_connector
        self.lifecycle_controller = lifecycle_controller

        # Hemisphere mappings
        self.hemisphere_mappings: Dict[str, HemisphereMapping] = {}

        # Synchronization state
        self.sync_events: List[SynchronizationEvent] = []
        self.max_events = 1000

        # Synchronization tasks
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        self.running = False

        # Performance metrics
        self.sync_performance = {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "avg_sync_time": 0.0
        }

        # Hemisphere specialization
        self.hemisphere_specializations = {
            Hemisphere.LEFT: ["logical", "analytical", "sequential"],
            Hemisphere.RIGHT: ["intuitive", "creative", "parallel"]
        }

        print("🧠 Dual-Core Integration initialized")

    def register_hemisphere_mapping(self, component_name: str, left_instance: Any,
                                   right_instance: Any, sync_mode: SynchronizationMode,
                                   sync_interval: int = 30):
        """
        Register a hemisphere mapping for a component.

        Args:
            component_name: Name of the component
            left_instance: Left hemisphere instance
            right_instance: Right hemisphere instance
            sync_mode: Synchronization mode
            sync_interval: Sync interval in seconds
        """
        mapping = HemisphereMapping(
            component_name=component_name,
            left_instance=left_instance,
            right_instance=right_instance,
            sync_mode=sync_mode,
            sync_interval=sync_interval
        )

        self.hemisphere_mappings[component_name] = mapping

        # Start synchronization task
        if self.running:
            self._start_sync_task(component_name)

        print(f"✅ Registered hemisphere mapping for {component_name} ({sync_mode.value})")

    def unregister_hemisphere_mapping(self, component_name: str):
        """
        Unregister a hemisphere mapping.

        Args:
            component_name: Name of the component
        """
        if component_name in self.hemisphere_mappings:
            # Stop sync task
            if component_name in self.sync_tasks:
                self.sync_tasks[component_name].cancel()
                del self.sync_tasks[component_name]

            del self.hemisphere_mappings[component_name]
            print(f"✅ Unregistered hemisphere mapping for {component_name}")

    def start_synchronization(self):
        """Start all synchronization tasks"""
        if self.running:
            return

        self.running = True

        for component_name in self.hemisphere_mappings.keys():
            self._start_sync_task(component_name)

        print("🔄 Started dual-core synchronization")

    def stop_synchronization(self):
        """Stop all synchronization tasks"""
        self.running = False

        for task in self.sync_tasks.values():
            task.cancel()

        self.sync_tasks.clear()
        print("🛑 Stopped dual-core synchronization")

    def _start_sync_task(self, component_name: str):
        """Start synchronization task for a component"""
        if component_name not in self.hemisphere_mappings:
            return

        async def sync_loop():
            while self.running and component_name in self.hemisphere_mappings:
                try:
                    await self._perform_synchronization(component_name)
                    mapping = self.hemisphere_mappings[component_name]
                    await asyncio.sleep(mapping.sync_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"⚠️  Sync error for {component_name}: {e}")
                    await asyncio.sleep(10)  # Brief pause before retry

        task = asyncio.create_task(sync_loop())
        self.sync_tasks[component_name] = task

    async def _perform_synchronization(self, component_name: str):
        """Perform synchronization for a component"""
        if component_name not in self.hemisphere_mappings:
            return

        mapping = self.hemisphere_mappings[component_name]
        start_time = time.time()

        try:
            if mapping.sync_mode == SynchronizationMode.REDUNDANT:
                success = await self._sync_redundant(mapping)
            elif mapping.sync_mode == SynchronizationMode.MIRROR:
                success = await self._sync_mirror(mapping)
            elif mapping.sync_mode == SynchronizationMode.SPECIALIZED:
                success = await self._sync_specialized(mapping)
            elif mapping.sync_mode == SynchronizationMode.COMPETITIVE:
                success = await self._sync_competitive(mapping)
            elif mapping.sync_mode == SynchronizationMode.COLLABORATIVE:
                success = await self._sync_collaborative(mapping)
            else:
                print(f"⚠️  Unknown sync mode for {component_name}: {mapping.sync_mode}")
                return

            duration = time.time() - start_time
            mapping.last_sync = datetime.now()

            # Update performance metrics
            self.sync_performance["total_syncs"] += 1
            if success:
                self.sync_performance["successful_syncs"] += 1
            else:
                self.sync_performance["failed_syncs"] += 1

            # Update average sync time
            total_time = self.sync_performance["avg_sync_time"] * (self.sync_performance["total_syncs"] - 1) + duration
            self.sync_performance["avg_sync_time"] = total_time / self.sync_performance["total_syncs"]

            # Record sync event
            event = SynchronizationEvent(
                component_name=component_name,
                event_type="sync_completed" if success else "sync_failed",
                source_hemisphere=Hemisphere.LEFT,  # Arbitrary choice
                data={
                    "success": success,
                    "duration": duration,
                    "sync_mode": mapping.sync_mode.value
                }
            )
            self._record_sync_event(event)

        except Exception as e:
            print(f"❌ Synchronization failed for {component_name}: {e}")

            # Record failure event
            event = SynchronizationEvent(
                component_name=component_name,
                event_type="sync_error",
                source_hemisphere=Hemisphere.LEFT,
                data={"error": str(e), "sync_mode": mapping.sync_mode.value}
            )
            self._record_sync_event(event)

    async def _sync_redundant(self, mapping: HemisphereMapping) -> bool:
        """Perform redundant synchronization (identical state)"""
        try:
            # In redundant mode, ensure both hemispheres have identical state
            # This is a simplified implementation

            # Check if both instances are healthy
            left_healthy = await self._check_hemisphere_health(mapping.left_instance, Hemisphere.LEFT)
            right_healthy = await self._check_hemisphere_health(mapping.right_instance, Hemisphere.RIGHT)

            if not left_healthy or not right_healthy:
                return False

            # For vault components, ensure data consistency
            if hasattr(mapping.left_instance, 'get_vault_stats'):
                left_stats = mapping.left_instance.get_vault_stats()
                right_stats = mapping.right_instance.get_vault_stats()

                # Simple consistency check
                if left_stats.get('total_entries') != right_stats.get('total_entries'):
                    # Trigger reconciliation
                    await self._reconcile_vault_data(mapping)
                    return True

            return True

        except Exception as e:
            print(f"❌ Redundant sync failed: {e}")
            return False

    async def _sync_mirror(self, mapping: HemisphereMapping) -> bool:
        """Perform mirror synchronization (reflect operations)"""
        try:
            # In mirror mode, operations on one hemisphere are reflected to the other

            # Check health
            left_healthy = await self._check_hemisphere_health(mapping.left_instance, Hemisphere.LEFT)
            right_healthy = await self._check_hemisphere_health(mapping.right_instance, Hemisphere.RIGHT)

            if not left_healthy or not right_healthy:
                return False

            # For mirror sync, we could implement operation mirroring
            # This is a simplified version that just ensures both are operational

            return True

        except Exception as e:
            print(f"❌ Mirror sync failed: {e}")
            return False

    async def _sync_specialized(self, mapping: HemisphereMapping) -> bool:
        """Perform specialized synchronization (different functions)"""
        try:
            # In specialized mode, hemispheres perform different functions
            # Left: logical/analytical, Right: intuitive/creative

            left_healthy = await self._check_hemisphere_health(mapping.left_instance, Hemisphere.LEFT)
            right_healthy = await self._check_hemisphere_health(mapping.right_instance, Hemisphere.RIGHT)

            if not left_healthy or not right_healthy:
                return False

            # Specialized sync could involve cross-hemisphere collaboration
            # For now, just ensure both are healthy

            return True

        except Exception as e:
            print(f"❌ Specialized sync failed: {e}")
            return False

    async def _sync_competitive(self, mapping: HemisphereMapping) -> bool:
        """Perform competitive synchronization (optimal solutions)"""
        try:
            # In competitive mode, hemispheres compete for best solutions

            left_healthy = await self._check_hemisphere_health(mapping.left_instance, Hemisphere.LEFT)
            right_healthy = await self._check_hemisphere_health(mapping.right_instance, Hemisphere.RIGHT)

            if not left_healthy or not right_healthy:
                return False

            # Competitive sync could involve comparing results
            # For now, just ensure both are operational

            return True

        except Exception as e:
            print(f"❌ Competitive sync failed: {e}")
            return False

    async def _sync_collaborative(self, mapping: HemisphereMapping) -> bool:
        """Perform collaborative synchronization (complex tasks)"""
        try:
            # In collaborative mode, hemispheres work together on complex tasks

            left_healthy = await self._check_hemisphere_health(mapping.left_instance, Hemisphere.LEFT)
            right_healthy = await self._check_hemisphere_health(mapping.right_instance, Hemisphere.RIGHT)

            if not left_healthy or not right_healthy:
                return False

            # Collaborative sync could involve distributed processing
            # For now, just ensure both are healthy

            return True

        except Exception as e:
            print(f"❌ Collaborative sync failed: {e}")
            return False

    async def _check_hemisphere_health(self, instance: Any, hemisphere: Hemisphere) -> bool:
        """Check health of a hemisphere instance"""
        try:
            if hasattr(instance, 'health_check'):
                return instance.health_check()
            elif hasattr(instance, 'get_system_health'):
                health = instance.get_system_health()
                return health.get('overall_health') in ['good', 'excellent']
            else:
                # Basic health check - assume healthy if no explicit check
                return True
        except Exception:
            return False

    async def _reconcile_vault_data(self, mapping: HemisphereMapping):
        """Reconcile vault data between hemispheres"""
        try:
            # This would implement actual data reconciliation
            # For now, it's a placeholder
            print(f"🔄 Reconciling vault data for {mapping.component_name}")
        except Exception as e:
            print(f"❌ Vault reconciliation failed: {e}")

    def _record_sync_event(self, event: SynchronizationEvent):
        """Record a synchronization event"""
        self.sync_events.append(event)

        # Maintain event limit
        if len(self.sync_events) > self.max_events:
            self.sync_events = self.sync_events[-self.max_events:]

    async def synchronize_hemispheres(self, component_name: Optional[str] = None) -> bool:
        """
        Manually trigger synchronization for specified component(s).

        Args:
            component_name: Specific component to sync (None for all)

        Returns:
            Synchronization success status
        """
        if component_name:
            if component_name not in self.hemisphere_mappings:
                return False

            await self._perform_synchronization(component_name)
            return True
        else:
            # Sync all components
            tasks = [
                self._perform_synchronization(name)
                for name in self.hemisphere_mappings.keys()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check if all succeeded
            return all(not isinstance(r, Exception) for r in results)

    def get_hemisphere_status(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get hemisphere status for a component.

        Args:
            component_name: Component name

        Returns:
            Hemisphere status information
        """
        mapping = self.hemisphere_mappings.get(component_name)
        if not mapping:
            return None

        # Ensure health_status is always a dict
        if mapping.health_status is None:
            mapping.health_status = {Hemisphere.LEFT.value: True, Hemisphere.RIGHT.value: True}

        return {
            "component_name": component_name,
            "sync_mode": mapping.sync_mode.value,
            "last_sync": mapping.last_sync.isoformat() if mapping.last_sync else None,
            "sync_interval": mapping.sync_interval,
            "left_healthy": mapping.health_status[Hemisphere.LEFT.value],
            "right_healthy": mapping.health_status[Hemisphere.RIGHT.value],
            "both_healthy": all(mapping.health_status.values())
        }

    def get_sync_performance(self) -> Dict[str, Any]:
        """Get synchronization performance metrics"""
        total_syncs = self.sync_performance["total_syncs"]

        return {
            "total_syncs": total_syncs,
            "successful_syncs": self.sync_performance["successful_syncs"],
            "failed_syncs": self.sync_performance["failed_syncs"],
            "success_rate": round(self.sync_performance["successful_syncs"] / total_syncs * 100, 1) if total_syncs > 0 else 0,
            "average_sync_time": round(self.sync_performance["avg_sync_time"], 3),
            "active_mappings": len(self.hemisphere_mappings),
            "running": self.running
        }

    def get_sync_events(self, component_name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get synchronization events.

        Args:
            component_name: Optional component filter
            limit: Maximum events to return

        Returns:
            List of synchronization events
        """
        events = self.sync_events

        if component_name:
            events = [e for e in events if e.component_name == component_name]

        return [event.to_dict() for event in events[-limit:]]

    def hemispheric_collaboration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform hemispheric collaboration on a complex task.

        Args:
            task: Task description and parameters

        Returns:
            Collaboration results
        """
        # This is a high-level function that would coordinate
        # complex tasks between hemispheres

        task_type = task.get("type", "unknown")

        # Route to appropriate hemispheres based on task type
        if task_type in ["analysis", "logic", "calculation"]:
            # Left hemisphere dominant
            result = self._process_left_dominant_task(task)
        elif task_type in ["creativity", "intuition", "pattern_recognition"]:
            # Right hemisphere dominant
            result = self._process_right_dominant_task(task)
        else:
            # Balanced collaboration
            result = self._process_balanced_task(task)

        return result

    def _process_left_dominant_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process left-dominant task"""
        # Simplified implementation
        return {
            "task_id": task.get("id", "unknown"),
            "processing_type": "left_dominant",
            "result": "processed_analytically",
            "confidence": 0.85
        }

    def _process_right_dominant_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process right-dominant task"""
        # Simplified implementation
        return {
            "task_id": task.get("id", "unknown"),
            "processing_type": "right_dominant",
            "result": "processed_creatively",
            "confidence": 0.78
        }

    def _process_balanced_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process balanced collaborative task"""
        # Simplified implementation
        return {
            "task_id": task.get("id", "unknown"),
            "processing_type": "balanced_collaboration",
            "result": "processed_collaboratively",
            "confidence": 0.92
        }

    def get_hemisphere_specializations(self) -> Dict[str, List[str]]:
        """Get hemisphere specialization information"""
        return {
            hemisphere.value: specializations
            for hemisphere, specializations in self.hemisphere_specializations.items()
        }

    def update_hemisphere_health(self, component_name: str, hemisphere: Hemisphere, healthy: bool):
        """
        Update hemisphere health status.

        Args:
            component_name: Component name
            hemisphere: Hemisphere to update
            healthy: Health status
        """
        mapping = self.hemisphere_mappings.get(component_name)
        if mapping:
            if mapping.health_status is None:
                mapping.health_status = {Hemisphere.LEFT.value: True, Hemisphere.RIGHT.value: True}
            mapping.health_status[hemisphere.value] = healthy

    def graceful_shutdown(self):
        """Perform graceful shutdown of dual-core integration"""
        print("🧠 Shutting down dual-core integration")

        self.stop_synchronization()

        # Final sync attempt
        try:
            asyncio.run(self.synchronize_hemispheres())
        except Exception as e:
            print(f"⚠️  Final sync failed: {e}")

        print("✅ Dual-core integration shutdown complete")