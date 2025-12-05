"""
Tests for error_handler module - Error handling and classification.
"""

from unittest.mock import MagicMock

import pytest

from pbjrag.crown_jewel.error_handler import ErrorHandler, handle_error, resolve_ambiguity


class TestErrorHandler:
    """Test ErrorHandler class."""

    def test_error_handler_initialization(self):
        """Test error handler initialization."""
        handler = ErrorHandler()
        assert handler is not None
        assert handler.config is not None
        assert handler._error_patterns is not None
        assert handler._solution_templates is not None

    def test_error_handler_with_config(self):
        """Test error handler with custom config."""
        config = {"verbose": True, "max_retries": 3}
        handler = ErrorHandler(config)
        assert handler.config == config


class TestErrorClassification:
    """Test error classification and pattern matching."""

    def test_missing_dependency_error(self):
        """Test missing dependency error classification."""
        handler = ErrorHandler()
        error = "ModuleNotFoundError: No module named 'numpy'"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "missing_dependency"
        assert result["solution"]["action"] == "install_dependency"
        assert "numpy" in result["solution"]["message"]

    def test_import_error(self):
        """Test import error classification."""
        handler = ErrorHandler()
        error = "ImportError: cannot import name 'DSCAnalyzer' from 'pbjrag'"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "missing_import"
        assert result["solution"]["action"] == "fix_import"

    def test_syntax_error(self):
        """Test syntax error classification."""
        handler = ErrorHandler()
        error = "SyntaxError: invalid syntax (test.py, line 42)"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "syntax_error"
        assert result["solution"]["action"] == "fix_syntax"
        assert "line 42" in result["solution"]["message"]

    def test_attribute_error(self):
        """Test attribute error classification."""
        handler = ErrorHandler()
        error = "AttributeError: 'NoneType' object has no attribute 'analyze'"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "missing_attribute"
        assert result["solution"]["action"] == "fix_attribute"

    def test_type_error(self):
        """Test type error classification."""
        handler = ErrorHandler()
        error = "TypeError: expected str, got int"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "type_error"
        assert result["solution"]["action"] == "fix_type"

    def test_value_error(self):
        """Test value error classification."""
        handler = ErrorHandler()
        error = "ValueError: invalid value for parameter"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "value_error"
        assert result["solution"]["action"] == "fix_value"

    def test_file_not_found_error(self):
        """Test file not found error classification."""
        handler = ErrorHandler()
        error = "FileNotFoundError: [Errno 2] No such file or directory: 'test.py'"

        result = handler.handle_error(error)

        assert result["success"] is True
        assert result["error_info"]["type"] == "missing_file"
        assert result["solution"]["action"] == "create_file"
        assert "test.py" in result["solution"]["message"]


class TestErrorFormatting:
    """Test error formatting and solution generation."""

    def test_solution_message_formatting(self):
        """Test solution message formatting."""
        handler = ErrorHandler()
        error = "ModuleNotFoundError: No module named 'requests'"

        result = handler.handle_error(error)

        assert "requests" in result["solution"]["message"]
        assert "pip install requests" in result["solution"]["command"]

    def test_error_with_field_context(self):
        """Test error handling with field context."""
        handler = ErrorHandler()
        mock_field = MagicMock()
        mock_field.add_conflict = MagicMock()

        error = "TypeError: expected str, got int"
        result = handler.handle_error(error, field=mock_field)

        assert result["success"] is True
        mock_field.add_conflict.assert_called_once()

    def test_error_with_exception_object(self):
        """Test error handling with exception object."""
        handler = ErrorHandler()
        exception = ValueError("Invalid configuration")

        result = handler.handle_error(exception)

        # ValueError doesn't match patterns, so it won't have success=True
        assert result is not None
        assert "Invalid configuration" in result["error"]

    def test_unmatched_error_pattern(self):
        """Test handling of unmatched error pattern."""
        handler = ErrorHandler()
        error = "CustomError: This is a custom error message"

        result = handler.handle_error(error)

        assert result["success"] is False
        assert "No matching pattern" in result["message"]
        assert result["solution"] is None


