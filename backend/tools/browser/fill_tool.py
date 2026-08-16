"""
Fill tool.

Types text into an input element in the shared browser session.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class FillTool(BrowserTool):
    """
    Type text into an element by CSS selector.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_fill",
            description=(
                "Type text into an input element by CSS selector."
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

        selector = context.argument("selector")

        if not isinstance(selector, str) or not selector:
            return self.missing_argument(
                "selector",
                started_at=started_at,
            )

        text = context.argument("text")

        if not isinstance(text, str):
            return self.missing_argument(
                "text",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.type(
            session,
            selector,
            text,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
