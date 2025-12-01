"""
CANS Synchronization Beacon Service
Broadcasts synchronization pulses to maintain cognitive rhythm
"""

import asyncio
import time
import logging
import httpx
from typing import Dict, Any, List

from cans.core.state import CANSState, SyncStatus
from cans.core.config import CANSConfig

logger = logging.getLogger("CANS.SyncBeacon")

class SyncBeacon:
    """
    Synchronization Beacon - broadcasts sync pulses to all cognitive modules

    This service maintains the master cognitive rhythm by:
    - Broadcasting synchronization pulses at regular intervals
    - Tracking module alignment with the master cycle
    - Detecting and correcting synchronization drift
    - Ensuring all modules operate on the same timing reference
    """

    def __init__(self, state: 'CANSState', config: 'CANSConfig'):
        self.state = state
        self.config = config
        self.is_running = False
        self.beacon_count = 0

    async def start_broadcasting(self):
        """
        Start the synchronization beacon broadcast loop
        """
        self.is_running = True
        logger.info(f"CANS Sync Beacon starting - interval: {self.config.sync_interval}s")

        while self.is_running and not self.state.is_shutting_down:
            try:
                await self._broadcast_sync_pulse()
                self.beacon_count += 1

                await asyncio.sleep(self.config.sync_interval)

            except Exception as e:
                logger.error(f"Sync beacon broadcast error: {e}")
                await asyncio.sleep(self.config.sync_interval)

        logger.info("CANS Sync Beacon stopped")

    async def stop_broadcasting(self):
        """
        Stop the synchronization beacon
        """
        self.is_running = False
        logger.info("CANS Sync Beacon stopping...")

    async def _broadcast_sync_pulse(self):
        """
        Broadcast a synchronization pulse to all monitored modules
        """
        current_time = time.time()
        self.state.current_sync_cycle += 1

        sync_pulse = {
            "sync_pulse": {
                "timestamp": current_time,
                "cycle_number": self.state.current_sync_cycle,
                "beacon_id": f"cans_sync_{self.beacon_count}_{int(current_time)}",
                "master_clock": current_time
            },
            "system_status": {
                "health_score": self.state.get_system_health_score(),
                "modules_total": len(self.state.module_states),
                "modules_isolated": len(self.state.isolated_modules)
            }
        }

        logger.debug(f"Sync pulse broadcast: cycle {self.state.current_sync_cycle}")

        # Broadcast to all monitored modules
        await self._send_sync_to_modules(sync_pulse)

        # Update state with sync metrics
        self._update_sync_metrics()

    async def _send_sync_to_modules(self, sync_pulse: Dict[str, Any]):
        """
        Send synchronization pulse to all monitored modules

        Args:
            sync_pulse: The synchronization pulse data to send
        """
        modules_in_sync = 0
        max_drift = 0.0
        drift_detected = False

        # Send to each module concurrently
        tasks = []
        for module_name, module_config in self.config.monitored_modules.items():
            task = self._send_sync_to_module(module_name, module_config, sync_pulse)
            tasks.append(task)

        # Wait for all sync acknowledgments
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            module_name = list(self.config.monitored_modules.keys())[i]

            if isinstance(result, Exception):
                logger.warning(f"Sync failed for {module_name}: {result}")
                self.state.record_module_failure(module_name, f"Sync error: {str(result)}")
            else:
                # Update module sync status
                ack_data = result
                if ack_data.get("acknowledged", False):
                    modules_in_sync += 1

                    # Check for drift
                    drift = ack_data.get("drift_detected", False)
                    if drift:
                        drift_detected = True
                        module_drift = abs(self.state.current_sync_cycle - ack_data.get("module_cycle", 0))
                        max_drift = max(max_drift, module_drift)

        # Record sync pulse in state
        self.state.record_sync_pulse(
            modules_in_sync=modules_in_sync,
            total_modules=len(self.config.monitored_modules),
            drift_detected=drift_detected,
            max_drift=max_drift
        )

    async def _send_sync_to_module(self, module_name: str, module_config: Dict[str, Any],
                                  sync_pulse: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send synchronization pulse to a specific module

        Args:
            module_name: Name of the module
            module_config: Module configuration
            sync_pulse: Sync pulse data

        Returns:
            Acknowledgment data from the module
        """
        try:
            sync_url = f"{module_config['url']}{module_config['sync_endpoint']}"

            async with httpx.AsyncClient(timeout=self.config.sync_timeout) as client:
                response = await client.post(
                    sync_url,
                    json={
                        "module_name": module_name,
                        "sync_pulse": sync_pulse,
                        "master_cycle": self.state.current_sync_cycle,
                        "timestamp": time.time()
                    },
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            # Return error data for processing
            return {
                "acknowledged": False,
                "error": str(e),
                "module_name": module_name
            }

    def _update_sync_metrics(self):
        """
        Update internal synchronization metrics
        """
        # Calculate sync health
        total_modules = len(self.state.module_states)
        if total_modules > 0:
            synced_modules = len([m for m in self.state.module_states.values()
                                 if m.sync_status == SyncStatus.IN_SYNC])
            sync_health = (synced_modules / total_modules) * 100

            # Update overall system health based on sync
            current_health = self.state.get_system_health_score()
            sync_penalty = (100 - sync_health) * 0.3  # 30% weight on sync health
            adjusted_health = max(0, current_health - sync_penalty)

            # This is a simplified health adjustment - in practice,
            # you'd want more sophisticated health calculation

    def get_beacon_stats(self) -> Dict[str, Any]:
        """
        Get synchronization beacon statistics

        Returns:
            Dictionary with beacon statistics
        """
        return {
            "beacons_broadcast": self.beacon_count,
            "is_running": self.is_running,
            "interval": self.config.sync_interval,
            "current_cycle": self.state.current_sync_cycle,
            "total_sync_pulses": self.state.total_sync_pulses,
            "drift_level": self.state.current_drift_level
        }