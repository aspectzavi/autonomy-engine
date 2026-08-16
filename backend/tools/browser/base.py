"""
Browser tool base class.

Shared foundation for every browser automation tool. Each tool
translates a Tool.execute(context) call into a single deterministic
BrowserProvider action against the shared default session -- no LLM
call happens inside a tool itself, keeping per-action cost at zero
regardless of provider (Playwright today; a BrowserUse-backed provider
can be swapped in later behind the same BrowserProvider interface for
tasks that need it).
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.providers.provider_result import (
    ProviderResult,
)
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class BrowserTool(Tool):
    """
    Base class for tools that drive the browser subsystem.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._sessions = sessions

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def sessions(
        self,
    ) -> BrowserSessionManager:
        """
        Shared browser session manager.
        """

        return self._sessions

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def to_tool_result(
        result: ProviderResult,
        *,
        started_at: datetime | None = None,
    ) -> ToolResult:
        """
        Convert a ProviderResult into a ToolResult.
        """

        if result.success:
            return ToolResult.ok(
                output=result.output,
                started_at=started_at or result.started_at,
            )

        return ToolResult.failure(
            error=result.error or "Browser action failed.",
            started_at=started_at or result.started_at,
        )

    @staticmethod
    def missing_argument(
        name: str,
        *,
        started_at: datetime | None = None,
    ) -> ToolResult:
        """
        Build a standard failure result for a missing argument.
        """

        return ToolResult.failure(
            error=f"Missing required argument '{name}'.",
            started_at=started_at,
        )

    @staticmethod
    def now() -> datetime:
        """
        Current UTC time, for started_at timestamps.
        """

        return datetime.now(UTC)
