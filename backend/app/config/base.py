"""
Base configuration infrastructure for the Autonomous AI Framework.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from typing import Any

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class BaseConfig(BaseSettings):
    """
    Base class for all configuration models.

    Every configuration section should inherit from this class.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
        env_nested_delimiter="__",
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        frozen=True,
        populate_by_name=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Configure the order in which settings are loaded.
        """
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the configuration as a dictionary."""
        return self.model_dump()

    def to_json(self, *, indent: int = 4) -> str:
        """Return the configuration as JSON."""
        return self.model_dump_json(indent=indent)

    def copy_with(self, **updates: Any) -> "BaseConfig":
        """
        Return a validated copy of the configuration with updates.
        """
        return self.model_copy(update=updates)