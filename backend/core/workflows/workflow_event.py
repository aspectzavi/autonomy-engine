"""
Workflow event.

Represents an immutable event emitted during workflow execution.

Workflow events provide a decoupled communication mechanism between the
workflow runtime and interested observers.

Typical events include:

- workflow.created
- workflow.validated
- workflow.started
- workflow.scheduled
- workflow.batch.started
- workflow.batch.completed
- workflow.completed
- workflow.failed
- workflow.cancelled

Future implementations may additionally support:

- distributed event streaming
- CloudEvents
- OpenTelemetry events
- persistent event sourcing
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
class WorkflowEvent:
    """
    Immutable workflow event.
    """

    name: str

    workflow: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    source: str = "workflow-runtime"

    correlation_id: str | None = None

    parent_event_id: str | None = None

    payload: dict[str, object] = field(
        default_factory=dict,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_terminal(
        self,
    ) -> bool:
        """
        Whether this represents a terminal workflow event.
        """

        return self.name in {
            "workflow.completed",
            "workflow.failed",
            "workflow.cancelled",
        }

    @property
    def category(
        self,
    ) -> str:
        """
        Return the event category.

        Example:

            workflow.started
            └───────┘
        """

        return self.name.partition(".")[0]

    @property
    def action(
        self,
    ) -> str:
        """
        Return the event action.

        Example:

            workflow.started
                     └─────┘
        """

        return self.name.partition(".")[2]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return event diagnostics.
        """

        return {
            "name": self.name,
            "workflow": self.workflow,
            "timestamp": (
                self.timestamp.isoformat()
            ),
            "source": self.source,
            "category": self.category,
            "action": self.action,
            "is_terminal": (
                self.is_terminal
            ),
            "correlation_id": (
                self.correlation_id
            ),
            "parent_event_id": (
                self.parent_event_id
            ),
            "payload": self.payload,
            "metadata": self.metadata,
        }