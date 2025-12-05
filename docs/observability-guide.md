# PBJRAG Observability Guide

## Overview

This guide covers the observability infrastructure added to PBJRAG, including SLO definitions, structured logging, Prometheus metrics, and health checks.

## Components

### 1. SLO Declarations (`slo.yaml`)

Service Level Objectives define the performance and reliability targets for PBJRAG:

- **Analysis Latency**: P99 latency < 5000ms
- **Search Latency**: P95 latency < 500ms
- **Availability**: 99.9% uptime (43.2 min downtime/month)
- **Throughput**: Minimum 10 requests/second

#### Automatic Rollback Triggers

The SLO configuration defines conditions that trigger automatic rollbacks:

```yaml
rollback_triggers:
  - condition: "error_rate > 1% for 5 minutes"
    action: "automatic_rollback"
  - condition: "p99_latency > 10000ms for 5 minutes"
    action: "automatic_rollback"
  - condition: "health_check_failures > 3 in 10 minutes"
    action: "alert_and_manual_review"
```

### 2. Observability Module (`src/pbjrag/observability.py`)

Provides structured logging, metrics, and health checks.

#### Structured Logging

JSON-formatted logs with trace IDs for request correlation:

```python
from pbjrag.observability import logger, trace_operation

# Context manager for automatic tracing
with trace_operation("analyze_file") as trace_id:
    result = analyzer.analyze_file(file_path)
    # Logs include trace_id, duration, status

# Manual logging
logger.info("Processing started", file=file_path, size=file_size)
logger.error("Analysis failed", error=str(e), trace_id=trace_id)
```

Example log output:
```json
{
  "timestamp": "2024-12-05T02:30:45+0000",
  "level": "INFO",
  "message": "Completed analyze_file",
  "service": "pbjrag",
  "trace_id": "a3b5c7d9",
  "operation": "analyze_file",
  "duration_ms": 234.56,
  "status": "success"
}
```

#### Prometheus Metrics

Optional Prometheus metrics for monitoring (requires `prometheus-client`):

```python
from pbjrag.observability import traced, record_blessing_tier

# Decorator for automatic metrics
@traced("custom_operation")
def process_data(data):
    # Automatically records:
    # - Request count (success/error)
    # - Duration histogram
    # - Active request gauge
    return result

# Record custom metrics
record_blessing_tier("platinum")
```

Available metrics:
- `pbjrag_requests_total{operation, status}` - Counter
- `pbjrag_request_duration_seconds{operation}` - Histogram
- `pbjrag_errors_total{operation, error_type}` - Counter
- `pbjrag_active_requests{operation}` - Gauge
- `pbjrag_blessing_tiers_total{tier}` - Counter

#### Health Checks

Built-in health check endpoint:

```python
from pbjrag.observability import health_check

status = health_check()
# Returns:
# {
#   "status": "healthy",
#   "timestamp": "2024-12-05T02:30:45+0000",
#   "checks": {
#     "core_imports": "ok",
#     "vector_store": "available"
#   }
# }
```

### 3. Performance SLO Tests (`tests/test_performance_slo.py`)

Automated tests that enforce SLO compliance:

```bash
# Run performance tests
pytest tests/test_performance_slo.py -m performance

# Run only performance tests, skip others
pytest -m "performance" -v
```

Test coverage:
- **Chunking Latency**: P99 < 100ms
- **Analysis Latency**: P99 < 5000ms
- **Availability**: 99.9% initialization success rate

## Integration Examples

### Basic Usage with Tracing

```python
from pbjrag import DSCAnalyzer
from pbjrag.observability import trace_operation, logger

analyzer = DSCAnalyzer()

# Trace entire operation
with trace_operation("batch_analysis") as trace_id:
    logger.info("Starting batch analysis", batch_size=100)

    for file_path in files:
        with trace_operation("analyze_file", trace_id=trace_id):
            result = analyzer.analyze_file(file_path)

    logger.info("Batch analysis complete", files_processed=len(files))
```

