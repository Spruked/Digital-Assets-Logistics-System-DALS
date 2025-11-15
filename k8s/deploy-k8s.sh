#!/bin/bash
# DALS Phase 11-A2 Kubernetes Deployment Script
# Complete orchestration setup for Caleon Prime autonomous infrastructure

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
NAMESPACE="dals-system"
DOCKER_REGISTRY=""  # Set if using private registry

# Functions
print_header() {
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}☸️  DALS PHASE 11-A2 — KUBERNETES ORCHESTRATION${NC}"
    echo -e "${PURPLE}🔮 Caleon Prime: Production Autonomous Infrastructure${NC}"
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
    print_section "CHECK" "Verifying Kubernetes environment..."

    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi

    if ! command -v helm &> /dev/null; then
        print_warning "helm not found - will install required components manually"
    fi

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    print_success "Kubernetes environment verified"
}

create_namespace() {
    print_section "NAMESPACE" "Creating DALS namespace..."

    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        kubectl create namespace $NAMESPACE
        print_success "Namespace $NAMESPACE created"
    else
        print_warning "Namespace $NAMESPACE already exists"
    fi
}

setup_storage() {
    print_section "STORAGE" "Setting up persistent storage..."

    kubectl apply -f k8s/persistent-volumes.yml

    # Wait for PVCs to be bound
    echo "Waiting for PersistentVolumeClaims to be bound..."
    kubectl wait --for=condition=bound pvc --all -n $NAMESPACE --timeout=300s

    print_success "Persistent storage configured"
}

setup_secrets() {
    print_section "SECRETS" "Setting up Kubernetes secrets..."

    # Run the secrets management script
    chmod +x k8s/manage-secrets.sh
    ./k8s/manage-secrets.sh init

    print_success "Secrets configured"
}

setup_config() {
    print_section "CONFIG" "Setting up ConfigMaps..."

    kubectl apply -f k8s/configmap.yml

    print_success "ConfigMaps configured"
}

deploy_infrastructure() {
    print_section "INFRA" "Deploying supporting infrastructure..."

    # Deploy Redis
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/examples/master/guestbook/redis-master-deployment.yaml
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/examples/master/guestbook/redis-master-service.yaml

    # Wait for Redis to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/redis-master -n default

    print_success "Infrastructure deployed"
}

deploy_monitoring() {
    print_section "MONITORING" "Setting up monitoring stack..."

    # Add Prometheus community helm repo
    if command -v helm &> /dev/null; then
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update

        # Install kube-prometheus-stack
        helm install monitoring prometheus-community/kube-prometheus-stack \
            --namespace $NAMESPACE \
            --create-namespace \
            --set grafana.adminPassword='admin' \
            --set prometheus.service.type=ClusterIP \
            --set grafana.service.type=ClusterIP

        print_success "Monitoring stack deployed with Helm"
    else
        print_warning "Helm not available - monitoring stack not deployed"
        print_warning "Install manually: https://github.com/prometheus-community/helm-charts"
    fi
}

deploy_dals() {
    print_section "DALS" "Deploying DALS Phase 11-A2..."

    # Apply RBAC
    kubectl apply -f k8s/deployment.yml

    # Wait for deployment to be ready
    kubectl wait --for=condition=available --timeout=300s deployment/dals-controller -n $NAMESPACE

    print_success "DALS Phase 11-A2 deployed"
}

setup_ingress() {
    print_section "INGRESS" "Setting up ingress controllers..."

    # Create ingress for API and dashboard
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dals-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.dals.example.com
    - dashboard.dals.example.com
    secretName: dals-tls-certificates
  rules:
  - host: api.dals.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dals-service
            port:
              number: 8003
  - host: dashboard.dals.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dals-service
            port:
              number: 8008
EOF

    print_success "Ingress configured"
}

setup_network_policies() {
    print_section "NETWORK" "Setting up network policies..."

    # Create network policy for DALS
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: dals-network-policy
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      app: dals-11a2
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8003
    - protocol: TCP
      port: 8008
  - from:
    - podSelector:
        matchLabels:
          app: dals-11a2
    ports:
    - protocol: TCP
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
EOF

    print_success "Network policies configured"
}

deploy_caleon_prime() {
    print_section "CALEON-PRIME" "Deploying Caleon Prime with Immortal Memory..."

    # Use the dedicated Caleon Prime deployment script
    if [ -f "./deploy-caleon-prime.sh" ]; then
        print_section "IMMORTAL" "Using dedicated Caleon Prime deployment script..."
        ./deploy-caleon-prime.sh deploy
    else
        print_error "deploy-caleon-prime.sh not found. Please ensure it exists in the k8s directory."
        exit 1
    fi

    print_success "Caleon Prime immortal memory deployment complete"
}
        print_warning "Velero not found - backup not configured"
    fi

    print_success "Caleon Prime deployed with immortal memory"
}

