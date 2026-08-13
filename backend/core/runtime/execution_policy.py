"""
Execution policy.

Defines the policy governing how the runtime executes workflows.

The execution policy is intentionally immutable and acts as a runtime
configuration object consumed by the ExecutionEngine, Coordinator and
Scheduler.

Responsibilities:

- retry configuration
- timeout configuration
- scheduling preferences
- checkpoint behavior
- recovery behavior
- monitoring behavior

Future implementations may additionally support:

- priority inheritance
- resource quotas
- adaptive scheduling
- distributed execution policies
- security policies
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(
    frozen=True,
    slots=True,
)
class ExecutionPolicy:
    """
    Immutable runtime execution policy.
    """

    #
    # Retry
    #

    max_retry_attempts: int = 3

    enable_retry: bool = True

    #
    # Timeout
    #

    timeout_seconds: float = 300.0

    enable_timeout: bool = True

    #
    # Scheduling
    #

    enable_parallel_execution: bool = False

    max_parallel_tasks: int = 1

    #
    # Recovery
    #

    enable_checkpointing: bool = True

    enable_recovery: bool = True

    #
    # Monitoring
    #

    enable_metrics: bool = True

    enable_tracing: bool = True

    enable_events: bool = True

    #
    # Middleware
    #

    enable_logging_middleware: bool = True

    enable_retry_middleware: bool = True

    enable_timeout_middleware: bool = True

    enable_metrics_middleware: bool = True

    enable_tracing_middleware: bool = True

    #
    # User metadata
    #

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Derived Properties
    # ------------------------------------------------------------------

    @property
    def middleware_enabled(
        self,
    ) -> bool:
        """
        Whether any middleware is enabled.
        """

        return any(
            (
                self.enable_logging_middleware,
                self.enable_retry_middleware,
                self.enable_timeout_middleware,
                self.enable_metrics_middleware,
                self.enable_tracing_middleware,
            ),
        )

    @property
    def resilience_enabled(
        self,
    ) -> bool:
        """
        Whether resilience features are enabled.
        """

        return (
            self.enable_retry
            or self.enable_recovery
            or self.enable_checkpointing
        )

    @property
    def monitoring_enabled(
        self,
    ) -> bool:
        """
        Whether monitoring is enabled.
        """

        return any(
            (
                self.enable_metrics,
                self.enable_tracing,
                self.enable_events,
            ),
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution policy diagnostics.
        """

        return {
            "max_retry_attempts": (
                self.max_retry_attempts
            ),
            "timeout_seconds": (
                self.timeout_seconds
            ),
            "parallel_execution": (
                self.enable_parallel_execution
            ),
            "max_parallel_tasks": (
                self.max_parallel_tasks
            ),
            "checkpointing": (
                self.enable_checkpointing
            ),
            "recovery": (
                self.enable_recovery
            ),
            "monitoring": (
                self.monitoring_enabled
            ),
            "middleware": (
                self.middleware_enabled
            ),
            "metadata": (
                self.metadata
            ),
        }