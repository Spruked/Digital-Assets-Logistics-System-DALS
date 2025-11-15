# DALS IONOS Production Deployment Guide

## Overview

This guide provides complete instructions for deploying the Digital Asset Logistics System (DALS) to an IONOS server alongside your existing "Shioh Ridge Katahdins" website.

## Architecture

```
Internet → IONOS Server (Nginx Reverse Proxy)
├── Main Website (/) → Shioh Ridge Katahdins
├── DALS Login (/login) → Authentication
├── DALS Dashboard (/dashboard) → Admin Interface
├── DALS API (/api) → REST API Endpoints
├── UCM Engine (/ucm) → Cognitive Brain
└── Ollama API (/ollama) → Voice Processing
```

## Prerequisites

### IONOS Server Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Storage**: 50GB minimum, 100GB recommended
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **Network**: Stable internet connection

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl
- openssl

### Domain Requirements
- Domain name registered and DNS management access
- Ability to add A/CNAME records
- SSL certificate (Let's Encrypt recommended)

## Quick Start Deployment

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Restart session to apply Docker group changes
newgrp docker
```

### 2. Clone and Configure
```bash
# Clone repository
git clone https://github.com/your-repo/dals-system.git
cd dals-system

# Update configuration scripts with your values
nano deploy-ionos.sh  # Update DOMAIN_NAME and IONOS_SERVER_IP
nano setup-ionos-domain.sh  # Update domain and IP
```

### 3. Deploy DALS System
```bash
# Run deployment script
./deploy-ionos.sh
```

### 4. Configure Domain
```bash
# Run domain setup script
./setup-ionos-domain.sh
```

### 5. Verify Deployment
```bash
# Run comprehensive verification
./verify-ionos-deployment.sh
```

## Detailed Configuration

### Environment Variables

Update the `.env` file with production values:

```bash
# DALS Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FORMAT=json

# Service Configuration
ISS_SERVICE_NAME=dals-api
ISS_HOST=0.0.0.0
ISS_PORT=8003
DASHBOARD_PORT=8008

# Security
SECRET_KEY=your-secure-random-key-here
ADMIN_USER=your-admin-username
ADMIN_PASSWORD_HASH=your-bcrypt-hash-here

# UCM Configuration
UCM_HOST=ucm-service
UCM_PORT=8081

# Ollama Configuration
OLLAMA_HOST=ollama-service
OLLAMA_PORT=11434

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_ENABLED=true

# Monitoring
WEBSOCKET_ENABLED=true
MODULE_STATUS_TRACKING=true
DALS_001_ENFORCED=true
```

### DNS Configuration

Add these records in your IONOS DNS management:

```
Type: A
Host: @
Value: YOUR_IONOS_SERVER_IP
TTL: 3600

Type: A
Host: www
Value: YOUR_IONOS_SERVER_IP
TTL: 3600

Type: CNAME (optional)
Host: dals
Value: your-domain.com
TTL: 3600
```

### SSL Certificate Setup

The deployment script includes automatic SSL setup. For manual setup:

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy to DALS ssl directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/dals.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/dals.key
```

## Service Architecture

### Docker Services

1. **nginx**: Reverse proxy and load balancer
2. **dals-api**: Main FastAPI application server
3. **dals-dashboard**: Web dashboard interface
4. **ucm-service**: Unified Cognition Module (cognitive brain)
5. **ollama-service**: Voice processing with Phi-3 Mini
6. **redis**: Caching and session storage
7. **prometheus**: Metrics collection
8. **loki**: Log aggregation
9. **consul**: Service discovery

### Port Mapping

```
80/443 → nginx (public)
8003 → dals-api (internal)
8008 → dals-dashboard (internal)
8081 → ucm-service (internal)
11434 → ollama-service (internal)
6379 → redis (internal)
9090 → prometheus (internal)
3100 → loki (internal)
8500 → consul (internal)
```

## Monitoring and Maintenance

### Health Checks

All services include health check endpoints:

- **DALS API**: `https://your-domain.com/api/health`
- **Dashboard**: `https://your-domain.com/dashboard/health`
- **UCM**: `https://your-domain.com/ucm/health`
- **Ollama**: `https://your-domain.com/ollama/api/tags`

### Monitoring Scripts

```bash
# Monitor all services
./monitor-dals.sh

# Monitor domain and SSL
./monitor-domain.sh

# Comprehensive verification
./verify-ionos-deployment.sh
```

### Backup Strategy

```bash
# Run backup script
./backup-dals.sh

# Backup includes:
# - Docker volumes
# - Configuration files
# - SSL certificates
# - Database dumps (if applicable)
```

### Log Management

```bash
# View service logs
docker-compose -f docker-compose.ionos.yml logs -f

# View specific service logs
docker-compose -f docker-compose.ionos.yml logs -f dals-api

# Loki log aggregation
# Access via: http://localhost:3100
```

## Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker-compose -f docker-compose.ionos.yml ps

# View detailed logs
docker-compose -f docker-compose.ionos.yml logs <service-name>

# Restart specific service
docker-compose -f docker-compose.ionos.yml restart <service-name>
```

#### SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Restart nginx to load new certificate
docker-compose -f docker-compose.ionos.yml restart nginx
```

#### Voice Integration Not Working
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Check UCM service
curl http://localhost:8081/health

# Verify model loading
docker-compose -f docker-compose.ionos.yml exec ollama ollama list
```

#### Database Connection Issues
```bash
# Check Redis connectivity
docker-compose -f docker-compose.ionos.yml exec redis redis-cli ping

# View Redis logs
docker-compose -f docker-compose.ionos.yml logs redis
```

### Performance Optimization

#### Resource Monitoring
```bash
# Monitor Docker resource usage
docker stats

# Check system resources
htop
df -h
free -h
```

#### Scaling Services
```bash
# Scale specific service
docker-compose -f docker-compose.ionos.yml up -d --scale dals-api=3

# Update resource limits in docker-compose.ionos.yml
# deploy:
#   resources:
#     limits:
#       memory: 1G
#       cpus: '1.0'
```

## Security Considerations

### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

### SSL/TLS Configuration
- SSL certificates are automatically configured
- HSTS headers enabled
- Security headers configured in nginx
- Rate limiting enabled

### Access Control
- Admin authentication required for dashboard
- API endpoints protected with authentication
- CALEON security layer active
- DALS-001 governance enforced

## Backup and Recovery

### Automated Backups
```bash
# Set up cron job for daily backups
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * cd /path/to/dals && ./backup-dals.sh
```

### Disaster Recovery
1. **Stop current services**: `docker-compose -f docker-compose.ionos.yml down`
2. **Restore from backup**: Extract backup archive
3. **Update configuration**: Verify `.env` and nginx configs
4. **Restart services**: `docker-compose -f docker-compose.ionos.yml up -d`
5. **Verify functionality**: Run `./verify-ionos-deployment.sh`

## Support and Maintenance

### Regular Maintenance Tasks
- **Weekly**: Security updates and log rotation
- **Monthly**: SSL certificate renewal check
- **Quarterly**: Full system backup verification
- **Annually**: Security audit and performance review

### Monitoring Dashboards
- **Grafana**: Access via configured endpoint
- **Prometheus**: Metrics at `http://localhost:9090`
- **Consul**: Service discovery at `http://localhost:8500`

### Emergency Contacts
- **Technical Support**: [Your Contact Information]
- **IONOS Support**: https://www.ionos.com/help
- **Emergency Procedures**: See `production-readiness-checklist.md`

## File Structure

```
dals-system/
├── docker-compose.ionos.yml      # Production Docker configuration
├── nginx/
│   └── conf.d/
│       └── dals.ionos.conf       # Nginx routing configuration
├── ssl/                          # SSL certificates
├── data/                         # Persistent data volumes
├── backups/                      # Backup archives
├── deploy-ionos.sh              # Main deployment script
├── setup-ionos-domain.sh        # Domain configuration script
├── verify-ionos-deployment.sh   # Comprehensive verification
├── monitor-dals.sh              # Service monitoring
├── monitor-domain.sh            # Domain monitoring
├── backup-dals.sh               # Backup script
├── maintain-dals.sh             # Maintenance script
├── production-readiness-checklist.md  # Deployment checklist
└── IONOS_DEPLOYMENT_README.md   # This file
```

---

## Final Checklist

Before going live, ensure:

- [ ] All services are running and healthy
- [ ] SSL certificates are valid
- [ ] DNS records are propagated
- [ ] Authentication is working
- [ ] Voice integration is functional
- [ ] Backup systems are operational
- [ ] Monitoring is configured
- [ ] Emergency procedures are documented

**Deployment Complete!** 🚀

Your DALS system is now running alongside your existing website on IONOS infrastructure.