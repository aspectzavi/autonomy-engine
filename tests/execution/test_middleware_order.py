"""
Middleware pipeline ordering tests.
"""

from __future__ import annotations


import pytest

from backend.core.agents.goal import Goal
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import MiddlewareContext
from backend.core.runtime.middleware_pipeline import (
    MiddlewarePipeline,
)


class RecordingMiddleware(RuntimeMiddleware):
    """
    Middleware that records execution order.
    """

    def __init__(
        self,
        name: str,
        trace: list[str],
    ) -> None:
        self._name = name
        self._trace = trace

    @property
    def name(
        self,
    ) -> str:
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
async def test_middleware_order() -> None:
    """
    Middleware should execute in registration order
    and unwind in reverse order.
    """

    trace: list[str] = []

    pipeline = MiddlewarePipeline(
        (
            RecordingMiddleware(
                "first",
                trace,
            ),
            RecordingMiddleware(
                "second",
                trace,
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="middleware ordering",
        ),
    )

    context = MiddlewareContext()

    async def terminal(
        request: ExecutionRequest,
    ) -> ExecutionResult:
        trace.append(
            "terminal",
        )

        return ExecutionResult(
            success=True,
        )

    result = await pipeline.execute(
        context=context,
        request=request,
        terminal=terminal,
    )

    assert result.success is True

    assert trace == [
        "first:before",
        "second:before",
        "terminal",
        "second:after",
        "first:after",
    ]

    diagnostics = pipeline.diagnostics()

    assert diagnostics["count"] == 2

    assert diagnostics["middleware"] == (
        "first",
        "second",
    )