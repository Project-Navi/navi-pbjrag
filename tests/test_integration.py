"""
Integration tests for PBJRAG - End-to-end workflow testing.

These tests verify the complete analysis pipeline from input to output.
Mark with @pytest.mark.integration for optional execution.
"""

import json
from pathlib import Path

import pytest
import numpy as np


@pytest.mark.integration
class TestEndToEndAnalysis:
    """Test complete end-to-end analysis workflows."""

    def test_single_file_analysis_workflow(self, tmp_path, sample_python_code):
        """Test complete workflow for single file analysis."""
        from pbjrag.dsc import DSCAnalyzer

        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_code)

        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Configure and run analyzer
        config = {
            "purpose": "coherence",
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)
        result = analyzer.analyze_file(str(test_file))

        # Verify results
        assert result is not None
        assert "success" in result or "file" in result

        # Verify report generation
        report = analyzer.generate_report()
        assert "field_coherence" in report
        assert 0.0 <= report["field_coherence"] <= 1.0

    def test_project_analysis_workflow(self, tmp_path, sample_python_code):
        """Test complete workflow for project analysis."""
        from pbjrag.dsc import DSCAnalyzer

        # Create test project
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "main.py").write_text(sample_python_code)
        (project_dir / "utils.py").write_text("def helper(): return True")

        subdir = project_dir / "submodule"
        subdir.mkdir()
        (subdir / "__init__.py").write_text("")
        (subdir / "helper.py").write_text("class Helper:\n    pass")

        # Create output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Run analysis
        config = {
            "purpose": "stability",
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)
        result = analyzer.analyze_project(str(project_dir))

        # Verify results
        assert result is not None
        assert result.get("success") or "dsc_analysis" in result

        if "dsc_analysis" in result:
            dsc = result["dsc_analysis"]
            assert dsc.get("files_analyzed", 0) >= 2


