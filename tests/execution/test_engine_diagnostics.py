"""
ExecutionEngine diagnostics tests.
"""

from __future__ import annotations

from typing import cast

from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult


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
            "running": True,
            "workers": 4,
        }


def test_engine_diagnostics() -> None:
    """
    ExecutionEngine should expose the coordinator
    diagnostics unchanged.
    """

    coordinator = cast(
        RuntimeCoordinator,
        DummyCoordinator(),
    )

    engine = ExecutionEngine(
        coordinator=coordinator,
    )

    diagnostics = engine.diagnostics()

    assert diagnostics == {
        "coordinator": {
            "running": True,
            "workers": 4,
        },
    }

    #
    # Property should expose the coordinator.
    #
    assert engine.coordinator is coordinator