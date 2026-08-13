"""
Kernel runtime information models.

This module defines immutable runtime information shared by all
kernel-managed services.

Unlike ServiceHealth, which represents the health of a service,
ServiceRuntimeInfo represents the current execution state and
operational metrics of a service.

These models are intended for diagnostics, telemetry, monitoring,
runtime inspection, and future observability endpoints.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceRuntimeInfo(BaseModel):
    """
    Immutable runtime snapshot for a kernel-managed service.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    state: str = Field(
        default="initialized",
        description="Current runtime state.",
    )

    started_at: datetime | None = Field(
        default=None,
        description="Time when the service was started.",
    )

    last_activity: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of the most recent activity.",
    )

    uptime_seconds: float = Field(
        default=0.0,
        ge=0.0,
        description="Service uptime in seconds.",
    )

    active_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of currently executing tasks.",
    )

    pending_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of queued tasks.",
    )

    completed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of completed tasks.",
    )

    failed_tasks: int = Field(
        default=0,
        ge=0,
        description="Number of failed tasks.",
    )

    worker_count: int = Field(
        default=0,
        ge=0,
        description="Number of active worker threads or processes.",
    )

    memory_usage_mb: float = Field(
        default=0.0,
        ge=0.0,
        description="Approximate memory usage in megabytes.",
    )

    process_id: int | None = Field(
        default=None,
        description="Operating system process identifier.",
    )

    thread_count: int = Field(
        default=0,
        ge=0,
        description="Number of active threads.",
    )

    attributes: dict[str, str] = Field(
        default_factory=dict,
        description="Additional runtime-specific attributes.",
    )

    @property
    def busy(self) -> bool:
        """
        Whether the service is currently executing work.
        """
        return self.active_tasks > 0

    @property
    def idle(self) -> bool:
        """
        Whether the service is idle.
        """
        return self.active_tasks == 0

    @property
    def total_processed_tasks(self) -> int:
        """
        Total number of processed tasks.
        """
        return self.completed_tasks + self.failed_tasks

    def touch(self) -> "ServiceRuntimeInfo":
        """
        Return a copy with an updated activity timestamp.
        """
        return self.model_copy(
            update={
                "last_activity": datetime.now(UTC),
            }
        )

    def with_state(self, state: str) -> "ServiceRuntimeInfo":
        """
        Return a copy with an updated runtime state.
        """
        return self.model_copy(
            update={
                "state": state,
                "last_activity": datetime.now(UTC),
            }
        )

    def increment_active_tasks(self) -> "ServiceRuntimeInfo":
        """
        Return a copy with one additional active task.
        """
        return self.model_copy(
            update={
                "active_tasks": self.active_tasks + 1,
                "last_activity": datetime.now(UTC),
            }
        )

    def decrement_active_tasks(self) -> "ServiceRuntimeInfo":
        """
        Return a copy with one fewer active task.

        The active task count will never become negative.
        """
        return self.model_copy(
            update={
                "active_tasks": max(0, self.active_tasks - 1),
                "last_activity": datetime.now(UTC),
            }
        )

    def task_completed(self) -> "ServiceRuntimeInfo":
        """
        Return a copy reflecting a successfully completed task.
        """
        return self.model_copy(
            update={
                "completed_tasks": self.completed_tasks + 1,
                "active_tasks": max(0, self.active_tasks - 1),
                "last_activity": datetime.now(UTC),
            }
        )

    def task_failed(self) -> "ServiceRuntimeInfo":
        """
        Return a copy reflecting a failed task.
        """
        return self.model_copy(
            update={
                "failed_tasks": self.failed_tasks + 1,
                "active_tasks": max(0, self.active_tasks - 1),
                "last_activity": datetime.now(UTC),
            }
        )

    def with_attribute(
        self,
        key: str,
        value: str,
    ) -> "ServiceRuntimeInfo":
        """
        Return a copy with an updated runtime attribute.
        """
        attributes = dict(self.attributes)
        attributes[key] = value

        return self.model_copy(
            update={
                "attributes": attributes,
                "last_activity": datetime.now(UTC),
            }
        )