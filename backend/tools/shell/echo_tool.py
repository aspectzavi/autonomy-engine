"""
Echo tool.

A simple tool that returns the supplied message.

This tool is primarily intended for validating the complete tool
execution pipeline.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.core.tools.tool import Tool


class EchoTool(Tool):
    """
    Tool that echoes a supplied message.
    """

    def __init__(self) -> None:
        super().__init__(
            name="echo",
            description="Return the supplied message.",
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        """
        Execute the echo tool.
        """
        started_at = datetime.now(UTC)

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        message = context.argument(
            "message",
        )

        if message is None:
            return ToolResult.failure(
                error=(
                    "Missing required argument "
                    "'message'."
                ),
                started_at=started_at,
            )

        return ToolResult.ok(
            output=str(message),
            started_at=started_at,
            metadata={
                "tool": self.name,
            },
        )