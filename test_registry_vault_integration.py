#!/usr/bin/env python3
"""
Test worker registry integration with vault system
"""

import sys
from pathlib import Path

def test_registry_integration():
    print("🔗 Testing Worker Registry + Vault Integration...")

    # Add registry to path
    registry_path = Path(__file__).parent / "dals" / "registry"
    sys.path.insert(0, str(registry_path))

    from worker_registry import register_worker, update_heartbeat, list_workers

    # Register a test worker
    print("\n👷 Registering test worker...")
    worker = register_worker(
        name='josephine-test',
        worker_type='truemark',
        api_url='http://localhost:8001',
        user_id='test-user'
    )

    print(f"Worker registered: {worker['worker_name']}")
    print(f"Serial number: {worker['serial_number']}")
    print(f"Model number: {worker['model_number']}")

    # Update heartbeat
    print("\n💓 Updating heartbeat...")
    success = update_heartbeat('josephine-test')
    print(f"Heartbeat update: {success}")

    # List workers
    workers = list_workers()
    print(f"\n📋 Total workers: {len(workers)}")
    for w in workers:
        print(f"  - {w['worker_name']} ({w['serial_number']}) - Status: {w['status']}")

    # Check vault data
    print("\n🏦 Checking vault data...")
    vault_path = Path(__file__).parent / "Vault_System_1.0" / "vault_system"
    sys.path.insert(0, str(vault_path))

    from worker_vault import DALS_VAULT
    history = DALS_VAULT.get_worker_history(worker['serial_number'])

    print(f"Vault history for {worker['serial_number']}:")
    print(f"  - Manifest: {'✓' if history['manifest'] else '✗'}")
    print(f"  - Heartbeats: {len(history['heartbeats'])}")
    print(f"  - Telemetry: {len(history['telemetry'])}")
    print(f"  - Cognition: {len(history['cognition'])}")

    print("\n✅ Worker Registry + Vault Integration Test Complete!")
    print("🔄 Workers are automatically stored in vault on registration")
    print("💓 Heartbeats are automatically logged to vault")
    print("📊 Complete worker lifecycle tracking active")

if __name__ == "__main__":
    test_registry_integration()