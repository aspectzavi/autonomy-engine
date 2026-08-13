"""
Browser configuration.

Composes all browser-related configuration sections into a single model.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from backend.app.config.base import BaseConfig

from .context import ContextSettings
from .downloads import DownloadSettings
from .launch import LaunchSettings
from .recovery import RecoverySettings
from .screenshots import ScreenshotSettings
from .tracing import TraceSettings
from .video import VideoSettings


class BrowserSettings(BaseConfig):
    """
    Root browser configuration.
    """

    launch: LaunchSettings = Field(
        default_factory=LaunchSettings,
    )

    context: ContextSettings = Field(
        default_factory=ContextSettings,
    )

    downloads: DownloadSettings = Field(
        default_factory=DownloadSettings,
    )

    tracing: TraceSettings = Field(
        default_factory=TraceSettings,
    )

    video: VideoSettings = Field(
        default_factory=VideoSettings,
    )

    screenshots: ScreenshotSettings = Field(
        default_factory=ScreenshotSettings,
    )

    recovery: RecoverySettings = Field(
        default_factory=RecoverySettings,
    )

    model_config = SettingsConfigDict(
        env_prefix="BROWSER__",
    )