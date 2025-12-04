# DALS (Digital Asset Logistics System) Dockerfile
# Multi-stage build for production optimization with UCM integration readiness
# Updated for Phase 11-A2: Autonomous Predictive Prevention

# Build stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Install the package
RUN pip install -e .

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production \
    ISS_HOST=0.0.0.0 \
    ISS_PORT=8003 \
    # Phase 11-A2 Environment Variables
    PREDICTIVE_ENGINE_ENABLED=true \
    AUTONOMOUS_PREVENTION_MODE=11-A2 \
    PREDICTIVE_SCAN_INTERVAL=5 \
    RISK_THRESHOLD_HIGH=70 \
    RISK_THRESHOLD_CRITICAL=90 \
    SELF_MODEL_ENABLED=true \
    AWARENESS_LAYER_ACTIVE=true \
    VOICE_AWARENESS_ENABLED=true \
    CANS_AUTONOMOUS_MODE=aggressive \
    # Cali_X_One Host Bubble
    CALI_X_ONE_ENABLED=true \
    HOST_BUBBLE_ENABLED=true \
    SPEECH_RECOGNITION_ENABLED=true \
    ELEVENLABS_VOICE_ENABLED=true \
    WEBSOCKET_COMMUNICATION=true \
    # Cali Ethics Gate Integration
    CALI_ETHICS_URL=http://localhost:8006 \
    PHI3_ENDPOINT=http://localhost:8005 \
    ETHICS_THRESHOLD=0.80 \
    STREAM_TIMEOUT=30.0 \
    # Worker Vault System
    WORKER_VAULT_ENABLED=true \
    WORKER_INVENTORY_VAULT_PATH=/app/vault/worker_inventory \
    ACTIVE_WORKERS_VAULT_PATH=/app/vault/active_workers \
    WORKER_DEPLOYMENT_TRACKING=true \
    WORKER_PERFORMANCE_MONITORING=true \
    VAULT_AUTO_BACKUP_ENABLED=true \
    VAULT_BACKUP_INTERVAL_SECONDS=21600

# Install runtime dependencies (before switching to non-root user)
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r iss && useradd -r -g iss iss

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application
COPY --from=builder /app /app
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data/logs /app/data/vault /app/exports \
    /app/vault/worker_inventory /app/vault/active_workers && \
    chown -R iss:iss /app

# Switch to non-root user
USER iss

# Create supervisor configuration
RUN mkdir -p /var/log/supervisor
COPY <<EOF /etc/supervisor/conf.d/dals.conf
[supervisord]
nodaemon=true
user=root

[program:dals-api]
command=python -m iss_module.service
directory=/app
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/dals-api.log
stderr_logfile=/var/log/supervisor/dals-api-error.log

[program:dals-dashboard]
command=python dashboard_server.py
directory=/app
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/dals-dashboard.log
stderr_logfile=/var/log/supervisor/dals-dashboard-error.log
EOF

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Expose ports
EXPOSE 8003 8008

# Run both services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/dals.conf"]