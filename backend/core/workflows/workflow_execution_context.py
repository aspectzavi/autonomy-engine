"""
Workflow execution context.

Represents the mutable execution state shared across the complete
workflow runtime.

The WorkflowExecutionContext becomes the single object passed through
the runtime pipeline:

    Scheduler
        ↓
    Middleware
        ↓
    Executor
        ↓
    Monitor
        ↓
    Recovery
        ↓
    Resilience
        ↓
    Event Bus

Each runtime component may read and update the context without needing
to know about the other components.

The context intentionally stores runtime state only. Workflow
definitions remain immutable.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime
from typing import Any

from backend.core.tasks.context import TaskContext
from backend.core.workflows.workflow import Workflow


@dataclass(slots=True)
class WorkflowExecutionContext:
    """
    Shared workflow runtime execution context.
    """

    workflow: Workflow

    task_context: TaskContext

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    state: dict[str, object] = field(
        default_factory=dict,
    )

    events: list[str] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )

    retry_count: int = 0

    cancelled: bool = False

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store metadata.
        """

        self.metadata[key] = value

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ------------------------------------------------------------------
    # Runtime State
    # ------------------------------------------------------------------

    def put_state(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store runtime state.
        """

        self.state[key] = value

    def state_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve runtime state.
        """

        return self.state.get(
            key,
            default,
        )

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def publish(
        self,
        event: str,
    ) -> None:
        """
        Record an execution event.
        """

        self.events.append(
            event,
        )

    # ------------------------------------------------------------------
    # Errors
    # ------------------------------------------------------------------

    def add_error(
        self,
        error: str,
    ) -> None:
        """
        Record an execution error.
        """

        self.errors.append(
            error,
        )

    @property
    def has_errors(
        self,
    ) -> bool:
        """
        Whether execution has errors.
        """

        return bool(
            self.errors,
        )

    # ------------------------------------------------------------------
    # Retry
    # ------------------------------------------------------------------

    def increment_retry(
        self,
    ) -> None:
        """
        Increment retry counter.
        """

        self.retry_count += 1

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    def cancel(
        self,
    ) -> None:
        """
        Mark execution as cancelled.
        """

        self.cancelled = True

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, Any]:
        """
        Return execution diagnostics.
        """

        return {
            "workflow": self.workflow.name,
            "started_at": self.started_at.isoformat(),
            "retry_count": self.retry_count,
            "cancelled": self.cancelled,
            "metadata": dict(self.metadata),
            "state_keys": tuple(self.state.keys()),
            "events": tuple(self.events),
            "errors": tuple(self.errors),
        }