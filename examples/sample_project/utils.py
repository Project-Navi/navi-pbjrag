"""
Utility functions - Various helper functions.

This module has mixed quality code to demonstrate different blessing tiers.
"""

import re


def format_number(n):
    """Format a number - POORLY DOCUMENTED"""
    # No type hints, no docstring details
    if n > 1000:
        return f"{n/1000:.1f}K"
    return str(n)


def validate_input(user_input):
    """
    Validate user input string.

    Args:
        user_input: String to validate

    Returns:
        bool: True if valid
    """
    # Mediocre implementation - works but could be better
    if not user_input:
        return False
    if len(user_input) > 100:
        return False
    return True


def parse_expression(expr: str) -> tuple:
    """
    Parse a mathematical expression string.

    This is a well-documented function that properly parses
    simple mathematical expressions.

    Args:
        expr: Expression string like "5 + 3" or "10 * 2"

    Returns:
        tuple: (operand1, operator, operand2)

    Raises:
        ValueError: If expression format is invalid

    Examples:
        >>> parse_expression("5 + 3")
        (5.0, '+', 3.0)
        >>> parse_expression("10 * 2")
        (10.0, '*', 2.0)
    """
    # Clean the expression
    expr = expr.strip()

    # Match pattern: number operator number
    pattern = r'^([+-]?\d+\.?\d*)\s*([+\-*/])\s*([+-]?\d+\.?\d*)$'
    match = re.match(pattern, expr)

    if not match:
        raise ValueError(f"Invalid expression format: {expr}")

    num1, operator, num2 = match.groups()

    try:
        operand1 = float(num1)
        operand2 = float(num2)
    except ValueError as e:
        raise ValueError(f"Invalid number in expression: {e}")

    return operand1, operator, operand2


# Bad practice: Unused function with no documentation
def old_function(x, y):
    return x + y + 42


def quick_calc(x, y, op):
    """Quick calculation - minimal error handling"""
    # This function works but has poor error handling
    if op == '+':
        return x + y
    elif op == '-':
        return x - y
    elif op == '*':
        return x * y
    elif op == '/':
        return x / y  # No division by zero check!
    else:
        return None


def is_numeric(value: str) -> bool:
    """
    Check if a string represents a numeric value.

    Well-implemented utility function with proper error handling.

    Args:
        value: String to check

    Returns:
        True if string is numeric, False otherwise

    Examples:
        >>> is_numeric("123")
        True
        >>> is_numeric("12.34")
        True
        >>> is_numeric("abc")
        False
    """
    if not isinstance(value, str):
        return False

    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
