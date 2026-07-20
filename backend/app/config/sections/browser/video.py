from __future__ import annotations

from pathlib import Path

from pydantic import Field

from backend.app.config.schemas.enums import VideoMode

from .filesystem import DirectorySettings


class VideoSettings(DirectorySettings):
    """
    Browser video recording configuration.
    """

    mode: VideoMode = Field(
        default=VideoMode.ON_FAILURE,
    )

    directory: Path = Field(
        default=Path("artifacts/videos"),
    )

    width: int = Field(default=1440, ge=320)
    height: int = Field(default=900, ge=240)