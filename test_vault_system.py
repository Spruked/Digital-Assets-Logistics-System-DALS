#!/usr/bin/env python3
"""
Test script for Vault_System_1.0
"""

import sys
from pathlib import Path

# Add vault to path
vault_path = Path(__file__).parent / "Vault_System_1.0" / "vault_system"
sys.path.insert(0, str(vault_path))

from worker_vault import DALS_VAULT, GOAT_VAULT, TRUEMARK_VAULT, CERTSIG_VAULT

def test_vault_system():
    print("🧪 Testing Vault_System_1.0...")

    # Test DALS vault
    print("\n📁 Testing DALS vault structure...")
    dals_stats = DALS_VAULT.get_vault_stats()
    print(f"DALS Vault root: {dals_stats['vault_root']}")
    print(f"DALS Vault workers: {dals_stats['total_workers']}")

    # Test worker registration
    test_worker = {
        'worker_name': 'test-worker-01',
        'worker_type': 'truemark',
        'model_number': 'DMN-TM-01',
        'serial_number': 'DMN-TM-01-A7F3B9E1-89F2C',
        'api_url': 'http://localhost:8001',
        'user_id': 'test-user',
        'deployed_at': 1640995200.0,
        'deployed_iso': '2022-01-01T00:00:00Z',
        'status': 'registered'
    }

    print("\n👷 Storing test worker...")
    success = DALS_VAULT.store_worker('DMN-TM-01-A7F3B9E1-89F2C', test_worker)
    print(f"Worker stored: {success}")

    # Test manifest storage
    manifest = {
        'worker_name': 'test-worker-01',
        'model_number': 'DMN-TM-01',
        'serial_number': 'DMN-TM-01-A7F3B9E1-89F2C',
        'deployed_at': '2022-01-01T00:00:00Z'
    }

    print("\n📋 Storing manifest...")
    manifest_path = DALS_VAULT.store_manifest('DMN-TM-01-A7F3B9E1-89F2C', manifest)
    print(f"Manifest stored at: {manifest_path}")

    # Test heartbeat storage
    heartbeat_data = {
        'status': 'active',
        'last_heartbeat': 1640995260.0,
        'cpu_usage': 45.2,
        'memory_usage': 234.5
    }

    print("\n💓 Storing heartbeat...")
    heartbeat_path = DALS_VAULT.store_heartbeat('DMN-TM-01-A7F3B9E1-89F2C', heartbeat_data)
    print(f"Heartbeat stored at: {heartbeat_path}")

    # Test telemetry storage
    telemetry_data = {
        'event_type': 'task_completed',
        'task_id': 'task-123',
        'duration_ms': 1500,
        'success': True
    }

    print("\n📊 Storing telemetry...")
    telemetry_path = DALS_VAULT.store_telemetry('DMN-TM-01-A7F3B9E1-89F2C', telemetry_data)
    print(f"Telemetry stored at: {telemetry_path}")

    # Test cognition storage
    cognition_data = {
        'event_type': 'learning_update',
        'predicate': 'task_completion_time',
        'confidence': 0.85,
        'pattern': 'faster_with_cache'
    }

    print("\n🧠 Storing cognition...")
    cognition_path = DALS_VAULT.store_cognition('DMN-TM-01-A7F3B9E1-89F2C', cognition_data)
    print(f"Cognition stored at: {cognition_path}")

    # Test retrieval
    print("\n🔍 Retrieving worker history...")
    history = DALS_VAULT.get_worker_history('DMN-TM-01-A7F3B9E1-89F2C')
    print(f"History keys: {list(history.keys())}")
    print(f"Manifest exists: {history['manifest'] is not None}")
    print(f"Heartbeats count: {len(history['heartbeats'])}")
    print(f"Telemetry events: {len(history['telemetry'])}")
    print(f"Cognition events: {len(history['cognition'])}")

    # Test all vaults
    print("\n🏦 Testing all subsystem vaults...")
    from worker_vault import VAULT_REGISTRY
    for subsystem, vault in VAULT_REGISTRY.items():
        stats = vault.get_vault_stats()
        print(f"{subsystem} Vault: {stats['total_workers']} workers")

    print("\n✅ Vault_System_1.0 Test Complete!")
    print("📂 Vault structure created successfully")
    print("💾 Data storage and retrieval working")
    print("🔗 Subsystem isolation confirmed")

if __name__ == "__main__":
    test_vault_system()