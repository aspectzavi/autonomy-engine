"""
Runtime facade.

Provides the primary public interface for autonomous runtime execution.

The facade hides request construction and execution orchestration behind
a simple API suitable for applications, APIs, CLIs, and future desktop
interfaces.
"""

from __future__ import annotations

from backend.core.agents.goal import Goal
from backend.core.runtime.execution_pipeline import (
    ExecutionPipeline,
)
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.request_builder import RequestBuilder


class RuntimeFacade:
    """
    Public runtime execution interface.
    """

    def __init__(
        self,
        *,
        execution_pipeline: ExecutionPipeline,
        request_builder: RequestBuilder | None = None,
    ) -> None:
        self._execution_pipeline = (
            execution_pipeline
        )

        self._request_builder = (
            request_builder
            or RequestBuilder()
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def execution_pipeline(
        self,
    ) -> ExecutionPipeline:
        """
        Runtime execution pipeline.
        """
        return self._execution_pipeline

    @property
    def request_builder(
        self,
    ) -> RequestBuilder:
        """
        Runtime request builder.
        """
        return self._request_builder

    # ------------------------------------------------------------------
    # Request Creation
    # ------------------------------------------------------------------

    def create_request(
        self,
        goal: Goal,
        *,
        metadata: dict[str, object] | None = None,
    ) -> ExecutionRequest:
        """
        Build an execution request.
        """
        return self.request_builder.build(
            goal=goal,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        goal: Goal,
        *,
        metadata: dict[str, object] | None = None,
    ) -> ExecutionResult:
        """
        Execute a goal through the runtime.
        """
        request = self.create_request(
            goal,
            metadata=metadata,
        )

        return await self.execution_pipeline.execute(
            request,
        )

    async def execute_request(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute an existing runtime request.
        """
        return await self.execution_pipeline.execute(
            request,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return runtime facade diagnostics.
        """
        return {
            "execution_pipeline": (
                self.execution_pipeline.diagnostics()
            ),
            "request_builder": (
                self.request_builder.diagnostics()
            ),
        }