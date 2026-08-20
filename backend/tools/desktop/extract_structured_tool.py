"""
Extract structured tool (desktop).

Extracts a generic structured summary of the connected window's UI
tree. Works on any app that exposes a UI Automation tree.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ExtractStructuredTool(DesktopTool):
    """
    Extract a generic structured summary of the connected window.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_extract_structured",
            description=(
                "Extract every control in the connected window's UI "
                "tree: type, name, automation ID, and bounding "
                "rectangle. Works on any app without needing to "
                "know its layout ahead of time."
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

        result = await self.sessions.provider.extract_structured(
            session,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
