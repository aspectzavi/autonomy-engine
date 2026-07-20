from __future__ import annotations

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from backend.app.config.base import BaseConfig

from .backend import StorageBackendSettings
from .cleanup import CleanupSettings
from .retention import RetentionSettings


class StorageSettings(BaseConfig):
    """
    Root storage configuration.
    """

    backend: StorageBackendSettings = Field(
        default_factory=StorageBackendSettings,
    )

    retention: RetentionSettings = Field(
        default_factory=RetentionSettings,
    )

    cleanup: CleanupSettings = Field(
        default_factory=CleanupSettings,
    )

    model_config = SettingsConfigDict(
        env_prefix="STORAGE__",
    )