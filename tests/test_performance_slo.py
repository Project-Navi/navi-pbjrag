"""Performance tests enforcing SLO compliance."""

import tempfile
import time
from pathlib import Path

import pytest

from pbjrag import DSCAnalyzer, DSCCodeChunker

# Sample code for testing
SAMPLE_CODE = '''
def fibonacci(n: int) -> int:
    """Calculate fibonacci number recursively."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """A simple calculator class."""

    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b
'''


class TestAnalysisSLO:
    """Test analysis latency meets SLO targets."""

    @pytest.mark.performance
    def test_chunking_latency_p99(self):
        """Chunking should complete within 100ms p99."""
        chunker = DSCCodeChunker()
        latencies = []

        for _ in range(100):
            start = time.perf_counter()
            chunker.chunk_code(SAMPLE_CODE)
            latencies.append((time.perf_counter() - start) * 1000)

        latencies.sort()
        p99 = latencies[98]

        assert p99 < 100, f"Chunking p99 latency {p99:.2f}ms exceeds 100ms SLO"

    @pytest.mark.performance
    def test_analysis_latency_p99(self):
        """Full analysis should complete within 5000ms p99."""
        # Disable vector store for pure performance testing
        config = {"enable_vector_store": False}
        analyzer = DSCAnalyzer(config=config)
        latencies = []

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(SAMPLE_CODE)
            temp_file = f.name

        try:
            for _ in range(20):  # Fewer iterations for heavier operation
                start = time.perf_counter()
                analyzer.analyze_file(temp_file)
                latencies.append((time.perf_counter() - start) * 1000)

            latencies.sort()
            p99 = latencies[int(len(latencies) * 0.99)]

            assert p99 < 5000, f"Analysis p99 latency {p99:.2f}ms exceeds 5000ms SLO"
        finally:
            # Cleanup temp file
            Path(temp_file).unlink(missing_ok=True)


class TestAvailabilitySLO:
    """Test service availability meets SLO targets."""

    @pytest.mark.performance
    def test_analyzer_initialization_success_rate(self):
        """Analyzer should initialize successfully 99.9% of the time."""
        successes = 0
        attempts = 1000
        config = {"enable_vector_store": False}  # Disable to avoid connection failures

        for _ in range(attempts):
            try:
                analyzer = DSCAnalyzer(config=config)
                successes += 1
            except Exception:
                pass

        success_rate = successes / attempts * 100
        assert success_rate >= 99.9, f"Init success rate {success_rate}% below 99.9% SLO"
