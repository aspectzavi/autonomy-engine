"""
Navigate tool.

Navigates the shared browser session to a URL.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class NavigateTool(BrowserTool):
    """
    Navigate the browser to a URL.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_navigate",
            description="Navigate the browser to a URL.",
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

        url = context.argument("url")

        if not isinstance(url, str) or not url:
            return self.missing_argument(
                "url",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.navigate(
            session,
            url,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
