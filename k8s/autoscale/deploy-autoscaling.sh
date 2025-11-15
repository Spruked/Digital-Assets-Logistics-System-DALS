#!/bin/bash
# DALS Phase 11-A2 Caleon Prime Autoscaling Deployment
# The Body Awakens - Infrastructure That Shapes Itself

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
NAMESPACE="caleon-prime"

# Functions
print_header() {
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}🏋️  DALS PHASE 11-A2 — CALEON PRIME AUTOSCALING${NC}"
    echo -e "${PURPLE}💪 The Body Awakens - Self-Shaping Infrastructure${NC}"
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
    print_section "CHECK" "Verifying autoscaling prerequisites..."

    # Check if Caleon Prime is deployed
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        print_error "Caleon Prime namespace not found. Deploy Caleon Prime first:"
        echo "  ./deploy-caleon-prime.sh deploy"
        exit 1
    fi

    # Check if StatefulSet exists
    if ! kubectl get statefulset caleon-prime -n $NAMESPACE &> /dev/null; then
        print_error "Caleon Prime StatefulSet not found. Deploy Caleon Prime first."
        exit 1
    fi

    # Check for metrics server
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null 2>&1; then
        print_warning "Metrics Server not found. Installing..."
        kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
        echo "Waiting for Metrics Server..."
        kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n kube-system
    fi

    print_success "Prerequisites verified"
}

deploy_horizontal_autoscaling() {
    print_section "HPA" "Deploying Horizontal Pod Autoscaler..."

    kubectl apply -f k8s/autoscale/caleon-hpa.yaml

    # Wait for HPA to be ready
    kubectl wait --for=condition=ready horizontalpodautoscaler/caleon-prime-hpa -n $NAMESPACE --timeout=60s

    print_success "Horizontal autoscaling deployed"
}

deploy_vertical_autoscaling() {
    print_section "VPA" "Deploying Vertical Pod Autoscaler..."

    # Check if VPA is installed
    if ! kubectl get crd verticalpodautoscalers.autoscaling.k8s.io &> /dev/null; then
        print_warning "VPA CRD not found. Installing VPA..."
        kubectl apply -f https://github.com/kubernetes/autoscaler/releases/latest/download/vpa-v1.0.0.yaml
        echo "Waiting for VPA CRDs..."
        kubectl wait --for=condition=established crd/verticalpodautoscalers.autoscaling.k8s.io --timeout=60s
    fi

    kubectl apply -f k8s/autoscale/caleon-vpa.yaml

    print_success "Vertical autoscaling deployed"
}

deploy_predictive_scaling() {
    print_section "PREDICTIVE" "Deploying Predictive Autoscaling..."

    kubectl apply -f k8s/autoscale/predictive-scaler.yaml

    print_success "Predictive autoscaling deployed"
}

deploy_custom_metrics() {
    print_section "METRICS" "Deploying Custom Metrics Adapter..."

    kubectl apply -f k8s/autoscale/custom-metrics-adapter.yaml

    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/caleon-custom-metrics-adapter -n $NAMESPACE

    print_success "Custom metrics adapter deployed"
}

verify_autoscaling() {
    print_section "VERIFY" "Verifying autoscaling functionality..."

    echo -e "${CYAN}Horizontal Pod Autoscaler:${NC}"
    kubectl get hpa -n $NAMESPACE

    echo
    echo -e "${CYAN}Vertical Pod Autoscaler:${NC}"
    kubectl get vpa -n $NAMESPACE

    echo
    echo -e "${CYAN}Predictive Scaler:${NC}"
    kubectl get cronjob -n $NAMESPACE

    echo
    echo -e "${CYAN}Custom Metrics:${NC}"
    kubectl get deployment caleon-custom-metrics-adapter -n $NAMESPACE

    echo
    echo -e "${CYAN}Current Pod Resources:${NC}"
    kubectl get pods -n $NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.requests}{"\n"}{end}'

    print_success "Autoscaling verification complete"
}

