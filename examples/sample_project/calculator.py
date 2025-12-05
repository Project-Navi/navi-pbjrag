"""
Calculator module - A simple calculator with various operations.

This module demonstrates good code quality practices.
"""

import logging
from typing import List, Union

logger = logging.getLogger(__name__)


class Calculator:
    """
    A calculator class supporting basic arithmetic operations.

    This class maintains a history of operations and provides
    clear error handling.
    """

    def __init__(self):
        """Initialize calculator with empty history."""
        self.history: List[str] = []
        logger.info("Calculator initialized")

    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Sum of a and b
        """
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        logger.debug(f"Addition: {a} + {b} = {result}")
        return result

    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtract b from a.

        Args:
            a: Number to subtract from
            b: Number to subtract

        Returns:
            Difference of a and b
        """
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        logger.debug(f"Subtraction: {a} - {b} = {result}")
        return result

    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiply two numbers.

        Args:
            a: First number
            b: Second number

        Returns:
            Product of a and b
        """
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide a by b.

        Args:
            a: Numerator
            b: Denominator

        Returns:
            Quotient of a and b

        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            logger.error("Attempted division by zero")
            raise ValueError("Cannot divide by zero")

        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def get_history(self) -> List[str]:
        """
        Get the calculation history.

        Returns:
            List of calculation strings
        """
        return self.history.copy()

    def clear_history(self):
        """Clear the calculation history."""
        self.history.clear()
        logger.info("History cleared")
