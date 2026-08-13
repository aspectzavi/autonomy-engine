"""
In-memory checkpoint store.

Default in-memory implementation of CheckpointStore.

The implementation is intended for development, testing and local
runtime execution.

Future implementations may persist checkpoints in databases or cloud
storage without changing the recovery subsystem.
"""

from __future__ import annotations

from backend.core.workflows.checkpoint_store import (
    CheckpointStore,
)
from backend.core.workflows.workflow_checkpoint import (
    WorkflowCheckpoint,
)


class InMemoryCheckpointStore(
    CheckpointStore,
):
    """
    In-memory checkpoint store.
    """

    def __init__(
        self,
    ) -> None:
        self._checkpoints: dict[
            str,
            WorkflowCheckpoint,
        ] = {}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    async def save(
        self,
        checkpoint: WorkflowCheckpoint,
    ) -> None:
        """
        Persist a checkpoint.
        """

        self._checkpoints[
            checkpoint.workflow
        ] = checkpoint

    async def load(
        self,
        *,
        workflow: str,
    ) -> WorkflowCheckpoint | None:
        """
        Load a checkpoint.
        """

        return self._checkpoints.get(
            workflow,
        )

    async def delete(
        self,
        *,
        workflow: str,
    ) -> bool:
        """
        Delete a checkpoint.
        """

        return (
            self._checkpoints.pop(
                workflow,
                None,
            )
            is not None
        )

    async def exists(
        self,
        *,
        workflow: str,
    ) -> bool:
        """
        Determine whether a checkpoint exists.
        """

        return workflow in self._checkpoints

    async def list_workflows(
        self,
    ) -> tuple[str, ...]:
        """
        Return workflows with stored checkpoints.
        """

        return tuple(
            sorted(
                self._checkpoints.keys(),
            ),
        )

    async def clear(
        self,
    ) -> None:
        """
        Remove every checkpoint.
        """

        self._checkpoints.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return checkpoint store diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "checkpoint_count": len(
                    self._checkpoints,
                ),
                "stored_workflows": tuple(
                    sorted(
                        self._checkpoints.keys(),
                    ),
                ),
            },
        )

        return diagnostics