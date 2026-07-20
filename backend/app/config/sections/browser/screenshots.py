from __future__ import annotations

from pathlib import Path

from pydantic import Field

from backend.app.config.schemas.enums import ScreenshotFormat

from .filesystem import DirectorySettings


class ScreenshotSettings(DirectorySettings):
    """
    Screenshot configuration.
    """

    directory: Path = Field(
        default=Path("artifacts/screenshots"),
    )

    format: ScreenshotFormat = Field(
        default=ScreenshotFormat.PNG,
    )

    full_page: bool = Field(default=True)