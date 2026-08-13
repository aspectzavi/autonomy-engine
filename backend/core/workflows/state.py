"""
Workflow lifecycle states.
"""

from __future__ import annotations

from enum import StrEnum


class WorkflowState(StrEnum):
    """
    Lifecycle states for workflows.
    """

    CREATED = "created"

    VALIDATING = "validating"

    READY = "ready"

    RUNNING = "running"

    PAUSED = "paused"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        """
        Whether the workflow has completed.
        """
        return self in {
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.CANCELLED,
        }

    @property
    def is_active(self) -> bool:
        """
        Whether the workflow is currently active.
        """
        return self in {
            WorkflowState.READY,
            WorkflowState.RUNNING,
            WorkflowState.PAUSED,
        }