"""
Click tool.

Clicks an element in the shared browser session.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class ClickTool(BrowserTool):
    """
    Click an element by CSS selector.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_click",
            description="Click an element by CSS selector.",
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

        selector = context.argument("selector")

        if not isinstance(selector, str) or not selector:
            return self.missing_argument(
                "selector",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.click(
            session,
            selector,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
