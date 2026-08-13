"""
Checkpoint store.

Defines the persistence interface for workflow checkpoints.

A CheckpointStore is responsible for durable storage and retrieval of
WorkflowCheckpoint instances.

Concrete implementations may store checkpoints in:

- memory
- SQLite
- PostgreSQL
- Redis
- S3
- cloud object storage
- distributed databases
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.workflows.workflow_checkpoint import (
    WorkflowCheckpoint,
)


class CheckpointStore(ABC):
    """
    Base workflow checkpoint store.
    """

    @abstractmethod
    async def save(
        self,
        checkpoint: WorkflowCheckpoint,
    ) -> None:
        """
        Persist a checkpoint.
        """

    @abstractmethod
    async def load(
        self,
        *,
        workflow: str,
    ) -> WorkflowCheckpoint | None:
        """
        Load the latest checkpoint for a workflow.
        """

    @abstractmethod
    async def delete(
        self,
        *,
        workflow: str,
    ) -> bool:
        """
        Delete the stored checkpoint.

        Returns:
            True if a checkpoint existed and was removed.
        """

    @abstractmethod
    async def exists(
        self,
        *,
        workflow: str,
    ) -> bool:
        """
        Whether a checkpoint exists.
        """

    @abstractmethod
    async def list_workflows(
        self,
    ) -> tuple[str, ...]:
        """
        Return all workflows that currently have checkpoints.
        """

    @abstractmethod
    async def clear(
        self,
    ) -> None:
        """
        Remove every stored checkpoint.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return checkpoint store diagnostics.
        """

        return {
            "store": self.__class__.__name__,
        }