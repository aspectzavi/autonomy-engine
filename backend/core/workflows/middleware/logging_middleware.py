"""
Logging middleware.

Provides structured logging around workflow execution.

Current responsibilities:

- log workflow start
- log workflow completion
- log workflow failures
- record execution duration

Future implementations may additionally support:

- structured JSON logging
- OpenTelemetry logs
- distributed logging
- log enrichment
- log correlation identifiers
"""

from __future__ import annotations

from datetime import UTC
from datetime import datetime

from backend.core.workflows.middleware.middleware_context import (
    MiddlewareContext,
)
from backend.core.workflows.middleware.workflow_middleware import (
    NextMiddleware,
    WorkflowMiddleware,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)


class LoggingMiddleware(
    WorkflowMiddleware,
):
    """
    Default workflow logging middleware.
    """

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Execute workflow logging.
        """

        started = datetime.now(
            UTC,
        )

        context.task_context.events.publish(
            "workflow.started",
            {
                "workflow": (
                    context.workflow.name
                ),
            },
        )

        try:
            report = await next_handler(
                context,
            )

            finished = datetime.now(
                UTC,
            )

            duration = (
                finished - started
            ).total_seconds()

            context.task_context.events.publish(
                "workflow.completed",
                {
                    "workflow": (
                        context.workflow.name
                    ),
                    "success": (
                        report.success
                    ),
                    "duration_seconds": (
                        duration
                    ),
                },
            )

            return report

        except Exception as exc:
            finished = datetime.now(
                UTC,
            )

            duration = (
                finished - started
            ).total_seconds()

            context.task_context.events.publish(
                "workflow.failed",
                {
                    "workflow": (
                        context.workflow.name
                    ),
                    "error": str(
                        exc,
                    ),
                    "duration_seconds": (
                        duration
                    ),
                },
            )

            raise

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "logs_start": True,
                "logs_completion": True,
                "logs_failures": True,
            },
        )

        return diagnostics