#!/bin/bash
# DALS IONOS Deployment Script
# Deploys DALS alongside existing "Shioh Ridge Katahdins" website

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="dals-ionos"
DOCKER_COMPOSE_FILE="docker-compose.ionos.yml"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."

    # Check if running on Linux (IONOS servers are typically Linux)
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warning "This script is designed for Linux systems (IONOS servers)"
        log_warning "Current OS: $OSTYPE"
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    # Check available disk space (need at least 10GB)
    AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 10485760 ]; then  # 10GB in KB
        log_error "Insufficient disk space. Need at least 10GB available."
        exit 1
    fi

    log_success "All requirements satisfied"
}

create_backup() {
    log_info "Creating backup of existing configuration..."

    mkdir -p "$BACKUP_DIR"

    # Backup existing docker-compose files
    if [[ -f docker-compose.yml ]]; then
        cp docker-compose.yml "$BACKUP_DIR/"
        log_info "Backed up docker-compose.yml"
    fi

    # Backup existing nginx configs
    if [[ -d nginx ]]; then
        cp -r nginx "$BACKUP_DIR/"
        log_info "Backed up nginx configuration"
    fi

    # Backup existing environment files
    if [[ -f .env ]]; then
        cp .env "$BACKUP_DIR/"
        log_info "Backed up .env file"
    fi

    log_success "Backup created in $BACKUP_DIR"
}

setup_environment() {
    log_info "Setting up IONOS deployment environment..."

    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        log_info "Creating .env file for IONOS deployment..."
        cat > .env << EOF
# DALS IONOS Production Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FORMAT=json

# DALS API Configuration
ISS_SERVICE_NAME=dals-api
ISS_HOST=0.0.0.0
ISS_PORT=8003
DASHBOARD_PORT=8008

# UCM Configuration
UCM_HOST=ucm-service
UCM_PORT=8081

# Ollama Configuration
OLLAMA_HOST=ollama-service
OLLAMA_PORT=11434

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_ENABLED=true

# Security
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_USER=admin
ADMIN_PASSWORD_HASH=\$2b\$12\$hMDHY6YDS.LhqCsXXE8fFuYpL6vLq1Y7jZQlGChas0nHvcsgy8.26

# IONOS Specific
DOCKER_NETWORK=dals-network
COMPOSE_PROJECT_NAME=dals-ionos

# Monitoring
WEBSOCKET_ENABLED=true
MODULE_STATUS_TRACKING=true
DALS_001_ENFORCED=true
EOF
        log_success ".env file created"
    else
        log_warning ".env file already exists, skipping creation"
    fi

    # Create necessary directories
    mkdir -p data/logs data/vault exports monitoring ssl nginx/conf.d

    # Set proper permissions
    chmod 755 data/logs data/vault exports monitoring ssl

    log_success "Environment setup complete"
}

pull_ollama_model() {
    log_info "Setting up Ollama and pulling required models..."

    # Start Ollama service temporarily to pull models
    docker run -d --name ollama-temp -p 11434:11434 ollama/ollama:latest

    # Wait for Ollama to start
    log_info "Waiting for Ollama to start..."
    sleep 30

    # Pull required models
    log_info "Pulling phi3:mini model..."
    docker exec ollama-temp ollama pull phi3:mini

    # Stop and remove temporary container
    docker stop ollama-temp
    docker rm ollama-temp

    log_success "Ollama models prepared"
}

build_images() {
    log_info "Building Docker images for IONOS deployment..."

    # Build DALS API image
    log_info "Building DALS API image..."
    docker build -t dals-api:v1.0.0 -f Dockerfile .

    # Build UCM image
    log_info "Building UCM Cognitive Engine image..."
    cd Unified-Cognition-Module-Caleon-Prime-full-System
    docker build -t ucm-cognitive-engine:v1.0.0 -f Dockerfile .
    cd ..

    log_success "All images built successfully"
}

deploy_services() {
    log_info "Deploying DALS services to IONOS..."

    # Stop any existing services
    log_info "Stopping existing services..."
    docker-compose -f $DOCKER_COMPOSE_FILE down || true

    # Start services
    log_info "Starting DALS services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d

    # Wait for services to start
    log_info "Waiting for services to initialize..."
    sleep 60

    log_success "Services deployed successfully"
}

