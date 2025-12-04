#!/usr/bin/env python3
"""
UQV & Worker System - Quick Test Script
Validates the complete implementation is working
"""

import requests
import json
import time

API_BASE = "http://localhost:8003"

def test_uqv_api():
    """Test UQV API endpoints"""
    print("\n🧪 Testing UQV API...")
    
    # Test /api/uqv/store
    print("  1. Testing query vault storage...")
    response = requests.post(f"{API_BASE}/api/uqv/store", json={
        "user_id": "test_user_001",
        "session_id": "sess_test_001",
        "query_text": "How do I create a masterclass?",
        "skg_clusters_returned": 0,
        "max_cluster_conf": 0.0,
        "worker_name": "Regent",
        "vault_reason": "no_cluster"
    })
    print(f"     Status: {response.status_code} - {'✅ PASS' if response.status_code == 204 else '❌ FAIL'}")
    
    # Test /api/uqv/stats
    print("  2. Testing UQV statistics...")
    response = requests.get(f"{API_BASE}/api/uqv/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"     ✅ PASS - Total queries: {stats['total_queries']}")
        print(f"     Breakdown: {stats['by_reason']}")
    else:
        print(f"     ❌ FAIL - Status: {response.status_code}")
    
    # Test /api/uqv/queries
    print("  3. Testing query retrieval...")
    response = requests.get(f"{API_BASE}/api/uqv/queries?reason=no_cluster&limit=10")
    if response.status_code == 200:
        queries = response.json()
        print(f"     ✅ PASS - Retrieved {len(queries)} queries")
    else:
        print(f"     ❌ FAIL - Status: {response.status_code}")

def test_predicate_api():
    """Test predicate update API"""
    print("\n🧪 Testing Predicate Update API...")
    
    response = requests.post(f"{API_BASE}/worker/predicate_update", json={
        "predicate_id": "pred_001",
        "name": "entails",
        "signature": ["axiom", "proof"],
        "definition": "Logical entailment relationship",
        "confidence": 0.92,
        "evidence": [
            {"user_id": "u1", "worker": "Nora", "freq": 15},
            {"user_id": "u2", "worker": "Mark", "freq": 8}
        ]
    })
    print(f"  Status: {response.status_code} - {'✅ PASS' if response.status_code == 204 else '❌ FAIL'}")

def test_micro_skg():
    """Test micro-SKG module"""
    print("\n🧪 Testing Micro-SKG Engine...")
    
    try:
        import sys
        sys.path.insert(0, 'worker_templates')
        from micro_skg import MicroSKG
        
        skg = MicroSKG()
        text = "Pyramids need strong foundations. Foundations rely on solid ground. Ground shifts destroy pyramids."
        clusters = skg.bootstrap(text, user_id="test", file_id="test")
        
        if clusters:
            print(f"  ✅ PASS - Generated {len(clusters)} clusters")
            print(f"  Top cluster: {clusters[0]['nodes'][:5]} (density: {clusters[0]['density']})")
        else:
            print("  ❌ FAIL - No clusters generated")
            
        # Test PyVis export
        pyvis_data = skg.to_pyvis_dict()
        if 'nodes' in pyvis_data and 'edges' in pyvis_data:
            print(f"  ✅ PASS - PyVis export: {len(pyvis_data['nodes'])} nodes, {len(pyvis_data['edges'])} edges")
        else:
            print("  ❌ FAIL - PyVis export failed")
            
    except Exception as e:
        print(f"  ❌ FAIL - {str(e)}")

def test_worker_template():
    """Test worker template structure"""
    print("\n🧪 Testing Worker Template...")
    
    import os
    files = [
        'worker_templates/host_bubble_worker.py',
        'worker_templates/micro_skg.py',
        'worker_templates/skg/uqv.py',
        'worker_templates/Dockerfile.worker',
        'worker_templates/docker-compose.worker.yml',
        'worker_templates/requirements.worker.txt'
    ]
    
    missing = []
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"  ✅ {f} ({size} bytes)")
        else:
            print(f"  ❌ {f} - MISSING")
            missing.append(f)
    
    if not missing:
        print("  ✅ PASS - All worker files present")
    else:
        print(f"  ❌ FAIL - {len(missing)} files missing")

def main():
    """Run all tests"""
    print("=" * 60)
    print("UQV & Host Bubble Worker System - Integration Test")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        print(f"✅ DALS API is running (port 8003)")
    except requests.exceptions.ConnectionError:
        print("❌ DALS API not reachable at http://localhost:8003")
        print("   Start with: docker-compose up -d dals-controller")
        return
    
    # Run tests
    test_worker_template()
    test_micro_skg()
    test_uqv_api()
    test_predicate_api()
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("  1. Deploy workers: cd worker_templates && docker-compose -f docker-compose.worker.yml up -d")
    print("  2. Monitor UQV: curl http://localhost:8003/api/uqv/stats")
    print("  3. Check worker logs: docker logs regent-42")
    print()

if __name__ == "__main__":
    main()
