"""
ExecutionPipeline cancellation tests.
"""

from __future__ import annotations

import asyncio
from typing import cast

import pytest

from backend.core.agents.goal import Goal
from backend.core.observability.tracing import Tracing
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_pipeline import ExecutionPipeline
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import MiddlewareContext
from backend.core.runtime.middleware_pipeline import MiddlewarePipeline


class DummyCoordinator:
    """
    Coordinator that should never be reached.
    """

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        return ExecutionResult(
            success=True,
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {}


class CancellingMiddleware(RuntimeMiddleware):
    """
    Simulates cancellation.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        raise asyncio.CancelledError()


@pytest.mark.asyncio
async def test_pipeline_cancellation() -> None:
    """
    Cancellation should propagate through the
    execution pipeline.
    """

    engine = ExecutionEngine(
        coordinator=cast(
            RuntimeCoordinator,
            DummyCoordinator(),
        ),
    )

    pipeline = ExecutionPipeline(
        execution_engine=engine,
        tracing=Tracing(),
        middleware=MiddlewarePipeline(
            (
                CancellingMiddleware(),
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="pipeline cancellation",
        ),
    )

    with pytest.raises(
        asyncio.CancelledError,
    ):
        await pipeline.execute(
            request,
        )