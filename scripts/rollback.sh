#!/bin/bash
# PBJRAG Rollback Script
# Usage: ./scripts/rollback.sh [version]
#        ./scripts/rollback.sh --backup-only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"
LOG_FILE="${PROJECT_DIR}/logs/rollback-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Check for backup-only mode
BACKUP_ONLY=false
if [ "${1:-}" = "--backup-only" ]; then
    BACKUP_ONLY=true
    log "=== BACKUP-ONLY MODE ==="
fi

if [ "$BACKUP_ONLY" = false ]; then
    log "=== PBJRAG ROLLBACK INITIATED ==="
fi

# Get target version (previous or specified)
if [ "$BACKUP_ONLY" = false ]; then
    TARGET_VERSION="${1:-}"
    if [ -z "$TARGET_VERSION" ]; then
        # Find previous version from git tags
        TARGET_VERSION=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
        if [ -z "$TARGET_VERSION" ]; then
            error "Could not determine previous version. Please specify version."
        fi
    fi
    log "Rolling back to version: $TARGET_VERSION"
fi

# Step 1: Stop current services (skip in backup-only mode)
if [ "$BACKUP_ONLY" = false ]; then
    log "Stopping current services..."
    docker-compose down || warning "docker-compose down failed, continuing..."
fi

# Step 2: Backup current state
log "Creating backup of current state..."
BACKUP_NAME="pre-rollback-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup volumes
if docker volume ls | grep -q qdrant_storage; then
    log "Backing up Qdrant data..."
    docker run --rm -v qdrant_storage:/data -v "$BACKUP_DIR/$BACKUP_NAME":/backup \
        alpine tar czf /backup/qdrant-data.tar.gz -C /data . || warning "Qdrant backup failed"
fi

if docker volume ls | grep -q uploaded_codebases; then
    log "Backing up uploaded data..."
    docker run --rm -v uploaded_codebases:/data -v "$BACKUP_DIR/$BACKUP_NAME":/backup \
        alpine tar czf /backup/uploads.tar.gz -C /data . || warning "Uploads backup failed"
fi

# Backup current git state
log "Recording current git state..."
git rev-parse HEAD > "$BACKUP_DIR/$BACKUP_NAME/git-commit.txt" 2>/dev/null || true
git describe --tags --exact-match HEAD > "$BACKUP_DIR/$BACKUP_NAME/git-tag.txt" 2>/dev/null || true

success "Backup completed at: $BACKUP_DIR/$BACKUP_NAME"

if [ "$BACKUP_ONLY" = true ]; then
    log "=== BACKUP COMPLETE ==="
    exit 0
fi

# Step 3: Pull target version
log "Pulling target version: $TARGET_VERSION..."
git fetch --tags
git checkout "$TARGET_VERSION" || error "Failed to checkout $TARGET_VERSION"

# Step 4: Rebuild and start
log "Rebuilding containers..."
docker-compose build --no-cache || error "Build failed"

log "Starting services..."
docker-compose up -d || error "Failed to start services"

# Step 5: Health check
log "Waiting for services to start..."
sleep 30

log "Running health checks..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        success "WebUI health check passed"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    log "Health check attempt $RETRY_COUNT/$MAX_RETRIES failed, retrying..."
    sleep 10
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    error "Health checks failed after $MAX_RETRIES attempts"
fi

# Check Qdrant if running
if docker-compose ps | grep -q qdrant; then
    if curl -sf http://localhost:6333/healthz > /dev/null 2>&1; then
        success "Qdrant health check passed"
    else
        warning "Qdrant health check failed"
    fi
fi

# Step 6: Log completion
success "Rollback to $TARGET_VERSION completed successfully"
log "Backup stored at: $BACKUP_DIR/$BACKUP_NAME"
log "Log file: $LOG_FILE"

# Step 7: Send notification (placeholder)
log "Sending notification..."
echo "ROLLBACK ALERT: PBJRAG rolled back to $TARGET_VERSION at $(date)" \
    >> "${PROJECT_DIR}/logs/notifications.log"

log "=== ROLLBACK COMPLETE ==="
