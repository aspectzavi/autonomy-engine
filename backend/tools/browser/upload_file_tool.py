"""
Upload file tool.

Attaches a local file to a file-input element in the shared browser
session.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class UploadFileTool(BrowserTool):
    """
    Attach a local file to a file-input element.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_upload_file",
            description=(
                "Attach a local file to a file-input element."
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

        selector = context.argument("selector")

        if not isinstance(selector, str) or not selector:
            return self.missing_argument(
                "selector",
                started_at=started_at,
            )

        file_path = context.argument("file_path")

        if not isinstance(file_path, str) or not file_path:
            return self.missing_argument(
                "file_path",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.upload(
            session,
            selector,
            file_path,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
