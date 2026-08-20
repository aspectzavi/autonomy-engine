"""
Click at tool.

Clicks at absolute screen coordinates -- the fallback for apps with
no accessible UI Automation tree.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ClickAtTool(DesktopTool):
    """
    Click at absolute screen coordinates.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_click_at",
            description=(
                "Click at absolute screen coordinates. Use when the "
                "target has no accessible UI element (a game, a "
                "custom-rendered canvas, etc.) -- prefer "
                "desktop_click_element when possible."
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

        x = context.argument("x")
        y = context.argument("y")

        if x is None or y is None:
            return ToolResult.failure(
                error="'x' and 'y' are required.",
                started_at=started_at,
            )

        try:
            x = int(x)
            y = int(y)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'x' and 'y' must be integers.",
                started_at=started_at,
            )

        button = context.argument("button", "left")
        clicks = context.argument("clicks", 1)

        try:
            clicks = int(clicks)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'clicks' must be an integer.",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.click_at(
            session,
            x,
            y,
            button=button,
            clicks=clicks,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
