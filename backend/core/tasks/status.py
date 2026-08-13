"""
Task lifecycle states.

Defines the lifecycle of executable tasks within the autonomous
execution engine.
"""

from __future__ import annotations

from enum import StrEnum


class TaskStatus(StrEnum):
    """
    Lifecycle states for a task.
    """

    CREATED = "created"

    QUEUED = "queued"

    SCHEDULED = "scheduled"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    RETRYING = "retrying"

    TIMED_OUT = "timed_out"

    SKIPPED = "skipped"

    @property
    def is_terminal(self) -> bool:
        """
        Whether the task has reached a terminal state.
        """
        return self in {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT,
            TaskStatus.SKIPPED,
        }

    @property
    def is_active(self) -> bool:
        """
        Whether the task is actively progressing.
        """
        return self in {
            TaskStatus.QUEUED,
            TaskStatus.SCHEDULED,
            TaskStatus.RUNNING,
            TaskStatus.RETRYING,
        }

    @property
    def can_retry(self) -> bool:
        """
        Whether the task may be retried.
        """
        return self in {
            TaskStatus.FAILED,
            TaskStatus.TIMED_OUT,
        }