#!/usr/bin/env python3
"""
Test script for the Worker Forge Engine
"""
from forge_engine import forge_worker

# Test forging a worker
dals_db = {"workers": []}

try:
    # Temporarily modify forge_engine to skip docker for testing
    import forge_engine
    original_build = forge_engine.build_and_launch_worker
    forge_engine.build_and_launch_worker = lambda *args: print("Skipping Docker build for test")

    entry = forge_worker(
        worker_name="TestWorker",
        worker_type="ledger",
        class_code="300.100.000",
        seq=1,
        dals_db=dals_db
    )

    # Restore
    forge_engine.build_and_launch_worker = original_build

    print("Worker forged successfully!")
    print(f"Entry: {entry}")
    print(f"Total workers: {len(dals_db['workers'])}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()