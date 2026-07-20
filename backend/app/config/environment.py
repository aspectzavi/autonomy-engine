"""
Environment configuration utilities.

This module provides centralized runtime environment detection and
environment-specific helper methods.

The rest of the framework should never read environment variables
directly. Instead, use the helpers provided here.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

import os
from functools import lru_cache

from backend.shared.enums import Environment

_ENVIRONMENT_VARIABLE = "APP_ENV"


@lru_cache(maxsize=1)
def get_environment() -> Environment:
    """
    Return the current application environment.

    Reads the environment from the APP_ENV environment variable.

    Defaults to DEVELOPMENT.

    Returns
    -------
    Environment
        Current application environment.
    """
    value = os.getenv(
        _ENVIRONMENT_VARIABLE,
        Environment.DEVELOPMENT.value,
    ).strip().lower()

    try:
        return Environment(value)
    except ValueError as exc:
        valid = ", ".join(env.value for env in Environment)

        raise RuntimeError(
            f"Invalid APP_ENV '{value}'. "
            f"Expected one of: {valid}."
        ) from exc


def is_development() -> bool:
    """Return True if running in development."""
    return get_environment() is Environment.DEVELOPMENT


def is_testing() -> bool:
    """Return True if running tests."""
    return get_environment() is Environment.TESTING


def is_staging() -> bool:
    """Return True if running in staging."""
    return get_environment() is Environment.STAGING


def is_production() -> bool:
    """Return True if running in production."""
    return get_environment() is Environment.PRODUCTION


def reload_environment() -> Environment:
    """
    Reload the environment.

    Useful during testing when APP_ENV changes.

    Returns
    -------
    Environment
        Newly loaded environment.
    """
    get_environment.cache_clear()
    return get_environment()