"""
Tests for CLI module - Command line interface testing.
"""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pbjrag.cli import main


class TestCLIAnalyzeCommand:
    """Test analyze command functionality."""

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_single_file(self, mock_analyzer_class, tmp_path, capsys):
        """Test analyzing a single file."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        # Mock analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = {
            "success": True,
            "file": str(test_file),
        }
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        # Run CLI
        with patch.object(sys, "argv", ["pbjrag", "analyze", str(test_file)]):
            result = main()

        assert result == 0
        mock_analyzer.analyze_file.assert_called_once()
        captured = capsys.readouterr()
        assert "Analyzing" in captured.out
        assert "Analyzed 1 file" in captured.out

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_project_directory(self, mock_analyzer_class, tmp_path, capsys):
        """Test analyzing a project directory."""
        # Create test project structure
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "main.py").write_text("def main(): pass")
        (project_dir / "utils.py").write_text("def helper(): pass")

        # Mock analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_project.return_value = {
            "success": True,
            "dsc_analysis": {"files_analyzed": 2},
        }
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.75,
            "blessing_distribution": {"Φ+": 0.6, "Φ~": 0.3, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        # Run CLI
        with patch.object(sys, "argv", ["pbjrag", "analyze", str(project_dir)]):
            result = main()

        assert result == 0
        mock_analyzer.analyze_project.assert_called_once()
        captured = capsys.readouterr()
        assert "Analyzed 2 files" in captured.out

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_with_custom_output(self, mock_analyzer_class, tmp_path, capsys):
        """Test analyze command with custom output directory."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = {"success": True}
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        custom_output = str(tmp_path / "custom_output")

        with patch.object(
            sys,
            "argv",
            ["pbjrag", "analyze", str(test_file), "--output", custom_output],
        ):
            result = main()

        assert result == 0
        # Check that analyzer was initialized with correct config
        call_args = mock_analyzer_class.call_args[0][0]
        assert call_args["output_dir"] == custom_output

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_with_purpose(self, mock_analyzer_class, tmp_path):
        """Test analyze with different purpose options."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = {"success": True}
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        purposes = ["stability", "emergence", "coherence", "innovation"]
        for purpose in purposes:
            with patch.object(
                sys,
                "argv",
                ["pbjrag", "analyze", str(test_file), "--purpose", purpose],
            ):
                result = main()

            assert result == 0
            call_args = mock_analyzer_class.call_args[0][0]
            assert call_args["purpose"] == purpose

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_with_no_vector(self, mock_analyzer_class, tmp_path):
        """Test analyze with vector store disabled."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = {"success": True}
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(
            sys, "argv", ["pbjrag", "analyze", str(test_file), "--no-vector"]
        ):
            result = main()

        assert result == 0
        call_args = mock_analyzer_class.call_args[0][0]
        assert call_args["enable_vector_store"] is False

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_analyze_devops_persona(self, mock_analyzer_class, tmp_path, capsys):
        """Test analyze with devops persona output."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = {"success": True}
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(
            sys, "argv", ["pbjrag", "analyze", str(test_file), "--persona", "devops"]
        ):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "Production Readiness" in captured.out
        assert "Production-ready" in captured.out

    def test_analyze_nonexistent_path(self, tmp_path, capsys):
        """Test analyzing a path that doesn't exist."""
        nonexistent = tmp_path / "nonexistent.py"

        with patch.object(sys, "argv", ["pbjrag", "analyze", str(nonexistent)]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Path not found" in captured.out


class TestCLIReportCommand:
    """Test report command functionality."""

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_report_json_format(self, mock_analyzer_class, tmp_path, capsys):
        """Test generating JSON report."""
        mock_analyzer = MagicMock()
        mock_field_container = MagicMock()
        mock_field_container.load_field_state.return_value = True
        mock_analyzer.field_container = mock_field_container
        mock_analyzer.generate_report.return_value = {
            "field_coherence": 0.85,
            "blessing_distribution": {"Φ+": 0.7, "Φ~": 0.2, "Φ-": 0.1},
        }
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(
            sys,
            "argv",
            ["pbjrag", "report", "--input", str(tmp_path), "--format", "json"],
        ):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "field_coherence" in captured.out

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_report_markdown_format(self, mock_analyzer_class, tmp_path, capsys):
        """Test generating Markdown report."""
        # Create sample markdown report
        md_file = tmp_path / "dsc_analysis_report.md"
        md_file.write_text("# PBJRAG Analysis Report\n\nTest content")

        mock_analyzer = MagicMock()
        mock_field_container = MagicMock()
        mock_field_container.load_field_state.return_value = True
        mock_analyzer.field_container = mock_field_container
        mock_analyzer.generate_report.return_value = {"field_coherence": 0.85}
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(
            sys,
            "argv",
            ["pbjrag", "report", "--input", str(tmp_path), "--format", "markdown"],
        ):
            result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "PBJRAG Analysis Report" in captured.out

    @patch("pbjrag.dsc.DSCAnalyzer")
    @patch("pbjrag.cli.markdown")
    def test_report_html_format(self, mock_markdown, mock_analyzer_class, tmp_path):
        """Test generating HTML report."""
        # Create sample markdown report
        md_file = tmp_path / "dsc_analysis_report.md"
        md_file.write_text("# PBJRAG Analysis Report")

        mock_markdown.markdown.return_value = "<h1>PBJRAG Analysis Report</h1>"

        mock_analyzer = MagicMock()
        mock_field_container = MagicMock()
        mock_field_container.load_field_state.return_value = True
        mock_analyzer.field_container = mock_field_container
        mock_analyzer.generate_report.return_value = {"field_coherence": 0.85}
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(
            sys, "argv", ["pbjrag", "report", "--input", str(tmp_path), "--format", "html"]
        ):
            result = main()

        assert result == 0
        html_file = tmp_path / "dsc_analysis_report.html"
        assert html_file.exists()
        assert "<h1>" in html_file.read_text()

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_report_no_analysis_data(self, mock_analyzer_class, tmp_path, capsys):
        """Test report when no analysis data exists."""
        mock_analyzer = MagicMock()
        mock_field_container = MagicMock()
        mock_field_container.load_field_state.return_value = False
        mock_analyzer.field_container = mock_field_container
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(sys, "argv", ["pbjrag", "report", "--input", str(tmp_path)]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "No analysis data found" in captured.out


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_no_command(self, capsys):
        """Test CLI with no command."""
        with patch.object(sys, "argv", ["pbjrag"]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out or "Commands" in captured.out

    def test_import_error(self, tmp_path, capsys):
        """Test CLI with import error."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        with patch("pbjrag.cli.DSCAnalyzer", side_effect=ImportError("test error")):
            with patch.object(sys, "argv", ["pbjrag", "analyze", str(test_file)]):
                result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Import error" in captured.out

    @patch("pbjrag.dsc.DSCAnalyzer")
    def test_general_exception(self, mock_analyzer_class, tmp_path, capsys):
        """Test CLI with general exception."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.side_effect = Exception("Test exception")
        mock_analyzer_class.return_value = mock_analyzer

        with patch.object(sys, "argv", ["pbjrag", "analyze", str(test_file)]):
            result = main()

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_help_output(self, capsys):
        """Test help output."""
        with patch.object(sys, "argv", ["pbjrag", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "PBJRAG" in captured.out
        assert "analyze" in captured.out
        assert "report" in captured.out

    def test_version_output(self, capsys):
        """Test version output."""
        with patch.object(sys, "argv", ["pbjrag", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "3.0.0" in captured.out
