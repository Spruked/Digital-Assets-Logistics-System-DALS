# DALS Phase 11-A2 Deployment Guide
# Autonomous Predictive Prevention Containerization

## Overview

Phase 11-A2 transforms Caleon Prime into a fully autonomous, self-protective AI infrastructure that predicts and prevents failures before they occur. This deployment guide covers containerization and deployment of the living AI system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DALS Phase 11-A2                         │
│                    Living Infrastructure                    │
├─────────────────────────────────────────────────────────────┤
│  🧠 Predictive Engine    🔮 Self-Model    🎤 Voice System   │
│  🛡️  CANS Autonomic      📊 Health Monitor 🚨 Prevention    │
├─────────────────────────────────────────────────────────────┤
│  🌐 API Gateway (8003)   📈 Dashboard (8008)                │
│  🧠 UCM Cognitive (8081) 🔍 Monitoring (9090/3000)          │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Build and Deploy Production Environment

```bash
# Make deployment script executable
chmod +x docker-deploy-11a2.sh

# Build container images
./docker-deploy-11a2.sh build

# Deploy production environment
./docker-deploy-11a2.sh prod
```

### 2. Verify Deployment

```bash
# Check system status
./docker-deploy-11a2.sh status

# Run functionality tests
./docker-deploy-11a2.sh test
```

### 3. Access Interfaces

- **API Gateway**: http://localhost:8003
- **Dashboard**: http://localhost:8008
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **UCM Cognitive**: http://localhost:8081

## Deployment Options

### Production Deployment

```bash
./docker-deploy-11a2.sh prod
```

**Includes:**
- DALS Controller with Phase 11-A2
- Redis caching
- Prometheus monitoring
- Grafana dashboards
- Consul service discovery

### Development Deployment

```bash
./docker-deploy-11a2.sh dev
```

**Includes:**
- All production services
- PostgreSQL database
- Debug logging
- Development tools
- Hot reload capabilities

### Minimal Deployment

```bash
./docker-deploy-11a2.sh minimal
```

**Includes:**
- Core DALS Controller
- Redis caching
- Essential Phase 11-A2 features

## Phase 11-A2 Features

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

## Environment Variables

### Core Configuration
```bash
ENVIRONMENT=production
PREDICTIVE_ENGINE_ENABLED=true
AUTONOMOUS_PREVENTION_MODE=11-A2
```

### Phase 11-A2 Specific
```bash
PREDICTIVE_SCAN_INTERVAL=5
RISK_THRESHOLD=70
PREVENTION_MODE=aggressive
VOICE_AWARENESS=enabled
SELF_MODEL_TRACKING=true
```

### Monitoring
```bash
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

## API Endpoints

### Predictive Engine
- `GET /predictive/health` - Current system health assessment
- `GET /predictive/risk` - Risk scores for all components
- `GET /predictive/history` - Prevention action history
- `POST /predictive/scan` - Trigger manual system scan

### Awareness System
- `GET /awareness/identity` - Caleon self-identity
- `GET /awareness/status` - Current awareness state
- `GET /awareness/predictions` - Active predictions
- `POST /awareness/voice` - Voice interaction

### CANS System
- `GET /cans/status` - Autonomic system status
- `GET /cans/actions` - Recent autonomic actions
- `POST /cans/override` - Manual intervention

## Monitoring & Observability

### Prometheus Metrics
- `predictive_engine_active` - Engine operational status
- `predictive_risk_score` - Current risk assessment
- `predictive_prevention_actions_total` - Actions executed
- `cans_response_time_seconds` - Response latency
- `self_model_confidence_percent` - Prediction accuracy

### Grafana Dashboards
- **System Health**: Overall infrastructure status
- **Risk Trends**: Time-series risk analysis
- **Prevention Actions**: Executed interventions
- **CANS Performance**: Autonomic system metrics
- **Self-Model**: Awareness and learning metrics

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
./docker-deploy-11a2.sh logs dals-controller

# Verify environment
docker-compose config

# Check dependencies
docker-compose ps
```

#### Phase 11-A2 Not Active
```bash
# Verify environment variables
docker-compose exec dals-controller env | grep PREDICTIVE

# Check engine status
curl http://localhost:8003/predictive/health
```

