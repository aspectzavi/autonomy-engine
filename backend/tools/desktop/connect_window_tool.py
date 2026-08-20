"""
Connect window tool.

Connects the shared desktop session to an already-open window.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ConnectWindowTool(DesktopTool):
    """
    Connect to an already-open window by title, title pattern, or
    process ID.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_connect_window",
            description=(
                "Connect to an already-open window by title, title "
                "pattern (regex), or process ID."
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

        title = context.argument("title")
        title_pattern = context.argument("title_pattern")
        process_id = context.argument("process_id")

        if title is None and title_pattern is None and process_id is None:
            return ToolResult.failure(
                error=(
                    "At least one of 'title', 'title_pattern', or "
                    "'process_id' is required."
                ),
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.connect_window(
            session,
            title=title,
            title_pattern=title_pattern,
            process_id=(
                int(process_id)
                if process_id is not None
                else None
            ),
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
