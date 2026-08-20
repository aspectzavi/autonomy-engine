"""
Move mouse tool.

Moves the mouse to absolute screen coordinates.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class MoveMouseTool(DesktopTool):
    """
    Move the mouse to absolute screen coordinates.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_move_mouse",
            description="Move the mouse to absolute screen coordinates.",
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

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.move_to(
            session,
            x,
            y,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
