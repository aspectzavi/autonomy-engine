"""
In-memory workflow event bus.

Default implementation of WorkflowEventBus.

Events are dispatched synchronously to registered listeners inside the
current process.

Future implementations may support:

- asyncio queues
- Redis Pub/Sub
- Kafka
- RabbitMQ
- NATS
- distributed event streaming
"""

from __future__ import annotations

from backend.core.workflows.workflow_event import (
    WorkflowEvent,
)
from backend.core.workflows.workflow_event_bus import (
    WorkflowEventBus,
)
from backend.core.workflows.workflow_event_listener import (
    WorkflowEventListener,
)


class InMemoryWorkflowEventBus(
    WorkflowEventBus,
):
    """
    Default in-memory workflow event bus.
    """

    def __init__(
        self,
    ) -> None:
        self._listeners: list[
            WorkflowEventListener
        ] = []

    # ------------------------------------------------------------------
    # Publication
    # ------------------------------------------------------------------

    async def publish(
        self,
        event: WorkflowEvent,
    ) -> None:
        """
        Publish an event to every interested listener.
        """

        for listener in tuple(
            self._listeners,
        ):
            if listener.accepts(
                event,
            ):
                await listener.on_event(
                    event,
                )

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    async def subscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        """
        Register a listener.
        """

        if listener not in self._listeners:
            self._listeners.append(
                listener,
            )

    async def unsubscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        """
        Remove a listener.
        """

        if listener in self._listeners:
            self._listeners.remove(
                listener,
            )

    def listeners(
        self,
    ) -> tuple[
        WorkflowEventListener,
        ...,
    ]:
        """
        Return registered listeners.
        """

        return tuple(
            self._listeners,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return event bus diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "listeners": tuple(
                    type(
                        listener,
                    ).__name__
                    for listener in self._listeners
                ),
            },
        )

        return diagnostics