"""
Runtime execution pipeline.

Coordinates execution requests through the runtime execution engine.

The pipeline is intentionally lightweight. Workflow middleware,
monitoring, resilience, retries, tracing, checkpoints, and recovery are
handled by the WorkflowRuntime subsystem.

Responsibilities:

- accept execution requests
- delegate to the execution engine
- expose runtime diagnostics

Future implementations may additionally support:

- request validation
- admission control
- runtime policies
- execution throttling
"""

from __future__ import annotations

from backend.core.kernel.runtime_context import (
    RuntimeContext,
)
from backend.core.runtime.execution_engine import (
    ExecutionEngine,
)
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)


class ExecutionPipeline:
    """
    Coordinates runtime execution.

    The pipeline acts as a thin façade over the execution engine.
    """

    def __init__(
        self,
        *,
        execution_engine: ExecutionEngine,
        runtime_context: RuntimeContext | None = None,
    ) -> None:
        self._execution_engine = execution_engine
        self._runtime_context = runtime_context

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

        return await self.execution_engine.execute(
            request,
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
            "runtime_context_attached": (
                self.runtime_context is not None
            ),
        }