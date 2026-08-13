"""
Workflow event listener.

Defines the interface implemented by components interested in workflow
events.

Listeners receive immutable WorkflowEvent instances from a
WorkflowEventBus.

Typical listeners include:

- workflow monitor
- metrics collector
- audit logger
- UI streaming
- telemetry exporter
- event history
- distributed event bridge
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.workflows.workflow_event import (
    WorkflowEvent,
)


class WorkflowEventListener(ABC):
    """
    Base workflow event listener.
    """

    @abstractmethod
    async def on_event(
        self,
        event: WorkflowEvent,
    ) -> None:
        """
        Handle a published workflow event.
        """

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def accepts(
        self,
        event: WorkflowEvent,
    ) -> bool:
        """
        Determine whether this listener accepts an event.

        Default implementation accepts every event.
        """

        return True

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return listener diagnostics.
        """

        return {
            "listener": self.__class__.__name__,
        }