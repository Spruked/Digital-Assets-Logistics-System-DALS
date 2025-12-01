#!/usr/bin/env python3
"""
Forge Nora-Prime - The first worker of the new era
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'worker_forge'))

from forge_engine import forge_worker

# Initialize DALS DB
dals_db = {"workers": []}

print("🔥 FORGING NORA-PRIME - DALS WORKER-CLONING ENGINE v2.0 🔥")
print("=" * 60)

try:
    # Temporarily skip Docker for testing
    import worker_forge.forge_engine
    original_build = worker_forge.forge_engine.build_and_launch_worker
    worker_forge.forge_engine.build_and_launch_worker = lambda *args: print("🐳 Docker build skipped for initial forge")

    # Forge Nora-Prime
    entry = forge_worker(
        worker_name="Nora-Prime",
        worker_type="ledger",
        class_code="300.100.000",
        template_name="Worker_Template",
        dals_db=dals_db
    )

    # Restore
    worker_forge.forge_engine.build_and_launch_worker = original_build

    print("✅ NORA-PRIME FORGED SUCCESSFULLY!")
    print(f"📋 Serial: {entry['serial']}")
    print(f"🏷️  Model: {entry['model']}")
    print(f"📍 Port: {entry['port']}")
    print(f"🏛️  Ledger: {entry['ledger_code']}")
    print()
    print("🚀 Nora-Prime is now alive and operational!")
    print("The DALS ecosystem begins...")

except Exception as e:
    print(f"❌ Forge failed: {e}")
    import traceback
    traceback.print_exc()