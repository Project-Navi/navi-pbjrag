"""
Shared fixtures for PBJRAG test suite.
"""

import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import numpy as np


@pytest.fixture
def sample_python_code() -> str:
    """Returns a simple Python code sample for testing."""
    return '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """Simple calculator class."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
'''


@pytest.fixture
def sample_python_file(tmp_path: Path, sample_python_code: str) -> Path:
    """Creates a temporary Python file with sample code."""
    file_path = tmp_path / "sample.py"
    file_path.write_text(sample_python_code)
    return file_path


@pytest.fixture
def invalid_python_code() -> str:
    """Returns invalid Python code for error testing."""
    return '''
def broken_function(
    # Missing closing parenthesis
    return "incomplete"
'''


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Returns a basic test configuration."""
    return {
        "field_dim": 8,
        "quantization_precision": 4,
        "pareto_alpha": 2.0,
        "stability_threshold": 0.5,
        "enable_vector_store": False,  # Disable by default for tests
    }


@pytest.fixture
def sample_field_vector() -> np.ndarray:
    """Returns a sample field vector for testing."""
    return np.random.rand(8)


@pytest.fixture
def sample_blessing_vector() -> Dict[str, Any]:
    """Returns a sample blessing vector for testing."""
    return {
        "epc": 0.75,
        "qualia": 0.65,
        "contradiction": 0.35,
        "presence": 0.60,
        "resonance": 0.70,
    }


@pytest.fixture
def temp_project_dir(tmp_path: Path, sample_python_code: str) -> Path:
    """Creates a temporary project directory with sample files."""
    project = tmp_path / "test_project"
    project.mkdir()

    # Create some sample files
    (project / "main.py").write_text(sample_python_code)
    (project / "utils.py").write_text("def helper(): pass")

    # Create a subdirectory
    subdir = project / "submodule"
    subdir.mkdir()
    (subdir / "helper.py").write_text("class Helper: pass")

    return project
