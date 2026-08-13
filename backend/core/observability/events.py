"""
Kernel event system.

Provides internal event publishing
and subscription capabilities.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """
    Internal event dispatcher.

    Services publish events without
    knowing who consumes them.
    """

    def __init__(self) -> None:
        self._handlers: dict[
            str,
            list[EventHandler],
        ] = defaultdict(list)

    # ------------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------------

    def subscribe(
        self,
        event: str,
        handler: EventHandler,
    ) -> None:
        """
        Subscribe to an event.
        """

        self._handlers[event].append(
            handler,
        )

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    def publish(
        self,
        event: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Publish event.
        """

        for handler in self._handlers.get(
            event,
            [],
        ):
            handler(payload)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return event bus diagnostics.
        """

        return {
            "events": list(
                self._handlers.keys(),
            ),
            "subscriptions": {
                event: len(handlers)
                for event, handlers in self._handlers.items()
            },
        }