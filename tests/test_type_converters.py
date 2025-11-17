"""Tests for type converters."""

import decimal

import pytest

from luminnexus_alchemy_shared.converters import safe_decimal, safe_int, safe_str


class TestSafeDecimal:
    """Tests for safe_decimal function."""

    def test_valid_string(self):
        """Test conversion of valid decimal string."""
        result = safe_decimal("123.45")
        assert result == decimal.Decimal("123.45000")

    def test_valid_integer(self):
        """Test conversion of integer."""
        result = safe_decimal(42)
        assert result == decimal.Decimal("42.00000")

    def test_valid_float(self):
        """Test conversion of float."""
        result = safe_decimal(3.14)
        assert result == decimal.Decimal("3.14000")

    def test_less_than_value(self):
        """Test conversion of '<1' format."""
        result = safe_decimal("<1")
        assert result == decimal.Decimal("0.99990")

    def test_none_input(self):
        """Test None input returns None."""
        result = safe_decimal(None)
        assert result is None

    def test_invalid_string(self):
        """Test invalid string returns None."""
        result = safe_decimal("invalid")
        assert result is None

    def test_empty_string(self):
        """Test empty string returns None."""
        result = safe_decimal("")
        assert result is None


class TestSafeInt:
    """Tests for safe_int function."""

    def test_valid_string(self):
        """Test conversion of valid integer string."""
        result = safe_int("42")
        assert result == 42

    def test_float_string(self):
        """Test conversion of float string."""
        result = safe_int("3.14")
        assert result == 3

    def test_none_input(self):
        """Test None input returns None."""
        result = safe_int(None)
        assert result is None

    def test_invalid_string(self):
        """Test invalid string returns None."""
        result = safe_int("invalid")
        assert result is None


class TestSafeStr:
    """Tests for safe_str function."""

    def test_valid_string(self):
        """Test conversion of string with whitespace."""
        result = safe_str("  hello  ")
        assert result == "hello"

    def test_empty_string(self):
        """Test empty string returns None."""
        result = safe_str("")
        assert result is None

    def test_whitespace_only(self):
        """Test whitespace-only string returns None."""
        result = safe_str("   ")
        assert result is None

    def test_none_input(self):
        """Test None input returns None."""
        result = safe_str(None)
        assert result is None

    def test_non_string_input(self):
        """Test non-string input returns None."""
        result = safe_str(123)
        assert result is None
