# PBJRAG WebUI Deployment Guide

## Quick Start (5 minutes)

```bash
# 1. Clone repository
cd /home/ndspence/GitHub/navi-pbjrag

# 2. Launch entire stack
./quickstart.sh

# 3. Access WebUI
open http://localhost:8501

# 4. Access Qdrant Dashboard
open http://localhost:6333/dashboard
```

## System Requirements

### Minimum
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 10GB disk space

### Recommended
- Docker 24.0+
- Docker Compose 2.20+
- 8GB RAM
- 50GB disk space (for large codebases)

## Installation

### 1. Install Docker

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install docker.io docker-compose-plugin
sudo systemctl start docker
sudo usermod -aG docker $USER
```

**macOS**:
```bash
brew install docker docker-compose
```

**Arch Linux**:
```bash
sudo pacman -S docker docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### 2. Verify Installation

```bash
docker --version
docker-compose --version
docker info
```

## Service Architecture

### Container Stack

```yaml
services:
  qdrant:
    - Vector database
    - Ports: 6333 (HTTP), 6334 (gRPC)
    - Volume: qdrant_storage (persistent)

  webui:
    - Streamlit application
    - Port: 8501
    - Volumes: webui/, src/, examples/
    - Depends on: qdrant
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Embedding Configuration
INFINITY_URL=http://127.0.0.1:7997
EMBEDDING_MODEL=jinaai/jina-embeddings-v2-base-code

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Custom docker-compose Configuration

**Production**:
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  qdrant:
    extends:
      file: docker-compose.yml
      service: qdrant
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G

  webui:
    extends:
      file: docker-compose.yml
      service: webui
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Operations

### Starting Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d qdrant

# Start with rebuild
docker-compose up -d --build

# Start in foreground (see logs)
docker-compose up
```

### Stopping Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f webui

# Last 100 lines
docker-compose logs --tail=100 webui

# Since timestamp
docker-compose logs --since 2024-12-05T10:00:00 qdrant
```

### Restarting Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart webui

# Restart with rebuild
docker-compose up -d --build --force-recreate webui
```

### Service Status

```bash
# Check status
docker-compose ps

# Health check
curl http://localhost:6333/healthz  # Qdrant
curl http://localhost:8501/_stcore/health  # Streamlit

# Inspect service
docker-compose inspect qdrant
```

## Data Management

### Backup Qdrant Data

```bash
# Stop Qdrant
docker-compose stop qdrant

# Backup volume
docker run --rm \
  -v navi-pbjrag_qdrant_storage:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/qdrant-backup-$(date +%Y%m%d).tar.gz /data

# Restart Qdrant
docker-compose start qdrant
```

### Restore Qdrant Data

```bash
# Stop Qdrant
docker-compose stop qdrant

# Restore volume
docker run --rm \
  -v navi-pbjrag_qdrant_storage:/data \
  -v $(pwd)/backups:/backup \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/qdrant-backup-20241205.tar.gz -C /"

# Restart Qdrant
docker-compose start qdrant
```

### Clear All Data

```bash
# WARNING: Deletes all vector data!
docker-compose down -v
docker volume rm navi-pbjrag_qdrant_storage
docker volume rm navi-pbjrag_uploaded_codebases
```

## Monitoring

### Resource Usage

```bash
# Container stats
docker stats

# Specific service
docker stats navi-pbjrag-webui navi-pbjrag-qdrant

# Disk usage
docker system df
docker volume ls
```

### Health Monitoring

```bash
# Check health status
docker-compose ps

# Manual health checks
curl -f http://localhost:6333/healthz || echo "Qdrant unhealthy"
curl -f http://localhost:8501/_stcore/health || echo "WebUI unhealthy"
```

### Log Aggregation

**Using ELK Stack**:
```yaml
# Add to docker-compose.yml
services:
  webui:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=webui"
```

**Using Loki**:
```yaml
services:
  webui:
    logging:
      driver: loki
      options:
        loki-url: "http://localhost:3100/loki/api/v1/push"
```

## Scaling

### Horizontal Scaling (WebUI)

```yaml
# docker-compose.scale.yml
services:
  webui:
    deploy:
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - webui
```

**nginx.conf**:
```nginx
upstream webui {
    server webui:8501;
}

server {
    listen 80;

    location / {
        proxy_pass http://webui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Vertical Scaling (Resources)

```yaml
services:
  qdrant:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 16G
        reservations:
          cpus: '4'
          memory: 8G
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501
# or
netstat -tuln | grep 8501

# Kill process
kill -9 <PID>

# Change port in docker-compose.yml
ports:
  - "8502:8501"
```

#### 2. Qdrant Won't Start

```bash
# Check logs
docker-compose logs qdrant

# Verify volume permissions
docker volume inspect navi-pbjrag_qdrant_storage

# Reset Qdrant
docker-compose stop qdrant
docker volume rm navi-pbjrag_qdrant_storage
docker-compose up -d qdrant
```

#### 3. WebUI Connection Error

```bash
# Check if Qdrant is healthy
docker-compose exec webui curl -f http://qdrant:6333/healthz

# Restart WebUI
docker-compose restart webui

# Check network
docker network inspect navi-pbjrag_pbjrag-network
```

#### 4. Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Memory: 8GB

# Add swap to containers
docker-compose.yml:
  services:
    qdrant:
      mem_swappiness: 60
```

#### 5. Slow Performance

