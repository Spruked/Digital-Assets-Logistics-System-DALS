"""
DALS Worker Registry Verification Script
Verifies worker registration, model numbers, and heartbeat system.
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8003"

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def verify_registry_status():
    """Verify registry system is operational."""
    print_section("1. Registry System Status")
    
    try:
        response = requests.get(f"{API_BASE}/api/workers/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Registry Available: {data['available']}")
            print(f"✓ Total Workers: {data['total_workers']}")
            print(f"✓ Active Workers: {data['active_workers']}")
            print(f"✓ Model Families: {', '.join(data['model_families'])}")
            return True
        else:
            print(f"✗ Registry status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Registry not reachable: {e}")
        return False

def verify_model_catalog():
    """Verify model catalog is loaded."""
    print_section("2. Model Catalog")
    
    try:
        response = requests.get(f"{API_BASE}/api/workers/models/catalog", timeout=5)
        
        if response.status_code == 200:
            catalog = response.json()
            print(f"✓ Catalog loaded with {len(catalog)} worker types\n")
            
            # Group by family
            families = {}
            for worker_type, model_number in catalog.items():
                family = model_number.split("-")[1] if "-" in model_number else "UNKNOWN"
                if family not in families:
                    families[family] = []
                families[family].append((worker_type, model_number))
            
            # Display by family
            for family, workers in sorted(families.items()):
                print(f"\n{family} Family:")
                for worker_type, model_number in sorted(workers):
                    print(f"  • {worker_type:20s} → {model_number}")
            
            return True
        else:
            print(f"✗ Catalog fetch failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Catalog not accessible: {e}")
        return False

def list_registered_workers():
    """List all registered workers."""
    print_section("3. Registered Workers")
    
    try:
        response = requests.get(f"{API_BASE}/api/workers/list", timeout=5)
        
        if response.status_code == 200:
            workers = response.json()
            
            if not workers:
                print("⚠ No workers registered yet")
                return []
            
            print(f"✓ Found {len(workers)} registered worker(s)\n")
            
            for worker in workers:
                print(f"Worker: {worker['worker_name']}")
                print(f"  Model:      {worker['model_number']}")
                print(f"  Serial:     {worker['serial_number']}")
                print(f"  Type:       {worker['worker_type']}")
                print(f"  Status:     {worker['status']}")
                print(f"  User ID:    {worker['user_id']}")
                print(f"  Deployed:   {worker['deployed_iso']}")
                
                if worker['heartbeat']:
                    age = time.time() - worker['heartbeat']
                    print(f"  Heartbeat:  {age:.1f}s ago")
                else:
                    print(f"  Heartbeat:  Never")
                print()
            
            return workers
        else:
            print(f"✗ Worker list fetch failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"✗ Worker list not accessible: {e}")
        return []

def test_worker_registration():
    """Test registering a mock worker."""
    print_section("4. Registration Test")
    
    try:
        test_data = {
            "name": f"TestWorker-{int(time.time())}",
            "worker_type": "truemark",
            "api_url": "http://localhost:9999",
            "user_id": "test_user"
        }
        
        print(f"Registering test worker: {test_data['name']}")
        
        response = requests.post(
            f"{API_BASE}/api/workers/register",
            json=test_data,
            timeout=5
        )
        
        if response.status_code == 200:
            worker = response.json()
            print(f"\n✓ Registration successful!")
            print(f"  Model Number:  {worker['model_number']}")
            print(f"  Serial Number: {worker['serial_number']}")
            print(f"  Status:        {worker['status']}")
            
            # Test heartbeat
            print(f"\nTesting heartbeat for {worker['worker_name']}...")
            hb_response = requests.post(
                f"{API_BASE}/api/workers/heartbeat",
                json={"worker_name": worker['worker_name']},
                timeout=5
            )
            
            if hb_response.status_code == 200:
                print(f"✓ Heartbeat successful")
            else:
                print(f"✗ Heartbeat failed: {hb_response.status_code}")
            
            return True
        else:
            print(f"✗ Registration failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Registration test failed: {e}")
        return False

def verify_josephine():
    """Check if Josephine is registered."""
    print_section("5. Josephine Status")
    
    try:
        response = requests.get(f"{API_BASE}/api/workers/list", timeout=5)
        
        if response.status_code == 200:
            workers = response.json()
            josephine_workers = [w for w in workers if "josephine" in w['worker_name'].lower()]
            
            if josephine_workers:
                print(f"✓ Found {len(josephine_workers)} Josephine instance(s)\n")
                for worker in josephine_workers:
                    print(f"Instance: {worker['worker_name']}")
                    print(f"  Model:  {worker['model_number']} (Expected: DMN-TM-01)")
                    print(f"  Serial: {worker['serial_number']}")
                    print(f"  Status: {worker['status']}")
                    
                    if worker['heartbeat']:
                        age = time.time() - worker['heartbeat']
                        status_emoji = "🟢" if age < 120 else "🟡" if age < 300 else "🔴"
                        print(f"  Health: {status_emoji} Last seen {age:.0f}s ago")
                    else:
                        print(f"  Health: 🔴 No heartbeat")
                    print()
                return True
            else:
                print("⚠ No Josephine instances found")
                print("\nTo deploy Josephine:")
                print("  python worker_templates/josephine_truemark_worker.py")
                print("  (with TARGET_USER_ID=user_123 environment variable)")
                return False
        else:
            print(f"✗ Could not check workers: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Run complete verification suite."""
    print("\n" + "█" * 70)
    print("  DALS WORKER REGISTRY VERIFICATION")
    print("█" * 70)
    
    # Run all checks
    results = {
        "Registry Status": verify_registry_status(),
        "Model Catalog": verify_model_catalog(),
        "Worker Listing": list_registered_workers() is not None,
        "Registration Test": test_worker_registration(),
        "Josephine Check": verify_josephine()
    }
    
    # Summary
    print_section("Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {check}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All systems operational!")
        print("\nNext steps:")
        print("  1. Deploy Josephine worker instance")
        print("  2. Monitor registry: curl http://localhost:8003/api/workers/list | jq")
        print("  3. Check heartbeats every 30-60 seconds")
    else:
        print("\n⚠ Some checks failed. Review errors above.")
        print("\nTroubleshooting:")
        print("  • Ensure DALS API is running on port 8003")
        print("  • Check dals/registry/worker_registry.py exists")
        print("  • Verify worker_registry_api.py is imported in api.py")
    
    print("\n" + "█" * 70)

if __name__ == "__main__":
    main()
