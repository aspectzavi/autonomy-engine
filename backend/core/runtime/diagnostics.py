"""
Runtime diagnostics.

Aggregates diagnostic information from the runtime subsystem.

RuntimeDiagnostics provides a single immutable snapshot of the runtime's
health and configuration. It is intended for debugging, monitoring,
health checks and observability.

Future implementations may additionally include:

- memory statistics
- CPU utilization
- queue latency
- throughput metrics
- OpenTelemetry exporters
- distributed runtime health
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
class RuntimeDiagnostics:
    """
    Immutable runtime diagnostics snapshot.
    """

    collected_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    coordinator: dict[str, object] = field(
        default_factory=dict,
    )

    execution_engine: dict[str, object] = field(
        default_factory=dict,
    )

    scheduler: dict[str, object] = field(
        default_factory=dict,
    )

    workflow_runtime: dict[str, object] = field(
        default_factory=dict,
    )

    workflow_monitor: dict[str, object] = field(
        default_factory=dict,
    )

    workflow_recovery: dict[str, object] = field(
        default_factory=dict,
    )

    middleware: dict[str, object] = field(
        default_factory=dict,
    )

    execution_memory: dict[str, object] = field(
        default_factory=dict,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def component_count(
        self,
    ) -> int:
        """
        Number of populated runtime components.
        """

        components = (
            self.coordinator,
            self.execution_engine,
            self.scheduler,
            self.workflow_runtime,
            self.workflow_monitor,
            self.workflow_recovery,
            self.middleware,
            self.execution_memory,
        )

        return sum(
            bool(component)
            for component in components
        )

    @property
    def is_empty(
        self,
    ) -> bool:
        """
        Whether no diagnostics have been collected.
        """

        return self.component_count == 0

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime diagnostics.
        """

        return {
            "collected_at": (
                self.collected_at.isoformat()
            ),
            "component_count": (
                self.component_count
            ),
            "coordinator": (
                self.coordinator
            ),
            "execution_engine": (
                self.execution_engine
            ),
            "scheduler": (
                self.scheduler
            ),
            "workflow_runtime": (
                self.workflow_runtime
            ),
            "workflow_monitor": (
                self.workflow_monitor
            ),
            "workflow_recovery": (
                self.workflow_recovery
            ),
            "middleware": (
                self.middleware
            ),
            "execution_memory": (
                self.execution_memory
            ),
            "metadata": (
                self.metadata
            ),
        }