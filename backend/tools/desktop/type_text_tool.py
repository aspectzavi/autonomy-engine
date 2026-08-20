"""
Type text tool (desktop).

Types text at the current keyboard focus, regardless of which
element or window has focus.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class TypeTextTool(DesktopTool):
    """
    Type text at the current keyboard focus.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_type_text",
            description=(
                "Type text at the current keyboard focus, "
                "regardless of which window or element has focus."
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

        text = context.argument("text")

        if not isinstance(text, str):
            return self.missing_argument(
                "text",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.type_text(
            session,
            text,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
