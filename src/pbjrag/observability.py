"""
Observability infrastructure for PBJRAG.

Provides:
- Structured JSON logging with trace IDs
- Prometheus metrics (counters, histograms)
- Health check utilities
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

# Prometheus metrics (optional dependency)
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Metrics definitions
if PROMETHEUS_AVAILABLE:
    REQUEST_COUNT = Counter(
        "pbjrag_requests_total", "Total number of requests", ["operation", "status"]
    )
    REQUEST_DURATION = Histogram(
        "pbjrag_request_duration_seconds",
        "Request duration in seconds",
        ["operation"],
        buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
    )
    ERROR_COUNT = Counter(
        "pbjrag_errors_total", "Total number of errors", ["operation", "error_type"]
    )
    ACTIVE_REQUESTS = Gauge("pbjrag_active_requests", "Number of active requests", ["operation"])
    BLESSING_TIER_COUNT = Counter(
        "pbjrag_blessing_tiers_total", "Count of blessing tier assignments", ["tier"]
    )


class StructuredLogger:
    """JSON-formatted logger with trace ID support."""

    def __init__(self, name: str = "pbjrag"):
        self.logger = logging.getLogger(name)
        self._trace_id: Optional[str] = None

    def set_trace_id(self, trace_id: str):
        self._trace_id = trace_id

    def _format_entry(self, level: str, message: str, **kwargs) -> str:
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "level": level,
            "message": message,
            "service": "pbjrag",
            "trace_id": self._trace_id or str(uuid.uuid4())[:8],
            **kwargs,
        }
        return json.dumps(entry)

    def info(self, message: str, **kwargs):
        self.logger.info(self._format_entry("INFO", message, **kwargs))

    def error(self, message: str, **kwargs):
        self.logger.error(self._format_entry("ERROR", message, **kwargs))

    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_entry("WARNING", message, **kwargs))

    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_entry("DEBUG", message, **kwargs))


# Global logger instance
logger = StructuredLogger()


@contextmanager
def trace_operation(operation: str, trace_id: Optional[str] = None):
    """Context manager for tracing operations with metrics."""
    trace_id = trace_id or str(uuid.uuid4())[:8]
    logger.set_trace_id(trace_id)

    start_time = time.time()
    logger.info(f"Starting {operation}", operation=operation)

    if PROMETHEUS_AVAILABLE:
        ACTIVE_REQUESTS.labels(operation=operation).inc()

    try:
        yield trace_id
        duration = time.time() - start_time

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(operation=operation, status="success").inc()
            REQUEST_DURATION.labels(operation=operation).observe(duration)

        logger.info(
            f"Completed {operation}",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            status="success",
        )

    except Exception as e:
        duration = time.time() - start_time

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(operation=operation, status="error").inc()
            ERROR_COUNT.labels(operation=operation, error_type=type(e).__name__).inc()
            REQUEST_DURATION.labels(operation=operation).observe(duration)

        logger.error(
            f"Failed {operation}",
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            error=str(e),
            error_type=type(e).__name__,
        )
        raise

    finally:
        if PROMETHEUS_AVAILABLE:
            ACTIVE_REQUESTS.labels(operation=operation).dec()


def traced(operation: str):
    """Decorator for tracing function calls."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with trace_operation(operation):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def record_blessing_tier(tier: str):
    """Record a blessing tier assignment for metrics."""
    if PROMETHEUS_AVAILABLE:
        BLESSING_TIER_COUNT.labels(tier=tier).inc()


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format."""
    if PROMETHEUS_AVAILABLE:
        return generate_latest()
    return b"# Prometheus client not installed\n"


def health_check() -> Dict[str, Any]:
    """Perform health check and return status."""
    checks = {"status": "healthy", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "checks": {}}

    # Check core imports
    try:
        from pbjrag import DSCAnalyzer

        checks["checks"]["core_imports"] = "ok"
    except Exception as e:
        checks["checks"]["core_imports"] = f"error: {e}"
        checks["status"] = "unhealthy"

    # Check Qdrant (if configured)
    try:
        from pbjrag.dsc.vector_store import DSCVectorStore

        # Just check import, don't actually connect
        checks["checks"]["vector_store"] = "available"
    except ImportError:
        checks["checks"]["vector_store"] = "not_installed"

    return checks
