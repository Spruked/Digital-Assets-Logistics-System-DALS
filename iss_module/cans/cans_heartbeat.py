# cans_heartbeat.py
# CANS → UCM heartbeat monitoring
# Version 1.0.0

import time
import requests
import logging
from iss_module.cans.cans_awareness_bridge import CANSBridge
from iss_module.csmm.awareness.self_model import get_self_model, ModuleStatus

UCM_HEALTH_URL = "http://localhost:8080/health"
self_model = get_self_model()

logger = logging.getLogger("DALS.CANS.Heartbeat")

class CANSHeartbeat:
    """
    CANS Heartbeat Monitor - watches UCM health and triggers autonomic responses
    """
    interval = 2  # seconds

    @staticmethod
    def start():
        """
        Start the heartbeat monitoring loop
        """
        logger.info("CANS Heartbeat monitor starting - watching UCM")
        while True:
            try:
                response = requests.get(UCM_HEALTH_URL, timeout=1.2)
                if response.status_code == 200:
                    # UCM is healthy
                    self_model.update_module_status("UCM", ModuleStatus.OPERATIONAL.value, health=100)
                else:
                    CANSHeartbeat._handle_failure("UCM", f"HTTP status {response.status_code}")
            except requests.exceptions.Timeout:
                CANSHeartbeat._handle_failure("UCM", "heartbeat timeout")
            except requests.exceptions.ConnectionError:
                CANSHeartbeat._handle_failure("UCM", "connection refused")
            except Exception as e:
                CANSHeartbeat._handle_failure("UCM", str(e))

            time.sleep(CANSHeartbeat.interval)

    @staticmethod
    def _handle_failure(module: str, reason: str):
        """
        Handle UCM heartbeat failure - trigger autonomic repair

        Args:
            module: Module name (UCM)
            reason: Failure reason
        """
        logger.warning(f"CANS detected UCM heartbeat failure: {reason}")

        # Record failure in awareness layer
        isolation_report = CANSBridge.record_failure(module, reason)

        # Attempt autonomic recovery
        repair_report = CANSBridge.record_repair(
            module=module,
            action="UCM restart triggered by CANS",
            duration=0.25
        )

        logger.info(f"CANS autonomic repair initiated: {repair_report}")