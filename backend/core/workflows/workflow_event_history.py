"""
Workflow event history.

Maintains an immutable history of workflow events observed during
runtime.

WorkflowEventHistory is itself a WorkflowEventSubscriber and can be
registered directly with a WorkflowEventBus.

Future implementations may additionally support:

- persistent history
- event replay
- event sourcing
- distributed history
- event expiration
- indexed queries
"""

from __future__ import annotations

from backend.core.workflows.workflow_event import (
    WorkflowEvent,
)
from backend.core.workflows.workflow_event_subscriber import (
    WorkflowEventSubscriber,
)


class WorkflowEventHistory(
    WorkflowEventSubscriber,
):
    """
    Records workflow events.
    """

    def __init__(
        self,
        *,
        workflows: tuple[str, ...] = (),
        event_names: tuple[str, ...] = (),
    ) -> None:
        super().__init__(
            workflows=workflows,
            event_names=event_names,
        )

        self._events: list[
            WorkflowEvent
        ] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def events(
        self,
    ) -> tuple[
        WorkflowEvent,
        ...,
    ]:
        """
        Return recorded events.
        """

        return tuple(
            self._events,
        )

    @property
    def event_count(
        self,
    ) -> int:
        """
        Number of recorded events.
        """

        return len(
            self._events,
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no events have been recorded.
        """

        return (
            self.event_count == 0
        )

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    async def on_event(
        self,
        event: WorkflowEvent,
    ) -> None:
        """
        Record an event.
        """

        self._events.append(
            event,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def latest(
        self,
    ) -> WorkflowEvent | None:
        """
        Return the most recently recorded event.
        """

        if not self._events:
            return None

        return self._events[-1]

    def workflow_events(
        self,
        workflow: str,
    ) -> tuple[
        WorkflowEvent,
        ...,
    ]:
        """
        Return events for a workflow.
        """

        return tuple(
            event
            for event in self._events
            if event.workflow == workflow
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all recorded events.
        """

        self._events.clear()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return event history diagnostics.
        """

        latest = self.latest()

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "event_count": (
                    self.event_count
                ),
                "is_empty": (
                    self.is_empty
                ),
                "latest_event": (
                    latest.name
                    if latest is not None
                    else None
                ),
            },
        )

        return diagnostics