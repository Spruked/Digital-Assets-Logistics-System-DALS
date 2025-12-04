# DALS Worker Registry - Production System

## Overview

The DALS Worker Registry provides production-ready worker tracking with:

- **DMN** (DALS Model Numbers): Family + generation identifiers
- **DSN** (DALS Serial Numbers): Unique collision-proof serials with embedded metadata
- **Automatic registration**: Workers self-register on startup
- **Heartbeat monitoring**: Track worker health in real-time

## Model Number Format (DMN)

```
DMN-XX-YY
 │   │  │
 │   │  └─ Generation (01 = first stable, 02 = major upgrade)
 │   └──── Family code (TM=TrueMark, RG=Regent, GT=GOAT, etc.)
 └──────── DALS Model Number prefix
```

### Current Families

| Family | Code | Description              | Example Model |
|--------|------|--------------------------|---------------|
| TrueMark | TM | NFT Minting Workers     | DMN-TM-01     |
| Regent   | RG | Timeline/Greeter Workers| DMN-RG-01     |
| GOAT     | GT | Teaching System Workers | DMN-GT-01     |
| SKG      | SK | Knowledge Graph Workers | DMN-SK-01     |
| Bubble   | BB | Host Bubble Workers     | DMN-BB-01     |
| Generic  | GN | Experimental/Unknown    | DMN-GN-01     |

## Serial Number Format (DSN)

```
DMN-TM-01-A7F3B9E1-89F2C
│         │        │
│         │        └─ Counter (5 hex digits from timestamp)
│         └────────── UUID4 shard (8 hex digits)
└──────────────────── Model number prefix
```

**Properties:**
- Globally unique (UUID4 + timestamp)
- Embeds model lineage
- Never collides even with 10,000+ simultaneous deployments
- Sortable by deployment time (counter component)

## API Endpoints

### Register Worker
```bash
POST /api/workers/register
{
  "name": "Josephine-01",
  "worker_type": "truemark",
  "api_url": "http://localhost:8080",
  "user_id": "user_123"
}

Response:
{
  "worker_name": "Josephine-01",
  "worker_type": "truemark",
  "model_number": "DMN-TM-01",
  "serial_number": "DMN-TM-01-A7F3B9E1-89F2C",
  "api_url": "http://localhost:8080",
  "user_id": "user_123",
  "deployed_at": 1733154789.123,
  "deployed_iso": "2024-12-02T18:33:09Z",
  "status": "registered",
  "heartbeat": null
}
```

### Send Heartbeat
```bash
POST /api/workers/heartbeat
{
  "worker_name": "Josephine-01"
}

Response:
{
  "status": "updated",
  "worker": "Josephine-01"
}
```

### List All Workers
```bash
GET /api/workers/list

Response: [
  {
    "worker_name": "Josephine-01",
    "model_number": "DMN-TM-01",
    "serial_number": "DMN-TM-01-A7F3B9E1-89F2C",
    "status": "active",
    ...
  }
]
```

### Get Worker Details
```bash
GET /api/workers/Josephine-01

Response: {
  "worker_name": "Josephine-01",
  "model_number": "DMN-TM-01",
  ...
}
```

### Registry Status
```bash
GET /api/workers/status

Response:
{
  "available": true,
  "total_workers": 3,
  "active_workers": 2,
  "model_families": ["BB", "RG", "TM"]
}
```

### Model Catalog
```bash
GET /api/workers/models/catalog

Response:
{
  "truemark": "DMN-TM-01",
  "truemark-v2": "DMN-TM-02",
  "regent": "DMN-RG-01",
  "regent-pro": "DMN-RG-02",
  ...
}
```

## Worker Self-Registration

Workers automatically register on startup:

```python
def _register_with_dals(self) -> None:
    """Self-register with DALS Worker Registry."""
    try:
        registration_data = {
            "name": f"{WORKER_NAME}-{self.user_id}",
            "worker_type": "truemark",  # Must match MODEL_CATALOG key
            "api_url": f"http://localhost:{WORKER_PORT}",
            "user_id": self.user_id
        }
        
        response = requests.post(
            f"{API_BASE}/workers/register",
            json=registration_data,
            timeout=5
        )
        
        if response.status_code == 200:
            reg_data = response.json()
            self.model_number = reg_data.get("model_number")
            self.serial_number = reg_data.get("serial_number")
            print(f"✓ Registered: {self.model_number} - {self.serial_number}")
    except Exception as e:
        print(f"⚠ Registration failed: {e}")
```

