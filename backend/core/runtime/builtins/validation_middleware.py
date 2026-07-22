"""
Runtime validation middleware.

Performs lightweight validation of execution requests before they enter
the execution engine.

This middleware should generally be the first middleware registered in
the runtime pipeline.
"""

from __future__ import annotations

from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import (
    MiddlewareContext,
)


class ValidationMiddleware(RuntimeMiddleware):
    """
    Validates execution requests.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        """
        Validate the execution request before continuing.
        """

        #
        # Goal must exist.
        #
        if request.goal is None:
            return ExecutionResult(
                success=False,
                message="Execution request has no goal.",
                errors=(
                    "Missing execution goal.",
                ),
            )

        #
        # Goal description must not be empty.
        #
        description = request.goal.description.strip()

        if not description:
            return ExecutionResult(
                success=False,
                message="Execution goal is empty.",
                errors=(
                    "Goal description cannot be empty.",
                ),
            )

        #
        # Record validation.
        #
        context.set(
            "validated",
            True,
        )

        #
        # Continue execution.
        #
        return await call_next(
            request,
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "validation": (
                    "execution_request"
                ),
            }
        )

        return diagnostics