from __future__ import annotations

from pathlib import Path

from pydantic import Field

from backend.app.config.schemas.enums import TraceMode

from .filesystem import DirectorySettings


class TraceSettings(DirectorySettings):
    """
    Playwright tracing configuration.
    """

    mode: TraceMode = Field(
        default=TraceMode.ON_FAILURE,
    )

    directory: Path = Field(
        default=Path("artifacts/traces"),
    )

    snapshots: bool = Field(default=True)
    screenshots: bool = Field(default=True)
    sources: bool = Field(default=True)