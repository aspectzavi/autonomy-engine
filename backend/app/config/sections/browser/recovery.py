"""
Browser recovery and timeout configuration.
"""

from __future__ import annotations

from pydantic import Field

from backend.app.config.schemas.enums import WaitStrategy

from .base import BrowserConfigSection


class RecoverySettings(BrowserConfigSection):
    """
    Configuration controlling browser recovery behavior.
    """

    max_retries: int = Field(
        default=3,
        ge=0,
        le=20,
        description="Maximum retry attempts.",
    )

    action_timeout: int = Field(
        default=30_000,
        ge=1,
        description="Action timeout in milliseconds.",
    )

    navigation_timeout: int = Field(
        default=60_000,
        ge=1,
        description="Navigation timeout in milliseconds.",
    )

    wait_strategy: WaitStrategy = Field(
        default=WaitStrategy.NETWORKIDLE,
        description="Default page wait strategy.",
    )

    refresh_on_failure: bool = Field(
        default=True,
        description="Refresh the page before retrying.",
    )

    screenshot_before_retry: bool = Field(
        default=True,
        description="Capture a screenshot before retrying.",
    )

    recreate_context_after_failure: bool = Field(
        default=False,
        description="Recreate the browser context after repeated failures.",
    )

    exponential_backoff: bool = Field(
        default=True,
        description="Use exponential backoff between retries.",
    )

    backoff_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        le=10.0,
        description="Exponential backoff multiplier.",
    )