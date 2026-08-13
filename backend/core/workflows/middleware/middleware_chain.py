"""
Middleware chain.

Coordinates execution of WorkflowMiddleware instances.

The chain executes middleware in registration order, with each
middleware delegating to the next until the terminal handler is
reached.

Future implementations may additionally support:

- conditional middleware
- middleware priorities
- dynamic insertion/removal
- short-circuit execution
"""

from __future__ import annotations


from backend.core.workflows.middleware.middleware_context import (
    MiddlewareContext,
)
from backend.core.workflows.runtime_report import (
    RuntimeReport,
)
from backend.core.workflows.middleware.workflow_middleware import (
    NextMiddleware,
    WorkflowMiddleware,
)


class MiddlewareChain:
    """
    Executes workflow middleware.
    """

    def __init__(
        self,
        *,
        terminal_handler: NextMiddleware,
    ) -> None:
        self._terminal_handler = terminal_handler
        self._middleware: list[
            WorkflowMiddleware
        ] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def add(
        self,
        middleware: WorkflowMiddleware,
    ) -> None:
        """
        Register middleware.
        """

        self._middleware.append(
            middleware,
        )

    @property
    def middleware(
        self,
    ) -> tuple[
        WorkflowMiddleware,
        ...,
    ]:
        """
        Registered middleware.
        """

        return tuple(
            self._middleware,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: MiddlewareContext,
    ) -> RuntimeReport:
        """
        Execute the middleware pipeline.
        """

        async def invoke(
            index: int,
            ctx: MiddlewareContext,
        ) -> RuntimeReport:
            if index >= len(
                self._middleware,
            ):
                return await self._terminal_handler(
                    ctx,
                )

            middleware = self._middleware[
                index
            ]

            async def next_handler(
                next_context: MiddlewareContext,
            ) -> RuntimeReport:
                return await invoke(
                    index + 1,
                    next_context,
                )

            return await middleware.execute(
                ctx,
                next_handler,
            )

        return await invoke(
            0,
            context,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware chain diagnostics.
        """

        return {
            "middleware_count": len(
                self._middleware,
            ),
            "middleware": tuple(
                type(
                    middleware,
                ).__name__
                for middleware in self._middleware
            ),
        }