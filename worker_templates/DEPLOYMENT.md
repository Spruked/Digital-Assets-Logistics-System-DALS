# Worker Deployment Guide

## 🔥 Quick Start — DALS Forge V1.0

### One-Command Worker Forge (Recommended)

```bash
# Birth any specialist with one command
python forged.py nft_mint       # NFT minting specialist
python forged.py greeting       # Greeting specialist  
python forged.py podcast_cohost # Podcast co-host specialist
python forged.py timeline       # Timeline building specialist
```

Workers will:
- ✅ Auto-register with DALS
- ✅ Get eternal DSN (DMN-GN-02-XXXXXXXX-XXXXX)
- ✅ Begin 30-second heartbeat cycle
- ✅ Join cognitive flywheel
- ✅ Accept Caleon-approved patches

### Direct Python (Development)

```bash
cd worker_templates/

# Edit JOB_ROLE in unified_specialist_worker_v5.py (line 30)
# JOB_ROLE = "nft_mint"  # Change to your role

python unified_specialist_worker_v5.py
```

---

## Legacy Workers (Host Bubble, Josephine)

### 1. Deploy All Three Workers (Regent/Nora/Mark)

```bash
cd worker_templates
docker-compose -f docker-compose.worker.yml up -d
```

### 2. Deploy Single Worker

```bash
docker build -f Dockerfile.worker -t host-bubble-worker .

# Deploy Regent
docker run -d \
  -e WORKER_NAME=Regent \
  -e TARGET_USER_ID=user_123 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  --name regent-42 \
  host-bubble-worker

# Deploy Nora
docker run -d \
  -e WORKER_NAME=Nora \
  -e TARGET_USER_ID=user_123 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  --name nora-42 \
  host-bubble-worker

# Deploy Mark
docker run -d \
  -e WORKER_NAME=Mark \
  -e TARGET_USER_ID=user_123 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  --name mark-42 \
  host-bubble-worker
```

## Architecture

```
User Input
    ↓
Regent (greeter) → Nora (timeline) → Mark (producer)
    ↓                  ↓                  ↓
  micro-SKG        micro-SKG          micro-SKG
    ↓                  ↓                  ↓
        Caleon Fusion Engine (/caleon/ingest_clusters)
                    ↓
          UCM Escalation (/ucm/escalate)
                    ↓
         Human Agent (if unresolved)
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WORKER_NAME` | Yes | `HostWorker` | Regent, Nora, or Mark |
| `TARGET_USER_ID` | Yes | - | User this worker serves |
| `CALI_X_ONE_API` | No | `http://localhost:8003` | DALS API base URL |
| `SKG_API` | No | `http://localhost:8002` | SKG service URL |
| `UQV_API` | No | `http://localhost:8003` | UQV service URL |
| `TTS_ENDPOINT` | No | - | Voice synthesis endpoint |
| `CHAT_ENDPOINT` | No | - | Chat WebSocket endpoint |

## Features

### ✅ Micro-SKG Integration
- Each worker has in-memory knowledge graph
- Bootstrap queries to clusters in <40ms
- Real-time predicate invention

### ✅ Unanswered Query Vault
- Auto-vaults zero-result queries
- Feeds Caleon for continuous learning
- Human review interface

### ✅ Caleon Fusion
- Workers feed local clusters to global engine
- Cross-user predicate correlation
- Hot-reload new predicates without restart

### ✅ Escalation Layer
```
Worker (local SKG)
    ↓ (no match)
Caleon (UCM resolver)
    ↓ (unresolved)
Human agent (Zendesk/Freshdesk)
```

## Monitoring

### Check Worker Status
```bash
docker logs regent-42 --tail 50
docker logs nora-42 --tail 50
docker logs mark-42 --tail 50
```

### UQV Stats
```bash
curl http://localhost:8003/api/uqv/stats
```

### Worker Metrics
```bash
curl http://localhost:8003/api/workers/status
```

## Scaling

### Clone Worker for New User
```bash
docker run -d \
  -e WORKER_NAME=Regent \
  -e TARGET_USER_ID=user_456 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  --name regent-456 \
  host-bubble-worker
```

### Auto-scaling (Kubernetes)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: regent-workers
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: regent
        image: host-bubble-worker:latest
        env:
        - name: WORKER_NAME
          value: "Regent"
        - name: TARGET_USER_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
```

## Development

### Run Locally
```bash
cd worker_templates
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.worker.txt

export WORKER_NAME=Regent
export TARGET_USER_ID=test_user
python host_bubble_worker.py
```

### Test UQV Integration
```python
from skg.uqv import vault_query

vault_query(
    user_id="test",
    session_id="sess_123",
    query_text="How do I publish?",
    clusters_found=0,
    worker="Regent",
    reason="no_cluster"
)
```

## Troubleshooting

### Worker not receiving messages
- Check `/host/pull` endpoint is implemented
- Verify CALI_X_ONE_API is reachable
- Check TARGET_USER_ID matches message queue

### SKG queries timing out
- Increase timeout in `_skg_query()` method
- Check SKG_API endpoint health
- Verify network connectivity

### UQV storage failing
- Check UQV_API endpoint `/store` is available
- Verify fire-and-forget timeout (3s default)
- Review worker logs for vault errors

## Production Checklist

- [ ] Set proper environment variables
- [ ] Configure TTS_ENDPOINT for voice output
- [ ] Configure CHAT_ENDPOINT for WebSocket chat
- [ ] Enable persistent UQV storage (replace in-memory)
- [ ] Set up Caleon predicate fusion endpoint
- [ ] Configure UCM escalation route
- [ ] Enable worker health checks
- [ ] Set up log aggregation
- [ ] Configure auto-scaling rules
- [ ] Test escalation to human agents