verify_deployment() {
    print_section "VERIFY" "Verifying Phase 11-A2 deployment..."

    echo -e "${CYAN}Pod Status:${NC}"
    kubectl get pods -n $NAMESPACE -l app=dals-11a2

    echo
    echo -e "${CYAN}Service Status:${NC}"
    kubectl get services -n $NAMESPACE -l app=dals-11a2

    echo
    echo -e "${CYAN}Secret Status:${NC}"
    kubectl get secrets -n $NAMESPACE -l app=dals-11a2

    echo
    echo -e "${CYAN}PVC Status:${NC}"
    kubectl get pvc -n $NAMESPACE -l app=dals-11a2

    # Test health endpoint
    echo
    echo -e "${CYAN}Testing Health Endpoint:${NC}"
    if kubectl exec -n $NAMESPACE deployment/dals-controller -- curl -s http://localhost:8003/health > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_warning "Health check failed - check pod logs"
    fi
}

show_endpoints() {
    print_section "ENDPOINTS" "DALS Phase 11-A2 Service Endpoints"

    echo -e "${CYAN}Internal Services:${NC}"
    echo -e "   🌐 API Gateway:     dals-service.$NAMESPACE.svc.cluster.local:8003"
    echo -e "   📈 Dashboard:       dals-service.$NAMESPACE.svc.cluster.local:8008"
    echo -e "   🧠 UCM Cognitive:   ucm-service.$NAMESPACE.svc.cluster.local:8081"
    echo -e "   📊 Prometheus:      monitoring-prometheus-server.$NAMESPACE.svc.cluster.local"
    echo -e "   📈 Grafana:         monitoring-grafana.$NAMESPACE.svc.cluster.local"

    echo
    echo -e "${CYAN}External Access (if ingress configured):${NC}"
    echo -e "   🌐 API:             https://api.dals.example.com"
    echo -e "   📈 Dashboard:       https://dashboard.dals.example.com"
    echo -e "   📊 Prometheus:      https://prometheus.dals.example.com"
    echo -e "   📈 Grafana:         https://grafana.dals.example.com"

    echo
    echo -e "${CYAN}Port Forwarding for Local Access:${NC}"
    echo -e "   kubectl port-forward -n $NAMESPACE svc/dals-service 8003:8003"
    echo -e "   kubectl port-forward -n $NAMESPACE svc/dals-service 8008:8008"
}

cleanup() {
    print_section "CLEANUP" "Cleaning up Phase 11-A2 deployment..."

    read -p "This will remove all DALS resources. Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete namespace $NAMESPACE
        print_success "Cleanup complete"
    else
        print_warning "Cleanup cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    "full")
        print_header
        check_dependencies
        create_namespace
        setup_storage
        setup_secrets
        setup_config
        deploy_infrastructure
        deploy_monitoring
        deploy_dals
        setup_ingress
        setup_network_policies
        verify_deployment
        show_endpoints
        ;;
    "minimal")
        print_header
        check_dependencies
        create_namespace
        setup_storage
        setup_secrets
        setup_config
        deploy_dals
        verify_deployment
        show_endpoints
        ;;
    "secrets")
        print_header
        check_dependencies
        create_namespace
        setup_secrets
        ;;
    "monitoring")
        print_header
        check_dependencies
        create_namespace
        deploy_monitoring
        ;;
    "verify")
        print_header
        check_dependencies
        verify_deployment
        show_endpoints
        ;;
    "cleanup")
        print_header
        cleanup
        ;;
    "persistence")
        print_header
        check_dependencies
        deploy_caleon_prime
        ;;
    "help"|*)
        print_header
        echo -e "${CYAN}Usage: $0 <command>${NC}"
        echo
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "   ${GREEN}full${NC}       Complete Phase 11-A2 deployment"
        echo -e "   ${GREEN}minimal${NC}    Minimal deployment (DALS only)"
        echo -e "   ${GREEN}secrets${NC}    Setup secrets only"
        echo -e "   ${GREEN}monitoring${NC} Setup monitoring stack only"
        echo -e "   ${GREEN}persistence${NC} Deploy Caleon Prime with immortal memory"
        echo -e "   ${GREEN}verify${NC}     Verify deployment status"
        echo -e "   ${GREEN}cleanup${NC}    Remove all DALS resources"
        echo -e "   ${GREEN}help${NC}       Show this help"
        echo
        echo -e "${CYAN}Phase 11-A2 Features:${NC}"
        echo -e "   🔐 Kubernetes Secrets - Secure key management"
        echo -e "   💾 Persistent Volumes - Vault and logs storage"
        echo -e "   🧠 Immortal Memory - Caleon Prime's soul survives pod death"
        echo -e "   📊 Monitoring Stack - Prometheus + Grafana"
        echo -e "   🌐 Ingress + TLS - Secure external access"
        echo -e "   🛡️  Network Policies - Service isolation"
        echo -e "   🔄 Auto-scaling Ready - HPA configuration"
        echo
        ;;
esac