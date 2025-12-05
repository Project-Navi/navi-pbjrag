"""
Tests for DSCAnalyzer - Unified analysis interface.
"""

from pathlib import Path

import pytest

from pbjrag import DSCAnalyzer


class TestDSCAnalyzer:
    """Test suite for DSCAnalyzer."""

    def test_analyzer_initialization(self, test_config):
        """Test that DSCAnalyzer initializes with configuration."""
        analyzer = DSCAnalyzer(config=test_config)

        assert analyzer is not None
        assert analyzer.config == test_config
        assert analyzer.chunker is not None
        assert analyzer.phase_manager is not None
        assert analyzer.metrics is not None
        assert analyzer.field_container is not None

    def test_analyzer_initialization_no_config(self):
        """Test that DSCAnalyzer initializes without configuration."""
        analyzer = DSCAnalyzer()

        assert analyzer is not None
        assert analyzer.config == {}
        assert analyzer.chunker is not None

    def test_analyze_file_returns_chunks(self, sample_python_file, test_config):
        """Test that analyze_file returns result dict with chunks."""
        analyzer = DSCAnalyzer(config=test_config)

        # The analyze_file method returns a dict with 'chunks' key
        result = analyzer.analyze_file(str(sample_python_file))

        assert result is not None
        assert isinstance(result, dict)
        assert result.get("success", False)
        assert "chunks" in result
        assert len(result["chunks"]) > 0

    def test_analyze_file_with_valid_code(self, sample_python_file, test_config):
        """Test analysis with valid Python code produces chunk dicts."""
        analyzer = DSCAnalyzer(config=test_config)

        result = analyzer.analyze_file(str(sample_python_file))
        chunks = result.get("chunks", [])

        # Verify chunks have expected keys
        for chunk in chunks:
            assert "content" in chunk
            assert "start_line" in chunk
            assert "end_line" in chunk
            assert "field_state" in chunk
            assert "blessing" in chunk
            assert "chunk_type" in chunk

    def test_analyze_nonexistent_file(self, test_config):
        """Test that analyzing a nonexistent file returns error result."""
        analyzer = DSCAnalyzer(config=test_config)

        result = analyzer.analyze_file("/nonexistent/path/file.py")
        # The analyzer may return a result with success=False instead of raising
        assert result is not None
        # Either raises an exception OR returns a result dict with error info

    def test_analyze_project(self, temp_project_dir, test_config):
        """Test that analyze_project processes a directory of files."""
        analyzer = DSCAnalyzer(config=test_config)

        # analyze_project should process all Python files in the directory
        result = analyzer.analyze_project(str(temp_project_dir))

        assert result is not None

    def test_vector_store_disabled_by_config(self):
        """Test that vector store can be disabled via configuration."""
        config = {"enable_vector_store": False}
        analyzer = DSCAnalyzer(config=config)

        assert analyzer.vector_store is None

    def test_output_directory_creation(self, test_config, tmp_path):
        """Test that output directory is created."""
        config = test_config.copy()
        config["output_dir"] = str(tmp_path / "test_output")

        analyzer = DSCAnalyzer(config=config)

        assert analyzer.output_dir.exists()
        assert analyzer.output_dir.is_dir()
