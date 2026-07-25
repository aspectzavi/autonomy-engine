"""
ExecutionPipeline middleware ordering tests.
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
    Records execution reaching the coordinator.
    """

    def __init__(self, trace: list[str]) -> None:
        self._trace = trace

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        self._trace.append("engine")

        return ExecutionResult(
            success=True,
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {}


class RecordingMiddleware(RuntimeMiddleware):
    """
    Records middleware execution.
    """

    def __init__(
        self,
        name: str,
        trace: list[str],
    ) -> None:
        self._name = name
        self._trace = trace

    @property
    def name(self) -> str:
        return self._name

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        self._trace.append(
            f"{self.name}:before",
        )

        result = await call_next(
            request,
        )

        self._trace.append(
            f"{self.name}:after",
        )

        return result


@pytest.mark.asyncio
async def test_pipeline_order() -> None:
    """
    Middleware should execute in registration order
    and unwind in reverse order.
    """

    trace: list[str] = []

    coordinator = RecordingCoordinator(
        trace,
    )

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
                    "first",
                    trace,
                ),
                RecordingMiddleware(
                    "second",
                    trace,
                ),
                RecordingMiddleware(
                    "third",
                    trace,
                ),
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="pipeline ordering",
        ),
    )

    result = await pipeline.execute(
        request,
    )

    assert result.success is True

    assert trace == [
        "first:before",
        "second:before",
        "third:before",
        "engine",
        "third:after",
        "second:after",
        "first:after",
    ]