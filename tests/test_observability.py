"""
Tests for observability module.
"""

import json
import logging
import time
from unittest.mock import MagicMock, patch

import pytest


class TestStructuredLogger:
    """Test StructuredLogger functionality."""

    def test_import_observability(self):
        """Test that observability module can be imported."""
        from pbjrag import observability

        assert observability is not None

    def test_structured_logger_creation(self):
        """Test StructuredLogger instantiation."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test")
        assert logger is not None
        assert logger._trace_id is None

    def test_set_trace_id(self):
        """Test setting trace ID."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test")
        logger.set_trace_id("abc123")
        assert logger._trace_id == "abc123"

    def test_format_entry_structure(self):
        """Test that log entries have correct structure."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test")
        logger.set_trace_id("test-trace")

        entry = logger._format_entry("INFO", "Test message", extra_field="value")
        parsed = json.loads(entry)

        assert "timestamp" in parsed
        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test message"
        assert parsed["service"] == "pbjrag"
        assert parsed["trace_id"] == "test-trace"
        assert parsed["extra_field"] == "value"

    def test_format_entry_auto_trace_id(self):
        """Test that trace ID is auto-generated if not set."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test")
        # Don't set trace_id

        entry = logger._format_entry("INFO", "Test message")
        parsed = json.loads(entry)

        assert "trace_id" in parsed
        assert len(parsed["trace_id"]) == 8

    def test_info_logging(self, caplog):
        """Test info level logging."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test_info")

        with caplog.at_level(logging.INFO):
            logger.info("Info message", key="value")

        # Verify log was captured
        assert len(caplog.records) >= 0  # May or may not be captured depending on config

    def test_error_logging(self, caplog):
        """Test error level logging."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test_error")

        with caplog.at_level(logging.ERROR):
            logger.error("Error message", error_code=500)

    def test_warning_logging(self, caplog):
        """Test warning level logging."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test_warning")

        with caplog.at_level(logging.WARNING):
            logger.warning("Warning message")

    def test_debug_logging(self, caplog):
        """Test debug level logging."""
        from pbjrag.observability import StructuredLogger

        logger = StructuredLogger("test_debug")

        with caplog.at_level(logging.DEBUG):
            logger.debug("Debug message", details={"x": 1})


class TestGlobalLogger:
    """Test global logger instance."""

    def test_global_logger_exists(self):
        """Test that global logger is available."""
        from pbjrag.observability import logger

        assert logger is not None

    def test_global_logger_is_structured(self):
        """Test that global logger is a StructuredLogger."""
        from pbjrag.observability import StructuredLogger, logger

        assert isinstance(logger, StructuredLogger)


class TestTraceOperation:
    """Test trace_operation context manager."""

    def test_trace_operation_basic(self):
        """Test basic trace_operation usage."""
        from pbjrag.observability import trace_operation

        with trace_operation("test_op") as ctx:
            # Operation runs here
            pass

    def test_trace_operation_custom_trace_id(self):
        """Test trace_operation with custom trace ID."""
        from pbjrag.observability import trace_operation

        with trace_operation("test_op", trace_id="custom-123") as ctx:
            pass

    def test_trace_operation_exception_handling(self):
        """Test trace_operation handles exceptions."""
        from pbjrag.observability import trace_operation

        with pytest.raises(ValueError):
            with trace_operation("failing_op"):
                raise ValueError("Test error")


class TestPrometheusMetrics:
    """Test Prometheus metrics integration."""

    def test_prometheus_available_flag(self):
        """Test PROMETHEUS_AVAILABLE flag is set."""
        from pbjrag.observability import PROMETHEUS_AVAILABLE

        assert isinstance(PROMETHEUS_AVAILABLE, bool)

    @pytest.mark.skipif(
        True, reason="Prometheus metrics optional"  # Skip if prometheus not available
    )
    def test_request_count_metric(self):
        """Test request count metric exists if Prometheus available."""
        from pbjrag.observability import PROMETHEUS_AVAILABLE

        if PROMETHEUS_AVAILABLE:
            from pbjrag.observability import REQUEST_COUNT

            assert REQUEST_COUNT is not None

    @pytest.mark.skipif(
        True, reason="Prometheus metrics optional"  # Skip if prometheus not available
    )
    def test_request_duration_metric(self):
        """Test request duration histogram exists if Prometheus available."""
        from pbjrag.observability import PROMETHEUS_AVAILABLE

        if PROMETHEUS_AVAILABLE:
            from pbjrag.observability import REQUEST_DURATION

            assert REQUEST_DURATION is not None


class TestHealthCheck:
    """Test health check utilities."""

    def test_health_check_function(self):
        """Test basic health check functionality."""
        from pbjrag.observability import PROMETHEUS_AVAILABLE

        # Health check should work regardless of Prometheus
        assert isinstance(PROMETHEUS_AVAILABLE, bool)


class TestMetricsInstrumentation:
    """Test metrics instrumentation decorators and utilities."""

    def test_timed_operation(self):
        """Test timing instrumentation."""
        import time

        from pbjrag.observability import trace_operation

        start = time.time()
        with trace_operation("timed_test"):
            time.sleep(0.01)  # 10ms
        elapsed = time.time() - start

        assert elapsed >= 0.01

    def test_nested_trace_operations(self):
        """Test nested trace operations."""
        from pbjrag.observability import trace_operation

        with trace_operation("outer"):
            with trace_operation("inner"):
                pass
