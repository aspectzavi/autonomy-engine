"""
ExecutionEngine execute tests.
"""

from __future__ import annotations

from typing import cast

import pytest

from backend.core.agents.goal import Goal
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.execution_engine import ExecutionEngine
from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult


class RecordingCoordinator:
    """
    Coordinator used to verify delegation.
    """

    def __init__(self) -> None:
        self.called = False
        self.request: ExecutionRequest | None = None

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        self.called = True
        self.request = request

        return ExecutionResult(
            success=True,
            message="delegated",
        )

    def diagnostics(
        self,
    ) -> dict[str, object]:
        return {}


@pytest.mark.asyncio
async def test_engine_execute() -> None:
    """
    ExecutionEngine should delegate execution to the coordinator.
    """

    coordinator = RecordingCoordinator()

    engine = ExecutionEngine(
        coordinator=cast(
            RuntimeCoordinator,
            coordinator,
        ),
    )

    request = ExecutionRequest(
        goal=Goal(
            description="engine delegation",
        ),
    )

    result = await engine.execute(
        request,
    )

    assert coordinator.called is True
    assert coordinator.request is request

    assert result.success is True
    assert result.message == "delegated"