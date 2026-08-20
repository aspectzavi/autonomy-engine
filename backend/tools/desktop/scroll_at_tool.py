"""
Scroll at tool.

Scrolls at a screen position.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ScrollAtTool(DesktopTool):
    """
    Scroll at a screen position.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_scroll_at",
            description=(
                "Scroll at a screen position. Positive amount "
                "scrolls up."
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
        amount = context.argument("amount")

        if x is None or y is None or amount is None:
            return ToolResult.failure(
                error="'x', 'y', and 'amount' are required.",
                started_at=started_at,
            )

        try:
            x = int(x)
            y = int(y)
            amount = int(amount)
        except (TypeError, ValueError):
            return ToolResult.failure(
                error="'x', 'y', and 'amount' must be integers.",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.scroll_at(
            session,
            x,
            y,
            amount,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
