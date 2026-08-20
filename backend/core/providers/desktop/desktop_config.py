"""
Desktop configuration.

Defines common desktop automation configuration shared by all desktop
providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DesktopConfig:
    """
    Desktop provider configuration.
    """

    #
    # UI Automation backend pywinauto uses: "uia" (modern, works with
    # most apps including UWP/WinForms/WPF/Electron/Chromium) or
    # "win32" (legacy MSAA, faster but narrower app support).
    #
    backend: str = "uia"

    #
    # Default timeout (seconds) for element/window lookups.
    #
    timeout: float = 10.0

    #
    # Delay (seconds) pyautogui waits between individual actions.
    # Not per-call latency -- a small pause between primitive
    # mouse/keyboard events, which real UI automation generally
    # needs for reliability.
    #
    action_pause: float = 0.1

    #
    # Whether pyautogui's failsafe is enabled (aborts any pyautogui
    # call if the mouse is moved to a screen corner). Should stay
    # True outside of deliberate, controlled testing -- it's the
    # only manual kill-switch available for the coordinate-based
    # fallback actions.
    #
    failsafe: bool = True

    #
    # Extra environment variables for launched processes.
    #
    environment: dict[str, str] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return config diagnostics.
        """

        return {
            "backend": self.backend,
            "timeout": self.timeout,
            "action_pause": self.action_pause,
            "failsafe": self.failsafe,
        }
