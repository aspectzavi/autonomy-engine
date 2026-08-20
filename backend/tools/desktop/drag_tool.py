"""
Drag tool.

Drags the mouse from one point to another.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class DragTool(DesktopTool):
    """
    Drag the mouse from one point to another.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_drag",
            description="Drag the mouse from one point to another.",
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

        required = ("from_x", "from_y", "to_x", "to_y")
        values = {}

        for key in required:
            value = context.argument(key)

            if value is None:
                return self.missing_argument(
                    key,
                    started_at=started_at,
                )

            try:
                values[key] = int(value)
            except (TypeError, ValueError):
                return ToolResult.failure(
                    error=f"'{key}' must be an integer.",
                    started_at=started_at,
                )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.drag(
            session,
            from_x=values["from_x"],
            from_y=values["from_y"],
            to_x=values["to_x"],
            to_y=values["to_y"],
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
