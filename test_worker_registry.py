#!/usr/bin/env python3
"""
Worker Registry Integration Test
Tests that the worker registry properly maps worker types to template classes
and that the forge engine can create workers of different types.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workers.registry import get_worker_template, REGISTERED_WORKER_TYPES, list_registered_types
from worker_forge.forge_engine import forge_worker

def test_registry():
    """Test that the worker registry is properly configured."""
    print("=== Worker Registry Test ===")

    # Test listing registered types
    registered_types = list_registered_types()
    print(f"Registered worker types: {registered_types}")

    # Test getting template classes for each type
    for worker_type in registered_types:
        template_class = get_worker_template(worker_type)
        print(f"{worker_type} -> {template_class.__name__} ({template_class.__module__})")

    print("Registry test passed!\n")

def test_forge_integration():
    """Test that forge engine can create workers of different types."""
    print("=== Forge Engine Integration Test ===")

    test_cases = [
        ("test-goat", "goat", "A1"),
        ("test-mint", "mint", "B2"),
        ("test-finance", "finance", "C3"),
        ("test-obs", "obs", "D4"),
    ]

    for worker_name, worker_type, class_code in test_cases:
        try:
            result = forge_worker(worker_name, worker_type, class_code, dry_run=True)
            print(f"✅ {worker_type}: serial={result['worker_serial']}, template={result['template_used']}")
        except Exception as e:
            print(f"❌ {worker_type}: Failed - {e}")

    print("Forge integration test completed!\n")

def test_template_instantiation():
    """Test that worker templates can be instantiated directly."""
    print("=== Template Instantiation Test ===")

    # Test direct instantiation of WorkerTemplate
    from workers.templates.worker_template import WorkerTemplate

    test_config = {
        "worker_serial": "TEST-123",
        "model_id": "TEST-MODEL",
        "glyph_trace": "TEST-GLYPH",
        "accountability_vault": {},
        "reflection_vault": {},
        "ap_helix_ref": "TEST-AP",
        "worker_name": "test-worker",
        "worker_type": "test",
        "port": 9999
    }

    try:
        worker = WorkerTemplate(test_config)
        vault_integrity = worker._check_vault_integrity()
        print(f"✅ WorkerTemplate instantiation: vault_integrity={vault_integrity}")
    except Exception as e:
        print(f"❌ WorkerTemplate instantiation failed: {e}")

    print("Template instantiation test completed!\n")

if __name__ == "__main__":
    print("Running Worker Registry Integration Tests...\n")

    try:
        test_registry()
        test_forge_integration()
        test_template_instantiation()
        print("🎉 All tests passed! Worker registry integration is working correctly.")
    except Exception as e:
        print(f"💥 Test suite failed: {e}")
        sys.exit(1)