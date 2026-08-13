"""
Workflow event subscriber.

Provides a reusable base implementation of WorkflowEventListener.

Subscribers can optionally filter events by workflow and/or event names.

Future implementations may additionally support:

- wildcard subscriptions
- regex filtering
- priority subscriptions
- event transformations
"""

from __future__ import annotations

from abc import abstractmethod

from backend.core.workflows.workflow_event import (
    WorkflowEvent,
)
from backend.core.workflows.workflow_event_listener import (
    WorkflowEventListener,
)


class WorkflowEventSubscriber(
    WorkflowEventListener,
):
    """
    Base workflow event subscriber.
    """

    def __init__(
        self,
        *,
        workflows: tuple[str, ...] = (),
        event_names: tuple[str, ...] = (),
    ) -> None:
        self._workflows = workflows
        self._event_names = event_names

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def workflows(
        self,
    ) -> tuple[str, ...]:
        """
        Workflows accepted by this subscriber.
        Empty means all workflows.
        """

        return self._workflows

    @property
    def event_names(
        self,
    ) -> tuple[str, ...]:
        """
        Event names accepted by this subscriber.
        Empty means all events.
        """

        return self._event_names

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def accepts(
        self,
        event: WorkflowEvent,
    ) -> bool:
        """
        Determine whether this subscriber accepts an event.
        """

        if (
            self.workflows
            and event.workflow not in self.workflows
        ):
            return False

        if (
            self.event_names
            and event.name not in self.event_names
        ):
            return False

        return True

    # ------------------------------------------------------------------
    # Event Handling
    # ------------------------------------------------------------------

    @abstractmethod
    async def on_event(
        self,
        event: WorkflowEvent,
    ) -> None:
        """
        Handle an accepted workflow event.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return subscriber diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "workflows": self.workflows,
                "event_names": self.event_names,
            },
        )

        return diagnostics