"""
Press key tool (desktop).

Presses a key or key combination (e.g. "enter", "ctrl+c").
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class PressKeyTool(DesktopTool):
    """
    Press a key or key combination.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_press_key",
            description=(
                "Press a key or key combination, e.g. 'enter' or "
                "'ctrl+c'."
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

        key = context.argument("key")

        if not isinstance(key, str) or not key:
            return self.missing_argument(
                "key",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.press_key(
            session,
            key,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
