"""
Screenshot tool (desktop).

Captures a screenshot of the connected window (or the full screen if
none is connected), as base64-encoded PNG data.
"""

from __future__ import annotations

import base64

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ScreenshotTool(DesktopTool):
    """
    Capture a screenshot of the connected window or full screen.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_screenshot",
            description=(
                "Capture a screenshot of the connected window, or "
                "the full screen if none is connected."
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
