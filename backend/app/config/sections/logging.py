"""
Logging configuration.

Defines structured logging settings for the framework.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from backend.app.config.base import BaseConfig
from backend.app.config.constants import LOG_DIRECTORY_NAME
from backend.shared.enums import LogLevel


class LoggingSettings(BaseConfig):
    """
    Structured logging configuration.
    """

    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Minimum logging level."
    )

    console_enabled: bool = Field(
        default=True
    )

    file_enabled: bool = Field(
        default=True
    )

    json_enabled: bool = Field(
        default=True,
        description="Write structured JSON logs."
    )

    pretty_console: bool = Field(
        default=True,
        description="Pretty colored console logs."
    )

    directory: str = Field(
        default=LOG_DIRECTORY_NAME
    )

    filename: str = Field(
        default="framework.jsonl"
    )

    max_file_size_mb: int = Field(
        default=100,
        ge=1
    )

    backup_count: int = Field(
        default=10,
        ge=0
    )

    include_trace_id: bool = Field(
        default=True
    )

    include_session_id: bool = Field(
        default=True
    )

    include_process_id: bool = Field(
        default=True
    )

    include_thread_name: bool = Field(
        default=False
    )

    log_requests: bool = Field(
        default=True
    )

    log_responses: bool = Field(
        default=False
    )

    log_performance: bool = Field(
        default=True
    )

    log_exceptions: bool = Field(
        default=True
    )

    model_config = SettingsConfigDict(
        env_prefix="LOGGING__"
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Log filename cannot be empty.")

        return value