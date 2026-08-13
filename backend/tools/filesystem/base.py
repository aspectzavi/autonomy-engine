"""
Filesystem tool base classes.

Provides common functionality shared by filesystem tools.
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path

from backend.core.config.filesystem import (
    FilesystemConfig,
)
from backend.core.tools.tool import Tool


class FilesystemTool(Tool, ABC):
    """
    Base class for filesystem tools.

    All filesystem access is restricted according to the configured
    filesystem policy.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        config: FilesystemConfig | None = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
        )

        self._config = config or FilesystemConfig()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def config(
        self,
    ) -> FilesystemConfig:
        """
        Filesystem configuration.
        """
        return self._config

    @property
    def workspace(
        self,
    ) -> Path:
        """
        Workspace root directory.
        """
        return self.config.workspace

    # ------------------------------------------------------------------
    # Path Resolution
    # ------------------------------------------------------------------

    def resolve_path(
        self,
        value: str,
    ) -> Path:
        """
        Resolve a path according to the configured filesystem policy.
        """
        path = Path(value).expanduser()

        if path.is_absolute():
            if not self.config.allow_absolute_paths:
                raise PermissionError(
                    "Absolute paths are not permitted."
                )
        else:
            path = self.workspace / path

        path = path.resolve()

        if (
            path.is_symlink()
            and not self.config.allow_symlinks
        ):
            raise PermissionError(
                "Symbolic links are not permitted."
            )

        self.ensure_workspace(path)

        return path

    def ensure_workspace(
        self,
        path: Path,
    ) -> None:
        """
        Ensure a path resides inside the configured workspace.
        """
        try:
            path.relative_to(
                self.workspace,
            )
        except ValueError as exc:
            raise PermissionError(
                f"Path outside workspace: {path}"
            ) from exc

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def ensure_exists(
        self,
        path: Path,
    ) -> None:
        """
        Ensure the path exists.
        """
        if not path.exists():
            raise FileNotFoundError(path)

    def ensure_file(
        self,
        path: Path,
    ) -> None:
        """
        Ensure the path refers to a file.
        """
        self.ensure_exists(path)

        if not path.is_file():
            raise IsADirectoryError(path)

        size = path.stat().st_size

        if (
            size
            > self.config.max_file_size_bytes
        ):
            raise ValueError(
                "File exceeds configured maximum size."
            )

    def ensure_directory(
        self,
        path: Path,
    ) -> None:
        """
        Ensure the path refers to a directory.
        """
        self.ensure_exists(path)

        if not path.is_dir():
            raise NotADirectoryError(path)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return tool diagnostics.
        """
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "filesystem": (
                    self.config.diagnostics()
                ),
            }
        )

        return diagnostics