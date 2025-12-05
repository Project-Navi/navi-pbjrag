#!/bin/bash
# PBJRAG Deploy Script with SLO monitoring
# Usage: ./scripts/deploy.sh [--with-backup] [--canary]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="${PROJECT_DIR}/logs/deploy-$(date +%Y%m%d-%H%M%S).log"

WITH_BACKUP=false
CANARY=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

success() {
    log "${GREEN}SUCCESS: $1${NC}"
}

warning() {
    log "${YELLOW}WARNING: $1${NC}"
}

info() {
    log "${BLUE}INFO: $1${NC}"
}

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-backup) WITH_BACKUP=true; shift ;;
        --canary) CANARY=true; shift ;;
        *) error "Unknown option: $1" ;;
    esac
done

log "=== PBJRAG DEPLOYMENT STARTED ==="

# Get current version
CURRENT_VERSION=$(cat "$PROJECT_DIR/src/pbjrag/__init__.py" | grep -oP '__version__ = "\K[^"]+' || echo "unknown")
info "Deploying version: $CURRENT_VERSION"

# Pre-deploy backup
if [ "$WITH_BACKUP" = true ]; then
    log "Creating pre-deploy backup..."
    "$SCRIPT_DIR/rollback.sh" --backup-only || warning "Backup failed, continuing..."
fi

# Pre-deploy validation
log "Running pre-deploy validation..."

# Check if docker-compose.yml exists
if [ ! -f "$PROJECT_DIR/docker-compose.yml" ]; then
    error "docker-compose.yml not found"
fi

# Check if required env vars are set
if [ ! -f "$PROJECT_DIR/.env" ]; then
    warning ".env file not found, using defaults"
fi

# Build new version
log "Building new version..."
cd "$PROJECT_DIR"
docker-compose build || error "Build failed"

success "Build completed successfully"

# Deploy
if [ "$CANARY" = true ]; then
    info "Deploying canary (10% traffic)..."
    # Canary deployment would require additional infrastructure
    # For now, we'll just deploy to a separate instance
    warning "Canary deployment not fully implemented, deploying normally"
    docker-compose up -d
else
    log "Deploying to production..."
    docker-compose up -d || error "Deployment failed"
fi

# Post-deploy health check
log "Waiting for services to stabilize..."
sleep 30

log "Running post-deploy health checks..."
MAX_RETRIES=15
RETRY_COUNT=0
HEALTH_CHECK_PASSED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    # Check WebUI health
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        success "WebUI health check passed"
        HEALTH_CHECK_PASSED=true
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    warning "Health check attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying..."
    sleep 10
done

if [ "$HEALTH_CHECK_PASSED" = false ]; then
    error "Health check failed! Initiating rollback..."
    log "Starting automatic rollback..."
    "$SCRIPT_DIR/rollback.sh"
    exit 1
fi

# Check Qdrant health
log "Checking Qdrant health..."
if docker-compose ps | grep -q qdrant; then
    if curl -sf http://localhost:6333/healthz > /dev/null 2>&1; then
        success "Qdrant health check passed"
    else
        warning "Qdrant health check failed"
    fi
fi

# Post-deploy verification
log "Running post-deploy verification..."

# Check container status
CONTAINER_STATUS=$(docker-compose ps --format json | jq -r '.State' 2>/dev/null || echo "unknown")
if [ "$CONTAINER_STATUS" != "running" ]; then
    warning "Some containers not running properly"
fi

# Log deployment completion
success "Deployment successful!"
info "Version $CURRENT_VERSION deployed at $(date)"
info "Log file: $LOG_FILE"

# Send notification
log "Sending deployment notification..."
echo "DEPLOYMENT SUCCESS: PBJRAG v$CURRENT_VERSION deployed at $(date)" \
    >> "${PROJECT_DIR}/logs/notifications.log"

# Monitoring reminder
info "==================================="
info "IMPORTANT: Monitor the following for the next hour:"
info "- Error rates (should be < 0.1%)"
info "- Response times (p99 < SLO target)"
info "- Resource usage (CPU, memory)"
info "- Application logs for errors"
info "==================================="

log "=== DEPLOYMENT COMPLETE ==="
