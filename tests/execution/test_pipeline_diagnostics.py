"""
ExecutionPipeline diagnostics tests.
"""

from __future__ import annotations

from typing import cast

from backend.core.observability.tracing import Tracing
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_pipeline import ExecutionPipeline
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.middleware_pipeline import MiddlewarePipeline


class DummyCoordinator:
    """
    Minimal coordinator stub.
    """

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        raise NotImplementedError

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {
            "coordinator": "ok",
        }


def test_pipeline_diagnostics() -> None:
    """
    ExecutionPipeline should expose diagnostics from both
    the execution engine and middleware pipeline.
    """

    engine = ExecutionEngine(
        coordinator=cast(
            RuntimeCoordinator,
            DummyCoordinator(),
        ),
    )

    middleware = MiddlewarePipeline()

    pipeline = ExecutionPipeline(
        execution_engine=engine,
        tracing=Tracing(),
        middleware=middleware,
    )

    diagnostics = pipeline.diagnostics()

    assert diagnostics["execution_engine"] == {
        "coordinator": {
            "coordinator": "ok",
        },
    }

    assert diagnostics["middleware"] == {
        "count": 0,
        "middleware": (),
    }

    assert (
        diagnostics["runtime_context_attached"]
        is False
    )