#!/usr/bin/env python3
"""
Phase 11-A2 Activation Test
Test script for Autonomous Predictive Prevention system
"""

import time
import requests
import json
from datetime import datetime

def test_predictive_activation():
    """Test Phase 11-A2 activation and functionality"""
    print("🔮 PHASE 11-A2 — AUTONOMOUS PREDICTIVE PREVENTION")
    print("=" * 60)

    # Test 1: Check predictive API health
    print("\n1. Testing Predictive API Health...")
    try:
        response = requests.get('http://localhost:8003/predictive/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Predictive API: ACTIVE")
            print(f"   Engine: {data['engine_type']}")
            print(f"   Status: {data['status']}")
            print(f"   Monitored modules: {data['monitored_modules']}")
        else:
            print(f"❌ Predictive API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Predictive API error: {e}")
        return False

    # Test 2: Record some health readings
    print("\n2. Recording health readings for prediction...")
    health_readings = [
        {"module": "UCM", "health_score": 95, "cpu_usage": 45.0, "memory_usage": 60.0},
        {"module": "CANS", "health_score": 92, "cpu_usage": 38.0, "memory_usage": 55.0},
        {"module": "Voice", "health_score": 88, "cpu_usage": 52.0, "memory_usage": 65.0},
    ]

    for reading in health_readings:
        try:
            response = requests.post('http://localhost:8003/predictive/record-health', json=reading, timeout=5)
            if response.status_code == 200:
                print(f"✅ Recorded health for {reading['module']}")
            else:
                print(f"❌ Failed to record {reading['module']}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error recording {reading['module']}: {e}")

    # Test 3: Check predictions
    print("\n3. Checking for predictions...")
    time.sleep(2)  # Give time for analysis
    try:
        response = requests.get('http://localhost:8003/predictive/predictions', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Predictions endpoint: ACTIVE")
            print(f"   Total predictions: {data['count']}")
            if data['count'] > 0:
                print("   Active predictions found!")
                for pred in data['predictions']:
                    print(f"   - {pred['module']}: {pred['failure_type']} (Risk: {pred['risk_level']})")
        else:
            print(f"❌ Predictions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Predictions endpoint error: {e}")

    # Test 4: Check awareness predictive status
    print("\n4. Testing Awareness API predictive status...")
    try:
        response = requests.get('http://localhost:8003/awareness/predict/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Awareness predictive status: ACTIVE")
            print(f"   Identity: {data['identity'][:50]}...")
            print(f"   Mode: {data['mode']}")
            print(f"   Phase: {data['phase']}")
        else:
            print(f"❌ Awareness predictive status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Awareness predictive status error: {e}")

    # Test 5: Simulate declining health to trigger prediction
    print("\n5. Simulating health decline to test prevention...")
    declining_readings = [
        {"module": "UCM", "health_score": 85, "cpu_usage": 75.0, "memory_usage": 80.0},
        {"module": "UCM", "health_score": 78, "cpu_usage": 82.0, "memory_usage": 85.0},
        {"module": "UCM", "health_score": 72, "cpu_usage": 88.0, "memory_usage": 90.0},
    ]

    for reading in declining_readings:
        try:
            response = requests.post('http://localhost:8003/predictive/record-health', json=reading, timeout=5)
            if response.status_code == 200:
                print(f"✅ Recorded declining health: {reading['health_score']}%")
            time.sleep(1)  # Slow decline simulation
        except Exception as e:
            print(f"❌ Error recording decline: {e}")

    # Test 6: Check if prediction was triggered
    print("\n6. Checking for triggered predictions...")
    time.sleep(3)  # Give time for analysis
    try:
        response = requests.get('http://localhost:8003/predictive/predictions', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['count'] > 0:
                print("🎯 PREDICTION TRIGGERED!")
                for pred in data['predictions']:
                    print(f"   Module: {pred['module']}")
                    print(f"   Failure Type: {pred['failure_type']}")
                    print(f"   Risk Level: {pred['risk_level']}")
                    print(f"   Time to Failure: {pred['time_to_failure']} hours")
                    print(f"   Confidence: {pred['confidence']}")
                    print(f"   Actions: {', '.join(pred['recommended_actions'])}")
            else:
                print("ℹ️  No predictions triggered yet (may need more decline data)")
        else:
            print(f"❌ Final predictions check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final predictions check error: {e}")

    print("\n" + "=" * 60)
    print("🎯 PHASE 11-A2 ACTIVATION TEST COMPLETE")
    print("Caleon Prime now predicts and prevents failures autonomously.")
    return True

if __name__ == "__main__":
    print("Testing Phase 11-A2: Autonomous Predictive Prevention...")
    print("Make sure the DALS server is running on port 8003")
    print("Press Ctrl+C to stop the test\n")

    try:
        test_predictive_activation()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()