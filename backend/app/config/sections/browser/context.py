"""
Browser context configuration.

Defines browser context settings such as viewport, locale, timezone,
permissions, and user agent.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from .base import BrowserConfigSection


class ContextSettings(BrowserConfigSection):
    """
    Browser context configuration.
    """

    viewport_width: int = Field(
        default=1440,
        ge=320,
        description="Viewport width in pixels.",
    )

    viewport_height: int = Field(
        default=900,
        ge=240,
        description="Viewport height in pixels.",
    )

    locale: str = Field(
        default="en-US",
        description="Browser locale.",
    )

    timezone: str = Field(
        default="UTC",
        description="Browser timezone.",
    )

    user_agent: str | None = Field(
        default=None,
        description="Override browser user agent.",
    )

    java_script_enabled: bool = Field(
        default=True,
        description="Enable JavaScript execution.",
    )

    ignore_https_errors: bool = Field(
        default=False,
        description="Ignore HTTPS certificate errors.",
    )

    bypass_csp: bool = Field(
        default=False,
        description="Bypass Content Security Policy.",
    )

    accept_downloads: bool = Field(
        default=True,
        description="Automatically accept downloads.",
    )

    @field_validator("locale", "timezone")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value