import sys
sys.path.insert(0, '.')

try:
    from dashboard_server import app
    print('✅ Dashboard server imported successfully')

    # Test template loading
    from pathlib import Path
    templates_dir = Path('iss_module/templates')
    static_dir = Path('iss_module/static')

    print(f'📁 Templates dir exists: {templates_dir.exists()}')
    print(f'📁 Static dir exists: {static_dir.exists()}')
    print(f'📄 Dashboard template exists: {(templates_dir / "dashboard.html").exists()}')

    # Try to create a test request
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get('/')
    print(f'🧪 Test request: {response.status_code}')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()