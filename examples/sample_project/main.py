"""
Main application entry point.

This module demonstrates mixed code quality with some good practices
and some areas for improvement.
"""

import sys
from calculator import Calculator
from utils import parse_expression, validate_input, is_numeric, format_number


def main():
    """Main application loop - decent implementation."""
    print("🥜🍇 PBJRAG Sample Calculator")
    print("=" * 40)
    print("Enter expressions like: 5 + 3")
    print("Commands: history, clear, quit")
    print("=" * 40)

    calc = Calculator()

    while True:
        try:
            user_input = input("\n> ").strip()

            # Handle commands
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            elif user_input.lower() == 'history':
                show_history(calc)
                continue
            elif user_input.lower() == 'clear':
                calc.clear_history()
                print("History cleared!")
                continue

            # Validate input
            if not validate_input(user_input):
                print("❌ Invalid input")
                continue

            # Parse and calculate
            result = calculate(calc, user_input)
            if result is not None:
                print(f"✅ Result: {result}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def calculate(calc, expression):
    """Calculate expression - missing type hints and docstring."""
    # This function works but documentation is poor
    try:
        num1, op, num2 = parse_expression(expression)

        if op == '+':
            return calc.add(num1, num2)
        elif op == '-':
            return calc.subtract(num1, num2)
        elif op == '*':
            return calc.multiply(num1, num2)
        elif op == '/':
            return calc.divide(num1, num2)
        else:
            print("❌ Unsupported operator")
            return None

    except ValueError as e:
        print(f"❌ {e}")
        return None


def show_history(calc):
    """Display calculation history - acceptable implementation."""
    history = calc.get_history()

    if not history:
        print("No history yet!")
        return

    print("\n📜 Calculation History:")
    print("-" * 40)
    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry}")
    print("-" * 40)
    print(f"Total calculations: {format_number(len(history))}")


# Poor practice: Code outside functions
if __name__ == "__main__":
    # Should have better error handling at top level
    main()
