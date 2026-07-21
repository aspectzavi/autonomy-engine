"""
Read file tool.

Reads the contents of a text file.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import (
    FilesystemTool,
)


class ReadFileTool(FilesystemTool):
    """
    Read a UTF-8 text file.
    """

    def __init__(self) -> None:
        super().__init__(
            name="read_file",
            description="Read a text file.",
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        """
        Read a text file.
        """
        started_at = datetime.now(UTC)

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        path_argument = context.argument(
            "path",
        )

        if not isinstance(path_argument, str):
            return ToolResult.failure(
                error="Missing required argument 'path'.",
                started_at=started_at,
            )

        encoding = context.argument(
            "encoding",
            "utf-8",
        )

        try:
            path = self.resolve_path(
                path_argument,
            )

            self.ensure_file(
                path,
            )

            content = path.read_text(
                encoding=encoding,
            )

        except Exception as exc:
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={
                "path": str(path),
                "content": content,
                "encoding": encoding,
                "size": path.stat().st_size,
            },
            started_at=started_at,
            metadata={
                "tool": self.name,
            },
        )