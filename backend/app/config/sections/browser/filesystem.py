"""
Shared browser filesystem configuration models.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field

from .base import BrowserConfigSection


class DirectorySettings(BrowserConfigSection):
    """
    Base configuration for a filesystem-backed feature.
    """

    enabled: bool = Field(
        default=True,
        description="Whether the feature is enabled.",
    )

    directory: Path = Field(
        description="Directory used by the feature.",
    )