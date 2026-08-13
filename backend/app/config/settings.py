"""
Application settings.

This module exposes the root configuration object for the framework.

All application configuration should be accessed through
`get_settings()`.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field

from backend.app.config.base import BaseConfig
from backend.app.config.sections.api import ApiSettings
from backend.app.config.sections.logging import LoggingSettings
from backend.app.config.sections.browser import BrowserSettings
from backend.app.config.sections.storage import StorageSettings


class Settings(BaseConfig):
    """
    Root application configuration.

    This class composes all configuration sections into a single,
    strongly typed configuration object.
    """

    api: ApiSettings = Field(
        default_factory=ApiSettings,
        description="API configuration.",
    )

    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging configuration.",
    )

    browser: BrowserSettings = Field(
        default_factory=BrowserSettings,
        description="Browser configuration.",
    )

    storage: StorageSettings = Field(
        default_factory=StorageSettings,
        description="Storage configuration.",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton application settings.

    Settings are loaded once per process and cached for the lifetime
    of the application.
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Reload application settings.

    Primarily intended for testing.
    """
    get_settings.cache_clear()
    return get_settings()