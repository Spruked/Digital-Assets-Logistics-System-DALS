#!/bin/bash
# DALS Phase 11-A2 Kubernetes Secrets Management Script
# Secure secret creation and rotation for Caleon Prime

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
SECRET_PREFIX="dals"

# Functions
print_header() {
    echo -e "${PURPLE}================================================================================${NC}"
    echo -e "${PURPLE}🔐 DALS PHASE 11-A2 — KUBERNETES SECRETS MANAGEMENT${NC}"
    echo -e "${PURPLE}🔮 Caleon Prime: Secure Key Infrastructure${NC}"
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

    if ! command -v openssl &> /dev/null; then
        print_error "openssl is not installed or not in PATH"
        exit 1
    fi

    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        print_warning "Namespace $NAMESPACE does not exist. Creating..."
        kubectl create namespace $NAMESPACE
    fi

    print_success "Kubernetes environment verified"
}

generate_founder_keys() {
    print_section "KEYGEN" "Generating founder keys..."

    # Generate primary founder key
    PRIMARY_KEY=$(openssl rand -hex 32)
    BACKUP_KEY=$(openssl rand -hex 32)
    EMERGENCY_KEY=$(openssl rand -hex 32)

    echo "Founder Keys Generated:"
    echo "Primary: $PRIMARY_KEY"
    echo "Backup: $BACKUP_KEY"
    echo "Emergency: $EMERGENCY_KEY"
    echo

    # Create founder secrets
    kubectl create secret generic ${SECRET_PREFIX}-founder-secrets \
        --namespace=$NAMESPACE \
        --from-literal=founder-primary-key=$PRIMARY_KEY \
        --from-literal=founder-backup-key=$BACKUP_KEY \
        --from-literal=founder-emergency-key=$EMERGENCY_KEY \
        --dry-run=client -o yaml | kubectl apply -f -

    print_success "Founder keys created"
}

generate_caleon_keys() {
    print_section "KEYGEN" "Generating CALEON security keys..."

    # Generate CALEON keys
    MASTER_KEY=$(openssl rand -hex 32)
    DRIFT_KEY=$(openssl rand -hex 32)

    # Create CALEON secrets
    kubectl create secret generic ${SECRET_PREFIX}-caleon-secrets \
        --namespace=$NAMESPACE \
        --from-literal=caleon-master-key=$MASTER_KEY \
        --from-literal=caleon-drift-monitor-key=$DRIFT_KEY \
        --dry-run=client -o yaml | kubectl apply -f -

    print_success "CALEON security keys created"
}

generate_ucm_secrets() {
    print_section "KEYGEN" "Generating UCM integration secrets..."

    # Generate UCM tokens
    BRIDGE_TOKEN=$(openssl rand -hex 32)
    API_KEY=$(openssl rand -hex 32)

    # Create UCM secrets
    kubectl create secret generic ${SECRET_PREFIX}-ucm-secrets \
        --namespace=$NAMESPACE \
        --from-literal=ucm-bridge-token=$BRIDGE_TOKEN \
        --from-literal=ucm-api-key=$API_KEY \
        --dry-run=client -o yaml | kubectl apply -f -

    print_success "UCM integration secrets created"
}

generate_tls_certificates() {
    print_section "TLS" "Generating TLS certificates..."

    # Create temporary directory for certificates
    TMP_DIR=$(mktemp -d)
    cd $TMP_DIR

    # Generate CA private key
    openssl genrsa -out ca.key 4096

    # Generate CA certificate
    openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 \
        -subj "/C=US/ST=State/L=City/O=DALS/CN=DALS-CA" \
        -out ca.crt

    # Generate server private key
    openssl genrsa -out tls.key 2048

    # Generate certificate signing request
    openssl req -new -key tls.key \
        -subj "/C=US/ST=State/L=City/O=DALS/CN=dals-11a2.dals-system.svc.cluster.local" \
        -out tls.csr

    # Create extensions file
    cat > extensions.cnf << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = DALS
CN = dals-11a2.dals-system.svc.cluster.local

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = dals-11a2.dals-system.svc.cluster.local
DNS.2 = dals-11a2
DNS.3 = localhost
IP.1 = 127.0.0.1
EOF

    # Generate server certificate
    openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out tls.crt -days 365 -sha256 \
        -extfile extensions.cnf -extensions v3_req

    # Create TLS secret
    kubectl create secret tls ${SECRET_PREFIX}-tls-certificates \
        --namespace=$NAMESPACE \
        --cert=tls.crt \
        --key=tls.key \
        --dry-run=client -o yaml | kubectl apply -f -

    # Create CA secret
    kubectl create secret generic ${SECRET_PREFIX}-ca-certificate \
        --namespace=$NAMESPACE \
        --from-file=ca.crt \
        --dry-run=client -o yaml | kubectl apply -f -

    # Cleanup
    cd -
    rm -rf $TMP_DIR

    print_success "TLS certificates generated and stored"
}

