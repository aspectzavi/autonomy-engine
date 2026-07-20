"""
Browser download configuration.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from .filesystem import DirectorySettings


class DownloadSettings(DirectorySettings):
    """
    Download configuration.
    """

    directory: Path = Field(
        default=Path("data/downloads"),
    )

    preserve_downloads: bool = Field(
        default=True,
    )