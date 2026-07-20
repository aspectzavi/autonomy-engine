"""
Filesystem path management.

Provides centralized, validated access to all filesystem locations used
by the framework.

The PathManager is responsible for:

- discovering the project root
- exposing commonly used directories
- creating required runtime directories
- validating writable locations
- supporting future workspace isolation

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path

from backend.app.config.constants import (
    ARTIFACT_DIRECTORY_NAME,
    DATA_DIRECTORY_NAME,
    LOG_DIRECTORY_NAME,
    PROJECT_ROOT,
    SCREENSHOT_DIRECTORY_NAME,
    TEMP_DIRECTORY_NAME,
    VIDEO_DIRECTORY_NAME,
)


class PathManager:
    """
    Centralized filesystem path manager.

    This class provides lazily evaluated paths for all framework
    directories and ensures required runtime directories exist.
    """

    def __init__(self, root: Path | None = None) -> None:
        """
        Initialize the path manager.

        Parameters
        ----------
        root:
            Optional project root. If omitted, PROJECT_ROOT is used.
        """
        self._root = root or PROJECT_ROOT

    @property
    def root(self) -> Path:
        """Return the project root directory."""
        return self._root

    @cached_property
    def backend(self) -> Path:
        return self.root / "backend"

    @cached_property
    def logs(self) -> Path:
        return self.root / LOG_DIRECTORY_NAME

    @cached_property
    def data(self) -> Path:
        return self.root / DATA_DIRECTORY_NAME

    @cached_property
    def screenshots(self) -> Path:
        return self.root / SCREENSHOT_DIRECTORY_NAME

    @cached_property
    def recordings(self) -> Path:
        return self.root / VIDEO_DIRECTORY_NAME

    @cached_property
    def artifacts(self) -> Path:
        return self.root / ARTIFACT_DIRECTORY_NAME

    @cached_property
    def temp(self) -> Path:
        return self.root / TEMP_DIRECTORY_NAME

    def create_directories(self) -> None:
        """
        Create all runtime directories if they do not already exist.
        """
        for directory in (
            self.logs,
            self.data,
            self.screenshots,
            self.recordings,
            self.artifacts,
            self.temp,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """
        Validate that runtime directories are writable.

        Raises
        ------
        PermissionError
            If a directory cannot be written to.
        """
        self.create_directories()

        for directory in (
            self.logs,
            self.data,
            self.screenshots,
            self.recordings,
            self.artifacts,
            self.temp,
        ):
            if not os.access(directory, os.W_OK):
                raise PermissionError(
                    f"Directory is not writable: {directory}"
                )

    def as_dict(self) -> dict[str, Path]:
        """
        Return all managed paths.

        Returns
        -------
        dict[str, Path]
        """
        return {
            "root": self.root,
            "backend": self.backend,
            "logs": self.logs,
            "data": self.data,
            "screenshots": self.screenshots,
            "recordings": self.recordings,
            "artifacts": self.artifacts,
            "temp": self.temp,
        }
    
    def workspace(self, execution_id: str) -> Path:
        """
        Return the workspace directory for a specific execution.

        The directory is created automatically if it does not exist.
        """
        workspace = self.artifacts / execution_id
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace


paths = PathManager()