#!/bin/bash
# DALS IONOS Domain Setup Script
# Configures domain routing for DALS alongside existing website

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Update these with your actual values
DOMAIN_NAME="your-domain.com"
IONOS_SERVER_IP="YOUR_IONOS_SERVER_IP"
EXISTING_WEBSITE_PATH="/path/to/shioh-ridge-katahdins"

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

check_domain_config() {
    log_info "Checking domain configuration requirements..."

    # Check if domain is configured
    if [[ "$DOMAIN_NAME" == "your-domain.com" ]]; then
        log_error "Please update DOMAIN_NAME in this script with your actual domain"
        exit 1
    fi

    if [[ "$IONOS_SERVER_IP" == "YOUR_IONOS_SERVER_IP" ]]; then
        log_error "Please update IONOS_SERVER_IP in this script with your server IP"
        exit 1
    fi

    log_success "Domain configuration validated"
}

update_nginx_domain_config() {
    log_info "Updating Nginx configuration for domain routing..."

    # Update the IONOS nginx configuration with actual domain
    NGINX_CONFIG="nginx/conf.d/dals.ionos.conf"

    if [[ ! -f "$NGINX_CONFIG" ]]; then
        log_error "Nginx configuration file not found: $NGINX_CONFIG"
        exit 1
    fi

    # Replace placeholder domain with actual domain
    sed -i "s/your-ionos-domain\.com/$DOMAIN_NAME/g" "$NGINX_CONFIG"

    log_success "Nginx configuration updated for domain: $DOMAIN_NAME"
}

setup_ssl_certificates() {
    log_info "Setting up SSL certificates for domain..."

    # Create directory for SSL certificates
    mkdir -p ssl

    # Check if certbot is available for Let's Encrypt
    if command -v certbot &> /dev/null; then
        log_info "Certbot found. Setting up Let's Encrypt certificates..."

        # Stop nginx temporarily for certificate generation
        docker-compose -f docker-compose.ionos.yml exec nginx nginx -s stop || true

        # Generate certificate
        certbot certonly --standalone -d "$DOMAIN_NAME" --email "admin@$DOMAIN_NAME" --agree-tos --non-interactive

        # Copy certificates to ssl directory
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" ssl/dals.crt
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem" ssl/dals.key

        # Restart nginx
        docker-compose -f docker-compose.ionos.yml exec nginx nginx

        log_success "Let's Encrypt SSL certificates configured"
    else
        log_warning "Certbot not found. Using self-signed certificates."
        log_warning "Consider installing certbot and running: certbot certonly --standalone -d $DOMAIN_NAME"

        # Generate self-signed certificate
        openssl req -x509 -newkey rsa:4096 -keyout ssl/dals.key -out ssl/dals.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=DALS/CN=$DOMAIN_NAME"

        log_warning "Self-signed certificate generated. Browser will show security warning."
    fi

    # Set proper permissions
    chmod 600 ssl/dals.key
    chmod 644 ssl/dals.crt
}

