"""
Delete file tool.

Deletes a file within the workspace.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import FilesystemTool


class DeleteFileTool(FilesystemTool):
    """
    Delete a file.
    """

    def __init__(
        self,
        *,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name="delete_file",
            description="Delete a file within the workspace.",
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

        try:
            path = self.resolve_path(path_argument)
            self.ensure_file(path)
            path.unlink()
        except Exception as exc:  # noqa: BLE001
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={"path": str(path), "deleted": True},
            started_at=started_at,
            metadata={"tool": self.name},
        )
