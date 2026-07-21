"""
Security configuration.

Defines security policies governing autonomous agent capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class SecurityConfig:
    """
    Security policy configuration.

    Controls which privileged capabilities are available to the
    autonomy engine.
    """

    allow_shell: bool = True

    allow_python: bool = True

    allow_browser: bool = True

    allow_filesystem: bool = True

    allow_network: bool = True

    allow_subprocesses: bool = True

    sandbox_enabled: bool = False

    allowed_domains: tuple[str, ...] = field(
        default_factory=tuple,
    )

    blocked_commands: tuple[str, ...] = field(
        default_factory=tuple,
    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return security configuration diagnostics.
        """
        return {
            "allow_shell": self.allow_shell,
            "allow_python": self.allow_python,
            "allow_browser": self.allow_browser,
            "allow_filesystem": self.allow_filesystem,
            "allow_network": self.allow_network,
            "allow_subprocesses": (
                self.allow_subprocesses
            ),
            "sandbox_enabled": (
                self.sandbox_enabled
            ),
            "allowed_domains": (
                self.allowed_domains
            ),
            "blocked_commands": (
                self.blocked_commands
            ),
        }