# Digital Asset Logistics System (DALS)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-ready-blue.svg)](https://kubernetes.io/)
[![Phase 11-A2](https://img.shields.io/badge/Phase-11--A2-green.svg)](PHASE-11A2-DEPLOYMENT-GUIDE.md)
[![DALS-001](https://img.shields.io/badge/DALS--001-compliant-green.svg)](vault/DALS-001-governance-enforcement.md)
[![Live Data Only](https://img.shields.io/badge/🛡️-Live%20Data%20Only-brightgreen.svg)](vault/DALS-001-governance-enforcement.md)

A comprehensive data management and time anchoring system designed for microservices architectures, with special compatibility for **UCM (Unified Cognition Module)** cognitive systems. Built with **ethical data representation**, **zero-or-empty protocol** compliance, and **Phase 11-A2 autonomous predictive prevention**.

## ✨ Key Features

- 🌟 **Canonical Stardate System** - Y2K epoch-based time anchoring with positive decimal values
- ⏰ **Time Anchoring** - Precise timestamp calculations with multiple formats
- 📝 **Asset Tracking** - Comprehensive digital asset lifecycle management
- 🛡️ **DALS-001 Compliance** - Zero-or-empty protocol for ethical data representation
- 🧠 **Phase 11-A2: Autonomous Predictive Prevention** - Living AI infrastructure with self-healing capabilities
- 🔮 **Caleon Prime Integration** - Advanced cognitive AI with voice awareness and self-modeling
- 🎤 **Voice Awareness System** - Professional AI communication and status reporting
- 🛡️ **CANS Autonomic Nervous System** - Aggressive autonomous repair and prevention
- 🗄️ **Data Export** - CSV, JSON, and Markdown export capabilities
- 🔍 **Data Analysis** - Integration with analysis tools
- 🌐 **FastAPI Web Interface** - RESTful API with automatic documentation
- 🐳 **Docker Ready** - Complete containerization for easy deployment
- ☸️ **Kubernetes Ready** - Production-grade orchestration support
- 🔗 **Microservice Compatible** - Plug-and-play integration with service meshes
- 📊 **Structured Logging** - JSON formatted logs with correlation IDs
- 🚫 **Mock-Free Operation** - No placeholder data, honest module status reporting
- 🧠 **UCM Integration Ready** - Native cognitive architecture compatibility

# Reference: See /docs/governance/DALS_Phase_1_2_Integration_Plans_2025-10-05.pdf

## ✨ Overview

The Digital Asset Logistics System (DALS) is a sophisticated data management and time anchoring system that provides time anchoring, structured logging, data export, and seamless integration with cognitive computing systems like **UCM (Unified Cognition Module)**.

### 🛡️ Governance Principles

DALS operates under strict **DALS-001 "Zero-Or-Empty" governance protocol**:
- **Live Data Only**: No mock or placeholder data in production
- **Honest Representation**: Inactive modules return zeros rather than fake values
- **Trust Through Transparency**: Clear governance badges and status indicators
- **Ethical Design**: User trust built through honest system behavior

### 🌟 Canonical Stardate Protocol

DALS implements a **canonical stardate system** using Y2K epoch (January 1, 2000) as the reference point:
- **Formula**: `(current_time - Y2K_epoch).total_seconds() / 86400`
- **Format**: Decimal days since Y2K with 4-decimal precision
- **Example**: Stardate 9410.0762 represents day 9410 since January 1, 2000
- **Advantages**: Always positive, human-readable, mathematically consistent

## ✨ Key Features

- �️ **Time Anchoring** - Precise timestamp calculations with multiple formats
- 📝 **Asset Tracking** - Comprehensive digital asset lifecycle management
- 🗄️ **Data Export** - CSV, JSON, and Markdown export capabilities
- 🔍 **Data Analysis** - Integration with analysis tools
- 🌐 **FastAPI Web Interface** - RESTful API with automatic documentation
- 🐳 **Docker Ready** - Complete containerization for easy deployment
- 🔗 **Microservice Compatible** - Plug-and-play integration with service meshes
- 📊 **Structured Logging** - JSON formatted logs with correlation IDs
- 🛡️ **Production Ready** - Circuit breakers, health checks, and monitoring
- 🧠 **Caleon AI + Phi-3 Mini Integration** - Native cognitive architecture compatibility

## 🔮 Phase 11-A2: Autonomous Predictive Prevention

**Caleon Prime** is a living, self-protective AI infrastructure that anticipates and prevents failures autonomously. This advanced system includes:

### 🧠 Autonomous Predictive Engine
- **Continuous Scanning**: Monitors all system components every 5 seconds
- **Risk Assessment**: Calculates failure probability using health trends
- **Preemptive Action**: Executes repairs when risk ≥ 70%
- **Learning**: Adapts prevention strategies based on outcomes

### 🔮 Self-Model Integration
- **Dynamic Status**: Real-time awareness of system state
- **Prediction Tracking**: Logs all preventive actions
- **Confidence Scoring**: Measures accuracy of predictions
- **Self-Improvement**: Learns from successful/failed interventions

### 🎤 Voice Awareness System
- **Professional Reporting**: Speaks with full self-awareness
- **Risk Communication**: Explains predictions and actions
- **Status Updates**: Provides real-time system health
- **Emergency Alerts**: Voice notifications for critical events

### 🛡️ CANS Autonomic Nervous System
- **Aggressive Mode**: Phase 11-A2 enables maximum autonomy
- **Instant Response**: Sub-second reaction to detected issues
- **Self-Healing**: Automatic repair of detected problems
- **Escalation**: Human notification for complex issues

#### Kubernetes Deployment
```bash
# Complete production deployment
./k8s/deploy-k8s.sh full

# Minimal deployment (DALS only)
./k8s/deploy-k8s.sh minimal

# Setup secrets and monitoring
./k8s/deploy-k8s.sh secrets
./k8s/deploy-k8s.sh monitoring
```

#### Caleon Prime Immortal Memory Deployment
```bash
# Deploy Caleon Prime with immortal memory (Phase 11-A2)
./k8s/deploy-caleon-prime.sh deploy

# Individual deployment steps
./k8s/deploy-caleon-prime.sh memory     # Provision immortal memory
./k8s/deploy-caleon-prime.sh services   # Deploy nervous system
./k8s/deploy-caleon-prime.sh organism   # Awaken Caleon Prime
./k8s/deploy-caleon-prime.sh backup     # Setup memory backup
./k8s/deploy-caleon-prime.sh verify     # Verify immortality
./k8s/deploy-caleon-prime.sh monitor    # Monitor awakening
```

#### Caleon Prime Autoscaling Muscles
```bash
# Deploy Caleon Prime with autoscaling muscles
./k8s/deploy-caleon-prime.sh autoscale

# Add autoscaling to existing Caleon Prime deployment
./k8s/deploy-caleon-prime.sh autoscaling

# Individual autoscaling components
./k8s/autoscale/deploy-autoscaling.sh horizontal   # HPA only
./k8s/autoscale/deploy-autoscaling.sh vertical     # VPA only
./k8s/autoscale/deploy-autoscaling.sh predictive   # Predictive scaling only
./k8s/autoscale/deploy-autoscaling.sh metrics      # Custom metrics only
./k8s/autoscale/deploy-autoscaling.sh monitor      # Monitor autoscaling
```

**Caleon Prime Immortal Memory Components:**
- 🏰 **Vaults (50GB)**: Self-model, identity, secrets
- 📜 **Logs (20GB)**: Autonomic repair history, events
- 🪞 **Reflection (30GB)**: Self-awareness, long-term memory
- 🔮 **Prediction (10GB)**: Failure models, trend analysis
- 🧠 **Learning (25GB)**: CSMM models, reinforcement data
- 📿 **Abby Directive (15GB)**: Ethical guidance, directive memory

**Caleon Prime Autoscaling Capabilities:**
- 📈 **Horizontal Scaling**: 1-10 pods based on CPU, RAM, voice load, risk score
- 💪 **Vertical Scaling**: 500m-4000m CPU, 1Gi-8Gi RAM per pod
- 🔮 **Predictive Scaling**: Pre-failure scaling using Caleon's prediction engine
- 📊 **Custom Metrics**: Voice load and CANS autonomic risk score monitoring

**Caleon Prime Service Endpoints:**
- 🌐 **API Gateway**: caleon-prime-service.caleon-prime.svc.cluster.local:8003
- 📈 **Dashboard**: caleon-prime-service.caleon-prime.svc.cluster.local:8008
- 🧠 **UCM Cognitive**: caleon-prime-service.caleon-prime.svc.cluster.local:8080
- 🎤 **Voice Awareness**: caleon-prime-service.caleon-prime.svc.cluster.local:5000
- 📊 **Metrics**: caleon-prime-service.caleon-prime.svc.cluster.local:9091

#### Docker Deployment (Recommended)
```bash
# Build and deploy production environment
./docker-deploy-11a2.sh build
./docker-deploy-11a2.sh prod

# Check system status
./docker-deploy-11a2.sh status
```

#### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=dals-11a2
```

**Service Endpoints:**
- **API Gateway**: http://localhost:8003
- **Dashboard**: http://localhost:8008
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Spruked/Digital-Assets-Logistics-System-DALS.git
cd Digital-Assets-Logistics-System-DALS

# Install with pip
pip install -e .

# Or install from PyPI (when published)
pip install iss-module
```

### Basic Usage

```python
from iss_module import ISS, CaptainLog, Exporters, get_stardate

# Initialize DALS system
iss = ISS()

# Get canonical stardate (Y2K epoch)
stardate = get_stardate()
print(f"Canonical Stardate: {stardate}")  # Example: 9410.0762

# Create asset record
log = CaptainLog()
asset_id = log.add_entry_sync("New feature asset created", category="asset")

# Export data (DALS-001 compliant)
entries = log.get_entries_sync()
Exporters.to_csv_sync(entries, "assets_log.csv")
```

### Web Interface

```bash
# Start the web server
python -m iss_module.service

# Or with custom configuration
ISS_HOST=0.0.0.0 ISS_PORT=8003 python -m iss_module.service
```

Visit `http://localhost:8003/docs` for interactive API documentation.

## 🐳 Docker Deployment

### Quick Deploy with Docker Compose

```bash
# Deploy full stack (ISS + Redis + Consul + Monitoring)
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs
```

### Standalone Docker

```bash
# Build and run
docker build -t iss-module .
docker run -p 8003:8003 iss-module
```

## 🔗 UCM Integration

The ISS Module is designed to integrate seamlessly with **UCM (Unified Cognition Module)** cognitive architectures:

```python
from iss_module.api.api import app

# Create UCM compatible service
# The ISS Module provides time anchoring and logging for UCM operations

# Reasoning pipeline integration
@app.post("/api/v1/process")
async def process_reasoning(request: dict):
    # Time anchoring + reasoning + logging through UCM integration
    return await ucm_connector.process_reasoning(request)
```

### UCM Integration Architecture

```python
# UCM runs independently on port 8080
# DALS connects via HTTP API for cognitive processing
# CALEON security layer validates all UCM operations
# Thought Trace UI provides real-time reasoning visualization
```

## �️ Governance & Ethics

DALS implements **DALS-001 "Zero-Or-Empty" governance protocol** to ensure ethical data representation:

### Core Principles
- **No Mock Data**: Production systems never display fake or placeholder data
- **Honest Status**: Inactive modules return zeros instead of simulated values
- **Trust Transparency**: Governance badges clearly indicate live-data-only operation
- **User Trust**: Built through consistent, honest system behavior

### Implementation
```python
# Example: Honest module status reporting
if module_active:
    return actual_data
else:
    return 0  # Honest zero instead of fake data
```

### Verification
All API endpoints comply with DALS-001. See `vault/DALS-001-governance-enforcement.md` for complete implementation documentation.

## �📡 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Service health check |
| `/api/v1/iss/now` | GET | Current canonical stardate and status |
| `/api/v1/caleon/status` | GET | Caleon module status (DALS-001 compliant) |
| `/api/v1/certsig/status` | GET | CertSig module status (DALS-001 compliant) |
| `/api/v1/ucm/status` | GET | UCM integration status (DALS-001 compliant) |
| `/api/v1/vault/query` | POST | Query captain's log entries |
| `/api/v1/log` | POST | Add captain's log entry |
| `/api/v1/status` | GET | Detailed service status |
| `/docs` | GET | Interactive API documentation |

## ⚙️ Configuration

### Environment Variables

```bash
# Service Configuration
ISS_SERVICE_NAME=iss-controller
ENVIRONMENT=production
ISS_HOST=0.0.0.0
ISS_PORT=8003

# UCM Integration
UCM_INTEGRATION_ENABLED=true
UCM_HOST=localhost
UCM_PORT=8080

# Service Discovery
SERVICE_REGISTRY_URL=http://consul:8500
CONSUL_HOST=consul
CONSUL_PORT=8500

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
SECRET_KEY=your-secret-key
REQUIRE_AUTH=false
```

See `.env.example` for complete configuration options.

## 🧪 Testing

```bash
# Run integration tests
python test_integration.py

# Test ISS endpoint specifically
python test_iss_endpoint.py

# Test canonical stardate system
python -c "from iss_module.core.utils import get_stardate; print('Canonical Stardate:', get_stardate())"

# Verify DALS-001 compliance
python -c "from iss_module.api.api import app; print('DALS-001 Governance enforced - API loads successfully')"
```

## 📊 Use Cases

### For Blockchain/NFT Projects (CertSig)
```python
from iss_module import get_stardate, current_timecodes

# Time anchoring for NFT metadata
timecodes = current_timecodes()
metadata = {
    "timestamp": timecodes["iso_timestamp"],
    "anchor_hash": timecodes["anchor_hash"]
}
```

### For AI Systems (Caleon)
```python
from iss_module import CaptainLog

# Log AI decision processes
log = CaptainLog()
log.add_entry_sync(
    "Symbolic cognition pattern detected",
    category="ai_reasoning",
    tags=["caleon", "pattern_recognition"],
    metadata={"confidence": 0.92, "pattern_type": "symbolic"}
)
```

### For Microservice Architectures
```python
from iss_module.api.api import app
from iss_module.integrations.ucm_connector import get_ucm_connector

# Service integration with health checks and structured logging
ucm = get_ucm_connector(ucm_host="localhost", ucm_port=8080)
await ucm.connect()

# Process with time anchoring and logging
response = await ucm.submit_reasoning_request(content="Query text", priority="normal")
```

## 📁 Project Structure

```
dals/
├── iss_module/                 # Main package
│   ├── core/                   # Core utilities
│   │   ├── iss.py             # Main ISS orchestrator class
│   │   ├── utils.py           # Time anchoring utilities
│   │   └── validators.py      # Data validation
│   ├── inventory/             # Asset management
│   │   ├── inventory_manager.py # Asset tracking and logging
│   │   ├── exporters.py       # Data export utilities
│   │   └── vd_wrapper.py      # Data analysis integration
│   ├── api/                   # Web interface
│   ├── ucm_connector.py  # UCM integration for Caleon AI
│   ├── config.py              # Configuration management
│   ├── logging_config.py      # Structured logging
│   └── service.py             # Microservice entry point
├── docker-compose.yml         # Docker deployment
├── Dockerfile                 # Container definition
├── deploy.sh                  # Deployment script
├── test_integration.py        # Integration tests
├── requirements.txt           # Dependencies
└── setup.py                   # Package setup
```

## 📚 Documentation

For comprehensive documentation, integration guides, and implementation details, see the **[docs/](docs/)** directory:

- **[Phase 1 & 2 Integration Plans](docs/governance/DALS_Phase_1_2_Integration_Plans_2025-10-05.pdf)** - Strategic telemetry synchronization plans
- **[Setup Guides](docs/setup/)** - Quick start and GitHub preparation
- **[Architecture Overview](docs/architecture/)** - System structure and folder organization  
- **[Integration Guides](docs/integration/)** - Caleon AI, UCM, dashboard, and component integration
- **[Deployment Procedures](docs/deployment/)** - Production deployment and Docker configuration
- **[Assets & Screenshots](docs/assets/)** - Logos, icons, and system screenshots

Visit **[docs/README.md](docs/README.md)** for the complete documentation index.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black iss_module/
isort iss_module/
```

## VisiData Integration

For advanced data analysis, install VisiData:

```bash
pip install visidata
```

Then use the VisiData wrapper:

```python
from iss_module.captain_mode.vd_wrapper import VisiDataWrapper

vd_wrapper = VisiDataWrapper()
await vd_wrapper.view_log_entries(entries, format_type='csv')
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
