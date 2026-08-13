"""
Workflow recovery.

Defines the interface responsible for recovering workflow execution
from previously persisted checkpoints.

A WorkflowRecovery implementation coordinates checkpoint loading,
validation and workflow restoration.

Responsibilities:

- locate checkpoints
- validate checkpoints
- restore workflow state
- generate recovery reports

Concrete implementations may additionally support:

- distributed recovery
- checkpoint migration
- partial recovery
- workflow replay
- state reconciliation
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.workflows.recovery_report import (
    RecoveryReport,
)
from backend.core.workflows.workflow import (
    Workflow,
)


class WorkflowRecovery(ABC):
    """
    Base interface for workflow recovery.
    """

    @abstractmethod
    async def recover(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RecoveryReport:
        """
        Attempt to recover a workflow.

        Returns:
            Immutable recovery report.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return recovery diagnostics.
        """

        return {
            "recovery": self.__class__.__name__,
        }