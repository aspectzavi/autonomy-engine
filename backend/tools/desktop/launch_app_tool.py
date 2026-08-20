"""
Launch app tool.

Launches a new process and connects the shared desktop session to
its window.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class LaunchAppTool(DesktopTool):
    """
    Launch an application and connect to its window.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_launch_app",
            description=(
                "Launch an application (by path or command) and "
                "connect the desktop session to its window."
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

        path = context.argument("path")

        if not isinstance(path, str) or not path:
            return self.missing_argument(
                "path",
                started_at=started_at,
            )

        arguments = context.argument("arguments", ())

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.launch(
            session,
            path,
            arguments=tuple(arguments),
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
