"""
Click element tool.

Clicks an element in the connected window, matched by name,
automation ID, and/or control type.
"""

from __future__ import annotations

from backend.core.providers.desktop.desktop_session_manager import (
    DesktopSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.desktop.base import DesktopTool


class ClickElementTool(DesktopTool):
    """
    Click an element in the connected window.
    """

    def __init__(
        self,
        *,
        sessions: DesktopSessionManager,
    ) -> None:
        super().__init__(
            name="desktop_click_element",
            description=(
                "Click an element in the connected window, matched "
                "by name, automation ID, and/or control type."
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

        name = context.argument("name")
        automation_id = context.argument("automation_id")
        control_type = context.argument("control_type")

        if name is None and automation_id is None and control_type is None:
            return ToolResult.failure(
                error=(
                    "At least one of 'name', 'automation_id', or "
                    "'control_type' is required."
                ),
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.click_element(
            session,
            name=name,
            automation_id=automation_id,
            control_type=control_type,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
