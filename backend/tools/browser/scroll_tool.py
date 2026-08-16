"""
Scroll tool.

Scrolls the shared browser session's page.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class ScrollTool(BrowserTool):
    """
    Scroll the page by a pixel offset.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_scroll",
            description="Scroll the page by a pixel offset.",
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

        x = context.argument("x", 0)
        y = context.argument("y", 0)

        try:
            x = int(x)
            y = int(y)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'x' and 'y' must be integers.",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.scroll(
            session,
            x=x,
            y=y,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
