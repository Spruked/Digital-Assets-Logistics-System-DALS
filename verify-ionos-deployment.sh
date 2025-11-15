#!/bin/bash
# DALS IONOS Deployment Verification Script
# Comprehensive testing of all deployed services and functionality

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
DOMAIN_NAME="your-domain.com"  # Update with actual domain
TEST_USER="admin"
TEST_PASSWORD="admin123"  # Update with actual test credentials

# Results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((PASSED_TESTS++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((FAILED_TESTS++))
}

log_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
    ((TOTAL_TESTS++))
}

test_service_health() {
    local service_name="$1"
    local url="$2"
    local expected_code="${3:-200}"

    log_test "Testing $service_name health at $url"

    if response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" 2>/dev/null); then
        local body=$(echo "$response" | sed 's/HTTPSTATUS.*//')
        local status=$(echo "$response" | grep "HTTPSTATUS:" | sed 's/.*HTTPSTATUS://')

        if [[ "$status" == "$expected_code" ]]; then
            log_success "$service_name is healthy (HTTP $status)"
            return 0
        else
            log_error "$service_name returned HTTP $status (expected $expected_code)"
            return 1
        fi
    else
        log_error "$service_name is unreachable"
        return 1
    fi
}

test_ssl_certificate() {
    log_test "Testing SSL certificate validity"

    if echo | openssl s_client -connect "$DOMAIN_NAME:443" -servername "$DOMAIN_NAME" 2>/dev/null | openssl x509 -noout -checkend 86400 >/dev/null 2>&1; then
        log_success "SSL certificate is valid and not expiring soon"
        return 0
    else
        log_error "SSL certificate issue detected"
        return 1
    fi
}

test_dns_resolution() {
    log_test "Testing DNS resolution for $DOMAIN_NAME"

    if host "$DOMAIN_NAME" >/dev/null 2>&1; then
        local ip=$(dig +short "$DOMAIN_NAME" | head -1)
        log_success "DNS resolves $DOMAIN_NAME to $ip"
        return 0
    else
        log_error "DNS resolution failed for $DOMAIN_NAME"
        return 1
    fi
}

test_docker_services() {
    log_test "Testing Docker service status"

    if ! docker-compose -f docker-compose.ionos.yml ps | grep -q "Up"; then
        log_error "Some Docker services are not running"
        docker-compose -f docker-compose.ionos.yml ps
        return 1
    fi

    local running_services=$(docker-compose -f docker-compose.ionos.yml ps | grep "Up" | wc -l)
    local total_services=$(docker-compose -f docker-compose.ionos.yml ps | grep -E "(Up|Exit)" | wc -l)

    if [[ "$running_services" == "$total_services" ]]; then
        log_success "All $running_services Docker services are running"
        return 0
    else
        log_warning "$running_services/$total_services Docker services are running"
        return 1
    fi
}

test_authentication() {
    log_test "Testing DALS authentication"

    # Test login endpoint
    local login_response=$(curl -s -X POST "https://$DOMAIN_NAME/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$TEST_USER\",\"password\":\"$TEST_PASSWORD\"}")

    if echo "$login_response" | grep -q "token"; then
        log_success "Authentication successful"
        return 0
    else
        log_error "Authentication failed"
        echo "Response: $login_response"
        return 1
    fi
}

test_voice_integration() {
    log_test "Testing voice integration (Ollama + UCM)"

    # Test Ollama API
    if curl -s "https://$DOMAIN_NAME/ollama/api/tags" | grep -q "models"; then
        log_success "Ollama API accessible"
    else
        log_error "Ollama API not accessible"
        return 1
    fi

    # Test UCM health
    if curl -s "https://$DOMAIN_NAME/ucm/health" | grep -q "healthy"; then
        log_success "UCM Cognitive Engine healthy"
    else
        log_error "UCM Cognitive Engine not healthy"
        return 1
    fi

    # Test voice processing (basic connectivity test)
    local voice_test=$(curl -s -X POST "https://$DOMAIN_NAME/api/voice/process" \
        -H "Content-Type: application/json" \
        -d '{"text":"Hello world","voice":"test"}' 2>/dev/null || echo "failed")

    if [[ "$voice_test" != "failed" ]]; then
        log_success "Voice processing endpoint accessible"
        return 0
    else
        log_warning "Voice processing endpoint not accessible (may be expected if not authenticated)"
        return 0
    fi
}

test_minting_platform() {
    log_test "Testing minting platform pages"

    local pages=("tiktok-landing" "pricing" "alpha-certsig" "truemark")
    local failed_pages=0

    for page in "${pages[@]}"; do
        if curl -s "https://$DOMAIN_NAME/$page" | grep -q "DALS"; then
            log_success "$page page loads correctly"
        else
            log_error "$page page failed to load"
            ((failed_pages++))
        fi
    done

    [[ "$failed_pages" == 0 ]] && return 0 || return 1
}

