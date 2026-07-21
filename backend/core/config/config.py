"""
Engine configuration.

Composes all subsystem configurations into a single immutable object.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.core.config.browser import BrowserConfig
from backend.core.config.filesystem import FilesystemConfig
from backend.core.config.llm import LLMConfig
from backend.core.config.runtime import RuntimeConfig
from backend.core.config.security import SecurityConfig


@dataclass(slots=True, frozen=True)
class EngineConfig:
    """
    Root configuration for the autonomy engine.

    Every subsystem receives its configuration from this object.
    """

    runtime: RuntimeConfig = field(
        default_factory=RuntimeConfig,
    )

    filesystem: FilesystemConfig = field(
        default_factory=FilesystemConfig,
    )

    browser: BrowserConfig = field(
        default_factory=BrowserConfig,
    )

    security: SecurityConfig = field(
        default_factory=SecurityConfig,
    )

    llm: LLMConfig = field(
        default_factory=LLMConfig,
    )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return configuration diagnostics.
        """
        return {
            "runtime": self.runtime.diagnostics(),
            "filesystem": self.filesystem.diagnostics(),
            "browser": self.browser.diagnostics(),
            "security": self.security.diagnostics(),
            "llm": self.llm.diagnostics(),
        }