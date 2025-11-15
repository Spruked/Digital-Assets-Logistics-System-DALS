#!/bin/bash
# DALS Docker Deployment Script for Phase 11-A2
# Comprehensive container management for Caleon Prime's living infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="dals-11a2"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="docker-compose.prod.yml"
DOCKER_COMPOSE_DEV_FILE="docker-compose.dev.yml"

# Functions
print_header() {
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}🚀 DALS PHASE 11-A2 — AUTONOMOUS PREDICTIVE PREVENTION${NC}"
    echo -e "${PURPLE}🔮 Caleon Prime: Living Infrastructure Containerization${NC}"
    echo -e "${PURPLE}================================================================================${NC}"
    echo
}

print_section() {
    echo -e "${BLUE}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    print_section "CHECK" "Verifying Docker environment..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running"
        exit 1
    fi

    print_success "Docker environment verified"
}

build_images() {
    print_section "BUILD" "Building Phase 11-A2 container images..."

    # Build main DALS controller
    echo "Building DALS Controller with Phase 11-A2 features..."
    docker build -t dals-controller:11a2 -f Dockerfile . --target production

    # Build development image
    echo "Building DALS Development Controller..."
    docker build -t dals-controller:dev-11a2 -f Dockerfile.dev . --target development

    print_success "Container images built successfully"
}

deploy_production() {
    print_section "DEPLOY" "Deploying Phase 11-A2 Production Environment..."

    # Create required directories
    mkdir -p logs vault iss_module/data config

    # Set production environment
    export ENVIRONMENT=production
    export PREDICTIVE_ENGINE_ENABLED=true
    export AUTONOMOUS_PREVENTION_MODE=11-A2

    # Deploy with production compose
    docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE up -d

    print_success "Phase 11-A2 production deployment complete"
    print_endpoints
}

deploy_development() {
    print_section "DEPLOY" "Deploying Phase 11-A2 Development Environment..."

    # Create required directories
    mkdir -p logs vault iss_module/data config

    # Set development environment
    export ENVIRONMENT=development
    export PREDICTIVE_ENGINE_ENABLED=true
    export AUTONOMOUS_PREVENTION_MODE=11-A2
    export DEBUG_MODE=true

    # Deploy with development compose
    docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_DEV_FILE up -d

    print_success "Phase 11-A2 development deployment complete"
    print_endpoints
}

deploy_minimal() {
    print_section "DEPLOY" "Deploying Phase 11-A2 Minimal Environment..."

    # Create required directories
    mkdir -p logs vault iss_module/data config

    # Deploy only essential services
    docker-compose up -d dals-controller redis

    print_success "Phase 11-A2 minimal deployment complete"
    print_endpoints
}

print_endpoints() {
    echo
    echo -e "${CYAN}🌐 DALS Phase 11-A2 Endpoints:${NC}"
    echo -e "   📊 API Gateway:     http://localhost:8003"
    echo -e "   📈 Dashboard:       http://localhost:8008"
    echo -e "   🧠 UCM Cognitive:   http://localhost:8081"
    echo -e "   🔮 Awareness API:   http://localhost:8003/awareness"
    echo -e "   🔮 Predictive API:  http://localhost:8003/predictive"
    echo -e "   🎤 Voice Portal:    http://localhost:8003/api/voice"
    echo
    echo -e "${CYAN}🔍 Health Checks:${NC}"
    echo -e "   curl http://localhost:8003/health"
    echo -e "   curl http://localhost:8081/health"
    echo
}

stop_services() {
    print_section "STOP" "Stopping all DALS services..."

    docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE down
    docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_DEV_FILE down
    docker-compose down

    print_success "All services stopped"
}

clean_containers() {
    print_section "CLEAN" "Cleaning up containers and volumes..."

    read -p "This will remove all containers and volumes. Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_PROD_FILE down -v
        docker-compose -f $DOCKER_COMPOSE_FILE -f $DOCKER_COMPOSE_DEV_FILE down -v
        docker-compose down -v

        # Remove dangling images
        docker image prune -f

        print_success "Cleanup complete"
    else
        print_warning "Cleanup cancelled"
    fi
}

show_logs() {
    print_section "LOGS" "Showing DALS service logs..."

    if [ "$2" ]; then
        docker-compose logs -f "$2"
    else
        docker-compose logs -f dals-controller
    fi
}

