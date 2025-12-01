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
    # Worker Vault System
    WORKER_VAULT_ENABLED=true \
    WORKER_INVENTORY_VAULT_PATH=/app/vault/worker_inventory \
    ACTIVE_WORKERS_VAULT_PATH=/app/vault/active_workers \
    WORKER_DEPLOYMENT_TRACKING=true \
    WORKER_PERFORMANCE_MONITORING=true \
    VAULT_AUTO_BACKUP_ENABLED=true \
    VAULT_BACKUP_INTERVAL_SECONDS=21600

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
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

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${ISS_PORT}/health || exit 1

# Expose port
EXPOSE 8003

# Run the service
CMD ["python", "-m", "iss_module.service"]