class TestRecoverySuggestions:
    """Test recovery suggestions generation."""

    def test_dependency_recovery_suggestion(self):
        """Test dependency error recovery suggestion."""
        handler = ErrorHandler()
        error = "ModuleNotFoundError: No module named 'pandas'"

        result = handler.handle_error(error)

        assert result["solution"]["command"] == "pip install pandas"

    def test_import_recovery_suggestion(self):
        """Test import error recovery suggestion."""
        handler = ErrorHandler()
        error = "ImportError: cannot import name 'function' from 'module'"

        result = handler.handle_error(error)

        assert "suggestion" in result["solution"]
        assert "function" in result["solution"]["suggestion"]
        assert "module" in result["solution"]["suggestion"]

    def test_syntax_error_recovery_suggestion(self):
        """Test syntax error recovery suggestion."""
        handler = ErrorHandler()
        error = "SyntaxError: invalid syntax (main.py, line 10)"

        result = handler.handle_error(error)

        assert "suggestion" in result["solution"]
        assert "correct the syntax" in result["solution"]["suggestion"]


class TestAmbiguityResolution:
    """Test ambiguity resolution functionality."""

    def test_resolve_no_options(self):
        """Test ambiguity resolution with no options."""
        handler = ErrorHandler()
        result = handler.resolve_ambiguity([])

        assert result["success"] is False
        assert result["selected"] is None

    def test_resolve_single_option(self):
        """Test ambiguity resolution with single option."""
        handler = ErrorHandler()
        options = ["option1"]

        result = handler.resolve_ambiguity(options)

        assert result["success"] is True
        assert result["selected"] == "option1"

    def test_resolve_first_strategy(self):
        """Test ambiguity resolution with first strategy."""
        handler = ErrorHandler()
        options = ["option1", "option2", "option3"]
        context = {"strategy": "first"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"] == "option1"
        assert result["strategy"] == "first"

    def test_resolve_last_strategy(self):
        """Test ambiguity resolution with last strategy."""
        handler = ErrorHandler()
        options = ["option1", "option2", "option3"]
        context = {"strategy": "last"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"] == "option3"
        assert result["strategy"] == "last"

    def test_resolve_highest_score_strategy(self):
        """Test ambiguity resolution with highest score strategy."""
        handler = ErrorHandler()
        options = [
            {"name": "option1", "score": 0.5},
            {"name": "option2", "score": 0.9},
            {"name": "option3", "score": 0.3},
        ]
        context = {"strategy": "highest_score", "score_key": "score"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"]["name"] == "option2"
        assert result["strategy"] == "highest_score"

    def test_resolve_highest_score_missing_key(self):
        """Test ambiguity resolution with missing score key."""
        handler = ErrorHandler()
        options = ["option1", "option2", "option3"]
        context = {"strategy": "highest_score", "score_key": "score"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"] == "option1"  # Falls back to first

    def test_resolve_random_strategy(self):
        """Test ambiguity resolution with random strategy."""
        handler = ErrorHandler()
        options = ["option1", "option2", "option3"]
        context = {"strategy": "random"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"] in options
        assert result["strategy"] == "random"

    def test_resolve_unknown_strategy(self):
        """Test ambiguity resolution with unknown strategy."""
        handler = ErrorHandler()
        options = ["option1", "option2", "option3"]
        context = {"strategy": "unknown"}

        result = handler.resolve_ambiguity(options, context)

        assert result["success"] is True
        assert result["selected"] == "option1"  # Falls back to first


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    def test_handle_error_function(self):
        """Test module-level handle_error function."""
        error = "ModuleNotFoundError: No module named 'test'"
        result = handle_error(error)

        assert result["success"] is True
        assert "solution" in result

    def test_resolve_ambiguity_function(self):
        """Test module-level resolve_ambiguity function."""
        options = ["opt1", "opt2"]
        result = resolve_ambiguity(options)

        assert result["success"] is True
        assert result["selected"] in options

    def test_handle_error_with_field(self):
        """Test handle_error with field parameter."""
        mock_field = MagicMock()
        mock_field.add_conflict = MagicMock()

        error = "TypeError: test error"
        result = handle_error(error, field=mock_field)

        assert result["success"] is True
        mock_field.add_conflict.assert_called_once()
