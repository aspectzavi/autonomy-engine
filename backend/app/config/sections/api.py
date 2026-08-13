"""
API configuration.

Defines all HTTP API related configuration used by the framework.

Copyright (c) 2026 Envisio.
Licensed under the MIT License.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

from backend.app.config.base import BaseConfig
from backend.app.config.constants import (
    DEFAULT_HOST,
    DEFAULT_PORT,
)


class ApiSettings(BaseConfig):
    """
    FastAPI configuration.
    """

    host: str = Field(
        default=DEFAULT_HOST,
        description="Host address to bind the HTTP server."
    )

    port: int = Field(
        default=DEFAULT_PORT,
        ge=1,
        le=65535,
        description="HTTP server port."
    )

    reload: bool = Field(
        default=False,
        description="Enable auto reload."
    )

    workers: int = Field(
        default=1,
        ge=1,
        description="Number of worker processes."
    )

    title: str = Field(
        default="Autonomy Engine API"
    )

    description: str = Field(
        default="Production-grade autonomous AI automation framework."
    )

    version: str = Field(
        default="0.1.0"
    )

    openapi_url: str = Field(
        default="/openapi.json"
    )

    docs_url: str = Field(
        default="/docs"
    )

    redoc_url: str = Field(
        default="/redoc"
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: ["*"]
    )

    cors_methods: list[str] = Field(
        default_factory=lambda: ["*"]
    )

    cors_headers: list[str] = Field(
        default_factory=lambda: ["*"]
    )

    trusted_hosts: list[str] = Field(
        default_factory=lambda: ["*"]
    )

    model_config = SettingsConfigDict(
        env_prefix="API__",
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        """
        Validate host value.
        """
        value = value.strip()

        if not value:
            raise ValueError("Host cannot be empty.")

        return value