#### Monitoring Not Working
```bash
# Check Prometheus targets
curl http://localhost:9090/targets

# Verify Grafana access
curl http://localhost:3000/api/health
```

### Health Checks

```bash
# API Gateway
curl http://localhost:8003/health

# UCM Cognitive
curl http://localhost:8081/health

# Predictive Engine
curl http://localhost:8003/predictive/health

# All services
./docker-deploy-11a2.sh status
```

## Kubernetes Production Deployment

For production environments, DALS Phase 11-A2 supports full Kubernetes orchestration with enterprise-grade features:

### 🚀 Quick Kubernetes Deployment

```bash
# Complete production deployment
./k8s/deploy-k8s.sh full

# Minimal deployment (DALS only)
./k8s/deploy-k8s.sh minimal

# Setup secrets only
./k8s/deploy-k8s.sh secrets
```

### 🔐 Kubernetes Secrets Management

DALS implements comprehensive secret management for founder keys and secure communications:

```bash
# Initialize all secrets
./k8s/manage-secrets.sh init

# Generate founder override keys
./k8s/manage-secrets.sh founder

# Rotate all secrets with backup
./k8s/manage-secrets.sh rotate

# Check secrets status
./k8s/manage-secrets.sh status
```

**Secret Types:**
- **Founder Keys**: Emergency system override capabilities
- **CALEON Keys**: AI ethical governance and security layer
- **UCM Tokens**: Cognitive system integration secrets
- **TLS Certificates**: Auto-generated with proper SAN extensions
- **Service Accounts**: Inter-service authentication tokens

### 💾 Persistent Storage

Phase 11-A2 uses Kubernetes PersistentVolumes for data persistence:

- **Vault Storage**: Encrypted secrets and configuration (10GB)
- **Logs Storage**: Structured logging and audit trails (5GB)
- **Redis Storage**: Session and cache persistence (2GB)

### 📊 Kubernetes Monitoring

Integrated Prometheus + Grafana stack for comprehensive observability:

```bash
# Deploy monitoring stack
./k8s/deploy-k8s.sh monitoring

# Access Grafana dashboard
kubectl port-forward -n dals-system svc/monitoring-grafana 3000:80
# Open: http://localhost:3000 (admin/admin)
```

**Monitored Metrics:**
- Predictive engine performance and risk scores
- CANS autonomic response times
- Self-model confidence and learning metrics
- Voice awareness activity
- System health and resource utilization

### 🌐 Ingress and TLS

Production-ready ingress with automatic TLS certificate management:

```yaml
# External access endpoints
api.dals.example.com      # API Gateway (port 8003)
dashboard.dals.example.com # Dashboard (port 8008)
prometheus.dals.example.com # Monitoring
grafana.dals.example.com   # Analytics
```

### 🛡️ Security Features

- **Network Policies**: Service isolation and traffic control
- **RBAC**: Role-based access control for service accounts
- **Pod Security**: Restricted security contexts
- **Secret Rotation**: Automated key rotation with backup
- **Audit Logging**: Complete audit trails for all operations

### 🔄 Auto-scaling Support

Phase 11-A2 is ready for Horizontal Pod Autoscaling (HPA):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dals-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dals-controller
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
        target:
        type: Utilization
        averageUtilization: 80
```

### 📈 High Availability

Production deployment includes:
- **Multi-zone replicas** for fault tolerance
- **Load balancing** across pods
- **Rolling updates** with zero downtime
- **Health checks** and automatic recovery
- **Backup and restore** capabilities

### 🔍 Troubleshooting

```bash
# Check pod status
kubectl get pods -n dals-system

# View logs
kubectl logs -n dals-system deployment/dals-controller

# Debug pod
kubectl exec -n dals-system -it deployment/dals-controller -- /bin/bash

# Port forward for local access
kubectl port-forward -n dals-system svc/dals-service 8003:8003
```

### 📋 Production Checklist

- [ ] Kubernetes cluster with adequate resources
- [ ] Persistent storage classes configured
- [ ] TLS certificates for custom domains
- [ ] External DNS configuration
- [ ] Monitoring and alerting setup
- [ ] Backup and disaster recovery procedures
- [ ] Security policies and compliance requirements

---

## Development vs Production