## Heartbeat System

Workers send heartbeats every 30-60 seconds:

```python
def _send_heartbeat(self) -> None:
    """Send heartbeat to DALS registry."""
    try:
        requests.post(
            f"{API_BASE}/workers/heartbeat",
            json={"worker_name": f"{WORKER_NAME}-{self.user_id}"},
            timeout=3
        )
    except:
        pass  # Silent fail - heartbeat is non-critical

# In main loop:
heartbeat_counter = 0
while True:
    # ... process messages ...
    
    heartbeat_counter += 1
    if heartbeat_counter >= 60:  # Every ~30s at 0.5s sleep
        self._send_heartbeat()
        heartbeat_counter = 0
    
    time.sleep(0.5)
```

## Deployment

### 1. Start DALS API
```bash
python -m iss_module.api.api
# Runs on port 8003
```

### 2. Verify Registry
```bash
python verify_worker_registry.py
```

### 3. Deploy Worker
```bash
# Josephine (TrueMark worker)
export TARGET_USER_ID=user_123
python worker_templates/josephine_truemark_worker.py

# Or via Docker
docker run -d \
  -e WORKER_NAME=Josephine \
  -e TARGET_USER_ID=user_123 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  --name josephine-user123 \
  host-bubble-worker
```

### 4. Monitor Workers
```bash
# List all workers
curl http://localhost:8003/api/workers/list | jq

# Check specific worker
curl http://localhost:8003/api/workers/Josephine-user_123 | jq

# Monitor registry status
watch -n 5 'curl -s http://localhost:8003/api/workers/status | jq'
```

## Adding New Worker Types

1. **Add to MODEL_CATALOG** in `dals/registry/worker_registry.py`:
   ```python
   MODEL_CATALOG = {
       # ... existing entries ...
       "new-worker-type": "DMN-NW-01",  # NW = New Worker family
   }
   ```

2. **Worker registers using the type**:
   ```python
   registration_data = {
       "name": "NewWorker-01",
       "worker_type": "new-worker-type",  # Matches catalog key
       ...
   }
   ```

3. **Deploy and verify**:
   ```bash
   python verify_worker_registry.py
   ```

## Benefits

✅ **Instant lineage visibility**: See family and generation at a glance  
✅ **Bug isolation**: Know if issue affects DMN-TM-01 only or all v01  
✅ **Collision-proof**: UUID4 + timestamp ensures uniqueness  
✅ **Monitoring ready**: Serial numbers in logs, telemetry, Caleon  
✅ **Version tracking**: Easy to identify which workers need upgrades  
✅ **Health monitoring**: Heartbeat system shows which workers are alive  

## File Structure

```
dals/
  registry/
    __init__.py              # Module exports
    worker_registry.py       # Core registry logic

iss_module/
  api/
    worker_registry_api.py   # FastAPI endpoints
    api.py                   # Main app (includes registry router)

worker_templates/
  josephine_truemark_worker.py  # Example: Self-registering worker

verify_worker_registry.py    # Verification script
register_josephine.py         # Legacy DALS serial assignment (still valid)
```

## Production Checklist

- [x] Registry module created (`dals/registry/`)
- [x] API endpoints implemented (`worker_registry_api.py`)
- [x] Integrated into main API (`api.py`)
- [x] Josephine self-registers on startup
- [x] Heartbeat system active
- [x] Verification script created
- [ ] Replace in-memory storage with Redis/PostgreSQL
- [ ] Add worker status dashboard
- [ ] Implement worker auto-restart on heartbeat failure
- [ ] Add Caleon integration for worker telemetry
- [ ] Create worker deployment automation (Ansible/K8s)

## Next Steps

**STEP 2 — Confirm Josephine's registration in DALS**

Run the verification:
```bash
python verify_worker_registry.py
```

This will:
1. ✓ Check registry system status
2. ✓ Display model catalog (all DMN codes)
3. ✓ List registered workers
4. ✓ Test registration + heartbeat
5. ✓ Verify Josephine's registration

Then deploy Josephine and watch her appear in the registry! 🎉
