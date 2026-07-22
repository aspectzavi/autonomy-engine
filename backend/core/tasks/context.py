"""
Task execution context.

Provides shared runtime infrastructure to executable tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.container.container import Container
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.core.kernel.runtime import Runtime
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger


@dataclass(slots=True)
class TaskContext:
    """
    Shared execution context for tasks.
    """

    runtime: Runtime

    container: Container

    logger: KernelLogger

    events: EventBus

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    cancelled: bool = False

    def cancel(self) -> None:
        """
        Mark the execution context as cancelled.
        """
        self.cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """
        Whether execution has been cancelled.
        """
        return self.cancelled