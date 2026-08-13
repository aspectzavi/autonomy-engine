"""
Storage cleanup configuration.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.app.config.schemas.enums import CleanupPolicy


class CleanupSettings(BaseModel):
    """
    Cleanup policy.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    policy: CleanupPolicy = Field(
        default=CleanupPolicy.NEVER,
    )

    remove_empty_directories: bool = Field(
        default=True,
    )

    verify_before_delete: bool = Field(
        default=True,
    )