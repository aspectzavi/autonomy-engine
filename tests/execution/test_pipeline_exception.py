"""
ExecutionPipeline exception propagation tests.
"""

from __future__ import annotations

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


class FailingMiddleware(RuntimeMiddleware):
    """
    Middleware that intentionally fails.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        raise RuntimeError(
            "middleware failure",
        )


@pytest.mark.asyncio
async def test_pipeline_exception() -> None:
    """
    Exceptions raised by middleware should propagate
    through the execution pipeline.
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
                FailingMiddleware(),
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="pipeline exception",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="middleware failure",
    ):
        await pipeline.execute(
            request,
        )