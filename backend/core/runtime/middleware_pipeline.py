"""
Runtime middleware pipeline.

Executes a chain of runtime middleware before delegating to the
execution engine.
"""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable

from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.middleware import (
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import MiddlewareContext


TerminalHandler = Callable[
    [ExecutionRequest],
    Awaitable[ExecutionResult],
]


class MiddlewarePipeline:
    """
    Executes runtime middleware in registration order.
    """

    def __init__(
        self,
        middleware: tuple[RuntimeMiddleware, ...] = (),
    ) -> None:
        self._middleware = list(
            middleware,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def middleware(
        self,
    ) -> tuple[RuntimeMiddleware, ...]:
        """
        Registered middleware.
        """
        return tuple(
            self._middleware,
        )

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def add(
        self,
        middleware: RuntimeMiddleware,
    ) -> None:
        """
        Register middleware.
        """
        self._middleware.append(
            middleware,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        terminal: TerminalHandler,
    ) -> ExecutionResult:
        """
        Execute the middleware pipeline.
        """

        async def invoke(
            index: int,
            current_request: ExecutionRequest,
        ) -> ExecutionResult:
            if index >= len(
                self._middleware,
            ):
                return await terminal(
                    current_request,
                )

            middleware = self._middleware[
                index
            ]

            async def next_handler(
                next_request: ExecutionRequest,
            ) -> ExecutionResult:
                return await invoke(
                    index + 1,
                    next_request,
                )

            return await middleware.invoke(
                context,
                current_request,
                next_handler,
            )

        return await invoke(
            0,
            request,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware pipeline diagnostics.
        """
        return {
            "count": len(
                self._middleware,
            ),
            "middleware": tuple(
                middleware.name
                for middleware in self._middleware
            ),
        }