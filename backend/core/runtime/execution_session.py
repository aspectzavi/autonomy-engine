"""
Execution session.

Tracks the lifecycle of a single autonomous runtime execution.

The execution session owns mutable runtime state while the associated
ExecutionRequest remains immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_state import (
    ExecutionState,
)


@dataclass(slots=True)
class ExecutionSession:
    """
    Runtime execution session.
    """

    request: ExecutionRequest

    state: ExecutionState = (
        ExecutionState.CREATED
    )

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    completed_at: datetime | None = None

    events: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def transition(
        self,
        state: ExecutionState,
    ) -> None:
        """
        Transition the execution to a new state.
        """

        self.state = state

        self.updated_at = datetime.now(
            UTC,
        )

        if state.is_terminal:
            self.completed_at = (
                self.updated_at
            )

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def record(
        self,
        event: str,
    ) -> None:
        """
        Record an execution event.
        """

        self.events.append(
            event,
        )

        self.updated_at = datetime.now(
            UTC,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution diagnostics.
        """

        return {
            "request": (
                self.request.diagnostics()
            ),
            "state": self.state.value,
            "started_at": (
                self.started_at.isoformat()
            ),
            "updated_at": (
                self.updated_at.isoformat()
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "events": tuple(
                self.events,
            ),
            "metadata": self.metadata,
        }