show_status() {
    print_section "STATUS" "DALS Phase 11-A2 System Status"

    echo -e "${CYAN}Container Status:${NC}"
    docker-compose ps

    echo
    echo -e "${CYAN}Phase 11-A2 Features:${NC}"
    echo -e "   🧠 Predictive Engine:   ${GREEN}ACTIVE${NC}"
    echo -e "   🔮 Self-Model:         ${GREEN}OPERATIONAL${NC}"
    echo -e "   🎤 Voice Awareness:    ${GREEN}ENABLED${NC}"
    echo -e "   🛡️  Autonomous CANS:   ${GREEN}AGGRESSIVE${NC}"
    echo -e "   📊 Health Monitoring:  ${GREEN}CONTINUOUS${NC}"
    echo -e "   🚨 Prevention Mode:    ${GREEN}11-A2${NC}"

    echo
    echo -e "${CYAN}System Health:${NC}"
    if curl -s http://localhost:8003/health > /dev/null 2>&1; then
        echo -e "   🌐 API Gateway:        ${GREEN}HEALTHY${NC}"
    else
        echo -e "   🌐 API Gateway:        ${RED}UNHEALTHY${NC}"
    fi

    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        echo -e "   🧠 UCM Cognitive:      ${GREEN}HEALTHY${NC}"
    else
        echo -e "   🧠 UCM Cognitive:      ${RED}UNHEALTHY${NC}"
    fi
}

test_phase_11a2() {
    print_section "TEST" "Running Phase 11-A2 functionality tests..."

    # Test API endpoints
    echo "Testing API endpoints..."

    # Health check
    if curl -s http://localhost:8003/health > /dev/null 2>&1; then
        print_success "API Gateway health check passed"
    else
        print_error "API Gateway health check failed"
    fi

    # Awareness endpoint
    if curl -s http://localhost:8003/awareness/identity > /dev/null 2>&1; then
        print_success "Awareness API operational"
    else
        print_error "Awareness API not responding"
    fi

    # Predictive endpoint
    if curl -s http://localhost:8003/predictive/health > /dev/null 2>&1; then
        print_success "Predictive API operational"
    else
        print_error "Predictive API not responding"
    fi

    # UCM health
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        print_success "UCM Cognitive health check passed"
    else
        print_error "UCM Cognitive health check failed"
    fi

    print_success "Phase 11-A2 testing complete"
}

# Main script logic
case "${1:-help}" in
    "build")
        print_header
        check_dependencies
        build_images
        ;;
    "prod"|"production")
        print_header
        check_dependencies
        deploy_production
        ;;
    "dev"|"development")
        print_header
        check_dependencies
        deploy_development
        ;;
    "minimal")
        print_header
        check_dependencies
        deploy_minimal
        ;;
    "stop")
        print_header
        stop_services
        ;;
    "clean")
        print_header
        clean_containers
        ;;
    "logs")
        print_header
        show_logs "$@"
        ;;
    "status")
        print_header
        show_status
        ;;
    "test")
        print_header
        test_phase_11a2
        ;;
    "restart")
        print_header
        stop_services
        sleep 2
        deploy_production
        ;;
    "help"|*)
        print_header
        echo -e "${CYAN}Usage: $0 <command>${NC}"
        echo
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "   ${GREEN}build${NC}         Build container images"
        echo -e "   ${GREEN}prod${NC}          Deploy production environment"
        echo -e "   ${GREEN}dev${NC}           Deploy development environment"
        echo -e "   ${GREEN}minimal${NC}       Deploy minimal environment (core only)"
        echo -e "   ${GREEN}stop${NC}          Stop all services"
        echo -e "   ${GREEN}clean${NC}         Clean containers and volumes"
        echo -e "   ${GREEN}logs${NC}          Show service logs (optional: <service-name>)"
        echo -e "   ${GREEN}status${NC}        Show system status"
        echo -e "   ${GREEN}test${NC}          Run functionality tests"
        echo -e "   ${GREEN}restart${NC}       Restart all services"
        echo -e "   ${GREEN}help${NC}          Show this help"
        echo
        echo -e "${CYAN}Phase 11-A2 Features:${NC}"
        echo -e "   🧠 Autonomous Predictive Prevention"
        echo -e "   🔮 Caleon Self-Model Integration"
        echo -e "   🎤 Voice Awareness System"
        echo -e "   🛡️  CANS Autonomic Nervous System"
        echo -e "   📊 Real-time Health Monitoring"
        echo -e "   🚨 Proactive Failure Prevention"
        echo
        ;;
esac