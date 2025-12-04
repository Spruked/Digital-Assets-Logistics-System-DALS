# dals/registry/worker_registry.py
import uuid
import time
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add vault to path for imports
vault_path = Path(__file__).parent.parent.parent / "Vault_System_1.0" / "vault_system"
if str(vault_path) not in sys.path:
    sys.path.insert(0, str(vault_path))

from worker_vault import store_worker_registration, store_worker_manifest

# Global in-memory registry (will be backed by Redis/DB in v2)
WORKER_REGISTRY: Dict[str, Dict[str, Any]] = {}

# ──────────────────────────────────────────────────────────────
# MODEL CATALOG – this is the source of truth for every worker species
# Format: DMN = DALS Model Number → DMN-XX-YY
#   XX = Family (TM=TrueMark, RG=Regent, GT=GOAT, SK=SKG, BB=Bubble, etc.)
#   YY = Generation (01 = first stable, 02 = next major capability jump)
# ──────────────────────────────────────────────────────────────
MODEL_CATALOG = {
    # TrueMark family
    "truemark":          "DMN-TM-01",   # current stable Josephine
    "truemark-v2":       "DMN-TM-02",   # future multi-modal TrueMark

    # Regent family
    "regent":            "DMN-RG-01",
    "regent-pro":        "DMN-RG-02",

    # GOAT family
    "goat-parser":       "DMN-GT-01",
    "goat-struct":       "DMN-GT-02",

    # Micro-SKG family
    "skg":               "DMN-SK-01",
    "skg-reasoner":      "DMN-SK-02",

    # Host Bubble family
    "bubble":            "DMN-BB-01",
    "bubble-voice":      "DMN-BB-02",

    # Unified Specialist family (v5 self-patching narrow workers)
    "unified_specialist": "DMN-US-01",   # The eternal template
    
    # Narrow Specialist v5 family (DMN-GN-02)
    "nft_mint":          "DMN-GN-02",    # V5 NFT mint specialists
    "greeting":          "DMN-GN-02",    # V5 greeting specialists
    "timeline":          "DMN-GN-02",    # V5 timeline specialists
    "podcast_cohost":    "DMN-GN-02",    # V5 podcast specialists

    # Fallback / experimental
    "generic":           "DMN-GN-01",
}

def _generate_serial(model: str) -> str:
    """
    DSN = DALS Serial Number
    Format: <MODEL>-<8-HEX>-<5-HEX>
            ↑          ↑        ↑
            model      uuid4   counter/incremental shard
    Example: DMN-TM-01-A7F3B9E1-89F2C
    """
    short_uuid = uuid.uuid4().hex[:8].upper()
    counter    = hex(int(time.time() * 100) % 0xFFFFF)[2:].upper().zfill(5)
    return f"{model}-{short_uuid}-{counter}"

def register_worker(name: str, worker_type: str, api_url: str, user_id: str) -> Dict[str, Any]:
    """
    Register a new worker with DALS model number and serial number.
    
    Args:
        name: Worker name (e.g., "Josephine-01")
        worker_type: Worker type key from MODEL_CATALOG (e.g., "truemark")
        api_url: Worker API endpoint
        user_id: Target user ID
        
    Returns:
        Worker registration entry with model_number and serial_number
    """
    model_number = MODEL_CATALOG.get(worker_type.lower(), MODEL_CATALOG["generic"])
    serial_number = _generate_serial(model_number)

    entry = {
        "worker_name":     name,
        "worker_type":     worker_type,
        "model_number":    model_number,        # DMN-TM-01
        "serial_number":   serial_number,       # DMN-TM-01-A7F3B9E1-89F2C
        "api_url":         api_url,
        "user_id":         user_id,
        "deployed_at":     time.time(),
        "deployed_iso":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status":          "registered",
        "heartbeat":       None,                # will be updated by /ping
    }

    WORKER_REGISTRY[name] = entry
    
    # Store in vault system
    try:
        store_worker_registration("DALS", serial_number, entry)
        
        # Create and store deployment manifest
        manifest = {
            "worker_name": name,
            "model_number": model_number,
            "serial_number": serial_number,
            "deployed_at": entry["deployed_iso"],
            "worker_type": worker_type,
            "api_url": api_url,
            "user_id": user_id
        }
        store_worker_manifest("DALS", serial_number, manifest)
        
    except Exception as e:
        print(f"Warning: Failed to store worker in vault: {e}")
    
    return entry


def update_heartbeat(worker_name: str) -> bool:
    """
    Update worker heartbeat timestamp.
    
    Args:
        worker_name: Name of worker to update
        
    Returns:
        True if worker exists and was updated, False otherwise
    """
    if worker_name in WORKER_REGISTRY:
        heartbeat_time = time.time()
        WORKER_REGISTRY[worker_name]["heartbeat"] = heartbeat_time
        WORKER_REGISTRY[worker_name]["status"] = "active"
        
        # Store heartbeat in vault
        try:
            worker_entry = WORKER_REGISTRY[worker_name]
            serial_number = worker_entry.get("serial_number")
            if serial_number:
                heartbeat_data = {
                    "worker_name": worker_name,
                    "status": "active",
                    "last_heartbeat": heartbeat_time,
                    "last_heartbeat_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(heartbeat_time))
                }
                from worker_vault import store_worker_heartbeat
                store_worker_heartbeat("DALS", serial_number, heartbeat_data)
        except Exception as e:
            print(f"Warning: Failed to store heartbeat in vault: {e}")
        
        return True
    return False

def list_workers() -> list:
    """
    List all registered workers.
    
    Returns:
        List of worker registration entries
    """
    return list(WORKER_REGISTRY.values())

def get_worker(worker_name: str) -> Optional[Dict[str, Any]]:
    """
    Get worker by name.
    
    Args:
        worker_name: Name of worker to retrieve
        
    Returns:
        Worker entry or None if not found
    """
    return WORKER_REGISTRY.get(worker_name)
