"""
List directory tool.

Lists files and subdirectories within a workspace directory.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import FilesystemTool


class ListDirectoryTool(FilesystemTool):
    """
    List the contents of a directory.
    """

    def __init__(
        self,
        *,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name="list_directory",
            description=(
                "List files and subdirectories within a directory."
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

        path_argument = context.argument("path", ".")
        recursive = context.argument("recursive", False)

        try:
            path = self.resolve_path(path_argument)
            self.ensure_directory(path)

            iterator = (
                path.rglob("*")
                if recursive
                else path.iterdir()
            )

            entries = sorted(
                (
                    {
                        "name": entry.name,
                        "path": str(
                            entry.relative_to(self.workspace),
                        ),
                        "is_directory": entry.is_dir(),
                        "size": (
                            entry.stat().st_size
                            if entry.is_file()
                            else None
                        ),
                    }
                    for entry in iterator
                ),
                key=lambda item: str(item["path"]),
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={
                "path": str(path),
                "count": len(entries),
                "entries": entries,
            },
            started_at=started_at,
            metadata={"tool": self.name},
        )
