"""
Calculator module providing basic and advanced arithmetic operations.
"""

import math


class Calculator:
    """
    A simple calculator class supporting basic and advanced mathematical operations.
    """

    def add(self, a, b):
        """
        Add two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Sum of a and b
        """
        return a + b

    def subtract(self, a, b):
        """
        Subtract second number from first number.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Difference of a and b
        """
        return a - b

    def multiply(self, a, b):
        """
        Multiply two numbers.

        Args:
            a (float): First number
            b (float): Second number

        Returns:
            float: Product of a and b
        """
        return a * b

    def divide(self, a, b):
        """
        Divide first number by second number.

        Args:
            a (float): Numerator
            b (float): Denominator

        Returns:
            float: Quotient of a and b

        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    def power(self, base, exponent):
        """
        Raise base to the power of exponent.

        Args:
            base (float): Base number
            exponent (float): Exponent

        Returns:
            float: base raised to exponent
        """
        return base**exponent

    def square_root(self, number):
        """
        Calculate square root of a number.

        Args:
            number (float): Number to find square root of

        Returns:
            float: Square root of number

        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(number)

    def modulo(self, a, b):
        """
        Calculate remainder of a divided by b.

        Args:
            a (float): Dividend
            b (float): Divisor

        Returns:
            float: Remainder of a divided by b

        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot perform modulo with zero divisor")
        return a % b

    def percentage(self, number, percent):
        """
        Calculate percentage of a number.

        Args:
            number (float): The base number
            percent (float): The percentage to calculate

        Returns:
            float: The percentage value

        Examples:
            percentage(200, 10) returns 20.0 (10% of 200)
            percentage(50, 25) returns 12.5 (25% of 50)
        """
        return (number * percent) / 100
    