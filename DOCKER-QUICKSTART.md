# DALS Minimal Stack - Quick Start Guide

## ✅ What's Running (After Build Completes)

This Docker stack includes:

1. **Redis** (port 6379)
   - Caching and session storage
   - Module status tracking

2. **UCM Service** (port 8081)
   - Caleon's cognitive brain
   - Voice reasoning and processing
   - Thought processing engine

3. **DALS Controller** (port 8003, 8008)
   - Main API: http://localhost:8003
   - Dashboard: http://localhost:8008
   - Voice communication endpoints
   - **Cali_X_One Host Bubble** - Sovereign AI supervisor

4. **Consul** (port 8500)
   - Service discovery
   - Health monitoring dashboard

---

## 🎯 Quick Access URLs

- **DALS Dashboard**: http://localhost:8008
  - Voice & I/O tab for speaking to Caleon
  - **Host Bubble**: Floating blue orb (bottom-right) for Cali_X_One

- **DALS API Docs**: http://localhost:8003/docs
  - Interactive API documentation

- **UCM Health**: http://localhost:8081/health
  - Caleon cognitive brain status

- **Consul UI**: http://localhost:8500
  - Service discovery dashboard

---

## 🎤 Cali_X_One Host Bubble - Sovereign AI Supervisor

**Instant Access to System Orchestration:**

1. **Look for the Blue Orb** in bottom-right corner of any page
2. **Say "Cali"** to activate voice interface
3. **Or Click the Orb** to open control panel
4. **Ask Questions** about system status, workers, or request assistance
5. **Get Real-time Help** with system orchestration and monitoring

**Cali_X_One Capabilities:**
- System health monitoring and alerts
- Worker status and performance tracking
- Voice-activated assistance and commands
- Real-time system orchestration
- Sovereign AI decision support

---

## 🎤 Voice Communication Setup

1. **Open Dashboard**: http://localhost:8008
2. **Click "Voice & I/O" Tab** (9th tab)
3. **Grant Microphone Permission** (browser will ask)
4. **Click Green Microphone Button** to start recording
5. **Speak to Caleon**
6. **Click Again to Stop** - she'll process and respond

### Voice Pipeline Status Check

Visit: http://localhost:8003/api/cochlear/status

Should return:
```json
{
  "status": "active",
  "ucm_connected": true,
  "sessions_active": 0
}
```

---

## 🐳 Docker Commands

### Start Services
```bash
docker-compose -f docker-compose.minimal.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.minimal.yml down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.minimal.yml logs -f

# Specific service
docker-compose -f docker-compose.minimal.yml logs -f dals-controller
docker-compose -f docker-compose.minimal.yml logs -f ucm-service
```

### Rebuild After Code Changes
```bash
docker-compose -f docker-compose.minimal.yml up -d --build
```

### Check Service Status
```bash
docker-compose -f docker-compose.minimal.yml ps
```

---

## 🔍 Health Checks

All services have health checks. Check status:

```powershell
# DALS API
Invoke-WebRequest http://localhost:8003/health

# UCM Brain
Invoke-WebRequest http://localhost:8081/health

# Redis
docker exec -it dals-redis redis-cli PING
```

---

## 🐛 Troubleshooting

### Voice Communication Not Working?

1. **Check UCM is running**:
   ```bash
   docker-compose -f docker-compose.minimal.yml ps ucm-service
   ```

2. **Check UCM health**:
   ```powershell
   Invoke-WebRequest http://localhost:8081/health
   ```

3. **Check DALS logs**:
   ```bash
   docker-compose -f docker-compose.minimal.yml logs dals-controller | Select-String "UCM"
   ```

### Port Conflicts?

If ports 8003, 8008, 8081, 6379, or 8500 are in use:

1. Stop conflicting services
2. Or modify `docker-compose.minimal.yml` port mappings

### Services Won't Start?

```bash
# Check what's wrong
docker-compose -f docker-compose.minimal.yml logs

# Reset everything
docker-compose -f docker-compose.minimal.yml down -v
docker-compose -f docker-compose.minimal.yml up -d --build
```

---

## 📊 What's DALS-001 Compliant?

All status endpoints return:
- **Real data** when services are active
- **Zero/null** when services are inactive
- **Never** mock or fake metrics

Examples:
- `/api/cochlear/status` - Real session count or 0
- `/api/phonatory/status` - Real synthesis count or 0  
- `/api/caleon/ucm/status` - Real UCM connection or null

---

## 🚀 Next Steps

1. **Wait for build to complete** (watch terminal)
2. **Open dashboard**: http://localhost:8008
3. **Test voice**: Click Voice & I/O tab
4. **Speak to Caleon**: Click microphone button

---

## 📝 Notes

- **UCM Port**: Changed from 8080 → 8081 to match config
- **No NFT Services**: Minting services excluded (missing dependencies)
- **Data Persistence**: Redis data persists in Docker volume
- **Logs**: Available in `./logs/` and via Docker logs