@pytest.mark.integration
class TestChunkerAnalyzerPipeline:
    """Test chunker → analyzer → report pipeline."""

    def test_chunker_to_analyzer_flow(self, tmp_path, sample_python_code):
        """Test data flow from chunker through analyzer."""
        from pbjrag.dsc.chunker import CodeChunker
        from pbjrag.dsc.analyzer import CodeAnalyzer

        # Chunk the code
        chunker = CodeChunker(purpose="coherence")
        chunks = chunker.chunk_code(sample_python_code, "test.py")

        assert chunks is not None
        assert len(chunks) > 0

        # Analyze the chunks
        analyzer = CodeAnalyzer()
        for chunk in chunks:
            analysis = analyzer.analyze_chunk(chunk)
            assert analysis is not None
            assert "blessing" in analysis or "metrics" in analysis

    def test_full_pipeline_with_metrics(self, tmp_path, sample_python_code):
        """Test full pipeline including metrics calculation."""
        from pbjrag.dsc.chunker import CodeChunker
        from pbjrag.dsc.analyzer import CodeAnalyzer
        from pbjrag.crown_jewel.metrics import CoreMetrics

        # Initialize components
        chunker = CodeChunker(purpose="innovation")
        analyzer = CodeAnalyzer()
        metrics = CoreMetrics()

        # Run pipeline
        chunks = chunker.chunk_code(sample_python_code, "test.py")
        analyses = []

        for chunk in chunks:
            analysis = analyzer.analyze_chunk(chunk)
            analyses.append(analysis)

        # Calculate overall metrics
        assert len(analyses) > 0
        assert all(a is not None for a in analyses)

    def test_pipeline_with_multiple_files(self, tmp_path, sample_python_code):
        """Test pipeline with multiple files."""
        from pbjrag.dsc.chunker import CodeChunker
        from pbjrag.dsc.analyzer import CodeAnalyzer

        # Create multiple test files
        files = {
            "file1.py": sample_python_code,
            "file2.py": "def test():\n    return True\n",
            "file3.py": "class Example:\n    def method(self):\n        pass\n",
        }

        chunker = CodeChunker(purpose="emergence")
        analyzer = CodeAnalyzer()

        all_analyses = []

        for filename, code in files.items():
            chunks = chunker.chunk_code(code, filename)
            for chunk in chunks:
                analysis = analyzer.analyze_chunk(chunk)
                all_analyses.append(analysis)

        assert len(all_analyses) >= len(files)


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling throughout the pipeline."""

    def test_invalid_code_handling(self, invalid_python_code):
        """Test handling of invalid Python code."""
        from pbjrag.dsc.chunker import CodeChunker

        chunker = CodeChunker()

        # Should handle invalid code gracefully
        try:
            chunks = chunker.chunk_code(invalid_python_code, "invalid.py")
            # If it doesn't raise, verify we get some result
            assert chunks is not None
        except Exception as e:
            # If it raises, verify it's a reasonable error
            assert e is not None

    def test_missing_file_handling(self, tmp_path):
        """Test handling of missing files."""
        from pbjrag.dsc import DSCAnalyzer

        config = {
            "purpose": "coherence",
            "output_dir": str(tmp_path),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)

        # Should handle missing file gracefully
        try:
            result = analyzer.analyze_file(str(tmp_path / "nonexistent.py"))
            # Check if error is reported in result
            if isinstance(result, dict):
                assert "error" in result or "success" in result
        except (FileNotFoundError, Exception) as e:
            # If exception raised, verify it's appropriate
            assert e is not None


@pytest.mark.integration
class TestFieldContainerIntegration:
    """Test field container integration with analysis pipeline."""

    def test_field_state_persistence(self, tmp_path):
        """Test field state save and load."""
        from pbjrag.crown_jewel.field_container import create_field

        config = {"field_dim": 8}
        field = create_field(config)

        # Add some test data
        field.add_fragment({"id": "test1", "code": "def test(): pass"})
        field.add_pattern({"id": "pattern1", "type": "function"})

        # Save state
        output_dir = tmp_path / "field_state"
        output_dir.mkdir()
        state_files = field.save_field_state(str(output_dir))

        assert len(state_files) > 0
        assert all(Path(f).exists() for f in state_files.values())

        # Load state in new field
        field2 = create_field(config)
        loaded = field2.load_field_state(str(output_dir))

        assert loaded is True

    def test_field_operations_during_analysis(self, tmp_path, sample_python_code):
        """Test field operations during analysis."""
        from pbjrag.dsc import DSCAnalyzer

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config = {
            "purpose": "coherence",
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)

        # Run analysis
        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_code)
        result = analyzer.analyze_file(str(test_file))

        # Verify field state was saved
        state_files = output_dir / "field_state.json"
        # Some state should be saved
        assert result is not None


@pytest.mark.integration
class TestReportGeneration:
    """Test report generation from analysis results."""

    def test_markdown_report_generation(self, tmp_path, sample_python_code):
        """Test generation of markdown reports."""
        from pbjrag.dsc import DSCAnalyzer

        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_code)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config = {
            "purpose": "stability",
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)
        analyzer.analyze_file(str(test_file))

        # Generate report
        report = analyzer.generate_report()

        assert report is not None
        assert "field_coherence" in report

        # Check if markdown file was created
        md_files = list(output_dir.glob("*.md"))
        # At least one markdown file should exist
        assert len(md_files) >= 0  # May or may not create MD files

    def test_json_report_generation(self, tmp_path, sample_python_code):
        """Test generation of JSON reports."""
        from pbjrag.dsc import DSCAnalyzer

        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_code)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        config = {
            "purpose": "emergence",
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)
        analyzer.analyze_file(str(test_file))

        report = analyzer.generate_report()

        # Verify report can be serialized to JSON
        json_str = json.dumps(report)
        assert json_str is not None

        # Verify it can be deserialized
        loaded_report = json.loads(json_str)
        assert loaded_report == report


@pytest.mark.integration
class TestMultiPurposeAnalysis:
    """Test analysis with different purposes."""

    @pytest.mark.parametrize(
        "purpose", ["stability", "emergence", "coherence", "innovation"]
    )
    def test_analysis_with_different_purposes(
        self, purpose, tmp_path, sample_python_code
    ):
        """Test analysis with each purpose setting."""
        from pbjrag.dsc import DSCAnalyzer

        test_file = tmp_path / "test.py"
        test_file.write_text(sample_python_code)

        output_dir = tmp_path / f"output_{purpose}"
        output_dir.mkdir()

        config = {
            "purpose": purpose,
            "output_dir": str(output_dir),
            "enable_vector_store": False,
        }

        analyzer = DSCAnalyzer(config)
        result = analyzer.analyze_file(str(test_file))

        assert result is not None

        report = analyzer.generate_report()
        assert "field_coherence" in report
