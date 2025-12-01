import subprocess
import sys
import requests
import os

print('🚀 DALS Complete System Health Check')
print('=' * 60)

def check_service(name, command=None, url=None):
    print(f'\n🔍 Testing {name}...')
    try:
        if command:
            result = subprocess.run([sys.executable] + command,
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f'✅ {name}: Command executed successfully')
                return True
            else:
                print(f'❌ {name}: Command failed')
                return False

        if url:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f'✅ {name}: HTTP {response.status_code}')
                return True
            else:
                print(f'❌ {name}: HTTP {response.status_code}')
                return False

    except Exception as e:
        print(f'❌ {name}: Error - {str(e)}')
        return False

    return False

# Test components
results = []

# 1. Basic imports
results.append(check_service('Core Imports', ['-c', 'from iss_module.core import utils; print("Import OK")']))

# 2. API endpoints
try:
    response = requests.get('http://localhost:8003/api/v1/iss/now', timeout=5)
    print('\n✅ API Endpoints: Available')
    results.append(True)
except:
    print('\n❌ API Endpoints: Server not running')
    results.append(False)

# 3. Dashboard
try:
    response = requests.get('http://localhost:8008/', timeout=5)
    print('✅ Dashboard: Available')
    results.append(True)
except:
    print('❌ Dashboard: Server not running')
    results.append(False)

# 4. Vault integrity
vaults = ["vault", "minds/soul_vault", "Vault_System_1.0/vault_system"]
vault_count = len([v for v in vaults if os.path.exists(v)])
print(f'\n🔍 Testing Vault Integrity...')
print(f'✅ Vault Integrity: {vault_count}/3 vaults present')
results.append(vault_count == 3)

# 5. Integration tests
results.append(check_service('Integration Tests', ['test_integration.py']))

print('\n' + '=' * 60)
passed = sum(results)
total = len(results)
print(f'📊 Health Check Results: {passed}/{total} components healthy')

if passed == total:
    print('🎉 ALL SYSTEMS OPERATIONAL - DALS is ready!')
else:
    print('⚠️  Some components need attention')

print('=' * 60)