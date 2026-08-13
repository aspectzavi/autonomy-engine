"""
Workflow event bus.

Defines the publish/subscribe interface used by the workflow subsystem.

The event bus is intentionally decoupled from any transport mechanism.

Concrete implementations may support:

- in-memory pub/sub
- asyncio queues
- Redis Pub/Sub
- RabbitMQ
- Kafka
- NATS
- cloud event buses
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.workflows.workflow_event import (
    WorkflowEvent,
)
from backend.core.workflows.workflow_event_listener import (
    WorkflowEventListener,
)


class WorkflowEventBus(ABC):
    """
    Base workflow event bus.
    """

    @abstractmethod
    async def publish(
        self,
        event: WorkflowEvent,
    ) -> None:
        """
        Publish a workflow event.
        """

    @abstractmethod
    async def subscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        """
        Register an event listener.
        """

    @abstractmethod
    async def unsubscribe(
        self,
        listener: WorkflowEventListener,
    ) -> None:
        """
        Remove an event listener.
        """

    @abstractmethod
    def listeners(
        self,
    ) -> tuple[
        WorkflowEventListener,
        ...,
    ]:
        """
        Return registered listeners.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return event bus diagnostics.
        """

        return {
            "event_bus": (
                self.__class__.__name__
            ),
            "listener_count": len(
                self.listeners(),
            ),
        }