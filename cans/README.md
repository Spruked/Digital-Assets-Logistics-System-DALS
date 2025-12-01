# CANS - Cognitive Autonomous Neural Synchronizer

## 🧠 Overview

**C.A.N.S. = Cognitive Autonomous Neural Synchronizer**

CANS is the autonomic nervous system for the DALS AI architecture, serving as the heartbeat manager and synchronization coordinator for all cognitive modules. It maintains real-time synchronization between UCM and all submodules, detects drift, and ensures stable reasoning cycles.

## 🎯 Core Functions

### 🔷 **1. Heartbeat Emitter**
- Emits JSON heartbeat packets every 1 second
- Signals CANS operational status
- Provides timing synchronization reference

### 🔷 **2. Synchronization Beacon**
- Broadcasts sync pulses to all cognitive modules
- Maintains master cognitive rhythm
- Coordinates reasoning cycle timing

### 🔷 **3. Module Responsiveness Monitor**
- Checks health endpoints of all modules
- Measures response latency
- Detects cognitive drift and failures

### 🔷 **4. Cycle Alignment Supervisor**
- Ensures all modules operate on same cycle numbers
- Detects and corrects synchronization drift
- Maintains logical consistency across modules

### 🔷 **5. Autonomic Recovery Manager**
- Isolates failing modules to prevent cascade failures
- Triggers recovery processes for degraded modules
- Maintains system stability during incidents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UCM (8080)    │◄──►│   CANS (8020)   │◄──►│ Harmonizer      │
│                 │    │                 │    │ (8003)          │
│ • Reasoning     │    │ • Heartbeat     │    │                 │
│ • Logic Packets │    │ • Sync Beacon   │    │ • Verdict Engine│
└─────────────────┘    │ • Monitoring    │    └─────────────────┘
                       │ • Alignment     │
┌─────────────────┐    │ • Recovery      │    ┌─────────────────┐
│   Dashboard     │◄──►│                 │◄──►│   DALS API      │
│   (8008)        │    └─────────────────┘    │   (8003)        │
│                 │                           │                 │
│ • Real-time UI  │                           │ • REST Endpoints│
└─────────────────┘                           └─────────────────┘
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
cd cans
pip install -r requirements.txt
```

2. **Start CANS service:**
```bash
python main.py
```

3. **Verify service is running:**
```bash
curl http://localhost:8020/health
```

### Docker Deployment

1. **Build and run:**
```bash
docker-compose up -d
```

2. **Check logs:**
```bash
docker-compose logs -f cans
```

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /api/cans/heartbeat` - Current heartbeat status
- `GET /api/cans/status` - Comprehensive system status

### Synchronization

- `GET /api/cans/sync/pulse` - Current sync pulse
- `POST /api/cans/sync/acknowledge` - Acknowledge sync pulse
- `GET /api/cans/sync/status` - Sync status for all modules
- `POST /api/cans/sync/align` - Request cycle alignment

### Monitoring

- `GET /api/cans/monitor/status` - Monitoring overview
- `GET /api/cans/monitor/modules` - All monitored modules
- `POST /api/cans/monitor/check/{module}` - Manual health check
- `POST /api/cans/monitor/isolate/{module}` - Isolate module
- `POST /api/cans/monitor/recover/{module}` - Recover module
- `GET /api/cans/monitor/alerts` - Active alerts
- `GET /api/cans/monitor/performance` - Performance metrics

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CANS_HOST` | `0.0.0.0` | Service bind address |
| `CANS_PORT` | `8020` | Service port |
| `CANS_DEBUG` | `false` | Enable debug mode |
| `CANS_HEARTBEAT_INTERVAL` | `1.0` | Heartbeat interval (seconds) |
| `CANS_SYNC_INTERVAL` | `0.5` | Sync beacon interval (seconds) |
| `CANS_MONITOR_INTERVAL` | `2.0` | Monitoring check interval (seconds) |
| `UCM_URL` | `http://localhost:8080` | UCM service URL |
| `HARMONIZER_URL` | `http://localhost:8003` | Harmonizer service URL |

### Monitored Modules

CANS automatically monitors these modules:

- **UCM** (port 8080) - Critical reasoning engine
- **Harmonizer** (port 8003) - Verdict processing
- **DALS API** (port 8003) - Core API service
- **Dashboard** (port 8008) - User interface

## 🔍 Monitoring & Health Checks

### Health Check Response

```json
{
  "status": "healthy",
  "health_score": 95.2,
  "timestamp": 1731153102.291,
  "modules_monitored": 4,
  "sync_cycles": 1283
}
```

### Heartbeat Response

```json
{
  "module": "CANS",
  "timestamp": 1731153102.291,
  "status": "alive",
  "cycle": 1283,
  "system_health": 95.2,
  "modules_monitored": 4,
  "isolated_modules": 0
}
```

## 🛠️ Development

### Project Structure

```
cans/
├── main.py                 # Service entry point
├── core/
│   ├── config.py          # Configuration management
│   └── state.py           # Global state tracking
├── api/
│   ├── heartbeat_router.py # Heartbeat endpoints
│   ├── sync_router.py     # Sync endpoints
│   └── monitor_router.py  # Monitoring endpoints
├── services/
│   ├── heartbeat_emitter.py # Heartbeat service
│   ├── sync_beacon.py     # Sync beacon service
│   ├── module_monitor.py  # Module monitoring
│   └── cycle_aligner.py   # Cycle alignment
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
└── docker-compose.yml    # Docker orchestration
```

