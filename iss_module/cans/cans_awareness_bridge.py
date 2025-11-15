# cans_awareness_bridge.py
# Connects CANS (Autonomic Nervous System) to the Awareness Layer
# Version 1.0.0

from datetime import datetime
from iss_module.csmm.awareness.self_model import get_self_model, ModuleStatus

self_model = get_self_model()

class CANSBridge:
    """
    Bridge between CANS (Caleon Autonomic Nervous System) and Awareness Layer.
    Records all autonomic actions in Caleon's self-model for operational awareness.
    """

    @staticmethod
    def record_failure(module: str, reason: str):
        """
        Record a module failure in the awareness layer.

        Args:
            module: Name of the failed module
            reason: Description of the failure

        Returns:
            Isolation report string
        """
        # Update health + status
        self_model.update_module_status(
            module,
            ModuleStatus.DEGRADED.value,
            health=45,
            repair_time=datetime.utcnow().isoformat()
        )
        return self_model.report_isolation(module)

    @staticmethod
    def record_repair(module: str, action: str, duration: float):
        """
        Record a successful repair in the awareness layer.

        Args:
            module: Name of the repaired module
            action: Repair action taken
            duration: Time taken for repair in seconds

        Returns:
            Repair report string
        """
        self_model.update_module_status(
            module,
            ModuleStatus.OPERATIONAL.value,
            health=100,
            repair_time=datetime.utcnow().isoformat()
        )
        return self_model.report_repair(
            module=module,
            issue="repair completed",
            action=action,
            duration=duration
        )

    @staticmethod
    def record_isolation(module: str):
        """
        Record module isolation in the awareness layer.

        Args:
            module: Name of the isolated module

        Returns:
            Isolation report string
        """
        self_model.update_module_status(
            module,
            ModuleStatus.ISOLATED.value,
            health=10
        )
        return self_model.report_isolation(module)

    @staticmethod
    def record_recovery(module: str):
        """
        Record module recovery in the awareness layer.

        Args:
            module: Name of the recovered module

        Returns:
            Recovery report string
        """
        self_model.update_module_status(
            module,
            ModuleStatus.OPERATIONAL.value,
            health=100
        )
        return self_model.report_recovery(module)

    @staticmethod
    def activate_fallback(module: str, details: str):
        """
        Activate fallback mode for a module.

        Args:
            module: Name of the module entering fallback
            details: Details about the fallback activation

        Returns:
            Fallback activation message
        """
        self_model.update_module_status(
            module,
            ModuleStatus.FALLBACK_ACTIVE.value,
            health=70
        )
        self_model.active_fallbacks.append((module, details))
        return f"{module} fallback activated: {details}"

    @staticmethod
    def clear_fallback(module: str):
        """
        Clear fallback mode for a module.

        Args:
            module: Name of the module exiting fallback

        Returns:
            Fallback clearance message
        """
        self_model.update_module_status(
            module,
            ModuleStatus.OPERATIONAL.value,
            health=100
        )
        self_model.active_fallbacks = [
            f for f in self_model.active_fallbacks if f[0] != module
        ]
        return f"{module} fallback cleared."