generate_service_account_tokens() {
    print_section "SA" "Generating service account tokens..."

    # Generate tokens for each service
    PREDICTIVE_TOKEN=$(openssl rand -hex 32)
    CANS_TOKEN=$(openssl rand -hex 32)
    VOICE_TOKEN=$(openssl rand -hex 32)
    SELF_MODEL_TOKEN=$(openssl rand -hex 32)

    # Create service account secret
    kubectl create secret generic ${SECRET_PREFIX}-service-accounts \
        --namespace=$NAMESPACE \
        --from-literal=predictive-engine-sa-token=$PREDICTIVE_TOKEN \
        --from-literal=cans-system-sa-token=$CANS_TOKEN \
        --from-literal=voice-awareness-sa-token=$VOICE_TOKEN \
        --from-literal=self-model-sa-token=$SELF_MODEL_TOKEN \
        --dry-run=client -o yaml | kubectl apply -f -

    print_success "Service account tokens created"
}

rotate_secrets() {
    print_section "ROTATE" "Rotating all secrets..."

    # Backup current secrets
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    kubectl get secrets -n $NAMESPACE -l app=dals-11a2 -o yaml > secrets_backup_$TIMESTAMP.yml

    # Generate new secrets
    generate_founder_keys
    generate_caleon_keys
    generate_ucm_secrets
    generate_service_account_tokens

    print_success "Secrets rotated successfully"
    print_warning "Backup saved to: secrets_backup_$TIMESTAMP.yml"
}

show_secrets_status() {
    print_section "STATUS" "DALS Phase 11-A2 Secrets Status"

    echo -e "${CYAN}Secrets in namespace: $NAMESPACE${NC}"
    kubectl get secrets -n $NAMESPACE -l app=dals-11a2

    echo
    echo -e "${CYAN}Secret Details:${NC}"

    # Check each secret type
    for secret in founder-secrets caleon-secrets ucm-secrets tls-certificates service-accounts; do
        if kubectl get secret ${SECRET_PREFIX}-$secret -n $NAMESPACE &> /dev/null; then
            echo -e "✅ ${SECRET_PREFIX}-$secret: ${GREEN}PRESENT${NC}"
        else
            echo -e "❌ ${SECRET_PREFIX}-$secret: ${RED}MISSING${NC}"
        fi
    done
}

backup_secrets() {
    print_section "BACKUP" "Backing up all secrets..."

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="dals-secrets-backup-$TIMESTAMP.yml"

    kubectl get secrets -n $NAMESPACE -l app=dals-11a2 -o yaml > $BACKUP_FILE

    print_success "Secrets backed up to: $BACKUP_FILE"
}

restore_secrets() {
    if [ -z "$2" ]; then
        print_error "Usage: $0 restore <backup-file>"
        exit 1
    fi

    BACKUP_FILE="$2"

    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    print_section "RESTORE" "Restoring secrets from: $BACKUP_FILE"

    kubectl apply -f $BACKUP_FILE

    print_success "Secrets restored successfully"
}

# Main script logic
case "${1:-help}" in
    "init")
        print_header
        check_dependencies
        generate_founder_keys
        generate_caleon_keys
        generate_ucm_secrets
        generate_tls_certificates
        generate_service_account_tokens
        ;;
    "founder")
        print_header
        check_dependencies
        generate_founder_keys
        ;;
    "caleon")
        print_header
        check_dependencies
        generate_caleon_keys
        ;;
    "ucm")
        print_header
        check_dependencies
        generate_ucm_secrets
        ;;
    "tls")
        print_header
        check_dependencies
        generate_tls_certificates
        ;;
    "sa")
        print_header
        check_dependencies
        generate_service_account_tokens
        ;;
    "rotate")
        print_header
        check_dependencies
        rotate_secrets
        ;;
    "status")
        print_header
        check_dependencies
        show_secrets_status
        ;;
    "backup")
        print_header
        check_dependencies
        backup_secrets
        ;;
    "restore")
        print_header
        check_dependencies
        restore_secrets "$@"
        ;;
    "help"|*)
        print_header
        echo -e "${CYAN}Usage: $0 <command>${NC}"
        echo
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "   ${GREEN}init${NC}       Initialize all secrets for Phase 11-A2"
        echo -e "   ${GREEN}founder${NC}    Generate founder override keys"
        echo -e "   ${GREEN}caleon${NC}    Generate CALEON security keys"
        echo -e "   ${GREEN}ucm${NC}       Generate UCM integration secrets"
        echo -e "   ${GREEN}tls${NC}        Generate TLS certificates"
        echo -e "   ${GREEN}sa${NC}         Generate service account tokens"
        echo -e "   ${GREEN}rotate${NC}     Rotate all secrets with backup"
        echo -e "   ${GREEN}status${NC}     Show secrets status"
        echo -e "   ${GREEN}backup${NC}     Backup all secrets"
        echo -e "   ${GREEN}restore${NC}    Restore secrets from backup"
        echo -e "   ${GREEN}help${NC}       Show this help"
        echo
        echo -e "${CYAN}Phase 11-A2 Security Features:${NC}"
        echo -e "   🔐 Founder Override Keys - Emergency system control"
        echo -e "   🛡️  CALEON Security Layer - AI ethical governance"
        echo -e "   🌉 UCM Bridge Tokens - Cognitive system integration"
        echo -e "   🔒 TLS Certificates - Encrypted communications"
        echo -e "   👤 Service Accounts - Inter-service authentication"
        echo
        ;;
esac