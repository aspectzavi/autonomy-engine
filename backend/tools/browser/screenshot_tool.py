"""
Screenshot tool.

Captures a screenshot of the current page as base64-encoded PNG data,
so the result stays JSON-serializable for callers that need it.
"""

from __future__ import annotations

import base64

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class ScreenshotTool(BrowserTool):
    """
    Capture a screenshot of the current page.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_screenshot",
            description=(
                "Capture a screenshot of the current page."
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

        result = await self.sessions.provider.screenshot(
            session,
        )

        if not result.success:
            return self.to_tool_result(
                result,
                started_at=started_at,
            )

        image_bytes = result.output

        encoded = (
            base64.b64encode(image_bytes).decode("ascii")
            if isinstance(image_bytes, (bytes, bytearray))
            else image_bytes
        )

        return ToolResult.ok(
            output={
                "format": "png",
                "encoding": "base64",
                "data": encoded,
            },
            started_at=started_at,
        )
