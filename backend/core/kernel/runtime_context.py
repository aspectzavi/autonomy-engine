"""
Runtime context.

Provides shared runtime dependencies required during autonomous
execution.

The runtime context acts as the bridge between the kernel runtime and
execution subsystems such as agents, workflows, and tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from backend.app.container.container import Container
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.tasks.context import TaskContext

if TYPE_CHECKING:
    from backend.core.kernel.runtime import Runtime


@dataclass(frozen=True, slots=True)
class RuntimeContext:
    """
    Shared runtime execution context.
    """

    runtime: Runtime

    container: Container

    logger: KernelLogger

    events: EventBus

    # ------------------------------------------------------------------
    # Task Context
    # ------------------------------------------------------------------

    def task_context(
        self,
    ) -> TaskContext:
        """
        Create a task execution context.
        """

        return TaskContext(
            runtime=self.runtime,
            container=self.container,
            logger=self.logger,
            events=self.events,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime context diagnostics.
        """

        return {
            "runtime": self.runtime.diagnostics(),
            "container": self.container.diagnostics(),
            "events": self.events.diagnostics(),
            "logger": type(
                self.logger,
            ).__name__,
        }