```bash
# Check Qdrant indexing status
curl http://localhost:6333/collections/crown_jewel_dsc

# Optimize Qdrant
curl -X POST http://localhost:6333/collections/crown_jewel_dsc/optimize

# Reduce batch size in webui/app.py
batch_size = 50  # down from 100
```

### Debug Mode

**Enable verbose logging**:
```yaml
services:
  webui:
    environment:
      - STREAMLIT_LOGGER_LEVEL=debug
      - PYTHONUNBUFFERED=1

  qdrant:
    environment:
      - QDRANT__LOG_LEVEL=DEBUG
```

**Interactive debugging**:
```bash
# Exec into container
docker-compose exec webui bash

# Python shell
python3
>>> from pbjrag.dsc.analyzer import DSCAnalyzer
>>> analyzer = DSCAnalyzer()
```

## Security

### Production Hardening

1. **Use secrets for credentials**:
```yaml
services:
  webui:
    secrets:
      - qdrant_api_key
    environment:
      - QDRANT_API_KEY=/run/secrets/qdrant_api_key

secrets:
  qdrant_api_key:
    file: ./secrets/qdrant_api_key.txt
```

2. **Enable TLS**:
```yaml
services:
  nginx:
    volumes:
      - ./certs:/etc/nginx/certs
    ports:
      - "443:443"
```

3. **Network isolation**:
```yaml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

services:
  webui:
    networks:
      - frontend
      - backend

  qdrant:
    networks:
      - backend
```

4. **Run as non-root**:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 8501/tcp  # WebUI
sudo ufw allow 443/tcp   # HTTPS (if using nginx)
sudo ufw deny 6333/tcp   # Block external Qdrant access
```

## Maintenance

### Regular Tasks

**Daily**:
- Check logs for errors
- Monitor disk usage
- Verify health checks

**Weekly**:
- Backup Qdrant volume
- Review resource usage
- Update Docker images

**Monthly**:
- Clean unused images/volumes
- Review security updates
- Test disaster recovery

### Automated Maintenance

**Cron job for backups**:
```bash
# /etc/cron.daily/qdrant-backup
#!/bin/bash
cd /home/ndspence/GitHub/navi-pbjrag
docker-compose stop qdrant
docker run --rm \
  -v navi-pbjrag_qdrant_storage:/data \
  -v /backups/qdrant:/backup \
  alpine tar czf /backup/qdrant-$(date +%Y%m%d).tar.gz /data
docker-compose start qdrant

# Keep only last 7 backups
find /backups/qdrant -name "qdrant-*.tar.gz" -mtime +7 -delete
```

### Update Procedure

```bash
# 1. Backup data
./scripts/backup-qdrant.sh

# 2. Pull latest images
docker-compose pull

# 3. Stop services
docker-compose down

# 4. Update code
git pull origin main

# 5. Start services
docker-compose up -d

# 6. Verify health
docker-compose ps
curl http://localhost:8501/_stcore/health
```

## Performance Tuning

### Qdrant Optimization

```bash
# Increase indexing threshold
curl -X PATCH http://localhost:6333/collections/crown_jewel_dsc \
  -H 'Content-Type: application/json' \
  -d '{
    "optimizers_config": {
      "indexing_threshold": 50000,
      "memmap_threshold": 100000
    }
  }'

# Create snapshot for faster recovery
curl -X POST http://localhost:6333/collections/crown_jewel_dsc/snapshots
```

### Streamlit Optimization

```yaml
services:
  webui:
    environment:
      - STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500
      - STREAMLIT_SERVER_ENABLE_CORS=false
      - STREAMLIT_BROWSER_SERVER_ADDRESS=localhost
```

## Disaster Recovery

### Backup Strategy

**What to backup**:
- Qdrant volume (vector data)
- Uploaded codebases (if persistent)
- Configuration files (.env, docker-compose.yml)

**Backup script** (`scripts/backup-all.sh`):
```bash
#!/bin/bash
BACKUP_DIR=/backups/navi-pbjrag-$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Backup Qdrant
docker-compose stop qdrant
docker run --rm \
  -v navi-pbjrag_qdrant_storage:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/qdrant.tar.gz /data
docker-compose start qdrant

# Backup config
cp docker-compose.yml .env $BACKUP_DIR/

# Backup uploads
docker run --rm \
  -v navi-pbjrag_uploaded_codebases:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/uploads.tar.gz /data

echo "Backup complete: $BACKUP_DIR"
```

### Recovery Procedure

```bash
# 1. Stop all services
docker-compose down -v

# 2. Restore Qdrant
docker volume create navi-pbjrag_qdrant_storage
docker run --rm \
  -v navi-pbjrag_qdrant_storage:/data \
  -v /backups/navi-pbjrag-20241205:/backup \
  alpine tar xzf /backup/qdrant.tar.gz -C /

# 3. Restore uploads
docker volume create navi-pbjrag_uploaded_codebases
docker run --rm \
  -v navi-pbjrag_uploaded_codebases:/data \
  -v /backups/navi-pbjrag-20241205:/backup \
  alpine tar xzf /backup/uploads.tar.gz -C /

# 4. Start services
docker-compose up -d

# 5. Verify
curl http://localhost:6333/collections/crown_jewel_dsc
```

---

**Last Updated**: 2025-12-05
**Guide Version**: 1.0.0
**Tested On**: Docker 24.0.7, Docker Compose 2.23.0
