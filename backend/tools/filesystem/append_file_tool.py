"""
Append file tool.

Appends text content to an existing file (or creates it, subject to
the same directory-creation policy as write_file).
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import FilesystemTool


class AppendFileTool(FilesystemTool):
    """
    Append text content to a file.
    """

    def __init__(
        self,
        *,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name="append_file",
            description="Append text content to the end of a file.",
            config=config,
        )

    async def execute(
        self,
        context: ToolContext,
    ) -> ToolResult:
        started_at = datetime.now(UTC)

        if context.is_cancelled:
            return ToolResult.failure(
                error="Tool execution was cancelled.",
                started_at=started_at,
            )

        path_argument = context.argument("path")

        if not isinstance(path_argument, str):
            return ToolResult.failure(
                error="Missing required argument 'path'.",
                started_at=started_at,
            )

        content = context.argument("content")

        if not isinstance(content, str):
            return ToolResult.failure(
                error="Missing required argument 'content'.",
                started_at=started_at,
            )

        encoding = context.argument(
            "encoding",
            self.config.encoding,
        )

        try:
            path = self.resolve_path(path_argument)

            if (
                not path.exists()
                and not path.parent.exists()
                and self.config.create_missing_directories
            ):
                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            self.ensure_exists(path.parent)

            with path.open(
                "a",
                encoding=encoding,
            ) as handle:
                handle.write(content)
        except Exception as exc:  # noqa: BLE001
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={
                "path": str(path),
                "total_size": path.stat().st_size,
                "encoding": encoding,
            },
            started_at=started_at,
            metadata={"tool": self.name},
        )
