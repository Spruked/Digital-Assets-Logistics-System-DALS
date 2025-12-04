"""
DALS Worker Vault — Enterprise-Class Worker Lifecycle Tracking

This module provides isolated worker vaults for each subsystem:
- DALS (core system workers)
- GOAT (General Operations & Automation Tasks)
- TrueMark (NFT minting workers)
- CertSig (Certificate signature workers)

Each vault maintains:
- Worker manifests (deployment records)
- Heartbeat logs (health monitoring)
- Telemetry data (performance metrics)
- Cognition records (learning history)
- Worker lineage (JSONL audit trail)

DALS Forge V1.0 — Enterprise Worker Vault
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class WorkerVault:
    """
    Enterprise-class worker vault for subsystem-isolated worker tracking.
    
    Each subsystem (DALS, GOAT, TrueMark, CertSig) has its own vault instance.
    """
    
    def __init__(self, subsystem: str, vault_root: Optional[Path] = None):
        """
        Initialize worker vault for a subsystem.
        
        Args:
            subsystem: Subsystem name (DALS, GOAT, TrueMark, CertSig)
            vault_root: Root directory for vault (defaults to Vault_System_1.0/vault_system/<subsystem>/worker_vault)
        """
        self.subsystem = subsystem.upper()
        
        if vault_root is None:
            # Default to Vault_System_1.0 structure
            base_path = Path(__file__).parent / self.subsystem / "worker_vault"
            vault_root = base_path
        else:
            vault_root = Path(vault_root)
        
        self.vault_root = vault_root
        
        # Create directory structure
        self.manifests_dir = self.vault_root / "manifests"
        self.heartbeats_dir = self.vault_root / "heartbeats"
        self.telemetry_dir = self.vault_root / "telemetry"
        self.cognition_dir = self.vault_root / "cognition"
        
        self._ensure_structure()
        
        self.workers_log = self.vault_root / "workers.jsonl"
    
    def _ensure_structure(self):
        """Create vault directory structure if it doesn't exist"""
        for directory in [
            self.vault_root,
            self.manifests_dir,
            self.heartbeats_dir,
            self.telemetry_dir,
            self.cognition_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def store_manifest(self, worker_dsn: str, manifest: Dict[str, Any]) -> Path:
        """
        Store worker deployment manifest.
        
        Args:
            worker_dsn: Worker Digital Serial Number (e.g., DMN-GN-02-A7F3B9E1-89F2C)
            manifest: Deployment manifest data
            
        Returns:
            Path to stored manifest file
        """
        manifest_file = self.manifests_dir / f"{worker_dsn}.json"
        
        with open(manifest_file, 'w') as f:
            json.dump({
                "subsystem": self.subsystem,
                "worker_dsn": worker_dsn,
                "stored_at": datetime.utcnow().isoformat() + "Z",
                "manifest": manifest
            }, f, indent=2)
        
        return manifest_file
    
    def store_worker(self, worker_dsn: str, worker_data: Dict[str, Any]) -> bool:
        """
        Store worker registration in JSONL audit trail.
        
        Args:
            worker_dsn: Worker Digital Serial Number
            worker_data: Worker registration data
            
        Returns:
            True if stored successfully
        """
        entry = {
            "subsystem": self.subsystem,
            "worker_dsn": worker_dsn,
            "timestamp": time.time(),
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            "event": "worker_registered",
            **worker_data
        }
        
        with open(self.workers_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return True
    
    def store_heartbeat(self, worker_dsn: str, heartbeat_data: Dict[str, Any]) -> Path:
        """
        Store worker heartbeat (append-only log).
        
        Args:
            worker_dsn: Worker Digital Serial Number
            heartbeat_data: Heartbeat metrics
            
        Returns:
            Path to heartbeat log file
        """
        heartbeat_file = self.heartbeats_dir / f"{worker_dsn}.jsonl"
        
        entry = {
            "subsystem": self.subsystem,
            "worker_dsn": worker_dsn,
            "timestamp": time.time(),
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            **heartbeat_data
        }
        
        with open(heartbeat_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return heartbeat_file
    
    def store_telemetry(self, worker_dsn: str, telemetry_data: Dict[str, Any]) -> Path:
        """
        Store worker telemetry (performance metrics, events).
        
        Args:
            worker_dsn: Worker Digital Serial Number
            telemetry_data: Telemetry data
            
        Returns:
            Path to telemetry log file
        """
        telemetry_file = self.telemetry_dir / f"{worker_dsn}.jsonl"
        
        entry = {
            "subsystem": self.subsystem,
            "worker_dsn": worker_dsn,
            "timestamp": time.time(),
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            **telemetry_data
        }
        
        with open(telemetry_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return telemetry_file
    
    def store_cognition(self, worker_dsn: str, cognition_data: Dict[str, Any]) -> Path:
        """
        Store worker cognition events (learning, patches, predicates).
        
        Args:
            worker_dsn: Worker Digital Serial Number
            cognition_data: Cognition/learning data
            
        Returns:
            Path to cognition log file
        """
        cognition_file = self.cognition_dir / f"{worker_dsn}.jsonl"
        
        entry = {
            "subsystem": self.subsystem,
            "worker_dsn": worker_dsn,
            "timestamp": time.time(),
            "timestamp_iso": datetime.utcnow().isoformat() + "Z",
            **cognition_data
        }
        
        with open(cognition_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        return cognition_file
    
    def get_worker_history(self, worker_dsn: str) -> Dict[str, Any]:
        """
        Retrieve complete worker history (all vault records).
        
        Args:
            worker_dsn: Worker Digital Serial Number
            
        Returns:
            Dictionary containing all worker records
        """
        history = {
            "worker_dsn": worker_dsn,
            "subsystem": self.subsystem,
            "manifest": None,
            "heartbeats": [],
            "telemetry": [],
            "cognition": []
        }
        
        # Load manifest
        manifest_file = self.manifests_dir / f"{worker_dsn}.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                history["manifest"] = json.load(f)
        
        # Load heartbeats
        heartbeat_file = self.heartbeats_dir / f"{worker_dsn}.jsonl"
        if heartbeat_file.exists():
            with open(heartbeat_file, 'r') as f:
                history["heartbeats"] = [json.loads(line) for line in f]
        
        # Load telemetry
        telemetry_file = self.telemetry_dir / f"{worker_dsn}.jsonl"
        if telemetry_file.exists():
            with open(telemetry_file, 'r') as f:
                history["telemetry"] = [json.loads(line) for line in f]
        
        # Load cognition
        cognition_file = self.cognition_dir / f"{worker_dsn}.jsonl"
        if cognition_file.exists():
            with open(cognition_file, 'r') as f:
                history["cognition"] = [json.loads(line) for line in f]
        
        return history
    
    def list_workers(self) -> list:
        """
        List all workers in this vault.
        
        Returns:
            List of worker DSNs
        """
        workers = set()
        
        # Scan manifests directory
        if self.manifests_dir.exists():
            for manifest_file in self.manifests_dir.glob("*.json"):
                workers.add(manifest_file.stem)
        
        return sorted(list(workers))
    
    def get_vault_stats(self) -> Dict[str, Any]:
        """
        Get vault statistics.
        
        Returns:
            Dictionary with vault stats
        """
        workers = self.list_workers()
        
        total_heartbeats = 0
        if self.heartbeats_dir.exists():
            total_heartbeats = sum(
                1 for f in self.heartbeats_dir.glob("*.jsonl")
                if f.exists()
                for _ in open(f)
            )
        
        total_telemetry = 0
        if self.telemetry_dir.exists():
            total_telemetry = sum(
                1 for f in self.telemetry_dir.glob("*.jsonl")
                if f.exists()
                for _ in open(f)
            )
        
        total_cognition = 0
        if self.cognition_dir.exists():
            total_cognition = sum(
                1 for f in self.cognition_dir.glob("*.jsonl")
                if f.exists()
                for _ in open(f)
            )
        
        return {
            "subsystem": self.subsystem,
            "vault_root": str(self.vault_root),
            "total_workers": len(workers),
            "total_heartbeats": total_heartbeats,
            "total_telemetry_events": total_telemetry,
            "total_cognition_events": total_cognition,
            "workers": workers
        }


# ═════════════════════════════════════════════════════════════════════════════════
# SUBSYSTEM VAULT INSTANCES
# ═════════════════════════════════════════════════════════════════════════════════

# Create vault instances for each subsystem
DALS_VAULT = WorkerVault("DALS")
GOAT_VAULT = WorkerVault("GOAT")
TRUEMARK_VAULT = WorkerVault("TrueMark")
CERTSIG_VAULT = WorkerVault("CertSig")

# Vault registry for dynamic access
VAULT_REGISTRY = {
    "DALS": DALS_VAULT,
    "GOAT": GOAT_VAULT,
    "TRUEMARK": TRUEMARK_VAULT,
    "CERTSIG": CERTSIG_VAULT
}


def get_vault(subsystem: str) -> WorkerVault:
    """
    Get worker vault for a subsystem.
    
    Args:
        subsystem: Subsystem name (DALS, GOAT, TrueMark, CertSig)
        
    Returns:
        WorkerVault instance
        
    Raises:
        ValueError: If subsystem not found
    """
    subsystem_upper = subsystem.upper()
    
    if subsystem_upper not in VAULT_REGISTRY:
        raise ValueError(
            f"Unknown subsystem: {subsystem}. "
            f"Available: {', '.join(VAULT_REGISTRY.keys())}"
        )
    
    return VAULT_REGISTRY[subsystem_upper]


# ═════════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════════

def store_worker_manifest(subsystem: str, worker_dsn: str, manifest: Dict[str, Any]) -> Path:
    """Store worker manifest in subsystem vault"""
    vault = get_vault(subsystem)
    return vault.store_manifest(worker_dsn, manifest)


def store_worker_registration(subsystem: str, worker_dsn: str, worker_data: Dict[str, Any]) -> bool:
    """Store worker registration in subsystem vault"""
    vault = get_vault(subsystem)
    return vault.store_worker(worker_dsn, worker_data)


def store_worker_heartbeat(subsystem: str, worker_dsn: str, heartbeat_data: Dict[str, Any]) -> Path:
    """Store worker heartbeat in subsystem vault"""
    vault = get_vault(subsystem)
    return vault.store_heartbeat(worker_dsn, heartbeat_data)


def store_worker_telemetry(subsystem: str, worker_dsn: str, telemetry_data: Dict[str, Any]) -> Path:
    """Store worker telemetry in subsystem vault"""
    vault = get_vault(subsystem)
    return vault.store_telemetry(worker_dsn, telemetry_data)


def store_worker_cognition(subsystem: str, worker_dsn: str, cognition_data: Dict[str, Any]) -> Path:
    """Store worker cognition event in subsystem vault"""
    vault = get_vault(subsystem)
    return vault.store_cognition(worker_dsn, cognition_data)


def get_all_vault_stats() -> Dict[str, Any]:
    """Get statistics for all vaults"""
    return {
        subsystem: vault.get_vault_stats()
        for subsystem, vault in VAULT_REGISTRY.items()
    }
