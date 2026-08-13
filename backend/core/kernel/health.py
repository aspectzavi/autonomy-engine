"""
Kernel health models.

This module defines the health models shared by all kernel-managed
services.

Health information is consumed by:

- Runtime diagnostics
- Health endpoints
- Telemetry
- Monitoring
- Automatic recovery
- Service registry
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceHealth(BaseModel):
    """
    Health information for a kernel-managed service.

    Every service should expose an instance of this model.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    healthy: bool = Field(
        default=True,
        description="Whether the service is considered healthy.",
    )

    status: str = Field(
        default="initialized",
        description="Current health status.",
    )

    started_at: datetime | None = Field(
        default=None,
        description="Time the service started.",
    )

    last_check: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of the latest health check.",
    )

    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Current uptime in seconds.",
    )

    restart_count: int = Field(
        default=0,
        ge=0,
        description="Number of automatic or manual restarts.",
    )

    warnings: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Current service warnings.",
    )

    last_error: str | None = Field(
        default=None,
        description="Most recent error message.",
    )

    details: dict[str, str] = Field(
        default_factory=dict,
        description="Additional diagnostic information.",
    )

    @property
    def has_warnings(self) -> bool:
        """
        Whether the service currently has warnings.
        """
        return bool(self.warnings)

    @property
    def is_running(self) -> bool:
        """
        Whether the service is currently running.
        """
        return self.status.lower() == "running"

    @property
    def is_failed(self) -> bool:
        """
        Whether the service is currently failed.
        """
        return not self.healthy

    def with_status(self, status: str) -> "ServiceHealth":
        """
        Return a copy with an updated status.
        """
        return self.model_copy(
            update={
                "status": status,
                "last_check": datetime.now(UTC),
            }
        )

    def with_error(self, message: str) -> "ServiceHealth":
        """
        Return a copy containing an error.
        """
        return self.model_copy(
            update={
                "healthy": False,
                "status": "failed",
                "last_error": message,
                "last_check": datetime.now(UTC),
            }
        )

    def recovered(self) -> "ServiceHealth":
        """
        Return a recovered health state.
        """
        return self.model_copy(
            update={
                "healthy": True,
                "status": "running",
                "last_error": None,
                "last_check": datetime.now(UTC),
            }
        )

    def restarted(self) -> "ServiceHealth":
        """
        Return a copy with an incremented restart count.
        """
        return self.model_copy(
            update={
                "restart_count": self.restart_count + 1,
                "last_check": datetime.now(UTC),
            }
        )

    def add_warning(self, warning: str) -> "ServiceHealth":
        """
        Return a copy with an additional warning.
        """
        return self.model_copy(
            update={
                "warnings": (*self.warnings, warning),
                "last_check": datetime.now(UTC),
            }
        )