"""
Default workflow recovery.

Production-ready implementation of WorkflowRecovery.

Coordinates workflow restoration using the configured checkpoint store.

Current responsibilities:

- locate checkpoints
- validate checkpoint existence
- report recovery outcome

Future versions may additionally support:

- workflow replay
- partial recovery
- checkpoint migration
- distributed recovery
- execution resumption
"""

from __future__ import annotations

from backend.core.tasks.context import (
    TaskContext,
)
from backend.core.workflows.checkpoint_store import (
    CheckpointStore,
)
from backend.core.workflows.recovery_report import (
    RecoveryReport,
)
from backend.core.workflows.workflow import (
    Workflow,
)
from backend.core.workflows.workflow_recovery import (
    WorkflowRecovery,
)


class DefaultWorkflowRecovery(
    WorkflowRecovery,
):
    """
    Default workflow recovery implementation.
    """

    def __init__(
        self,
        *,
        checkpoint_store: CheckpointStore,
    ) -> None:
        self._checkpoint_store = checkpoint_store

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def checkpoint_store(
        self,
    ) -> CheckpointStore:
        """
        Checkpoint store.
        """

        return self._checkpoint_store

    # ------------------------------------------------------------------
    # Recovery
    # ------------------------------------------------------------------

    async def recover(
        self,
        *,
        workflow: Workflow,
        context: TaskContext,
    ) -> RecoveryReport:
        """
        Attempt workflow recovery.
        """

        del context

        checkpoint = (
            await self.checkpoint_store.load(
                workflow=workflow.name,
            )
        )

        if checkpoint is None:
            return RecoveryReport(
                recovered=False,
                workflow=workflow.name,
                checkpoint_found=False,
                metadata={
                    "reason": (
                        "checkpoint_not_found"
                    ),
                },
            )

        return RecoveryReport(
            recovered=True,
            workflow=workflow.name,
            checkpoint_found=True,
            checkpoint_id=(
                checkpoint.checkpoint_id
            ),
            completed_nodes=(
                checkpoint.completed_count
            ),
            pending_nodes=(
                checkpoint.pending_count
            ),
            failed_nodes=(
                checkpoint.failed_count
            ),
            metadata={
                "completion_ratio": (
                    checkpoint.completion_ratio
                ),
            },
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return recovery diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "checkpoint_store": (
                    self.checkpoint_store.diagnostics()
                ),
            },
        )

        return diagnostics