"""
Runtime tracing manager.

Provides trace creation and lifecycle management for autonomous
executions.

The tracing service owns active execution traces and provides a central
API for middleware, runtime, agents, and workflows to create spans.
"""

from __future__ import annotations

from uuid import uuid4

from backend.core.observability.execution_trace import (
    ExecutionTrace,
)
from backend.core.observability.trace_span import (
    TraceSpan,
)


class Tracing:
    """
    Manages execution traces.
    """

    def __init__(
        self,
    ) -> None:
        self._traces: dict[str, ExecutionTrace] = {}

    # ------------------------------------------------------------------
    # Trace Lifecycle
    # ------------------------------------------------------------------

    def create_trace(
        self,
    ) -> ExecutionTrace:
        """
        Create a new execution trace.
        """

        trace = ExecutionTrace(
            trace_id=str(
                uuid4(),
            ),
        )

        self._traces[
            trace.trace_id
        ] = trace

        return trace

    def get_trace(
        self,
        trace_id: str,
    ) -> ExecutionTrace | None:
        """
        Retrieve a trace by id.
        """

        return self._traces.get(
            trace_id,
        )

    def remove_trace(
        self,
        trace_id: str,
    ) -> bool:
        """
        Remove a trace.
        """

        if trace_id not in self._traces:
            return False

        del self._traces[
            trace_id
        ]

        return True

    # ------------------------------------------------------------------
    # Span Helpers
    # ------------------------------------------------------------------

    def start_span(
        self,
        trace_id: str,
        name: str,
        *,
        parent_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> TraceSpan:
        """
        Create a span inside an existing trace.
        """

        trace = self.get_trace(
            trace_id,
        )

        if trace is None:
            raise ValueError(
                f"Unknown trace: {trace_id}",
            )

        return trace.start_span(
            name,
            parent_id=parent_id,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def traces(
        self,
    ) -> tuple[ExecutionTrace, ...]:
        """
        Return all traces.
        """

        return tuple(
            self._traces.values(),
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return tracing diagnostics.
        """

        return {
            "trace_count": len(
                self._traces,
            ),
            "traces": tuple(
                trace.diagnostics()
                for trace in self._traces.values()
            ),
        }