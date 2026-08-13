"""
Observability container.

Provides shared observability
infrastructure instances.
"""

from __future__ import annotations

from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger


class ObservabilityContainer:
    """
    Shared observability dependencies.
    """

    def __init__(self) -> None:
        self._logger = KernelLogger()
        self._events = EventBus()

    @property
    def logger(self) -> KernelLogger:
        """
        Return logging provider.
        """
        return self._logger

    @property
    def events(self) -> EventBus:
        """
        Return shared event bus.
        """
        return self._events