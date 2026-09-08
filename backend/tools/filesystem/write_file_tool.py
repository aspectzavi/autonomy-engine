"""
Write file tool.

Writes text content to a file.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import FilesystemTool


class WriteFileTool(FilesystemTool):
    """
    Write text content to a file.
    """

    def __init__(
        self,
        *,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name="write_file",
            description=(
                "Write text content to a file, creating it if it "
                "doesn't exist."
            ),
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
                path.exists()
                and not self.config.overwrite_existing_files
            ):
                raise FileExistsError(
                    f"File already exists and overwrite is "
                    f"disabled: {path}",
                )

            if (
                not path.parent.exists()
                and self.config.create_missing_directories
            ):
                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            self.ensure_exists(path.parent)

            path.write_text(
                content,
                encoding=encoding,
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={
                "path": str(path),
                "bytes_written": path.stat().st_size,
                "encoding": encoding,
            },
            started_at=started_at,
            metadata={"tool": self.name},
        )
