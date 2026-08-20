"""
List windows tool.

Lists currently open top-level windows.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ListWindowsTool(DesktopTool):
    """
    List currently open top-level windows.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_list_windows",
            description=(
                "List currently open top-level windows."
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

        result = await self.sessions.provider.list_windows(
            session,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
