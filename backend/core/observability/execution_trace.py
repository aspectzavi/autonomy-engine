"""
Execution trace.

Maintains the complete lifecycle trace of an autonomous execution.

An execution trace groups multiple TraceSpan objects into a single
observable execution timeline.

Example:

ExecutionTrace
    |
    ├── request.received
    ├── agent.planning
    ├── workflow.execution
    ├── tool.call
    └── response.generated
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.core.observability.trace_span import TraceSpan


class ExecutionTrace:
    """
    Collection of spans representing one execution.
    """

    def __init__(
        self,
        *,
        trace_id: str,
    ) -> None:
        self._trace_id = trace_id

        self._created_at = datetime.now(
            UTC,
        )

        self._spans: list[TraceSpan] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def trace_id(
        self,
    ) -> str:
        """
        Return trace identifier.
        """
        return self._trace_id

    @property
    def spans(
        self,
    ) -> tuple[TraceSpan, ...]:
        """
        Return trace spans.
        """
        return tuple(
            self._spans,
        )

    # ------------------------------------------------------------------
    # Span Management
    # ------------------------------------------------------------------

    def start_span(
        self,
        name: str,
        *,
        parent_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> TraceSpan:
        """
        Create and register a new span.
        """

        span = TraceSpan(
            name=name,
            parent_id=parent_id,
            metadata=metadata or {},
        )

        self._spans.append(
            span,
        )

        return span

    def add_span(
        self,
        span: TraceSpan,
    ) -> None:
        """
        Add an existing span.
        """

        self._spans.append(
            span,
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def find(
        self,
        name: str,
    ) -> tuple[TraceSpan, ...]:
        """
        Find spans by name.
        """

        return tuple(
            span
            for span in self._spans
            if span.name == name
        )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def completed(
        self,
    ) -> bool:
        """
        Whether all spans are completed.
        """

        return all(
            span.completed
            for span in self._spans
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
            "trace_id": self.trace_id,
            "created_at": (
                self._created_at.isoformat()
            ),
            "span_count": len(
                self._spans,
            ),
            "completed": self.completed,
            "spans": tuple(
                span.diagnostics()
                for span in self._spans
            ),
        }