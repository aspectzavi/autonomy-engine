"""
Browser configuration package.
"""

from .browser import BrowserSettings
from .context import ContextSettings
from .downloads import DownloadSettings
from .launch import LaunchSettings
from .recovery import RecoverySettings
from .screenshots import ScreenshotSettings
from .tracing import TraceSettings
from .video import VideoSettings

__all__ = [
    "BrowserSettings",
    "ContextSettings",
    "DownloadSettings",
    "LaunchSettings",
    "RecoverySettings",
    "ScreenshotSettings",
    "TraceSettings",
    "VideoSettings",
]