create_dns_instructions() {
    log_info "Creating DNS configuration instructions..."

    cat > dns-setup-instructions.md << EOF
# DALS IONOS DNS Setup Instructions

## Required DNS Records

Add the following DNS records in your IONOS DNS management panel:

### A Records
- **Type:** A
- **Host:** @
- **Value:** $IONOS_SERVER_IP
- **TTL:** 3600

- **Type:** A
- **Host:** www
- **Value:** $IONOS_SERVER_IP
- **TTL:** 3600

### CNAME Records (Optional)
- **Type:** CNAME
- **Host:** dals
- **Value:** $DOMAIN_NAME
- **TTL:** 3600

## Domain Routing

The Nginx reverse proxy is configured to route traffic as follows:

- **Main Website (Shioh Ridge Katahdins):** http://$DOMAIN_NAME/
- **DALS Login:** http://$DOMAIN_NAME/login
- **DALS Dashboard:** http://$DOMAIN_NAME/dashboard/
- **DALS API:** http://$DOMAIN_NAME/api/
- **UCM Engine:** http://$DOMAIN_NAME/ucm/
- **Ollama API:** http://$DOMAIN_NAME/ollama/

## SSL Configuration

SSL certificates are configured for HTTPS access. If using Let's Encrypt:

1. Ensure port 80 is accessible for certificate validation
2. Run certbot certificate renewal monthly:
   \`\`\`bash
   certbot renew
   docker-compose -f docker-compose.ionos.yml restart nginx
   \`\`\`

## Testing

After DNS propagation (may take 24-48 hours):

1. Test main website: https://$DOMAIN_NAME/
2. Test DALS login: https://$DOMAIN_NAME/login
3. Test DALS dashboard: https://$DOMAIN_NAME/dashboard/
4. Test API health: https://$DOMAIN_NAME/api/health

## Troubleshooting

- **DNS not resolving:** Wait for propagation or check DNS records
- **SSL errors:** Check certificate validity and nginx configuration
- **Service unavailable:** Check docker-compose logs and service health
- **Voice not working:** Verify Ollama service and UCM integration

EOF

    log_success "DNS setup instructions created: dns-setup-instructions.md"
}

setup_domain_monitoring() {
    log_info "Setting up domain monitoring..."

    # Create domain monitoring script
    cat > monitor-domain.sh << EOF
#!/bin/bash
# DALS Domain Monitoring Script

DOMAIN="$DOMAIN_NAME"
IP="$IONOS_SERVER_IP"

echo "=== DALS Domain Monitoring ==="
echo "Domain: \$DOMAIN"
echo "Server IP: \$IP"
echo "Timestamp: \$(date)"
echo

echo "=== DNS Resolution ==="
echo "Domain resolves to: \$(dig +short \$DOMAIN)"
echo "Expected IP: \$IP"
echo

echo "=== SSL Certificate ==="
echo "Certificate expiry:"
openssl s_client -connect \$DOMAIN:443 -servername \$DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -dates || echo "SSL check failed"
echo

echo "=== Service Availability ==="
echo "HTTPS access: \$(curl -s -o /dev/null -w "%{http_code}" https://\$DOMAIN/ || echo "Failed")"
echo "DALS API: \$(curl -s -o /dev/null -w "%{http_code}" https://\$DOMAIN/api/health || echo "Failed")"
echo "DALS Dashboard: \$(curl -s -o /dev/null -w "%{http_code}" https://\$DOMAIN/dashboard/ || echo "Failed")"
echo

echo "=== Performance ==="
echo "Response time: \$(curl -s -o /dev/null -w "%{time_total}" https://\$DOMAIN/) seconds"
EOF

    chmod +x monitor-domain.sh
    log_success "Domain monitoring script created: monitor-domain.sh"
}

create_backup_script() {
    log_info "Creating backup and maintenance scripts..."

    # Create backup script
    cat > backup-dals.sh << EOF
#!/bin/bash
# DALS IONOS Backup Script

BACKUP_DIR="./backups/\$(date +%Y%m%d_%H%M%S)"
mkdir -p "\$BACKUP_DIR"

echo "Creating backup in \$BACKUP_DIR..."

# Backup Docker volumes
docker run --rm -v dals-ionos_dals-data:/data -v "\$(pwd)/\$BACKUP_DIR:/backup" alpine tar czf /backup/dals-data.tar.gz -C / data

# Backup configurations
cp docker-compose.ionos.yml "\$BACKUP_DIR/"
cp nginx/conf.d/dals.ionos.conf "\$BACKUP_DIR/"
cp .env "\$BACKUP_DIR/"

# Backup SSL certificates
cp -r ssl "\$BACKUP_DIR/"

echo "Backup completed: \$BACKUP_DIR"
EOF

    # Create maintenance script
    cat > maintain-dals.sh << EOF
#!/bin/bash
# DALS IONOS Maintenance Script

echo "=== DALS Maintenance Tasks ==="

# Update Docker images
echo "Updating Docker images..."
docker-compose -f docker-compose.ionos.yml pull

# Restart services
echo "Restarting services..."
docker-compose -f docker-compose.ionos.yml restart

# Clean up old images
echo "Cleaning up Docker..."
docker image prune -f
docker volume prune -f

# Check SSL certificate expiry
echo "Checking SSL certificate..."
openssl x509 -in ssl/dals.crt -noout -dates

echo "Maintenance completed"
EOF

    chmod +x backup-dals.sh maintain-dals.sh
    log_success "Backup and maintenance scripts created"
}

print_domain_setup_info() {
    log_success "DALS IONOS Domain Setup Complete!"
    echo
    echo "=== Domain Configuration Summary ==="
    echo "🌐 Domain: $DOMAIN_NAME"
    echo "🏠 Server IP: $IONOS_SERVER_IP"
    echo "🔒 SSL: Configured (Let's Encrypt recommended)"
    echo
    echo "=== Traffic Routing ==="
    echo "Main Website → Shioh Ridge Katahdins"
    echo "DALS Services → /login, /dashboard, /api, /ucm, /ollama"
    echo
    echo "=== Next Steps ==="
    echo "1. Update DNS records as per dns-setup-instructions.md"
    echo "2. Wait for DNS propagation (24-48 hours)"
    echo "3. Test all endpoints with monitor-domain.sh"
    echo "4. Set up automated backups with backup-dals.sh"
    echo "5. Schedule maintenance with maintain-dals.sh"
    echo
    echo "=== Important Files ==="
    echo "📋 DNS Instructions: dns-setup-instructions.md"
    echo "🔍 Domain Monitor: monitor-domain.sh"
    echo "💾 Backup Script: backup-dals.sh"
    echo "🔧 Maintenance: maintain-dals.sh"
}

# Main domain setup flow
main() {
    echo "🌐 DALS IONOS Domain Setup Script"
    echo "=================================="
    echo

    check_domain_config
    update_nginx_domain_config
    setup_ssl_certificates
    create_dns_instructions
    setup_domain_monitoring
    create_backup_script
    print_domain_setup_info

    log_success "DALS IONOS domain setup completed successfully!"
}

# Run main function
main "$@"