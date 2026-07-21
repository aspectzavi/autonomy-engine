"""
Filesystem configuration.

Defines configuration for filesystem-based tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class FilesystemConfig:
    """
    Filesystem configuration.

    Controls the workspace and filesystem access policies used by
    filesystem tools.
    """

    workspace: Path = Path.cwd()

    allow_absolute_paths: bool = False

    allow_symlinks: bool = False

    create_missing_directories: bool = False

    overwrite_existing_files: bool = False

    max_file_size_bytes: int = 50 * 1024 * 1024

    encoding: str = "utf-8"

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize configuration values.
        """
        object.__setattr__(
            self,
            "workspace",
            self.workspace.expanduser().resolve(),
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return configuration diagnostics.
        """
        return {
            "workspace": str(self.workspace),
            "allow_absolute_paths": (
                self.allow_absolute_paths
            ),
            "allow_symlinks": (
                self.allow_symlinks
            ),
            "create_missing_directories": (
                self.create_missing_directories
            ),
            "overwrite_existing_files": (
                self.overwrite_existing_files
            ),
            "max_file_size_bytes": (
                self.max_file_size_bytes
            ),
            "encoding": self.encoding,
        }