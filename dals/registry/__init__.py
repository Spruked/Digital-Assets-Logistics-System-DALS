"""
DALS Worker Registry Module
Production-ready worker registration with DMN model numbers and DSN serial numbers.
"""

from .worker_registry import (
    register_worker,
    update_heartbeat,
    list_workers,
    get_worker,
    MODEL_CATALOG,
    WORKER_REGISTRY
)

__all__ = [
    "register_worker",
    "update_heartbeat", 
    "list_workers",
    "get_worker",
    "MODEL_CATALOG",
    "WORKER_REGISTRY"
]
