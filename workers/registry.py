# DALS Worker Registry
# Maps worker types to their template classes
# This registry enables DALS to instantiate the correct worker type

from workers.templates.worker_template import WorkerTemplate

# Registered worker types and their corresponding template classes
REGISTERED_WORKER_TYPES = {
    "template": WorkerTemplate,      # Base template for testing
    "goat": WorkerTemplate,          # General Operations & Automation Tasks
    "mint": WorkerTemplate,          # TrueMark certificate generation
    "finance": WorkerTemplate,       # Market analysis & trading
    "ucm_relay": WorkerTemplate,     # Cognitive processing bridges
    "obs": WorkerTemplate,           # Streaming & broadcasting control
    "telemetry": WorkerTemplate,     # System monitoring & metrics
    "ledger": WorkerTemplate,        # Ledger mind workers
    "archival": WorkerTemplate,      # Archival mind workers
    "mechanist": WorkerTemplate      # Mechanist mind workers
}

def get_worker_template(worker_type: str):
    """
    Get the template class for a worker type.

    Args:
        worker_type (str): The type of worker to create

    Returns:
        class: The WorkerTemplate class for this worker type

    Raises:
        ValueError: If the worker type is not registered
    """
    if worker_type not in REGISTERED_WORKER_TYPES:
        available_types = ", ".join(REGISTERED_WORKER_TYPES.keys())
        raise ValueError(f"Unknown worker type: {worker_type}. Available types: {available_types}")

    return REGISTERED_WORKER_TYPES[worker_type]

def list_registered_types():
    """
    List all registered worker types.

    Returns:
        list: List of registered worker type names
    """
    return list(REGISTERED_WORKER_TYPES.keys())

def is_worker_type_registered(worker_type: str):
    """
    Check if a worker type is registered.

    Args:
        worker_type (str): The worker type to check

    Returns:
        bool: True if registered, False otherwise
    """
    return worker_type in REGISTERED_WORKER_TYPES