"""
Trace span.

Represents a single unit of work inside an autonomous execution trace.

A span captures lifecycle information for operations such as:

- agent execution
- workflow steps
- tool calls
- planning phases
- task execution

Spans are immutable records after completion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class TraceSpan:
    """
    Represents one execution trace span.
    """

    name: str

    span_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    parent_id: str | None = None

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    finished_at: datetime | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    error: str | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def finish(
        self,
    ) -> None:
        """
        Mark span as completed.
        """

        if self.finished_at is None:
            self.finished_at = datetime.now(
                UTC,
            )

    def fail(
        self,
        error: Exception | str,
    ) -> None:
        """
        Mark span as failed.
        """

        self.error = str(
            error,
        )

        self.finish()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def completed(
        self,
    ) -> bool:
        """
        Whether the span has finished.
        """

        return self.finished_at is not None

    @property
    def failed(
        self,
    ) -> bool:
        """
        Whether the span failed.
        """

        return self.error is not None

    @property
    def duration(
        self,
    ) -> float | None:
        """
        Return execution duration in seconds.
        """

        if self.finished_at is None:
            return None

        return (
            self.finished_at - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set_metadata(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Attach metadata to the span.
        """

        self.metadata[key] = value

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return span diagnostics.
        """

        return {
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "started_at": (
                self.started_at.isoformat()
            ),
            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),
            "duration": self.duration,
            "metadata": self.metadata,
            "error": self.error,
            "completed": self.completed,
            "failed": self.failed,
        }