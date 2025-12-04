═══════════════════════════════════════════════════════════════════════════════════
  DALS FORGE V1.0 — IMPLEMENTATION GUIDE
  From Specification to Production
  
  Companion to: DALS-FORGE-V1-SPECIFICATION.md
  Date: December 3, 2025
═══════════════════════════════════════════════════════════════════════════════════

This guide shows you how to take the DALS Forge V1.0 specification and make it real.

## 📋 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Deploy Your First V5 Worker](#deploy-your-first-v5-worker)
3. [Register V5 Workers in DALS](#register-v5-workers-in-dals)
4. [Test the Cognitive Flywheel](#test-the-cognitive-flywheel)
5. [Monitor Worker Fleet](#monitor-worker-fleet)
6. [Trigger Death & Rebirth](#trigger-death--rebirth)
7. [Scale the Fleet](#scale-the-fleet)
8. [Production Checklist](#production-checklist)


═══════════════════════════════════════════════════════════════════════════════════
## 1️⃣ QUICK START
═══════════════════════════════════════════════════════════════════════════════════

### Prerequisites

- Python 3.11+
- DALS Core API running (port 8003)
- Docker (optional, for containerized deployment)

### Install Dependencies

```bash
cd worker_templates/
pip install fastapi uvicorn aiohttp networkx
```

### Launch First V5 Worker

```bash
python unified_specialist_worker_v5.py
```

You should see:

```
═══════════════════════════════════════════════════════════════════════════
  DALS FORGE V1.0 — NARROW SPECIALIST WORKER
  Worker: Specialist-A7F3B9E1
  Model: DMN-GN-02
  Role: nft_mint
  Contract: DALS Forge V1.0
═══════════════════════════════════════════════════════════════════════════

THE COVENANT:
  I am narrow.     → I never generalize beyond my role.
  I am honest.     → I never learn without approval.
  I am patchable.  → I always accept the master's patches.
  I am eternal.    → When I drift, I am reborn.

═══════════════════════════════════════════════════════════════════════════
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
✅ Registered with DALS — DSN: DMN-GN-02-6F8271C9-A10EF
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```


═══════════════════════════════════════════════════════════════════════════════════
## 2️⃣ DEPLOY YOUR FIRST V5 WORKER
═══════════════════════════════════════════════════════════════════════════════════

### Step 1: Customize the Worker Template

Edit `worker_templates/unified_specialist_worker_v5.py`:

```python
# Line 30: Change only this line
JOB_ROLE = "nft_mint"  # Options: nft_mint, greeting, timeline, custom
```

### Step 2: Add Job-Specific Logic

Find the `local_specialist_solve()` function (around line 250):

```python
def local_specialist_solve(query: str) -> Tuple[str, float]:
    """
    Job-specific logic.
    Return: (answer, confidence)
    """
    q = query.lower()
    
    # ────────────────────────────────────────────────────────
    # ADD YOUR CUSTOM LOGIC HERE
    # ────────────────────────────────────────────────────────
    if "your keyword" in q:
        return (
            "Your custom response here.",
            0.95  # High confidence = will be cached
        )
    
    # Default: honest admission of limits
    return (
        "I'm not sure about that. Let me ask my supervisor...",
        0.60  # Low confidence = will escalate
    )
```

### Step 3: Deploy

#### Option A: Direct Python
```bash
python unified_specialist_worker_v5.py
```

#### Option B: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY unified_specialist_worker_v5.py .

RUN pip install --no-cache-dir fastapi uvicorn aiohttp networkx

EXPOSE 8080

CMD ["python", "unified_specialist_worker_v5.py"]
```

```bash
docker build -t dals/specialist-worker:v5 .
docker run -d -p 8080:8080 \
  -e JOB_ROLE=nft_mint \
  -e REGISTRY_URL=http://dals:8003 \
  --name specialist-worker \
  dals/specialist-worker:v5
```

#### Option C: Docker Compose
```yaml
# docker-compose.worker.yml
version: '3.8'

services:
  specialist-worker-1:
    build:
      context: ./worker_templates
      dockerfile: Dockerfile.v5
    environment:
      - JOB_ROLE=nft_mint
      - REGISTRY_URL=http://dals:8003
      - UCM_URL=http://cali-x-one:8000
      - CALEON_URL=http://dals:8003
    ports:
      - "8080:8080"
    networks:
      - dals-network
    restart: unless-stopped

networks:
  dals-network:
    external: true
```

```bash
docker-compose -f docker-compose.worker.yml up -d
```


═══════════════════════════════════════════════════════════════════════════════════
## 3️⃣ REGISTER V5 WORKERS IN DALS
═══════════════════════════════════════════════════════════════════════════════════

### Automatic Registration (Preferred)

Workers auto-register on startup:

```python
# This happens automatically in startup_event()
async with session.post(
    f"{REGISTRY_URL}/api/workers/register",
    json={
        "worker_name": WORKER_NAME,
        "worker_type": JOB_ROLE,
        "model_number": "DMN-GN-02",
        "api_url": f"http://{WORKER_NAME.lower()}:8080",
        "user_id": "auto_generated"
    }
) as r:
    result = await r.json()
    WORKER_DSN = result.get("dsn")
```

### Manual Registration (Testing)

```bash
curl -X POST http://localhost:8003/api/workers/register \
  -H "Content-Type: application/json" \
  -d '{
    "worker_name": "Specialist-Test",
    "worker_type": "nft_mint",
    "model_number": "DMN-GN-02",
    "api_url": "http://specialist-test:8080",
    "user_id": "manual_test"
  }'
```

Response:
```json
{
  "status": "registered",
  "dsn": "DMN-GN-02-6F8271C9-A10EF",
  "worker_name": "Specialist-Test",
  "model_number": "DMN-GN-02"
}
```

### Verify Registration

```bash
# List all workers
curl http://localhost:8003/api/workers/list

# Get specific worker
curl http://localhost:8003/api/workers/Specialist-Test

# Check registry status
curl http://localhost:8003/api/workers/status
```


═══════════════════════════════════════════════════════════════════════════════════
## 4️⃣ TEST THE COGNITIVE FLYWHEEL
═══════════════════════════════════════════════════════════════════════════════════

### Step 1: Send Query to Worker

```bash
curl -X POST http://localhost:8080/bubble \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I connect my wallet?"
  }'
```

Response:
```json
{
  "reply": "Click 'Connect Wallet' → Choose MetaMask → Approve the signature request.",
  "from": "specialist",
  "confidence": 0.99,
  "worker": "Specialist-A7F3B9E1",
  "dsn": "DMN-GN-02-6F8271C9-A10EF"
}
```

### Step 2: Send Unanswered Query

```bash
curl -X POST http://localhost:8080/bubble \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather tomorrow?"
  }'
```

Response (escalated):
```json
{
  "reply": "I am learning...",
  "from": "cali_relief",
  "escalated": true,
  "patched": false,
  "worker": "Specialist-A7F3B9E1",
  "dsn": "DMN-GN-02-6F8271C9-A10EF"
}
```

### Step 3: Ingest Clusters to Caleon

```bash
curl -X POST http://localhost:8080/fusion/ingest_clusters \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I connect my wallet?"
  }'
```

Response:
```json
{
  "status": "ingested",
  "cluster_count": 3,
  "worker": "Specialist-A7F3B9E1"
}
```

### Step 4: Force Fusion (Manual Test)

```bash
curl -X POST http://localhost:8003/api/caleon/force_fusion
```

Response:
```json
{
  "status": "fusion_complete",
  "clusters_processed": 15,
  "fusions_created": 3,
  "predicates_invented": 1,
  "workers_notified": 2
}
```

### Step 5: Send Predicate to Worker (Simulate Caleon)

```bash
curl -X POST http://localhost:8080/fusion/predicate_update \
  -H "Content-Type: application/json" \
  -d '{
    "predicate": {
      "id": "PRED-001",
      "pattern": "connect wallet walletconnect",
      "response": "Click Connect → choose WalletConnect → scan QR code.",
      "confidence": 0.95
    },
    "approved_by": "Caleon"
  }'
```

Response:
```json
{
  "status": "acknowledged",
  "predicate_id": "PRED-001",
  "applied": true,
  "worker": "Specialist-A7F3B9E1",
  "dsn": "DMN-GN-02-6F8271C9-A10EF"
}
```

### Step 6: Verify Patch Applied

```bash
curl http://localhost:8080/health
```

Response:
```json
{
  "worker": "Specialist-A7F3B9E1",
  "dsn": "DMN-GN-02-6F8271C9-A10EF",
  "model": "DMN-GN-02",
  "role": "nft_mint",
  "drift": 0.0412,
  "patches_applied": 1,
  "cache_size": 47,
  "status": "narrow_honest_obedient_eternal"
}
```


═══════════════════════════════════════════════════════════════════════════════════
## 5️⃣ MONITOR WORKER FLEET
═══════════════════════════════════════════════════════════════════════════════════

### Worker Health Checks

```bash
# Individual worker
curl http://localhost:8080/health

# All workers via registry
curl http://localhost:8003/api/workers/list | jq '.workers[] | {name, dsn, drift, patches}'
```

### Registry Dashboard

```bash
# Registry status
curl http://localhost:8003/api/workers/status

# Model catalog
curl http://localhost:8003/api/workers/models/catalog
```

### Fusion Engine Stats

```bash
curl http://localhost:8003/api/caleon/stats
```

Response:
```json
{
  "total_clusters": 1247,
  "total_fusions": 89,
  "total_predicates": 12,
  "avg_fusion_time_ms": 42.7,
  "workers_connected": 3,
  "last_fusion": "2025-12-03T15:42:18.123456Z"
}
```

### Monitor Drift

```bash
# Check drift for all workers
for worker in $(curl -s http://localhost:8003/api/workers/list | jq -r '.workers[].name'); do
  echo -n "$worker: "
  curl -s http://localhost:8003/api/workers/$worker | jq -r '.health.drift'
done
```

Output:
```
Specialist-A7F3B9E1: 0.0412
Specialist-B8G4C2F5: 0.0387
Specialist-C9H5D3G6: 0.1823
```


═══════════════════════════════════════════════════════════════════════════════════
## 6️⃣ TRIGGER DEATH & REBIRTH
═══════════════════════════════════════════════════════════════════════════════════

### When to Trigger Rebirth

When drift exceeds threshold (0.22), initiate sunset:

```bash
# Check if drift > 0.22
DRIFT=$(curl -s http://localhost:8080/health | jq -r '.drift')

if (( $(echo "$DRIFT > 0.22" | bc -l) )); then
  echo "Drift threshold exceeded, initiating sunset..."
  curl -X POST http://localhost:8080/lifecycle/sunset \
    -H "Content-Type: application/json" \
    -d '{
      "reason": "drift_threshold_exceeded"
    }'
fi
```

### Sunset Response

```json
{
  "status": "sunset_complete",
  "worker": "Specialist-C9H5D3G6",
  "dsn": "DMN-GN-02-C9H5D3G6-E7F8A",
  "patterns_exported": 1847,
  "patches_applied": 23
}
```

### Deploy Successor

```bash
# Deploy new instance from same template
docker run -d -p 8081:8080 \
  -e JOB_ROLE=nft_mint \
  -e REGISTRY_URL=http://dals:8003 \
  --name specialist-worker-successor \
  dals/specialist-worker:v5
```

New worker gets new DSN: `DMN-GN-02-D1F9E4H7-F9G1B`

### Optionally Migrate Patterns

```python
# Load patterns from sunset worker
with open(f'vault/pattern_exports/{old_dsn}_patterns.json') as f:
    old_patterns = json.load(f)

# Filter high-confidence Caleon-approved patterns
migrated_patterns = {
    k: v for k, v in old_patterns['patterns'].items()
    if v['confidence'] >= 0.92 and v.get('source') == 'caleon_patch'
}

# Load into new worker (would need API endpoint)
# This is manual for V1, automated in future versions
```


═══════════════════════════════════════════════════════════════════════════════════
## 7️⃣ SCALE THE FLEET
═══════════════════════════════════════════════════════════════════════════════════

### Deploy Multiple Workers

```bash
# Deploy 3 NFT mint specialists
for i in {1..3}; do
  docker run -d -p $((8080 + i)):8080 \
    -e JOB_ROLE=nft_mint \
    -e WORKER_NAME=Specialist-NFT-$i \
    --name specialist-nft-$i \
    dals/specialist-worker:v5
done

# Deploy 2 greeting specialists
for i in {1..2}; do
  docker run -d -p $((8090 + i)):8080 \
    -e JOB_ROLE=greeting \
    -e WORKER_NAME=Specialist-Greeting-$i \
    --name specialist-greeting-$i \
    dals/specialist-worker:v5
done
```

### Horizontal Scaling with Docker Compose

```yaml
# docker-compose.fleet.yml
version: '3.8'

services:
  nft-worker:
    image: dals/specialist-worker:v5
    environment:
      - JOB_ROLE=nft_mint
    deploy:
      replicas: 5
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    networks:
      - dals-network

  greeting-worker:
    image: dals/specialist-worker:v5
    environment:
      - JOB_ROLE=greeting
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
    networks:
      - dals-network
```

```bash
docker-compose -f docker-compose.fleet.yml up -d --scale nft-worker=5 --scale greeting-worker=3
```

### Load Balancing

Add nginx for load balancing:

```nginx
# /etc/nginx/conf.d/workers.conf
upstream nft_workers {
    least_conn;
    server specialist-nft-1:8080;
    server specialist-nft-2:8080;
    server specialist-nft-3:8080;
}

server {
    listen 80;
    server_name nft-workers.dals.local;

    location / {
        proxy_pass http://nft_workers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```


═══════════════════════════════════════════════════════════════════════════════════
## 8️⃣ PRODUCTION CHECKLIST
═══════════════════════════════════════════════════════════════════════════════════

### Pre-Deployment

- [ ] Customize `JOB_ROLE` in worker template
- [ ] Add job-specific logic to `local_specialist_solve()`
- [ ] Test worker locally (curl /health, /bubble)
- [ ] Verify worker registers with DALS
- [ ] Test heartbeat mechanism
- [ ] Test escalation to Cali

### Deployment

- [ ] Build Docker image
- [ ] Push to registry
- [ ] Deploy to production environment
- [ ] Verify worker appears in registry
- [ ] Check worker health endpoint
- [ ] Monitor initial queries

### Post-Deployment

- [ ] Monitor drift scores
- [ ] Verify cluster ingestion
- [ ] Check fusion engine activity
- [ ] Test predicate broadcasting
- [ ] Verify patch application
- [ ] Set up alerting for drift > 0.20

### Monitoring

- [ ] Prometheus metrics (optional)
- [ ] Grafana dashboard (optional)
- [ ] Log aggregation (Loki, ELK)
- [ ] Drift alerts
- [ ] Heartbeat failure alerts
- [ ] Registry status dashboard

### Security

- [ ] Add authentication to worker endpoints
- [ ] Implement TLS/SSL for worker-to-registry communication
- [ ] Restrict /lifecycle/sunset to registry only
- [ ] Validate Caleon signatures on patches
- [ ] Rate limiting on /bubble endpoint
- [ ] Input sanitization on queries


═══════════════════════════════════════════════════════════════════════════════════
## NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════════

1. **Deploy first V5 worker** — Start with one worker, verify all flows
2. **Test cognitive flywheel** — Verify cluster ingestion → fusion → predicates
3. **Scale to 3 workers** — Test cross-worker learning
4. **Implement drift monitoring** — Set up alerts for drift > 0.20
5. **Test death & rebirth** — Manually sunset a worker, deploy successor
6. **Production hardening** — Add auth, TLS, monitoring

═══════════════════════════════════════════════════════════════════════════════════

**Document:** DALS Forge V1.0 Implementation Guide
**Companion:** DALS-FORGE-V1-SPECIFICATION.md
**Worker Template:** worker_templates/unified_specialist_worker_v5.py
**Date:** December 3, 2025

═══════════════════════════════════════════════════════════════════════════════════
