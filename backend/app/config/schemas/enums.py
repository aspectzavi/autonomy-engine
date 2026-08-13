"""
Configuration-specific enumerations.

These enums are only used by the configuration system.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from enum import StrEnum


class BrowserEngine(StrEnum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class ScreenshotFormat(StrEnum):
    PNG = "png"
    JPEG = "jpeg"


class TraceMode(StrEnum):
    OFF = "off"
    ON = "on"
    ON_FAILURE = "on_failure"


class VideoMode(StrEnum):
    OFF = "off"
    ON = "on"
    ON_FAILURE = "on_failure"


class WaitStrategy(StrEnum):
    LOAD = "load"
    DOMCONTENTLOADED = "domcontentloaded"
    NETWORKIDLE = "networkidle"


class StorageBackend(StrEnum):
    """
    Storage backend implementation.
    """

    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"


class CleanupPolicy(StrEnum):
    """
    Artifact cleanup policy.
    """

    NEVER = "never"
    ON_STARTUP = "startup"
    ON_SHUTDOWN = "shutdown"
    ALWAYS = "always"    