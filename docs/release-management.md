# Release Management

This document describes the release process and rollback procedures for PBJRAG.

## Quick Reference

```bash
# Deploy with backup
./scripts/deploy.sh --with-backup

# Rollback to previous version
./scripts/rollback.sh

# Rollback to specific version
./scripts/rollback.sh v2.9.0

# Create backup only
./scripts/rollback.sh --backup-only
```

## Files

- **RELEASE_CHECKLIST.md**: Complete pre-release verification checklist
- **scripts/deploy.sh**: Deployment automation with health checks
- **scripts/rollback.sh**: Rollback automation with backup creation

## Release Process

### 1. Pre-Release Verification

Follow the complete checklist in `RELEASE_CHECKLIST.md`:
- Code quality (tests, linting, type checking)
- Security scanning
- Performance validation
- Documentation updates

### 2. Deployment

```bash
# Deploy with automatic backup
./scripts/deploy.sh --with-backup

# Canary deployment (10% traffic)
./scripts/deploy.sh --canary
```

The deploy script will:
- Create pre-deploy backup (if `--with-backup`)
- Build new Docker images
- Deploy containers
- Run health checks
- Auto-rollback on failure

### 3. Post-Deployment Monitoring

Monitor for 1 hour after deployment:
- Error rates (target: < 0.1%)
- Response times (p99 < SLO target)
- Resource usage
- Application logs

### 4. Rollback (if needed)

If issues are detected:

```bash
# Rollback to previous version
./scripts/rollback.sh

# Rollback to specific version
./scripts/rollback.sh v2.9.0
```

The rollback script will:
- Stop current services
- Create backup of current state
- Checkout target version
- Rebuild and restart
- Verify health checks

## Rollback Criteria

### Automatic Rollback Triggers

The deployment script will automatically rollback if:
- Health checks fail after deployment
- Service fails to start properly

### Manual Rollback Triggers

Consider manual rollback if:
- Error rate > 1% for 5+ minutes
- p99 latency > 10000ms for 5+ minutes
- Health check failures > 3 in 10 minutes
- Memory usage > 90% for 10+ minutes
- User-reported critical issues
- Data corruption detected
- Security vulnerability discovered

## Backup and Recovery

### Backup Location

Backups are stored in `backups/` directory:
- Qdrant vector data
- Uploaded codebase files
- Git commit information
- Configuration state

### Backup Naming

```
backups/
└── pre-rollback-YYYYMMDD-HHMMSS/
    ├── qdrant-data.tar.gz
    ├── uploads.tar.gz
    ├── git-commit.txt
    └── git-tag.txt
```

### Manual Restore

To manually restore from backup:

```bash
# List backups
ls -la backups/

# Restore Qdrant data
docker run --rm \
  -v qdrant_storage:/data \
  -v $(pwd)/backups/pre-rollback-YYYYMMDD-HHMMSS:/backup \
  alpine tar xzf /backup/qdrant-data.tar.gz -C /data

# Restore uploads
docker run --rm \
  -v uploaded_codebases:/data \
  -v $(pwd)/backups/pre-rollback-YYYYMMDD-HHMMSS:/backup \
  alpine tar xzf /backup/uploads.tar.gz -C /data
```

## Logs

All deployment and rollback operations are logged:
- `logs/deploy-YYYYMMDD-HHMMSS.log`
- `logs/rollback-YYYYMMDD-HHMMSS.log`
- `logs/notifications.log`

## Integration with CI/CD

### GitHub Actions Integration

Add to `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy with backup
        run: ./scripts/deploy.sh --with-backup

      - name: Monitor deployment
        run: |
          # Wait and check health
          sleep 60
          curl -f http://production:8501/_stcore/health
```

### Rollback Workflow

Add to `.github/workflows/rollback.yml`:

```yaml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: false

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Execute rollback
        run: |
          if [ -n "${{ github.event.inputs.version }}" ]; then
            ./scripts/rollback.sh ${{ github.event.inputs.version }}
          else
            ./scripts/rollback.sh
          fi
```

## Testing

### Test Deployment Script

```bash
# Dry-run (check syntax)
bash -n scripts/deploy.sh

# Test in development
docker-compose -f docker-compose.dev.yml up -d
./scripts/deploy.sh
```

### Test Rollback Script

```bash
# Backup-only mode
./scripts/rollback.sh --backup-only

# Test full rollback in dev
git tag v2.9.0-test
git checkout -b test-rollback
./scripts/rollback.sh v2.9.0-test
```

## Troubleshooting

### Deployment Fails

1. Check logs: `logs/deploy-*.log`
2. Verify Docker status: `docker-compose ps`
3. Check container logs: `docker-compose logs -f`
4. Run manual health check: `curl -v http://localhost:8501/_stcore/health`

### Rollback Fails

1. Check logs: `logs/rollback-*.log`
2. Verify git state: `git status`
3. Check available versions: `git tag -l`
4. Manual recovery:
   ```bash
   docker-compose down
   git checkout <version>
   docker-compose build
   docker-compose up -d
   ```

### Backup Issues

1. Check Docker volumes: `docker volume ls`
2. Verify backup directory: `ls -la backups/`
3. Manual backup:
   ```bash
   docker run --rm \
     -v qdrant_storage:/data \
     -v $(pwd)/backups/manual:/backup \
     alpine tar czf /backup/qdrant-$(date +%Y%m%d).tar.gz -C /data .
   ```

## Best Practices

1. **Always backup before deployment**: Use `--with-backup` flag
2. **Monitor after deployment**: Watch metrics for 1 hour minimum
3. **Test in staging first**: Validate in non-production environment
4. **Keep backup retention**: Maintain last 7 days of backups
5. **Document issues**: Create incident reports for rollbacks
6. **Review logs regularly**: Check deployment and rollback logs
7. **Automate notifications**: Integrate with Slack/email alerts

## Security Considerations

1. **Backup storage**: Secure backup directory with proper permissions
2. **Log sanitization**: Ensure logs don't contain sensitive data
3. **Script permissions**: Keep scripts executable only by authorized users
4. **Secrets management**: Never commit secrets to version control
5. **Access control**: Restrict deployment permissions

## Version History

- v3.0.0 (2024): Initial release management documentation
