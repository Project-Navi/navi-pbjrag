# PBJRAG Release Checklist

## Pre-Release Verification

### Code Quality
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Linting clean: `ruff check src/`
- [ ] Type checking: `mypy src/pbjrag`
- [ ] Coverage >= 80%: `pytest --cov=pbjrag --cov-fail-under=80`

### Security
- [ ] Dependencies updated: `pip-compile --upgrade`
- [ ] No critical vulnerabilities: `trivy fs . --severity HIGH,CRITICAL`
- [ ] Secrets scan clean: `git secrets --scan`
- [ ] SBOM generated and reviewed

### Performance
- [ ] Performance tests pass: `pytest -m performance`
- [ ] SLO targets verified in staging
- [ ] Memory usage profiled
- [ ] No regression from previous release

### Documentation
- [ ] CHANGELOG.md updated
- [ ] README.md accurate
- [ ] API docs current
- [ ] Migration guide (if breaking changes)

## Release Process

### 1. Create Release Branch
```bash
git checkout -b release/v$(cat VERSION)
```

### 2. Update Version
```bash
# Update version in:
# - pyproject.toml
# - src/pbjrag/__init__.py
# - CHANGELOG.md
```

### 3. Build and Test Docker Image
```bash
docker build -t pbjrag:v$(cat VERSION) .
docker run --rm pbjrag:v$(cat VERSION) pytest tests/
```

### 4. Deploy to Staging
```bash
docker-compose -f docker-compose.staging.yml up -d
# Verify health checks
curl http://staging:8501/_stcore/health
```

### 5. Staging Validation (30 min minimum)
- [ ] Health endpoints responding
- [ ] Error rate < 0.1%
- [ ] Latency p99 < SLO target
- [ ] Manual smoke test of key features

### 6. Production Deployment
```bash
# Tag release
git tag -a v$(cat VERSION) -m "Release v$(cat VERSION)"

# Deploy with rollback ready
./scripts/deploy.sh --with-backup
```

### 7. Post-Deployment Monitoring
- [ ] Monitor for 1 hour
- [ ] Verify SLO compliance
- [ ] Check error logs
- [ ] Confirm metrics collection

## Rollback Criteria

**Automatic Rollback Triggers:**
- Error rate > 1% for 5 consecutive minutes
- p99 latency > 10000ms for 5 consecutive minutes
- Health check failures > 3 in 10 minutes
- Memory usage > 90% for 10 minutes

**Manual Rollback Decision:**
- User-reported critical issues
- Data corruption detected
- Security vulnerability discovered

## Rollback Procedure

1. Run rollback script: `./scripts/rollback.sh`
2. Verify previous version running
3. Notify stakeholders
4. Create incident report
