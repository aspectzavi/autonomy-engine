"""
Download tool.

Clicks an element that triggers a file download and saves the result
to a local path.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class DownloadTool(BrowserTool):
    """
    Trigger and save a file download.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_download",
            description=(
                "Click an element that triggers a download and "
                "save the downloaded file to a local path."
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

        trigger_selector = context.argument(
            "trigger_selector",
        )

        if (
            not isinstance(trigger_selector, str)
            or not trigger_selector
        ):
            return self.missing_argument(
                "trigger_selector",
                started_at=started_at,
            )

        destination = context.argument("destination")

        if not isinstance(destination, str) or not destination:
            return self.missing_argument(
                "destination",
                started_at=started_at,
            )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.download(
            session,
            trigger_selector=trigger_selector,
            destination=destination,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
