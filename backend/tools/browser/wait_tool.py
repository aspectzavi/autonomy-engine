"""
Wait tool.

Waits for a selector to appear, or for a fixed duration, in the
shared browser session.
"""

from __future__ import annotations

from backend.core.providers.browser.browser_session_manager import (
    BrowserSessionManager,
)
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.browser.base import BrowserTool


class WaitTool(BrowserTool):
    """
    Wait for a selector to appear, or for a fixed timeout.
    """

    def __init__(
        self,
        *,
        sessions: BrowserSessionManager,
    ) -> None:
        super().__init__(
            name="browser_wait",
            description=(
                "Wait for a selector to appear, or for a fixed "
                "number of seconds if no selector is given."
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
        timeout = context.argument("timeout_seconds")

        if selector is not None and not isinstance(selector, str):
            return ToolResult.failure(
                error="'selector' must be a string.",
                started_at=started_at,
            )

        if timeout is not None:
            try:
                timeout = float(timeout)
            except (TypeError, ValueError):
                return ToolResult.failure(
                    error="'timeout_seconds' must be a number.",
                    started_at=started_at,
                )

        session = await self.sessions.get_default_session()

        result = await self.sessions.provider.wait_for(
            session,
            selector=selector,
            timeout=timeout,
        )

        return self.to_tool_result(
            result,
            started_at=started_at,
        )
