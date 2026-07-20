"""
Browser launch configuration.

Defines how the browser process is started.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator

from backend.app.config.base import BaseConfig
from backend.app.config.schemas.enums import BrowserEngine


class LaunchSettings(BaseConfig):
    """
    Browser launch configuration.
    """

    engine: BrowserEngine = Field(
        default=BrowserEngine.CHROMIUM,
        description="Browser engine to use.",
    )

    channel: str | None = Field(
        default=None,
        description="Browser release channel (e.g. chrome, msedge).",
    )

    executable_path: Path | None = Field(
        default=None,
        description="Optional browser executable path.",
    )

    headless: bool = Field(
        default=False,
        description="Launch browser in headless mode.",
    )

    devtools: bool = Field(
        default=True,
        description="Open DevTools on startup.",
    )

    slow_mo: int = Field(
        default=50,
        ge=0,
        description="Delay (ms) between browser actions.",
    )

    timeout: int = Field(
        default=30_000,
        ge=1,
        description="Default browser operation timeout (ms).",
    )

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        return value or None