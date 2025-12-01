"""
CANS Configuration
Centralized configuration management for the Cognitive Autonomous Neural Synchronizer
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CANSConfig:
    """Configuration for CANS microservice"""

    # Service configuration
    host: str = os.getenv("CANS_HOST", "0.0.0.0")
    port: int = int(os.getenv("CANS_PORT", "8020"))
    debug: bool = os.getenv("CANS_DEBUG", "false").lower() == "true"

    # Heartbeat configuration
    heartbeat_interval: float = float(os.getenv("CANS_HEARTBEAT_INTERVAL", "1.0"))  # seconds
    heartbeat_timeout: float = float(os.getenv("CANS_HEARTBEAT_TIMEOUT", "2.0"))  # seconds

    # Sync beacon configuration
    sync_interval: float = float(os.getenv("CANS_SYNC_INTERVAL", "0.5"))  # seconds
    sync_timeout: float = float(os.getenv("CANS_SYNC_TIMEOUT", "1.0"))  # seconds

    # Module monitoring configuration
    monitor_interval: float = float(os.getenv("CANS_MONITOR_INTERVAL", "2.0"))  # seconds
    monitor_timeout: float = float(os.getenv("CANS_MONITOR_TIMEOUT", "3.0"))  # seconds
    max_latency_threshold: float = float(os.getenv("CANS_MAX_LATENCY", "1.0"))  # seconds

    # Cycle alignment configuration
    cycle_check_interval: float = float(os.getenv("CANS_CYCLE_CHECK_INTERVAL", "0.1"))  # seconds
    max_cycle_drift: int = int(os.getenv("CANS_MAX_CYCLE_DRIFT", "5"))  # cycles

    # Module endpoints to monitor
    monitored_modules: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize monitored modules configuration"""
        self.monitored_modules = {
            "UCM": {
                "url": os.getenv("UCM_URL", "http://localhost:8080"),
                "health_endpoint": "/health",
                "sync_endpoint": "/api/sync/pulse",
                "critical": True,
                "expected_response_time": 0.5
            },
            "Harmonizer": {
                "url": os.getenv("HARMONIZER_URL", "http://localhost:8003"),
                "health_endpoint": "/api/harmonizer/health",
                "sync_endpoint": "/api/harmonizer/sync",
                "critical": True,
                "expected_response_time": 1.0
            },
            "DALS_API": {
                "url": os.getenv("DALS_API_URL", "http://localhost:8003"),
                "health_endpoint": "/health",
                "sync_endpoint": "/api/dals/sync",
                "critical": False,
                "expected_response_time": 0.8
            },
            "Dashboard": {
                "url": os.getenv("DASHBOARD_URL", "http://localhost:8008"),
                "health_endpoint": "/health",
                "sync_endpoint": "/api/dashboard/sync",
                "critical": False,
                "expected_response_time": 1.2
            }
        }

    @property
    def all_module_urls(self) -> List[str]:
        """Get all module base URLs"""
        return [module["url"] for module in self.monitored_modules.values()]

    @property
    def critical_modules(self) -> List[str]:
        """Get names of critical modules"""
        return [name for name, config in self.monitored_modules.items() if config["critical"]]

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Get configuration for a specific module"""
        return self.monitored_modules.get(module_name, {})

# Global configuration instance
config = CANSConfig()