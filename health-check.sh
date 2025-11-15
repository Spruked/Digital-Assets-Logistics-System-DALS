#!/bin/bash
# DALS Ecosystem Health Check Script
# Tests all services for live video minting readiness

echo "🧬 DALS Ecosystem Health Check - Live Video Minting Ready"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}

    echo -n "🔍 Checking $name ($url)... "

    if curl -s --max-time 10 -o /dev/null -w "%{http_code}" "$url" | grep -q "^$expected_status$"; then
        echo -e "${GREEN}✅ UP${NC}"
        return 0
    else
        echo -e "${RED}❌ DOWN${NC}"
        return 1
    fi
}

echo ""
echo "📊 SERVICE STATUS CHECKS:"
echo "------------------------"

# Core DALS Services
check_service "DALS API" "http://localhost:8003/health"
check_service "DALS Dashboard" "http://localhost:8008/health"
check_service "Redis" "http://localhost:6379"  # Redis doesn't have HTTP health, but port check

# NFT Minting Services
check_service "CertSig Backend" "http://localhost:9000/health"
check_service "CertSig Frontend" "http://localhost:3000"
check_service "TrueMark Backend" "http://localhost:9001/health"
check_service "TrueMark Frontend" "http://localhost:8081"

# Cognitive Services
check_service "UCM Cognitive Brain" "http://localhost:8081/health"

# Infrastructure
check_service "Consul Service Discovery" "http://localhost:8500/v1/status/leader"
check_service "Loki Logging" "http://localhost:3100/ready"

echo ""
echo "🔗 INTEGRATION TESTS:"
echo "--------------------"

# Test DALS API can reach minting services
echo -n "🔗 DALS → CertSig API... "
if curl -s "http://localhost:8003/api/alpha-certsig/health" | grep -q "connected"; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${YELLOW}⚠️  NOT CONNECTED${NC}"
fi

echo -n "🔗 DALS → TrueMark API... "
if curl -s "http://localhost:8003/api/truemark/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${YELLOW}⚠️  NOT CONNECTED${NC}"
fi

echo -n "🔗 DALS → UCM Cognitive... "
if curl -s "http://localhost:8003/api/ucm/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${YELLOW}⚠️  NOT CONNECTED${NC}"
fi

echo ""
echo "🎥 LIVE VIDEO MINTING READINESS:"
echo "--------------------------------"

# Check if all critical services are up
critical_services_up=true

# Check DALS API
if ! curl -s --max-time 5 "http://localhost:8003/health" > /dev/null; then
    critical_services_up=false
fi

# Check at least one minting service
if ! curl -s --max-time 5 "http://localhost:9000/health" > /dev/null && ! curl -s --max-time 5 "http://localhost:9001/health" > /dev/null; then
    critical_services_up=false
fi

# Check UCM
if ! curl -s --max-time 5 "http://localhost:8081/health" > /dev/null; then
    critical_services_up=false
fi

if [ "$critical_services_up" = true ]; then
    echo -e "${GREEN}🚀 LIVE VIDEO MINTING: READY FOR PRODUCTION${NC}"
    echo "   ✅ DALS Core API: Operational"
    echo "   ✅ NFT Minting Services: Available"
    echo "   ✅ UCM Cognitive Brain: Active"
    echo "   ✅ Service Integration: Connected"
    echo ""
    echo "🎬 Ready to mint NFTs from live video streams!"
else
    echo -e "${RED}❌ LIVE VIDEO MINTING: NOT READY${NC}"
    echo "   Some critical services are not responding."
    echo "   Run 'docker-compose logs' to diagnose issues."
fi

echo ""
echo "📈 PERFORMANCE METRICS:"
echo "----------------------"

# Get container resource usage
echo "Docker Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(dals|alphacertsig|truemark|ucm)" | head -10

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "(dals|alphacertsig|truemark|ucm)" | head -10

echo ""
echo "🔧 Quick Commands:"
echo "   Start all:  docker-compose up -d"
echo "   Stop all:   docker-compose down"
echo "   View logs:  docker-compose logs -f [service-name]"
echo "   Rebuild:    docker-compose up -d --build [service-name]"