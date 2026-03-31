"""
Tests for scheduler validators module.
"""

from unittest.mock import patch

import pytest

from app.scheduler.validators import (
    validate_cron_expression,
    validate_parameters,
)


class TestValidateParameters:
    """Tests for validate_parameters function."""

    def test_validate_parameters_empty_string(self):
        """Test validation with empty string."""
        result = validate_parameters("")
        assert result == ""

    def test_validate_parameters_none(self):
        """Test validation with None."""
        result = validate_parameters(None)
        assert result == ""

    def test_validate_parameters_valid_string(self):
        """Test validation with valid string."""
        result = validate_parameters("  valid params  ")
        assert result == "valid params"

    @patch("app.scheduler.validators.settings")
    def test_validate_parameters_length_boundary(self, mock_settings):
        """Test validation at length boundaries."""
        mock_settings.scheduler_max_parameter_length = 10

        # Should pass at exact length
        result = validate_parameters("1234567890")
        assert result == "1234567890"

        # Should fail when too long
        with pytest.raises(ValueError, match="Parameters too long"):
            validate_parameters("12345678901")


class TestValidateCronExpression:
    """Tests for validate_cron_expression function."""

    def test_validate_cron_expression_valid(self):
        """Test validation with valid cron expression."""
        result = validate_cron_expression("0 0 * * *")
        assert result == "0 0 * * *"

    def test_validate_cron_expression_with_spaces(self):
        """Test validation with spaces around expression."""
        result = validate_cron_expression("  0 0 * * *  ")
        assert result == "0 0 * * *"

    def test_validate_cron_expression_empty(self):
        """Test validation with empty expression."""
        with pytest.raises(ValueError, match="Cron expression cannot be empty"):
            validate_cron_expression("")

    def test_validate_cron_expression_none(self):
        """Test validation with None."""
        with pytest.raises(ValueError, match="Cron expression cannot be empty"):
            validate_cron_expression(None)

    def test_validate_cron_expression_invalid(self):
        """Test validation with invalid cron expression."""
        with pytest.raises(ValueError, match="Invalid cron expression"):
            validate_cron_expression("invalid cron")
