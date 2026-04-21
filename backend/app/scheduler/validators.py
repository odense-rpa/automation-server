"""
Validation functions for scheduler parameters and configurations.

This module contains validation logic extracted from the original scheduler
to provide reusable and testable validation functions.
"""

from datetime import datetime

from cronsim import CronSim, CronSimError

from app.config import settings


def validate_parameters(parameters: str) -> str:
    """Simple parameter validation for trigger parameters.

    Args:
        parameters: Raw parameter string from trigger

    Returns:
        Cleaned parameter string

    Raises:
        ValueError: If parameters are too long
    """
    if not parameters:
        return ""

    # Simple length check for basic protection
    if len(parameters) > settings.scheduler_max_parameter_length:
        raise ValueError(
            f"Parameters too long (max {settings.scheduler_max_parameter_length} characters)"
        )

    return parameters.strip()


def validate_cron_expression(cron_expr: str) -> str:
    """Simple cron expression validation.

    Args:
        cron_expr: Cron expression string

    Returns:
        Validated cron expression

    Raises:
        ValueError: If cron expression is invalid
    """
    if not cron_expr or not cron_expr.strip():
        raise ValueError("Cron expression cannot be empty")

    cron_expr = cron_expr.strip()

    try:
        # Let cronsim handle all validation
        # We use a dummy datetime just for validation
        CronSim(cron_expr, datetime.now())
    except CronSimError as e:
        raise ValueError(f"Invalid cron expression: {e}")

    return cron_expr
