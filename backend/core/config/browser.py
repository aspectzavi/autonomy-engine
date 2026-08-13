"""
Browser configuration.

Defines configuration for browser automation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class BrowserConfig:
    """
    Browser automation configuration.
    """

    browser: str = "chromium"

    headless: bool = True

    channel: str | None = None

    viewport_width: int = 1920

    viewport_height: int = 1080

    timeout_ms: int = 30_000

    navigation_timeout_ms: int = 30_000

    downloads_enabled: bool = True

    javascript_enabled: bool = True

    user_agent: str | None = None

    locale: str = "en-US"

    timezone: str = "UTC"

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return browser configuration diagnostics.
        """
        return {
            "browser": self.browser,
            "headless": self.headless,
            "channel": self.channel,
            "viewport": {
                "width": self.viewport_width,
                "height": self.viewport_height,
            },
            "timeout_ms": self.timeout_ms,
            "navigation_timeout_ms": (
                self.navigation_timeout_ms
            ),
            "downloads_enabled": (
                self.downloads_enabled
            ),
            "javascript_enabled": (
                self.javascript_enabled
            ),
            "locale": self.locale,
            "timezone": self.timezone,
            "user_agent": self.user_agent,
        }