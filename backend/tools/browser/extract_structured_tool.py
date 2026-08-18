"""
Extract structured tool.

Extracts a generic structured summary (title, headings, text, links,
images, tables) of the current page. Works on any site -- unlike
click()/fill(), this needs no site-specific selector.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class ExtractStructuredTool(BrowserTool):
    """
    Extract a generic structured summary of the current page.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_extract_structured",
            description=(
                "Extract a structured summary of the current page: "
                "title, headings, text, links, images, and tables."
            ),
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

        result = await self.sessions.provider.extract_structured(
            session,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
