"""
Storage backend configuration.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.app.config.schemas.enums import StorageBackend


class StorageBackendSettings(BaseModel):
    """
    Storage backend configuration.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    backend: StorageBackend = Field(
        default=StorageBackend.LOCAL,
        description="Storage backend implementation.",
    )

    root_directory: str = Field(
        default="data",
        description="Root storage directory.",
    )

    create_directories: bool = Field(
        default=True,
        description="Create missing directories automatically.",
    )

    compress_artifacts: bool = Field(
        default=False,
        description="Compress artifacts before storage.",
    )