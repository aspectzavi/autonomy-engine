"""
ExecutionPipeline middleware integration tests.
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


class RecordingCoordinator:
    """
    Records whether execution reaches the coordinator.
    """

    def __init__(self) -> None:
        self.called = False

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        self.called = True

        return ExecutionResult(
            success=True,
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {}


class RecordingMiddleware(RuntimeMiddleware):
    """
    Records middleware execution order.
    """

    def __init__(
        self,
        events: list[str],
    ) -> None:
        self._events = events

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        self._events.append(
            "before",
        )

        result = await call_next(
            request,
        )

        self._events.append(
            "after",
        )

        return result


@pytest.mark.asyncio
async def test_pipeline_middleware() -> None:
    """
    Middleware should execute before and after
    the execution engine.
    """

    events: list[str] = []

    coordinator = RecordingCoordinator()

    engine = ExecutionEngine(
        coordinator=cast(
            RuntimeCoordinator,
            coordinator,
        ),
    )

    pipeline = ExecutionPipeline(
        execution_engine=engine,
        tracing=Tracing(),
        middleware=MiddlewarePipeline(
            (
                RecordingMiddleware(
                    events,
                ),
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="middleware integration",
        ),
    )

    result = await pipeline.execute(
        request,
    )

    assert result.success is True

    assert coordinator.called is True

    assert events == [
        "before",
        "after",
    ]