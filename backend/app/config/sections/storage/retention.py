"""
Storage retention configuration.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RetentionSettings(BaseModel):
    """
    Artifact retention policy.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    enabled: bool = Field(default=True)

    retention_days: int = Field(
        default=30,
        ge=1,
    )

    max_artifacts: int = Field(
        default=10_000,
        ge=1,
    )