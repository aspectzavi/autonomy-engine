"""
Copy file tool.

Copies a file from one workspace path to another.
"""

from __future__ import annotations

import shutil
from datetime import UTC, datetime

from backend.core.config.filesystem import FilesystemConfig
from backend.core.tools.context import ToolContext
from backend.core.tools.result import ToolResult
from backend.tools.filesystem.base import FilesystemTool


class CopyFileTool(FilesystemTool):
    """
    Copy a file.
    """

    def __init__(
        self,
        *,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name="copy_file",
            description="Copy a file to a new path within the workspace.",
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

        source_argument = context.argument("source")
        destination_argument = context.argument("destination")

        if not isinstance(source_argument, str):
            return ToolResult.failure(
                error="Missing required argument 'source'.",
                started_at=started_at,
            )

        if not isinstance(destination_argument, str):
            return ToolResult.failure(
                error="Missing required argument 'destination'.",
                started_at=started_at,
            )

        try:
            source = self.resolve_path(source_argument)
            destination = self.resolve_path(
                destination_argument,
            )

            self.ensure_file(source)

            if (
                destination.exists()
                and not self.config.overwrite_existing_files
            ):
                raise FileExistsError(
                    f"Destination already exists and overwrite is "
                    f"disabled: {destination}",
                )

            if (
                not destination.parent.exists()
                and self.config.create_missing_directories
            ):
                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            self.ensure_exists(destination.parent)

            shutil.copy2(source, destination)
        except Exception as exc:  # noqa: BLE001
            return ToolResult.failure(
                error=str(exc),
                started_at=started_at,
            )

        return ToolResult.ok(
            output={
                "source": str(source),
                "destination": str(destination),
            },
            started_at=started_at,
            metadata={"tool": self.name},
        )