verify_deployment() {
    log_info "Verifying IONOS deployment..."

    # Check if services are running
    if ! docker-compose -f $DOCKER_COMPOSE_FILE ps | grep -q "Up"; then
        log_error "Some services failed to start"
        docker-compose -f $DOCKER_COMPOSE_FILE logs
        exit 1
    fi

    # Test DALS API health
    if curl -f http://localhost:8003/health &> /dev/null; then
        log_success "DALS API is healthy"
    else
        log_error "DALS API health check failed"
        exit 1
    fi

    # Test DALS Dashboard
    if curl -f http://localhost:8008/health &> /dev/null; then
        log_success "DALS Dashboard is healthy"
    else
        log_error "DALS Dashboard health check failed"
        exit 1
    fi

    # Test UCM Service
    if curl -f http://localhost:8081/health &> /dev/null; then
        log_success "UCM Cognitive Engine is healthy"
    else
        log_error "UCM Cognitive Engine health check failed"
        exit 1
    fi

    # Test Ollama
    if curl -f http://localhost:11434/api/tags &> /dev/null; then
        log_success "Ollama service is healthy"
    else
        log_error "Ollama service health check failed"
        exit 1
    fi

    log_success "All services verified successfully"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."

    # Check if SSL certificates exist
    if [[ ! -f ssl/dals.crt ]] || [[ ! -f ssl/dals.key ]]; then
        log_warning "SSL certificates not found. Generating self-signed certificates..."

        # Generate self-signed certificate
        openssl req -x509 -newkey rsa:4096 -keyout ssl/dals.key -out ssl/dals.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=DALS/CN=localhost"

        log_warning "Self-signed certificates generated. Consider replacing with proper certificates from Let's Encrypt or your CA"
    else
        log_success "SSL certificates found"
    fi

    # Set proper permissions
    chmod 600 ssl/dals.key
    chmod 644 ssl/dals.crt
}

setup_firewall() {
    log_info "Configuring firewall rules..."

    # Check if ufw is available (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        log_info "Configuring UFW firewall..."

        # Allow SSH (important for IONOS access)
        ufw allow ssh

        # Allow HTTP and HTTPS
        ufw allow 80
        ufw allow 443

        # Allow DALS specific ports (optional, since nginx proxies)
        # ufw allow 8003
        # ufw allow 8008
        # ufw allow 8081
        # ufw allow 11434

        # Enable firewall
        ufw --force enable

        log_success "Firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        log_info "Configuring firewalld..."

        # Add services
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh

        # Reload firewall
        firewall-cmd --reload

        log_success "Firewall configured"
    else
        log_warning "No supported firewall detected. Please configure manually."
    fi
}

create_monitoring_dashboard() {
    log_info "Setting up monitoring dashboard..."

    # Create a simple monitoring script
    cat > monitor-dals.sh << 'EOF'
#!/bin/bash
# DALS IONOS Monitoring Script

echo "=== DALS IONOS Monitoring ==="
echo "Timestamp: $(date)"
echo

echo "=== Service Status ==="
docker-compose -f docker-compose.ionos.yml ps
echo

echo "=== Health Checks ==="
echo "DALS API: $(curl -s http://localhost:8003/health || echo 'DOWN')"
echo "Dashboard: $(curl -s http://localhost:8008/health || echo 'DOWN')"
echo "UCM: $(curl -s http://localhost:8081/health || echo 'DOWN')"
echo "Ollama: $(curl -s http://localhost:11434/api/tags | jq '.models | length' 2>/dev/null || echo 'DOWN')"
echo

echo "=== Resource Usage ==="
echo "Disk Usage:"
df -h /
echo
echo "Memory Usage:"
free -h
echo
echo "Docker Containers:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF

    chmod +x monitor-dals.sh
    log_success "Monitoring script created: monitor-dals.sh"
}

print_deployment_info() {
    log_success "DALS IONOS Deployment Complete!"
    echo
    echo "=== Deployment Information ==="
    echo "🌐 Main Website: http://your-ionos-domain.com/"
    echo "🔐 DALS Login: http://your-ionos-domain.com/login"
    echo "📊 DALS Dashboard: http://your-ionos-domain.com/dashboard/"
    echo "🔧 DALS API: http://your-ionos-domain.com/api/"
    echo
    echo "=== Service URLs (Internal) ==="
    echo "DALS API: http://localhost:8003"
    echo "Dashboard: http://localhost:8008"
    echo "UCM Engine: http://localhost:8081"
    echo "Ollama: http://localhost:11434"
    echo "Prometheus: http://localhost:9090"
    echo "Consul: http://localhost:8500"
    echo
    echo "=== Management Commands ==="
    echo "Start services: docker-compose -f docker-compose.ionos.yml up -d"
    echo "Stop services: docker-compose -f docker-compose.ionos.yml down"
    echo "View logs: docker-compose -f docker-compose.ionos.yml logs -f"
    echo "Monitor: ./monitor-dals.sh"
    echo
    echo "=== Next Steps ==="
    echo "1. Update nginx configuration with your actual domain"
    echo "2. Obtain proper SSL certificates"
    echo "3. Configure DNS to point to your IONOS server"
    echo "4. Test voice integration with Ollama"
    echo "5. Set up automated backups"
}

# Main deployment flow
main() {
    echo "🚀 DALS IONOS Deployment Script"
    echo "================================="
    echo

    check_requirements
    create_backup
    setup_environment
    pull_ollama_model
    build_images
    setup_ssl
    setup_firewall
    deploy_services
    verify_deployment
    create_monitoring_dashboard
    print_deployment_info

    log_success "DALS IONOS deployment completed successfully!"
}

# Run main function
main "$@"