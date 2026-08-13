"""
Workflow trace.

Represents an immutable execution trace for a workflow.

WorkflowTrace captures the high-level lifecycle of workflow execution.

Future implementations may additionally support:

- task-level traces
- span hierarchies
- distributed tracing
- OpenTelemetry integration
- execution timelines
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import UTC
from datetime import datetime


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowTrace:
    """
    Immutable workflow execution trace.
    """

    workflow: str = ""

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    finished_at: datetime | None = None

    successful: bool | None = None

    events: tuple[str, ...] = ()

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_finished(
        self,
    ) -> bool:
        """
        Whether execution has completed.
        """

        return self.finished_at is not None

    @property
    def duration_seconds(
        self,
    ) -> float | None:
        """
        Execution duration.
        """

        if self.finished_at is None:
            return None

        return (
            self.finished_at - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Factory Methods
    # ------------------------------------------------------------------

    @classmethod
    def start(
        cls,
        *,
        workflow: str,
    ) -> "WorkflowTrace":
        """
        Create a new execution trace.
        """

        return cls(
            workflow=workflow,
            started_at=datetime.now(
                UTC,
            ),
            events=(
                "workflow.started",
            ),
        )

    def finish(
        self,
        *,
        successful: bool,
    ) -> "WorkflowTrace":
        """
        Return a completed trace.
        """

        return WorkflowTrace(
            workflow=self.workflow,
            started_at=self.started_at,
            finished_at=datetime.now(
                UTC,
            ),
            successful=successful,
            events=(
                *self.events,
                "workflow.finished",
            ),
            metadata=self.metadata,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return trace diagnostics.
        """

        return {
            "workflow": self.workflow,
            "started_at": (
                self.started_at.isoformat()
            ),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at is not None
                else None
            ),
            "successful": self.successful,
            "duration_seconds": (
                self.duration_seconds
            ),
            "event_count": len(
                self.events,
            ),
            "events": self.events,
            "metadata": self.metadata,
        }