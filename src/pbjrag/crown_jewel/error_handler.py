"""
Error Handler Module - Centralized error processing for the Crown Jewel Planner.

This module consolidates error metabolization and ambiguity resolution into a
single, comprehensive system for handling errors and ambiguities.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    Centralized error handling system for the Crown Jewel Planner.
    Consolidates error metabolization and ambiguity resolution.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the error handler with optional configuration.

        Parameters:
        - config: Optional configuration dictionary
        """
        self.config = config or {}

        # Load error patterns and solution templates
        self._error_patterns = self._load_error_patterns()
        self._solution_templates = self._load_solution_templates()

    def _load_error_patterns(self) -> list[dict[str, Any]]:
        """
        Load error patterns from configuration.

        Returns:
        - List of error patterns
        """
        # Get patterns from config or use defaults
        patterns = self.config.get("error_patterns", [])

        if not patterns:
            # Default patterns
            patterns = [
                {
                    "pattern": r"No module named '([^']+)'",
                    "type": "missing_dependency",
                    "extract": lambda m: m.group(1),
                    "solution_type": "install_dependency",
                },
                {
                    "pattern": r"ModuleNotFoundError: No module named '([^']+)'",
                    "type": "missing_dependency",
                    "extract": lambda m: m.group(1),
                    "solution_type": "install_dependency",
                },
                {
                    "pattern": r"ImportError: cannot import name '([^']+)' from '([^']+)'",
                    "type": "missing_import",
                    "extract": lambda m: (m.group(1), m.group(2)),
                    "solution_type": "fix_import",
                },
                {
                    "pattern": r"SyntaxError: (.*) \(([^,]+), line (\d+)\)",
                    "type": "syntax_error",
                    "extract": lambda m: (m.group(1), m.group(2), int(m.group(3))),
                    "solution_type": "fix_syntax",
                },
                {
                    "pattern": r"AttributeError: '([^']+)' object has no attribute '([^']+)'",
                    "type": "missing_attribute",
                    "extract": lambda m: (m.group(1), m.group(2)),
                    "solution_type": "fix_attribute",
                },
                {
                    "pattern": r"TypeError: (.*)",
                    "type": "type_error",
                    "extract": lambda m: m.group(1),
                    "solution_type": "fix_type",
                },
                {
                    "pattern": r"ValueError: (.*)",
                    "type": "value_error",
                    "extract": lambda m: m.group(1),
                    "solution_type": "fix_value",
                },
                {
                    "pattern": (
                        r"FileNotFoundError: \[Errno 2\] No such file or directory: '([^']+)'"
                    ),
                    "type": "missing_file",
                    "extract": lambda m: m.group(1),
                    "solution_type": "create_file",
                },
            ]

        return patterns

    def _load_solution_templates(self) -> dict[str, dict[str, Any]]:
        """
        Load solution templates from configuration.

        Returns:
        - Dictionary of solution templates
        """
        # Get templates from config or use defaults
        templates = self.config.get("solution_templates", {})

        if not templates:
            # Default templates
            templates = {
                "install_dependency": {
                    "action": "install_dependency",
                    "message": "Install the missing dependency: {package}",
                    "command": "pip install {package}",
                },
                "fix_import": {
                    "action": "fix_import",
                    "message": "Fix the import of {name} from {module}",
                    "suggestion": (
                        "Check if {name} exists in {module} or if it needs to be "
                        "imported from a different module."
                    ),
                },
                "fix_syntax": {
                    "action": "fix_syntax",
                    "message": "Fix the syntax error: {error} in {file} at line {line}",
                    "suggestion": (
                        "Review the code at the specified location " "and correct the syntax error."
                    ),
                },
                "fix_attribute": {
                    "action": "fix_attribute",
                    "message": "Fix the missing attribute: {attr} in {obj}",
                    "suggestion": "Check if {attr} exists in {obj} or if it needs to be added.",
                },
                "fix_type": {
                    "action": "fix_type",
                    "message": "Fix the type error: {error}",
                    "suggestion": "Review the code and ensure the types are compatible.",
                },
                "fix_value": {
                    "action": "fix_value",
                    "message": "Fix the value error: {error}",
                    "suggestion": "Review the code and ensure the values are valid.",
                },
                "create_file": {
                    "action": "create_file",
                    "message": "Create the missing file: {file}",
                    "suggestion": "Create the file at the specified location.",
                },
            }

        return templates

    def handle_error(self, error: str | Exception, field: Any | None = None) -> dict[str, Any]:
        """
        Handle an error by metabolizing it and generating a solution.

        Parameters:
        - error: Error to handle (string or exception)
        - field: Optional field container for context

        Returns:
        - Error handling result
        """
        # Convert exception to string if needed
        error_str = str(error)

        logger.error(f"Handling error: {error_str}")

        # Extract error pattern
        error_info = self._extract_error_pattern(error_str)

        if not error_info:
            logger.warning(f"No matching pattern found for error: {error_str}")
            return {
                "success": False,
                "message": f"No matching pattern found for error: {error_str}",
                "error": error_str,
                "solution": None,
            }

        # Find matching solution template
        solution = self._find_matching_template(error_info)

        if not solution:
            logger.warning(
                f"No matching solution template found for error type: {error_info.get('type')}"
            )
            return {
                "success": False,
                "message": (
                    f"No matching solution template found for error type: "
                    f"{error_info.get('type')}"
                ),
                "error": error_str,
                "error_info": error_info,
                "solution": None,
            }

        # Apply the solution template
        applied_solution = self._apply_template(solution, error_info)

        # Add the solution to the field if provided
        if field is not None:
            try:
                field.add_conflict(
                    {
                        "type": error_info.get("type", "unknown"),
                        "error": error_str,
                        "solution": applied_solution,
                    }
                )
            except Exception as e:
                logger.warning(f"Error adding conflict to field: {e}")

        logger.info(f"Generated solution for error: {applied_solution.get('message')}")

        return {
            "success": True,
            "message": "Error handled successfully",
            "error": error_str,
            "error_info": error_info,
            "solution": applied_solution,
        }

    def _extract_error_pattern(self, error_str: str) -> dict[str, Any] | None:
        """
        Extract error pattern from an error string.

        Parameters:
        - error_str: Error string to analyze

        Returns:
        - Extracted error information or None if no match
        """
        for pattern in self._error_patterns:
            match = re.search(pattern["pattern"], error_str)

            if match:
                try:
                    # Extract information using the pattern's extract function
                    extract_fn = pattern["extract"]
                    extracted = extract_fn(match)

                    return {
                        "type": pattern["type"],
                        "solution_type": pattern["solution_type"],
                        "extracted": extracted,
                        "match": match.group(0),
                    }
                except Exception as e:
                    logger.warning(f"Error extracting information from pattern: {e}")

        return None

    def _find_matching_template(self, error_info: dict[str, Any]) -> dict[str, Any] | None:
        """
        Find a matching solution template for an error.

        Parameters:
        - error_info: Extracted error information

        Returns:
        - Matching solution template or None if no match
        """
        solution_type = error_info.get("solution_type")

        if not solution_type:
            return None

        return self._solution_templates.get(solution_type)

    def _apply_template(
        self, template: dict[str, Any], error_info: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply a solution template to an error.

        Parameters:
        - template: Solution template
        - error_info: Extracted error information

        Returns:
        - Applied solution
        """
        # Create a copy of the template
        solution = template.copy()

        # Extract the extracted information
        extracted = error_info.get("extracted")

        # Apply the extracted information to the template
        if isinstance(extracted, tuple):
            # Handle tuple extraction
            if template["action"] == "fix_import":
                solution["message"] = solution["message"].format(
                    name=extracted[0], module=extracted[1]
                )
                solution["suggestion"] = solution["suggestion"].format(
                    name=extracted[0], module=extracted[1]
                )
            elif template["action"] == "fix_syntax":
                solution["message"] = solution["message"].format(
                    error=extracted[0], file=extracted[1], line=extracted[2]
                )
                solution["suggestion"] = solution["suggestion"]
            elif template["action"] == "fix_attribute":
                solution["message"] = solution["message"].format(
                    attr=extracted[1], obj=extracted[0]
                )
                solution["suggestion"] = solution["suggestion"].format(
                    attr=extracted[1], obj=extracted[0]
                )
        else:
            # Handle single value extraction
            if template["action"] == "install_dependency":
                solution["message"] = solution["message"].format(package=extracted)
                solution["command"] = solution["command"].format(package=extracted)
            elif template["action"] == "fix_type" or template["action"] == "fix_value":
                solution["message"] = solution["message"].format(error=extracted)
                solution["suggestion"] = solution["suggestion"]
            elif template["action"] == "create_file":
                solution["message"] = solution["message"].format(file=extracted)
                solution["suggestion"] = solution["suggestion"]

        return solution

    def resolve_ambiguity(
        self, options: list[Any], context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Resolve ambiguity by selecting the best option based on context.

        Parameters:
        - options: List of options to choose from
        - context: Optional context for resolution

        Returns:
        - Resolution result
        """
        if not options:
            return {
                "success": False,
                "message": "No options provided for ambiguity resolution",
                "selected": None,
            }

        if len(options) == 1:
            return {
                "success": True,
                "message": "Only one option available, no ambiguity to resolve",
                "selected": options[0],
            }

        logger.info(f"Resolving ambiguity among {len(options)} options")

        if context is None:
            context = {}

        # Get resolution strategy from context or use default
        strategy = context.get("strategy", "first")

        if strategy == "first":
            # Select the first option
            selected = options[0]
        elif strategy == "last":
            # Select the last option
            selected = options[-1]
        elif strategy == "random":
            # Select a random option
            import random

            selected = random.choice(options)
        elif strategy == "highest_score":
            # Select the option with the highest score
            score_key = context.get("score_key", "score")

            if all(isinstance(opt, dict) and score_key in opt for opt in options):
                selected = max(options, key=lambda opt: opt[score_key])
            else:
                selected = options[0]
                logger.warning(
                    f"Not all options have the score key '{score_key}', "
                    "falling back to first option"
                )
        else:
            # Default to first option
            selected = options[0]
            logger.warning(
                f"Unknown resolution strategy '{strategy}', falling back to first option"
            )

        logger.info(f"Selected option: {selected}")

        return {
            "success": True,
            "message": f"Ambiguity resolved using strategy: {strategy}",
            "strategy": strategy,
            "selected": selected,
            "options": options,
        }


# Singleton instance
error_handler = ErrorHandler()


def handle_error(error: str | Exception, field: Any | None = None) -> dict[str, Any]:
    """
    Handle an error by metabolizing it and generating a solution.

    Parameters:
    - error: Error to handle (string or exception)
    - field: Optional field container for context

    Returns:
    - Error handling result
    """
    global error_handler
    return error_handler.handle_error(error, field)


def resolve_ambiguity(options: list[Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Resolve ambiguity by selecting the best option based on context.

    Parameters:
    - options: List of options to choose from
    - context: Optional context for resolution

    Returns:
    - Resolution result
    """
    global error_handler
    return error_handler.resolve_ambiguity(options, context)
