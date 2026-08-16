"""
Press key tool.

Presses a keyboard key in the shared browser session.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class PressKeyTool(BrowserTool):
    """
    Press a keyboard key (e.g. "Enter", "Tab", "Escape").
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_press_key",
            description="Press a keyboard key.",
            sessions=sessions,
        )

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        started_at = self.now()

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        key = context.argument("key")

        if not isinstance(key, str) or not key:
            return self.missing_argument(
                "key",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.press(
            session,
            key,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