### Adding New Modules

1. **Update configuration** in `core/config.py`:
```python
"NEW_MODULE": {
    "url": "http://localhost:9000",
    "health_endpoint": "/health",
    "sync_endpoint": "/api/sync",
    "critical": False,
    "expected_response_time": 1.0
}
```

2. **Restart CANS service** to pick up new module.

### Testing

```bash
# Run unit tests
pytest

# Test API endpoints
pytest test_api.py

# Integration tests
pytest test_integration.py
```

## 🔧 Troubleshooting

### Common Issues

**CANS not starting:**
- Check port 8020 is available
- Verify Python dependencies installed
- Check logs: `docker-compose logs cans`

**Modules not responding:**
- Verify module URLs are correct
- Check network connectivity
- Review module health endpoints

**High drift detected:**
- Check system clock synchronization
- Verify module processing capacity
- Review network latency

**Heartbeat failures:**
- Check UCM service is running on port 8080
- Verify CANS can reach UCM health endpoint
- Review firewall/network configuration

### Logs

CANS logs are structured JSON. Key log levels:

- `INFO`: Normal operations, heartbeats, sync pulses
- `WARNING`: High latency, moderate drift
- `ERROR`: Module failures, isolation events
- `CRITICAL`: System-wide issues, cascade failures

### Debug Mode

Enable debug logging:
```bash
export CANS_DEBUG=true
python main.py
```

## 📊 Metrics & Monitoring

CANS exposes Prometheus metrics on `/metrics` (when enabled):

- `cans_heartbeats_total` - Total heartbeats emitted
- `cans_sync_pulses_total` - Total sync pulses broadcast
- `cans_modules_monitored` - Number of monitored modules
- `cans_drift_level` - Current synchronization drift
- `cans_health_score` - Overall system health score

## 🤝 Integration

### UCM Integration

UCM pings CANS heartbeat endpoint:
```python
response = requests.get("http://localhost:8020/api/cans/heartbeat")
if response.status_code != 200:
    # CANS is down - isolate reasoning
    isolate_cans()
```

### Harmonizer Integration

Harmonizer receives sync pulses:
```python
# Harmonizer acknowledges sync
ack = requests.post("http://localhost:8020/api/cans/sync/acknowledge",
                   json={"module_name": "Harmonizer", "cycle_number": current_cycle})
```

## 📝 API Reference

### Heartbeat API

#### `GET /api/cans/heartbeat`
Returns current CANS heartbeat status.

**Response:**
```json
{
  "module": "CANS",
  "timestamp": 1731153102.291,
  "status": "alive",
  "cycle": 1283,
  "system_health": 95.2,
  "modules_monitored": 4,
  "isolated_modules": 0
}
```

#### `GET /api/cans/status`
Returns comprehensive system status.

#### `GET /api/cans/modules/{module_name}/status`
Returns status for specific module.

### Sync API

#### `GET /api/cans/sync/pulse`
Returns current synchronization pulse.

#### `POST /api/cans/sync/acknowledge`
Acknowledges receipt of sync pulse.

**Request:**
```json
{
  "module_name": "UCM",
  "cycle_number": 1283,
  "timestamp": 1731153102.291
}
```

### Monitor API

#### `GET /api/cans/monitor/status`
Returns monitoring overview.

#### `GET /api/cans/monitor/alerts`
Returns active monitoring alerts.

#### `POST /api/cans/monitor/isolate/{module_name}`
Manually isolates a module.

## 🔒 Security

CANS implements several security measures:

- **Service isolation**: Runs in separate container/network
- **Health validation**: Only accepts valid health responses
- **Autonomic isolation**: Automatically isolates compromised modules
- **Rate limiting**: Prevents abuse of monitoring endpoints
- **Audit logging**: All autonomic actions are logged

## 🤖 Autonomic Actions

CANS can take these autonomic actions:

1. **Module Isolation**: Quarantines failing modules
2. **Recovery Initiation**: Triggers module restart procedures
3. **Load Balancing**: Redirects traffic from degraded modules
4. **Alert Escalation**: Notifies administrators of critical issues
5. **Fallback Activation**: Enables backup systems when needed

## 📈 Performance

### Benchmarks

- **Heartbeat emission**: < 10ms
- **Sync pulse broadcast**: < 50ms to 4 modules
- **Health checks**: < 100ms per module
- **Cycle alignment**: < 25ms
- **Memory usage**: ~50MB
- **CPU usage**: < 5% on modern hardware

### Scaling

CANS is designed to monitor 10-50 modules efficiently. For larger deployments:

- Increase `monitor_interval` for less frequent checks
- Use async health checks for better concurrency
- Implement module sharding for distributed monitoring

## 🐛 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Standards

- Use type hints for all function parameters
- Include docstrings for all public functions
- Follow async/await patterns for I/O operations
- Use structured logging with correlation IDs
- Maintain DALS-001 compliance for status endpoints

## 📜 License

This project is part of the DALS (Digital Asset Logistics System) architecture.

## 🆘 Support

For issues or questions:

1. Check the logs: `docker-compose logs cans`
2. Verify service health: `curl http://localhost:8020/health`
3. Review configuration settings
4. Check network connectivity to monitored modules

---

**CANS: The Pulse of AI Consciousness** 🧠💓