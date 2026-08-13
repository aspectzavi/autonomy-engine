"""
Workflow middleware.

Defines the interface for middleware that intercepts workflow execution.

Middleware provides cross-cutting behavior around workflow execution
without modifying the runtime or executor.

Typical responsibilities include:

- logging
- metrics
- tracing
- authorization
- retries
- timeouts
- validation
- auditing

Middleware is executed as a chain.

Future implementations may additionally support:

- dependency injection
- dynamic middleware registration
- conditional middleware execution
- distributed middleware
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections.abc import Awaitable
from collections.abc import Callable

from backend.core.workflows.middleware.middleware_context import (
    MiddlewareContext,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)

# Signature of the next middleware in the chain.
NextMiddleware = Callable[
    [MiddlewareContext],
    Awaitable[RuntimeReport],
]


class WorkflowMiddleware(ABC):
    """
    Base workflow middleware.
    """

    @abstractmethod
    async def execute(
        self,
        context: MiddlewareContext,
        next_handler: NextMiddleware,
    ) -> RuntimeReport:
        """
        Execute middleware.

        Implementations may perform work before and/or after delegating
        to the next middleware.

        Args:
            context:
                Shared middleware execution context.

            next_handler:
                Delegate to the remainder of the middleware chain.

        Returns:
            Runtime execution report.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """

        return {
            "middleware": self.__class__.__name__,
        }