"""
Runtime scheduler.

Defines the interface responsible for selecting the next execution
session for the runtime.

The scheduler operates above the workflow scheduler.

Responsibilities:

- queue execution sessions
- select the next session
- support priorities
- expose queue diagnostics

Concrete implementations may support:

- FIFO scheduling
- priority scheduling
- fair scheduling
- deadline scheduling
- distributed scheduling
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.runtime.execution_session import (
    ExecutionSession,
)


class Scheduler(ABC):
    """
    Base runtime scheduler.
    """

    # ------------------------------------------------------------------
    # Queue Management
    # ------------------------------------------------------------------

    @abstractmethod
    async def submit(
        self,
        session: ExecutionSession,
    ) -> None:
        """
        Submit an execution session.
        """

    @abstractmethod
    async def next(
        self,
    ) -> ExecutionSession | None:
        """
        Return the next execution session.

        Returns None when the queue is empty.
        """

    @abstractmethod
    async def remove(
        self,
        session_id: str,
    ) -> bool:
        """
        Remove a queued session.

        Returns:
            True if removed.
        """

    # ------------------------------------------------------------------
    # Queue State
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def size(
        self,
    ) -> int:
        """
        Number of queued sessions.
        """

    @property
    def empty(
        self,
    ) -> bool:
        """
        Whether the scheduler is empty.
        """

        return self.size == 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def clear(
        self,
    ) -> None:
        """
        Remove all queued sessions.

        Default implementation repeatedly removes sessions using
        next().
        """

        while await self.next() is not None:
            pass

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return scheduler diagnostics.
        """

        return {
            "scheduler": self.__class__.__name__,
            "queue_size": self.size,
            "empty": self.empty,
        }