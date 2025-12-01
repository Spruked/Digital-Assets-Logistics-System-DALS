"""
CANS Heartbeat Emitter Service
Emits regular heartbeat signals to maintain autonomic monitoring
"""

import asyncio
import time
import logging
from typing import Dict, Any

from cans.core.state import CANSState
from cans.core.config import CANSConfig

logger = logging.getLogger("CANS.HeartbeatEmitter")

class HeartbeatEmitter:
    """
    Heartbeat Emitter - sends regular heartbeat signals to monitored modules

    This service emits heartbeat JSON packets at regular intervals to:
    - Signal CANS operational status
    - Provide timing synchronization
    - Enable module health monitoring
    """

    def __init__(self, state: 'CANSState', config: 'CANSConfig'):
        self.state = state
        self.config = config
        self.is_running = False
        self.heartbeat_count = 0

    async def start_emitting(self):
        """
        Start the heartbeat emission loop
        """
        self.is_running = True
        logger.info(f"CANS Heartbeat Emitter starting - interval: {self.config.heartbeat_interval}s")

        while self.is_running and not self.state.is_shutting_down:
            try:
                await self._emit_heartbeat()
                self.heartbeat_count += 1
                self.state.total_heartbeats_sent += 1

                await asyncio.sleep(self.config.heartbeat_interval)

            except Exception as e:
                logger.error(f"Heartbeat emission error: {e}")
                await asyncio.sleep(self.config.heartbeat_interval)

        logger.info("CANS Heartbeat Emitter stopped")

    async def stop_emitting(self):
        """
        Stop the heartbeat emission
        """
        self.is_running = False
        logger.info("CANS Heartbeat Emitter stopping...")

    async def _emit_heartbeat(self):
        """
        Emit a single heartbeat pulse
        """
        current_time = time.time()

        heartbeat_data = {
            "module": "CANS",
            "timestamp": current_time,
            "status": "alive",
            "cycle": self.state.current_sync_cycle,
            "heartbeat_id": f"cans_hb_{self.heartbeat_count}_{int(current_time)}",
            "system_health": self.state.get_system_health_score(),
            "modules_monitored": len(self.state.module_states),
            "isolated_count": len(self.state.isolated_modules)
        }

        # Log heartbeat emission (in production, this might broadcast to modules)
        logger.debug(f"Heartbeat emitted: cycle {self.state.current_sync_cycle}, "
                    f"health {heartbeat_data['system_health']}")

        # In a full implementation, this would broadcast to all monitored modules
        # For now, we just update the state and log

        # Update state with heartbeat metrics
        self._update_heartbeat_metrics(current_time)

    def _update_heartbeat_metrics(self, timestamp: float):
        """
        Update internal metrics based on heartbeat emission

        Args:
            timestamp: Time of heartbeat emission
        """
        # This could include tracking emission success rates,
        # monitoring broadcast reach, etc.

        # For now, just ensure modules are initialized
        for module_name in self.config.monitored_modules.keys():
            if module_name not in self.state.module_states:
                self.state.initialize_module(module_name,
                                           self.config.monitored_modules[module_name]["critical"])

    def get_heartbeat_stats(self) -> Dict[str, Any]:
        """
        Get heartbeat emission statistics

        Returns:
            Dictionary with heartbeat statistics
        """
        return {
            "heartbeats_emitted": self.heartbeat_count,
            "is_running": self.is_running,
            "interval": self.config.heartbeat_interval,
            "last_emission": time.time(),  # Approximate
            "total_sent": self.state.total_heartbeats_sent
        }