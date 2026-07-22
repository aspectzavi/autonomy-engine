"""
Runtime execution pipeline.

Coordinates execution requests through the runtime middleware pipeline
before delegating to the execution engine.
"""

from __future__ import annotations

from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.middleware_context import (
    MiddlewareContext,
)
from backend.core.runtime.middleware_pipeline import (
    MiddlewarePipeline,
)
from backend.core.runtime.middleware_registry import (
    MiddlewareRegistry,
)
from backend.core.runtime.default_middleware import (
    register_default_middleware,
)

from backend.core.observability.tracing import (
    Tracing,
)

class ExecutionPipeline:
    """
    Coordinates runtime execution.
    """

    def __init__(
        self,
        *,
        execution_engine: ExecutionEngine,
        tracing: Tracing,
        runtime_context: RuntimeContext | None = None,
        middleware: MiddlewarePipeline | None = None,
        middleware_registry: MiddlewareRegistry | None = None,
    ) -> None:
        self._execution_engine = execution_engine

        self._runtime_context = runtime_context

        if middleware is not None:
            self._middleware = middleware

        else:
            registry = (
                middleware_registry
                or MiddlewareRegistry()
            )

            if len(registry) == 0:
                register_default_middleware(
                    registry,
                    tracing=tracing,
                )

            self._middleware = MiddlewarePipeline(
                registry.middleware(),
            )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def execution_engine(
        self,
    ) -> ExecutionEngine:
        """
        Underlying execution engine.
        """
        return self._execution_engine

    @property
    def middleware(
        self,
    ) -> MiddlewarePipeline:
        """
        Runtime middleware pipeline.
        """
        return self._middleware

    @property
    def runtime_context(
        self,
    ) -> RuntimeContext | None:
        """
        Runtime execution context.
        """
        return self._runtime_context

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute a runtime request.
        """

        context = MiddlewareContext(
            runtime=self.runtime_context,
        )

        context.set(
            "request_id",
            request.request_id,
        )

        context.set(
            "goal",
            request.goal.description,
        )

        return await self.middleware.execute(
            context=context,
            request=request,
            terminal=self.execution_engine.execute,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution pipeline diagnostics.
        """

        return {
            "execution_engine": (
                self.execution_engine.diagnostics()
            ),
            "middleware": (
                self.middleware.diagnostics()
            ),
            "runtime_context_attached": (
                self.runtime_context is not None
            ),
        }