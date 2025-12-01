"""
CANS Module Monitor Service
Monitors responsiveness and health of all cognitive modules
"""

import asyncio
import time
import logging
import httpx
from typing import Dict, Any, List

from cans.core.state import CANSState, ModuleState, SyncStatus
from cans.core.config import CANSConfig

logger = logging.getLogger("CANS.ModuleMonitor")

class ModuleMonitor:
    """
    Module Monitor - checks health and responsiveness of cognitive modules

    This service performs continuous monitoring by:
    - Checking module health endpoints
    - Measuring response latency
    - Detecting cognitive drift
    - Triggering autonomic isolation/recovery
    - Maintaining module state tracking
    """

    def __init__(self, state: 'CANSState', config: 'CANSConfig'):
        self.state = state
        self.config = config
        self.is_running = False
        self.monitoring_cycles = 0

    async def start_monitoring(self):
        """
        Start the module monitoring loop
        """
        self.is_running = True
        logger.info(f"CANS Module Monitor starting - interval: {self.config.monitor_interval}s")

        # Initialize all modules
        for module_name in self.config.monitored_modules.keys():
            self.state.initialize_module(module_name,
                                       self.config.monitored_modules[module_name]["critical"])

        while self.is_running and not self.state.is_shutting_down:
            try:
                await self._perform_monitoring_cycle()
                self.monitoring_cycles += 1
                self.state.total_monitoring_cycles += 1

                await asyncio.sleep(self.config.monitor_interval)

            except Exception as e:
                logger.error(f"Module monitoring error: {e}")
                await asyncio.sleep(self.config.monitor_interval)

        logger.info("CANS Module Monitor stopped")

    async def stop_monitoring(self):
        """
        Stop the module monitoring
        """
        self.is_running = False
        logger.info("CANS Module Monitor stopping...")

    async def _perform_monitoring_cycle(self):
        """
        Perform a complete monitoring cycle on all modules
        """
        logger.debug(f"Starting monitoring cycle {self.monitoring_cycles}")

        # Monitor all modules concurrently
        tasks = []
        for module_name, module_config in self.config.monitored_modules.items():
            task = self._check_module_health(module_name, module_config)
            tasks.append(task)

        # Wait for all checks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and update state
        for i, result in enumerate(results):
            module_name = list(self.config.monitored_modules.keys())[i]

            if isinstance(result, Exception):
                logger.warning(f"Monitoring check failed for {module_name}: {result}")
                self.state.record_module_failure(module_name, f"Monitoring error: {str(result)}")
            else:
                health_data = result
                self._process_module_health(module_name, health_data)

    async def _check_module_health(self, module_name: str, module_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check health of a specific module

        Args:
            module_name: Name of the module to check
            module_config: Module configuration

        Returns:
            Health check results
        """
        health_url = f"{module_config['url']}{module_config['health_endpoint']}"

        try:
            start_time = time.time()

            async with httpx.AsyncClient(timeout=self.config.monitor_timeout) as client:
                response = await client.get(health_url)

            end_time = time.time()
            latency = end_time - start_time

            if response.status_code == 200:
                health_data = response.json()

                return {
                    "module": module_name,
                    "status": "healthy",
                    "latency": latency,
                    "response_code": response.status_code,
                    "health_score": health_data.get("health_score", 100),
                    "timestamp": end_time
                }
            else:
                return {
                    "module": module_name,
                    "status": "unhealthy",
                    "latency": latency,
                    "response_code": response.status_code,
                    "error": f"HTTP {response.status_code}",
                    "timestamp": end_time
                }

        except httpx.TimeoutException:
            return {
                "module": module_name,
                "status": "timeout",
                "latency": self.config.monitor_timeout,
                "error": "Request timeout",
                "timestamp": time.time()
            }

        except Exception as e:
            return {
                "module": module_name,
                "status": "error",
                "latency": 0,
                "error": str(e),
                "timestamp": time.time()
            }

    def _process_module_health(self, module_name: str, health_data: Dict[str, Any]):
        """
        Process health check results and update module state

        Args:
            module_name: Name of the module
            health_data: Health check results
        """
        status = health_data.get("status")
        latency = health_data.get("latency", 0)
        health_score = health_data.get("health_score", 0)

        if status == "healthy":
            # Module is responding well
            self.state.update_module_heartbeat(
                module_name=module_name,
                latency=latency,
                health_score=health_score
            )

            # Check for high latency
            if latency > self.config.max_latency_threshold:
                logger.warning(f"High latency detected for {module_name}: {latency:.3f}s "
                             f"(threshold: {self.config.max_latency_threshold}s)")

        elif status in ["timeout", "error", "unhealthy"]:
            # Module is having issues
            error_msg = health_data.get("error", f"Status: {status}")
            self.state.record_module_failure(module_name, error_msg)

            # Check if this is a critical module
            if self.config.monitored_modules[module_name]["critical"]:
                logger.error(f"Critical module {module_name} failure: {error_msg}")

        # Update sync status based on health
        self._update_sync_status_from_health(module_name, health_data)

    def _update_sync_status_from_health(self, module_name: str, health_data: Dict[str, Any]):
        """
        Update module synchronization status based on health check

        Args:
            module_name: Name of the module
            health_data: Health check results
        """
        if module_name in self.state.module_states:
            module = self.state.module_states[module_name]

            # If module is healthy and responding, assume it's in sync
            # In a real implementation, you'd check actual sync data
            if health_data.get("status") == "healthy":
                if module.sync_status != SyncStatus.IN_SYNC:
                    module.sync_status = SyncStatus.IN_SYNC
                    logger.debug(f"Module {module_name} sync status: IN_SYNC")
            else:
                # If module is unhealthy, mark as potentially out of sync
                if module.state in [ModuleState.DEGRADED, ModuleState.FAILED]:
                    module.sync_status = SyncStatus.OUT_OF_SYNC

    def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Get module monitoring statistics

        Returns:
            Dictionary with monitoring statistics
        """
        return {
            "monitoring_cycles": self.monitoring_cycles,
            "is_running": self.is_running,
            "interval": self.config.monitor_interval,
            "modules_monitored": len(self.config.monitored_modules),
            "total_cycles": self.state.total_monitoring_cycles,
            "failures_detected": self.state.total_failures_detected,
            "recoveries": self.state.total_recoveries
        }