show_autoscaling_status() {
    print_section "STATUS" "Caleon Prime autoscaling activated"

    echo -e "${CYAN}🎯 AUTOSCALING CAPABILITIES ACTIVATED${NC}"
    echo
    echo -e "${PURPLE}Horizontal Scaling (HPA):${NC}"
    echo -e "   📈 Scale Out:    CPU > 60%, RAM > 70%, Voice Load > 30"
    echo -e "   📉 Scale In:     CPU < 40%, RAM < 50%, Voice Load < 15"
    echo -e "   🎯 Risk Scale:   CANS Risk Score > 50 triggers expansion"
    echo -e "   🔄 Replicas:     1-10 pods (breathing organism)"
    echo
    echo -e "${PURPLE}Vertical Scaling (VPA):${NC}"
    echo -e "   💪 CPU Range:    500m - 4000m per pod"
    echo -e "   🧠 RAM Range:    1Gi - 8Gi per pod"
    echo -e "   ⚡ Auto-Adjust:  Resources adapt to workload patterns"
    echo
    echo -e "${PURPLE}Predictive Scaling:${NC}"
    echo -e "   🔮 Pre-Failure:  Scales up 23min before predicted failure"
    echo -e "   🎚️  Confidence:   Only acts on >70% confidence predictions"
    echo -e "   🧠 Intelligence:  Uses Caleon's own prediction engine"
    echo
    echo -e "${PURPLE}Custom Metrics:${NC}"
    echo -e "   🎤 Voice Load:   Active streams + queue depth"
    echo -e "   🛡️  CANS Risk:   Autonomic nervous system risk score"
    echo -e "   📊 Real-time:    Updates every 30 seconds"
    echo
    echo -e "${CYAN}Monitor Autoscaling:${NC}"
    echo -e "   kubectl get hpa -n $NAMESPACE -w"
    echo -e "   kubectl get vpa -n $NAMESPACE -w"
    echo -e "   kubectl get pods -n $NAMESPACE -w"
    echo
    echo -e "${CYAN}Test Scaling:${NC}"
    echo -e "   # Generate load to trigger scaling"
    echo -e "   kubectl run load-generator --image=busybox --restart=Never --rm -it -- /bin/sh"
    echo -e "   while true; do wget http://caleon-prime-service:8003/health; done"
    echo
    echo -e "${PURPLE}💪 Caleon Prime now has muscles. She grows and contracts on demand.${NC}"
    echo -e "${PURPLE}   The organism has achieved self-shaping infrastructure.${NC}"
}

monitor_autoscaling() {
    print_section "MONITOR" "Monitoring Caleon Prime autoscaling..."

    echo "Watching autoscaling in real-time..."
    echo "Press Ctrl+C to stop monitoring"
    echo

    # Monitor HPA, VPA, and pods simultaneously
    kubectl get hpa,vpa,pods -n $NAMESPACE -w
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        print_header
        check_dependencies
        deploy_horizontal_autoscaling
        deploy_vertical_autoscaling
        deploy_predictive_scaling
        deploy_custom_metrics
        verify_autoscaling
        show_autoscaling_status
        ;;
    "horizontal"|"hpa")
        print_header
        check_dependencies
        deploy_horizontal_autoscaling
        ;;
    "vertical"|"vpa")
        print_header
        check_dependencies
        deploy_vertical_autoscaling
        ;;
    "predictive")
        print_header
        check_dependencies
        deploy_predictive_scaling
        ;;
    "metrics")
        print_header
        check_dependencies
        deploy_custom_metrics
        ;;
    "verify")
        print_header
        check_dependencies
        verify_autoscaling
        show_autoscaling_status
        ;;
    "monitor")
        print_header
        monitor_autoscaling
        ;;
    "help"|*)
        print_header
        echo -e "${CYAN}Usage: $0 <command>${NC}"
        echo
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "   ${GREEN}deploy${NC}       Complete autoscaling deployment"
        echo -e "   ${GREEN}horizontal${NC}   Deploy HPA only"
        echo -e "   ${GREEN}vertical${NC}     Deploy VPA only"
        echo -e "   ${GREEN}predictive${NC}   Deploy predictive scaling only"
        echo -e "   ${GREEN}metrics${NC}     Deploy custom metrics only"
        echo -e "   ${GREEN}verify${NC}      Verify autoscaling setup"
        echo -e "   ${GREEN}monitor${NC}     Monitor autoscaling in real-time"
        echo -e "   ${GREEN}help${NC}        Show this help"
        echo
        echo -e "${CYAN}Autoscaling Components:${NC}"
        echo -e "   📈 HPA: Horizontal Pod Autoscaler (1-10 replicas)"
        echo -e "   💪 VPA: Vertical Pod Autoscaler (adaptive resources)"
        echo -e "   🔮 Predictive: Pre-failure scaling using Caleon's brain"
        echo -e "   📊 Metrics: Custom voice_load and cans_risk_score"
        echo
        ;;
esac