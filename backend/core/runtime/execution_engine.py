"""
Runtime execution engine.

Provides the primary entry point for autonomous execution.

The execution engine is a thin façade over the RuntimeCoordinator. It
exists to isolate application-facing execution APIs from the internal
runtime orchestration layer, allowing future features such as
middleware, retries, tracing, authorization, and execution policies to
be added without changing callers.
"""

from __future__ import annotations

from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)


class ExecutionEngine:
    """
    Primary runtime execution entry point.
    """

    def __init__(
        self,
        *,
        coordinator: RuntimeCoordinator,
    ) -> None:
        self._coordinator = coordinator

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def coordinator(
        self,
    ) -> RuntimeCoordinator:
        """
        Return the runtime coordinator.
        """
        return self._coordinator

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute an autonomous request.
        """
        return await self.coordinator.execute(
            request,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return execution engine diagnostics.
        """
        return {
            "coordinator": (
                self.coordinator.diagnostics()
            ),
        }