"""
Timeout middleware.

Enforces an execution timeout for workflow execution.

The middleware wraps the remaining middleware chain using
``asyncio.wait_for()`` and raises TimeoutError when the configured
deadline is exceeded.

Current responsibilities:

- enforce workflow timeout
- expose timeout metadata
- preserve execution context

Future implementations may additionally support:

- per-workflow timeouts
- adaptive deadlines
- cancellation propagation
- graceful task shutdown
- distributed timeout coordination
"""

from __future__ import annotations

import asyncio

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


class TimeoutMiddleware(
    WorkflowMiddleware,
):
    """
    Default workflow timeout middleware.
    """

    TIMEOUT_KEY = "workflow.timeout"

    def __init__(
        self,
        *,
        timeout_seconds: float = 300.0,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero.",
            )

        self._timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def timeout_seconds(
        self,
    ) -> float:
        """
        Configured timeout.
        """

        return self._timeout_seconds

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Execute the remaining middleware chain within the configured
        timeout.
        """

        try:
            report = await asyncio.wait_for(
                next_handler(
                    context,
                ),
                timeout=self.timeout_seconds,
            )

            context.set(
                self.TIMEOUT_KEY,
                {
                    "timed_out": False,
                    "timeout_seconds": (
                        self.timeout_seconds
                    ),
                },
            )

            return report

        except TimeoutError:
            context.set(
                self.TIMEOUT_KEY,
                {
                    "timed_out": True,
                    "timeout_seconds": (
                        self.timeout_seconds
                    ),
                },
            )

            raise TimeoutError(
                (
                    "Workflow execution exceeded "
                    f"{self.timeout_seconds:.2f} seconds."
                ),
            ) from None

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
                "timeout_seconds": (
                    self.timeout_seconds
                ),
                "uses_asyncio_wait_for": True,
            },
        )

        return diagnostics