"""
Unit tests for Calculator class.
Tests all methods with various inputs including edge cases.
"""

import pytest
import math
from src.calculator import Calculator


class TestCalculator:
    """Test suite for Calculator class."""

    @pytest.fixture
    def calculator(self):
        """
        Fixture to create a Calculator instance for each test.
        
        Returns:
            Calculator: Fresh calculator instance
        """
        return Calculator()

    # Tests for add method
    def test_add_positive_numbers(self, calculator):
        """Test addition of two positive numbers."""
        assert calculator.add(5, 3) == 8

    def test_add_negative_numbers(self, calculator):
        """Test addition of two negative numbers."""
        assert calculator.add(-5, -3) == -8

    def test_add_mixed_numbers(self, calculator):
        """Test addition of positive and negative numbers."""
        assert calculator.add(10, -4) == 6

    def test_add_with_zero(self, calculator):
        """Test addition with zero."""
        assert calculator.add(5, 0) == 5
        assert calculator.add(0, 5) == 5

    def test_add_floats(self, calculator):
        """Test addition of floating point numbers."""
        assert calculator.add(2.5, 3.7) == pytest.approx(6.2)

    # Tests for subtract method
    def test_subtract_positive_numbers(self, calculator):
        """Test subtraction of two positive numbers."""
        assert calculator.subtract(10, 4) == 6

    def test_subtract_negative_numbers(self, calculator):
        """Test subtraction of two negative numbers."""
        assert calculator.subtract(-5, -3) == -2

    def test_subtract_mixed_numbers(self, calculator):
        """Test subtraction with negative result."""
        assert calculator.subtract(3, 10) == -7

    def test_subtract_with_zero(self, calculator):
        """Test subtraction with zero."""
        assert calculator.subtract(5, 0) == 5
        assert calculator.subtract(0, 5) == -5

    def test_subtract_floats(self, calculator):
        """Test subtraction of floating point numbers."""
        assert calculator.subtract(10.5, 3.2) == pytest.approx(7.3)

    # Tests for multiply method
    def test_multiply_positive_numbers(self, calculator):
        """Test multiplication of two positive numbers."""
        assert calculator.multiply(6, 7) == 42

    def test_multiply_negative_numbers(self, calculator):
        """Test multiplication of two negative numbers."""
        assert calculator.multiply(-4, -5) == 20

    def test_multiply_mixed_numbers(self, calculator):
        """Test multiplication of positive and negative numbers."""
        assert calculator.multiply(6, -3) == -18

    def test_multiply_with_zero(self, calculator):
        """Test multiplication with zero."""
        assert calculator.multiply(5, 0) == 0
        assert calculator.multiply(0, 5) == 0

    def test_multiply_floats(self, calculator):
        """Test multiplication of floating point numbers."""
        assert calculator.multiply(2.5, 4.0) == pytest.approx(10.0)

    # Tests for divide method
    def test_divide_positive_numbers(self, calculator):
        """Test division of two positive numbers."""
        assert calculator.divide(15, 3) == 5.0

    def test_divide_negative_numbers(self, calculator):
        """Test division of two negative numbers."""
        assert calculator.divide(-20, -4) == 5.0

    def test_divide_mixed_numbers(self, calculator):
        """Test division of positive and negative numbers."""
        assert calculator.divide(20, -5) == -4.0

    def test_divide_with_zero_numerator(self, calculator):
        """Test division with zero as numerator."""
        assert calculator.divide(0, 5) == 0.0

    def test_divide_by_zero(self, calculator):
        """Test that division by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculator.divide(10, 0)

    def test_divide_floats(self, calculator):
        """Test division of floating point numbers."""
        assert calculator.divide(7.5, 2.5) == pytest.approx(3.0)

    # Tests for power method
    def test_power_positive_exponent(self, calculator):
        """Test power with positive exponent."""
        assert calculator.power(2, 8) == 256

    def test_power_zero_exponent(self, calculator):
        """Test power with zero exponent."""
        assert calculator.power(5, 0) == 1

    def test_power_negative_exponent(self, calculator):
        """Test power with negative exponent."""
        assert calculator.power(2, -3) == pytest.approx(0.125)

    def test_power_fractional_exponent(self, calculator):
        """Test power with fractional exponent."""
        assert calculator.power(4, 0.5) == pytest.approx(2.0)

    def test_power_negative_base(self, calculator):
        """Test power with negative base."""
        assert calculator.power(-2, 3) == -8

    def test_power_floats(self, calculator):
        """Test power with floating point numbers."""
        assert calculator.power(2.5, 2) == pytest.approx(6.25)

    # Tests for square_root method
    def test_square_root_positive_number(self, calculator):
        """Test square root of positive number."""
        assert calculator.square_root(16) == 4.0

    def test_square_root_zero(self, calculator):
        """Test square root of zero."""
        assert calculator.square_root(0) == 0.0

    def test_square_root_decimal(self, calculator):
        """Test square root of decimal number."""
        assert calculator.square_root(6.25) == pytest.approx(2.5)

    def test_square_root_large_number(self, calculator):
        """Test square root of large number."""
        assert calculator.square_root(144) == 12.0

    def test_square_root_negative_number(self, calculator):
        """Test that square root of negative number raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            calculator.square_root(-4)

    # Tests for modulo method
    def test_modulo_positive_numbers(self, calculator):
        """Test modulo with two positive numbers."""
        assert calculator.modulo(17, 5) == 2

    def test_modulo_negative_dividend(self, calculator):
        """Test modulo with negative dividend."""
        assert calculator.modulo(-17, 5) == 3  # ✅ Correct: Python modulo behavior

    def test_modulo_negative_divisor(self, calculator):
        """Test modulo with negative divisor."""
        assert calculator.modulo(17, -5) == -3  # ✅ Correct: Python modulo behavior

    def test_modulo_zero_remainder(self, calculator):
        """Test modulo with zero remainder."""
        assert calculator.modulo(15, 5) == 0

    def test_modulo_by_zero(self, calculator):
        """Test that modulo by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot perform modulo with zero divisor"):
            calculator.modulo(10, 0)

    def test_modulo_floats(self, calculator):
        """Test modulo with floating point numbers."""
        assert calculator.modulo(7.5, 2.5) == pytest.approx(0.0)
    
    # Tests for percentage method
    def test_percentage_basic(self, calculator):
        """Test basic percentage calculation."""
        assert calculator.percentage(200, 10) == pytest.approx(20.0)

    def test_percentage_decimal(self, calculator):
        """Test percentage with decimal values."""
        assert calculator.percentage(50, 25) == pytest.approx(12.5)

    def test_percentage_zero(self, calculator):
        """Test percentage of zero."""
        assert calculator.percentage(0, 50) == 0.0

    def test_percentage_hundred(self, calculator):
        """Test 100 percent."""
        assert calculator.percentage(80, 100) == pytest.approx(80.0)

    