"""
CANS Cycle Aligner Service
Ensures all modules operate on synchronized reasoning cycles
"""

import asyncio
import time
import logging
from typing import Dict, Any, List

from cans.core.state import CANSState, SyncStatus
from cans.core.config import CANSConfig

logger = logging.getLogger("CANS.CycleAligner")

class CycleAligner:
    """
    Cycle Aligner - ensures all cognitive modules operate on synchronized cycles

    This service maintains cycle alignment by:
    - Tracking module cycle numbers
    - Detecting cycle drift
    - Coordinating cycle transitions
    - Ensuring logical consistency across modules
    """

    def __init__(self, state: 'CANSState', config: 'CANSConfig'):
        self.state = state
        self.config = config
        self.is_running = False
        self.alignment_cycles = 0

    async def start_alignment(self):
        """
        Start the cycle alignment monitoring loop
        """
        self.is_running = True
        logger.info(f"CANS Cycle Aligner starting - check interval: {self.config.cycle_check_interval}s")

        while self.is_running and not self.state.is_shutting_down:
            try:
                await self._perform_alignment_check()
                self.alignment_cycles += 1

                await asyncio.sleep(self.config.cycle_check_interval)

            except Exception as e:
                logger.error(f"Cycle alignment error: {e}")
                await asyncio.sleep(self.config.cycle_check_interval)

        logger.info("CANS Cycle Aligner stopped")

    async def stop_alignment(self):
        """
        Stop the cycle alignment monitoring
        """
        self.is_running = False
        logger.info("CANS Cycle Aligner stopping...")

    async def _perform_alignment_check(self):
        """
        Perform cycle alignment check across all modules
        """
        logger.debug(f"Cycle alignment check {self.alignment_cycles}")

        # Check alignment for all modules
        misaligned_modules = []

        for module_name, module in self.state.module_states.items():
            cycle_drift = abs(self.state.current_sync_cycle - module.cycle_number)

            if cycle_drift > self.config.max_cycle_drift:
                misaligned_modules.append({
                    "module": module_name,
                    "current_cycle": module.cycle_number,
                    "master_cycle": self.state.current_sync_cycle,
                    "drift": cycle_drift
                })

                # Update module sync status
                module.sync_status = SyncStatus.OUT_OF_SYNC

        # Handle misaligned modules
        if misaligned_modules:
            await self._handle_misalignment(misaligned_modules)

        # Update overall drift level
        max_drift = max([m["drift"] for m in misaligned_modules], default=0)
        self.state.current_drift_level = max_drift

    async def _handle_misalignment(self, misaligned_modules: List[Dict[str, Any]]):
        """
        Handle cycle misalignment for affected modules

        Args:
            misaligned_modules: List of misaligned module information
        """
        logger.warning(f"Cycle misalignment detected for {len(misaligned_modules)} modules")

        for misaligned in misaligned_modules:
            module_name = misaligned["module"]
            drift = misaligned["drift"]

            # For critical modules with high drift, isolate temporarily
            if (self.config.monitored_modules[module_name]["critical"] and
                drift > self.config.max_cycle_drift * 2):

                logger.error(f"Isolating critical module {module_name} due to severe cycle drift ({drift})")
                self.state._isolate_module(module_name, f"Severe cycle drift: {drift}")

            else:
                # For non-critical or moderate drift, attempt realignment
                logger.info(f"Attempting realignment for {module_name} (drift: {drift})")

                # In a full implementation, this would send realignment commands
                # For now, just update the status
                if module_name in self.state.module_states:
                    self.state.module_states[module_name].sync_status = SyncStatus.REALIGNING

    async def force_cycle_sync(self, target_cycle: int = None) -> Dict[str, Any]:
        """
        Force synchronization of all modules to a specific cycle

        Args:
            target_cycle: Target cycle number (defaults to current master cycle)

        Returns:
            Synchronization results
        """
        if target_cycle is None:
            target_cycle = self.state.current_sync_cycle

        logger.info(f"Forcing cycle sync to {target_cycle}")

        sync_results = {
            "target_cycle": target_cycle,
            "modules_synced": 0,
            "modules_failed": 0,
            "timestamp": time.time()
        }

        # In a full implementation, this would send sync commands to all modules
        # For now, just update local state
        for module_name, module in self.state.module_states.items():
            try:
                module.cycle_number = target_cycle
                module.sync_status = SyncStatus.IN_SYNC
                sync_results["modules_synced"] += 1

            except Exception as e:
                logger.error(f"Failed to sync {module_name}: {e}")
                sync_results["modules_failed"] += 1

        # Reset drift level
        self.state.current_drift_level = 0

        logger.info(f"Cycle sync completed: {sync_results['modules_synced']} synced, "
                   f"{sync_results['modules_failed']} failed")

        return sync_results

    def get_alignment_stats(self) -> Dict[str, Any]:
        """
        Get cycle alignment statistics

        Returns:
            Dictionary with alignment statistics
        """
        total_modules = len(self.state.module_states)
        aligned_modules = len([m for m in self.state.module_states.values()
                              if m.sync_status == SyncStatus.IN_SYNC])
        drifting_modules = len([m for m in self.state.module_states.values()
                               if m.sync_status == SyncStatus.DRIFTING])
        out_of_sync_modules = len([m for m in self.state.module_states.values()
                                  if m.sync_status == SyncStatus.OUT_OF_SYNC])

        return {
            "alignment_cycles": self.alignment_cycles,
            "is_running": self.is_running,
            "check_interval": self.config.cycle_check_interval,
            "max_cycle_drift": self.config.max_cycle_drift,

            "alignment_status": {
                "total_modules": total_modules,
                "aligned_modules": aligned_modules,
                "drifting_modules": drifting_modules,
                "out_of_sync_modules": out_of_sync_modules,
                "alignment_percentage": (aligned_modules / total_modules * 100) if total_modules > 0 else 0
            },

            "drift_metrics": {
                "current_drift_level": self.state.current_drift_level,
                "max_observed_drift": self.state.max_observed_drift,
                "master_cycle": self.state.current_sync_cycle
            }
        }