test_api_endpoints() {
    log_test "Testing DALS API endpoints"

    local endpoints=(
        "/api/health:200"
        "/api/status:200"
        "/api/vault/status:200"
    )

    local failed_endpoints=0

    for endpoint in "${endpoints[@]}"; do
        local path=$(echo "$endpoint" | cut -d: -f1)
        local expected_code=$(echo "$endpoint" | cut -d: -f2)

        if test_service_health "API$path" "https://$DOMAIN_NAME$path" "$expected_code"; then
            :
        else
            ((failed_endpoints++))
        fi
    done

    [[ "$failed_endpoints" == 0 ]] && return 0 || return 1
}

test_performance() {
    log_test "Testing performance metrics"

    # Test response times
    local response_time=$(curl -s -o /dev/null -w "%{time_total}" "https://$DOMAIN_NAME/")

    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        log_success "Main page loads in ${response_time}s (acceptable)"
    else
        log_warning "Main page loads slowly: ${response_time}s"
    fi

    # Test API response time
    local api_time=$(curl -s -o /dev/null -w "%{time_total}" "https://$DOMAIN_NAME/api/health")

    if (( $(echo "$api_time < 1.0" | bc -l) )); then
        log_success "API responds in ${api_time}s (good)"
    else
        log_warning "API responds slowly: ${api_time}s"
    fi
}

test_security() {
    log_test "Testing security configuration"

    # Test HTTPS enforcement
    if curl -s -I "http://$DOMAIN_NAME/" | grep -q "301"; then
        log_success "HTTP redirects to HTTPS"
    else
        log_warning "HTTP does not redirect to HTTPS"
    fi

    # Test security headers
    local headers=$(curl -s -I "https://$DOMAIN_NAME/")
    if echo "$headers" | grep -q "X-Frame-Options"; then
        log_success "Security headers present"
    else
        log_warning "Some security headers missing"
    fi
}

test_monitoring() {
    log_test "Testing monitoring services"

    # Test Prometheus
    if curl -s "http://localhost:9090/-/healthy" >/dev/null 2>&1; then
        log_success "Prometheus is healthy"
    else
        log_warning "Prometheus not accessible"
    fi

    # Test Consul
    if curl -s "http://localhost:8500/v1/status/leader" >/dev/null 2>&1; then
        log_success "Consul is healthy"
    else
        log_warning "Consul not accessible"
    fi
}

generate_report() {
    log_header "DALS IONOS Deployment Verification Report"
    echo "Timestamp: $(date)"
    echo "Domain: $DOMAIN_NAME"
    echo
    echo "=== Test Results ==="
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Warnings: $WARNINGS"
    echo

    local success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))

    if [[ "$success_rate" -ge 90 ]]; then
        echo -e "${GREEN}✅ OVERALL STATUS: EXCELLENT ($success_rate% success rate)${NC}"
    elif [[ "$success_rate" -ge 75 ]]; then
        echo -e "${YELLOW}⚠️  OVERALL STATUS: GOOD ($success_rate% success rate)${NC}"
    else
        echo -e "${RED}❌ OVERALL STATUS: NEEDS ATTENTION ($success_rate% success rate)${NC}"
    fi

    echo
    echo "=== Recommendations ==="

    if [[ "$FAILED_TESTS" -gt 0 ]]; then
        echo "🔧 Address failed tests before going live"
    fi

    if [[ "$WARNINGS" -gt 0 ]]; then
        echo "⚠️  Review warnings for potential issues"
    fi

    if [[ "$success_rate" -ge 90 ]]; then
        echo "🚀 System is ready for production deployment"
    fi

    echo
    echo "=== Service Status ==="
    docker-compose -f docker-compose.ionos.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
}

# Main verification flow
main() {
    echo "🔍 DALS IONOS Deployment Verification"
    echo "====================================="
    echo

    # Pre-flight checks
    if [[ "$DOMAIN_NAME" == "your-domain.com" ]]; then
        log_error "Please update DOMAIN_NAME in this script with your actual domain"
        exit 1
    fi

    # Run all tests
    log_header "Infrastructure Tests"
    test_dns_resolution
    test_ssl_certificate
    test_docker_services

    log_header "Service Health Tests"
    test_service_health "Main Website" "https://$DOMAIN_NAME/"
    test_service_health "DALS Dashboard" "https://$DOMAIN_NAME/dashboard/"
    test_api_endpoints

    log_header "Authentication Tests"
    test_authentication

    log_header "Voice Integration Tests"
    test_voice_integration

    log_header "Platform Tests"
    test_minting_platform

    log_header "Performance Tests"
    test_performance

    log_header "Security Tests"
    test_security

    log_header "Monitoring Tests"
    test_monitoring

    # Generate final report
    echo
    generate_report

    # Exit with appropriate code
    if [[ "$FAILED_TESTS" -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

# Run main function
main "$@"