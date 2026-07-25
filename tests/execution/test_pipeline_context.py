"""
ExecutionPipeline context tests.
"""

from __future__ import annotations

from typing import cast

import pytest

from backend.core.agents.goal import Goal
from backend.core.observability.tracing import Tracing
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_pipeline import (
    ExecutionPipeline,
)
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import (
    MiddlewareContext,
)
from backend.core.runtime.middleware_pipeline import (
    MiddlewarePipeline,
)


class DummyCoordinator:
    """
    Minimal coordinator stub.
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


class ContextCaptureMiddleware(RuntimeMiddleware):
    """
    Captures values stored inside MiddlewareContext.
    """

    def __init__(
        self,
    ) -> None:
        self.request_id: str | None = None
        self.goal: str | None = None

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        self.request_id = cast(
            str,
            context.get(
                "request_id",
            ),
        )

        self.goal = cast(
            str,
            context.get(
                "goal",
            ),
        )

        return await call_next(
            request,
        )


@pytest.mark.asyncio
async def test_pipeline_context() -> None:
    """
    ExecutionPipeline should populate MiddlewareContext
    before executing middleware.
    """

    coordinator = cast(
        RuntimeCoordinator,
        DummyCoordinator(),
    )

    engine = ExecutionEngine(
        coordinator=coordinator,
    )

    middleware = ContextCaptureMiddleware()

    pipeline = ExecutionPipeline(
        execution_engine=engine,
        tracing=Tracing(),
        middleware=MiddlewarePipeline(
            (
                middleware,
            ),
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="test pipeline context",
        ),
    )

    result = await pipeline.execute(
        request,
    )

    assert result.success is True

    assert (
        middleware.request_id
        == request.request_id
    )

    assert (
        middleware.goal
        == request.goal.description
    )

    diagnostics = pipeline.diagnostics()

    assert diagnostics[
        "runtime_context_attached"
    ] is False