### Exposing Metrics Endpoint

```python
from flask import Flask, Response
from pbjrag.observability import get_metrics

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return Response(get_metrics(), mimetype='text/plain')

@app.route('/health')
def health():
    from pbjrag.observability import health_check
    return health_check()
```

### Custom Operation Tracing

```python
from pbjrag.observability import traced

class CustomAnalyzer:
    @traced("custom_analysis")
    def analyze(self, code: str):
        # Automatically tracked and timed
        result = self._perform_analysis(code)
        return result
```

## Monitoring Setup

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pbjrag'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboard

Example queries for visualization:

```promql
# Request rate by operation
rate(pbjrag_requests_total[5m])

# P99 latency
histogram_quantile(0.99, pbjrag_request_duration_seconds_bucket)

# Error rate
rate(pbjrag_errors_total[5m]) / rate(pbjrag_requests_total[5m])

# Active requests
pbjrag_active_requests

# Blessing tier distribution
rate(pbjrag_blessing_tiers_total[1h])
```

### Alert Rules

Example Prometheus alert rules:

```yaml
groups:
  - name: pbjrag_slo
    rules:
      - alert: HighErrorRate
        expr: rate(pbjrag_errors_total[5m]) > 0.01
        for: 5m
        annotations:
          summary: "PBJRAG error rate exceeds 1%"

      - alert: HighLatency
        expr: histogram_quantile(0.99, pbjrag_request_duration_seconds_bucket) > 10
        for: 5m
        annotations:
          summary: "PBJRAG P99 latency exceeds 10s"

      - alert: ServiceUnhealthy
        expr: up{job="pbjrag"} == 0
        for: 5m
        annotations:
          summary: "PBJRAG service is down"
```

## CI/CD Integration

### Running SLO Tests in CI

```yaml
# .github/workflows/slo-check.yml
name: SLO Compliance

on: [push, pull_request]

jobs:
  slo-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run SLO tests
        run: pytest tests/test_performance_slo.py -m performance -v
```

### Pre-deployment Checks

```bash
#!/bin/bash
# pre-deploy.sh - Run before deploying

echo "Running SLO compliance tests..."
pytest tests/test_performance_slo.py -m performance --tb=short

if [ $? -ne 0 ]; then
    echo "❌ SLO tests failed - blocking deployment"
    exit 1
fi

echo "✅ All SLO tests passed - deployment approved"
```

## Troubleshooting

### Missing prometheus-client

If Prometheus metrics are not working:

```bash
pip install prometheus-client
```

The observability module gracefully degrades without it.

### Trace ID Not Appearing

Ensure you're using the context manager or decorator:

```python
# ❌ Wrong - no trace ID
logger.info("message")

# ✅ Correct - trace ID included
with trace_operation("op"):
    logger.info("message")
```

### SLO Tests Failing

If performance tests fail:

1. Check system load - run tests on idle system
2. Increase iteration count for more stable P99
3. Adjust thresholds in test if consistently off
4. Review `slo.yaml` objectives vs actual performance

## Best Practices

1. **Always use trace_operation** for user-facing operations
2. **Record custom metrics** for business-critical events
3. **Run SLO tests** in CI/CD pipeline
4. **Monitor P99 latency**, not averages
5. **Set up alerts** for SLO violations
6. **Review error_budget** monthly
7. **Update SLOs** based on real usage patterns

## File Organization

- `/home/ndspence/GitHub/navi-pbjrag/slo.yaml` - SLO definitions
- `/home/ndspence/GitHub/navi-pbjrag/src/pbjrag/observability.py` - Observability module
- `/home/ndspence/GitHub/navi-pbjrag/tests/test_performance_slo.py` - SLO enforcement tests
- `/home/ndspence/GitHub/navi-pbjrag/pytest.ini` - Test markers configuration
