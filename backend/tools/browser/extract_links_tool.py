"""
Extract links tool.

Extracts every link on the current page: href, visible text, and rel
attribute. Works on any site.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class ExtractLinksTool(BrowserTool):
    """
    Extract every link on the current page.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_extract_links",
            description="Extract every link on the current page.",
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

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.extract_links(
            session,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
