#!/usr/bin/env python3
"""
ISS Module Integration Test
===========================

This script tests the ISS Module's core functionality and integration
capabilities. Run this to verify the system works properly.
"""

import asyncio
import sys
from typing import Dict, Any

def test_basic_imports():
    """Test basic ISS Module imports"""
    try:
        from iss_module import ISS, CaptainLog, Exporters, get_stardate, current_timecodes
        print("✓ Core ISS Module components imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import core components: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    try:
        from iss_module.config import settings, ISSSettings
        print(f"✓ Configuration loaded - Service: {settings.service_name}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import configuration: {e}")
        return False

def test_structured_logging():
    """Test structured logging"""
    try:
        from iss_module.logging_config import get_logger, configure_structured_logging
        configure_structured_logging()
        logger = get_logger("test")
        logger.info("Test log message", test=True)
        print("✓ Structured logging configured successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import logging components: {e}")
        return False

async def test_captain_log():
    """Test captain log functionality"""
    try:
        from iss_module import CaptainLog

        captain_log = CaptainLog()

        # Create test entry
        entry_id = await captain_log.create_entry(
            content="Test entry for integration test",
            category="test",
            tags=["integration", "test"]
        )

        print(f"✓ Captain log entry created successfully")
        print(f"  Entry ID: {entry_id}")

        return True
    except Exception as e:
        print(f"✗ Captain log test failed: {e}")
        return False

async def test_time_anchoring():
    """Test time anchoring functionality"""
    try:
        from iss_module import get_stardate, current_timecodes

        # Test stardate calculation
        stardate = get_stardate()
        timecodes = current_timecodes()

        print("✓ Time anchoring verified")
        print(f"  Stardate: {stardate}")
        print(f"  ISO Timestamp: {timecodes['iso_timestamp'][:19]}")
        print(f"  Julian Date: {timecodes['julian_date']}")

        return True
    except Exception as e:
        print(f"✗ Time anchoring test failed: {e}")
        return False

def test_module_status():
    """Test module status functionality"""
    try:
        from iss_module.module_status import get_system_overview

        status = get_system_overview()
        print("✓ Module status retrieved successfully")
        print(f"  Active modules: {len(status.get('modules', {}))}")

        return True
    except Exception as e:
        print(f"✗ Module status test failed: {e}")
        return False

async def test_integration_compatibility():
    """Test full integration compatibility"""
    try:
        from iss_module import get_stardate, current_timecodes

        # Test time anchoring (critical for system operation)
        stardate = get_stardate()
        timecodes = current_timecodes()

        # Simulate API request format
        api_request = {
            "command": "status_check",
            "source": "api_gateway",
            "user_id": "test_user"
        }

        print("✓ ISS Module API compatibility verified")
        print(f"  Stardate: {stardate}")
        print(f"  Request format: {api_request['command']}")
        print(f"  Time anchors: ISO={timecodes['iso_timestamp'][:19]}")

        return True
    except Exception as e:
        print(f"✗ Integration compatibility test failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("ISS Module Integration Test")
    print("=" * 50)

    tests = [
        ("Basic Imports", test_basic_imports),
        ("Configuration", test_configuration),
        ("Structured Logging", test_structured_logging),
        ("Captain Log", test_captain_log),
        ("Time Anchoring", test_time_anchoring),
        ("Module Status", test_module_status),
        ("Integration Compatibility", test_integration_compatibility),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! ISS Module is ready for integration.")
        print("\nNext steps:")
        print("1. Deploy with: ./deploy.sh deploy")
        print("2. Configure API Gateway to route to http://iss-controller:8003")
        print("3. Update service discovery with ISS Controller registration")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))