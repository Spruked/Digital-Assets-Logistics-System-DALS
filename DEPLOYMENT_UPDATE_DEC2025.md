"""
DALS Production Deployment Guide - Updated December 2025
========================================================

This guide covers deployment of DALS with the new Worker Fleet system.
"""

# ═══════════════════════════════════════════════════════════════
#  QUICK START
# ═══════════════════════════════════════════════════════════════

## 1. Build and Start All Services

```bash
# Build images
docker-compose build

# Start all services (DALS + Workers + NFT Minting)
docker-compose up -d

# Check status
docker-compose ps
```

## 2. Verify Deployment

```bash
# Check DALS API
curl http://localhost:8003/health

# Check Worker Registry
curl http://localhost:8003/api/workers/status

# Check Caleon Fusion Engine
curl http://localhost:8003/api/caleon/health

# Check Josephine Worker
docker logs josephine-default
```

## 3. Access Services

- **DALS API**: http://localhost:8003
- **Dashboard**: http://localhost:8008
- **Worker Registry**: http://localhost:8003/api/workers/list
- **Caleon Fusion**: http://localhost:8003/api/caleon/stats
- **Josephine Worker**: Container internal (port 8080)

# ═══════════════════════════════════════════════════════════════
#  WORKER DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

## Deploy Additional Workers

```bash
# Josephine for specific user
docker run -d \
  -e WORKER_NAME=Josephine \
  -e TARGET_USER_ID=user_123 \
  -e CALI_X_ONE_API=http://dals-controller:8003 \
  -e TRUEMARK_API=http://localhost:8003/api/truemark \
  --name josephine-user123 \
  --network dals-phase1-network \
  host-bubble-worker:v1.0.0

# Check registration
curl http://localhost:8003/api/workers/list | jq '.[] | select(.worker_name=="Josephine")'
```

## Worker Environment Variables

```bash
WORKER_NAME=Josephine           # Worker identity
TARGET_USER_ID=user_123         # User assignment
WORKER_PORT=8080                # Internal port
CALI_X_ONE_API=http://...:8003  # DALS API endpoint
TRUEMARK_API=http://...:8003    # TrueMark endpoint
UQV_API=http://...:8003/api/uqv # UQV endpoint
TTS_ENDPOINT=http://.../tts     # Voice synthesis
CHAT_ENDPOINT=http://.../chat   # Chat interface
```

# ═══════════════════════════════════════════════════════════════
#  TESTING THE COGNITIVE FLYWHEEL
# ═══════════════════════════════════════════════════════════════

## 1. Test Fusion Engine

```bash
# Run test suite
python test_caleon_fusion.py

# Manual fusion trigger
curl -X POST http://localhost:8003/api/caleon/force_fusion

# Check invented predicates
curl http://localhost:8003/api/caleon/predicates | jq
```

## 2. Monitor Workers

```bash
# List all workers
curl http://localhost:8003/api/workers/list | jq

# Get worker details
curl http://localhost:8003/api/workers/Josephine | jq

# Check fusion stats
curl http://localhost:8003/api/caleon/stats | jq
```

# ═══════════════════════════════════════════════════════════════
#  PRODUCTION CONFIGURATION
# ═══════════════════════════════════════════════════════════════

## Environment Variables (docker-compose.yml)

```yaml
environment:
  # Worker Registry & Cognitive Flywheel
  - WORKER_REGISTRY_ENABLED=true
  - CALEON_FUSION_ENABLED=true
  - PREDICATE_BROADCASTING=true
  - MICRO_SKG_ENABLED=true
  - UQV_ENABLED=true
  - FUSION_THRESHOLD=0.65
  - INVENTION_THRESHOLD=0.75
```

## Volume Mounts

```yaml
volumes:
  - ./vault:/app/vault              # Persistent storage
  - ./logs:/app/logs                # Log files
  - ./worker_templates:/app/workers # Worker code
```

# ═══════════════════════════════════════════════════════════════
#  MONITORING & LOGS
# ═══════════════════════════════════════════════════════════════

## View Logs

```bash
# DALS Controller
docker logs -f dals-controller

# Josephine Worker
docker logs -f josephine-default

# All services
docker-compose logs -f
```

## Health Checks

```bash
# All services
docker-compose ps

# Individual health
curl http://localhost:8003/health
curl http://localhost:8003/api/caleon/health
curl http://localhost:8003/api/workers/status
```

# ═══════════════════════════════════════════════════════════════
#  TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════

## Worker Won't Register

```bash
# Check network connectivity
docker exec josephine-default curl http://dals-controller:8003/health

# Check worker logs
docker logs josephine-default

# Manually register
curl -X POST http://localhost:8003/api/workers/register \
  -H "Content-Type: application/json" \
  -d '{
    "worker_name": "Josephine",
    "worker_type": "truemark",
    "api_url": "http://josephine:8080",
    "user_id": "user_123"
  }'
```

## Fusion Engine Not Working

```bash
# Check Caleon health
curl http://localhost:8003/api/caleon/health

# Check fusion stats
curl http://localhost:8003/api/caleon/stats

# Force fusion manually
curl -X POST http://localhost:8003/api/caleon/force_fusion
```

## Reset Everything

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

# ═══════════════════════════════════════════════════════════════
#  SCALING WORKERS
# ═══════════════════════════════════════════════════════════════

## Horizontal Scaling

```bash
# Deploy 5 Josephine instances
for i in {1..5}; do
  docker run -d \
    -e WORKER_NAME=Josephine-$i \
    -e TARGET_USER_ID=user_$i \
    -e CALI_X_ONE_API=http://dals-controller:8003 \
    --name josephine-user-$i \
    --network dals-phase1-network \
    host-bubble-worker:v1.0.0
done

# Verify all registered
curl http://localhost:8003/api/workers/list | jq 'length'
```

# ═══════════════════════════════════════════════════════════════
#  PRODUCTION CHECKLIST
# ═══════════════════════════════════════════════════════════════

- [ ] Docker images built
- [ ] All services started
- [ ] DALS API responding (port 8003)
- [ ] Dashboard accessible (port 8008)
- [ ] Worker Registry operational
- [ ] Caleon Fusion Engine active
- [ ] Josephine worker registered
- [ ] Fusion test passing
- [ ] Logs being collected
- [ ] Volumes persisting data
- [ ] Health checks passing
- [ ] Secrets configured
- [ ] Monitoring active
