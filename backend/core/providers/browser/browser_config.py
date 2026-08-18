"""
Browser configuration.

Defines common browser launch and runtime configuration shared by all
browser providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.core.config.browser import (
        BrowserConfig as EngineBrowserConfig,
    )


@dataclass(slots=True)
class BrowserConfig:
    """
    Browser provider configuration.
    """

    headless: bool = False

    viewport_width: int = 1440

    viewport_height: int = 900

    user_agent: str | None = None

    locale: str = "en-US"

    timezone: str = "UTC"

    downloads_path: Path | None = None

    storage_state: Path | None = None

    executable_path: Path | None = None

    slow_mo: int = 0

    timeout: float = 30.0

    navigation_timeout: float = 30.0

    accept_downloads: bool = True

    ignore_https_errors: bool = False

    args: tuple[str, ...] = ()

    environment: dict[str, str] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def viewport(
        self,
    ) -> tuple[int, int]:
        """
        Browser viewport dimensions.
        """

        return (
            self.viewport_width,
            self.viewport_height,
        )

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    @classmethod
    def from_engine_config(
        cls,
        config: "EngineBrowserConfig",
    ) -> "BrowserConfig":
        """
        Build a provider-level BrowserConfig from the engine's
        top-level EngineConfig.browser settings.

        EngineConfig.browser is the config the rest of the engine
        (and its env-var loading) actually populates; this is what
        lets that configuration reach the Playwright provider instead
        of the provider silently always using hardcoded defaults.
        """

        return cls(
            headless=config.headless,
            viewport_width=config.viewport_width,
            viewport_height=config.viewport_height,
            user_agent=config.user_agent,
            locale=config.locale,
            timezone=config.timezone,
            executable_path=None,
            timeout=config.timeout_ms / 1000,
            navigation_timeout=(
                config.navigation_timeout_ms / 1000
            ),
            accept_downloads=config.downloads_enabled,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Configuration diagnostics.
        """

        return {
            "headless": self.headless,
            "viewport": {
                "width": self.viewport_width,
                "height": self.viewport_height,
            },
            "locale": self.locale,
            "timezone": self.timezone,
            "user_agent": self.user_agent,
            "downloads_path": (
                str(self.downloads_path)
                if self.downloads_path is not None
                else None
            ),
            "storage_state": (
                str(self.storage_state)
                if self.storage_state is not None
                else None
            ),
            "executable_path": (
                str(self.executable_path)
                if self.executable_path is not None
                else None
            ),
            "slow_mo": self.slow_mo,
            "timeout": self.timeout,
            "navigation_timeout": self.navigation_timeout,
            "accept_downloads": self.accept_downloads,
            "ignore_https_errors": (
                self.ignore_https_errors
            ),
            "args": self.args,
            "environment": self.environment,
        }