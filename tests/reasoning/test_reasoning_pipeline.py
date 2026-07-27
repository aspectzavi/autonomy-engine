"""
Tests for the reasoning pipeline.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.memory.memory import Memory
from backend.core.observability.events import EventBus
from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_engine import (
    ReasoningEngine,
)
from backend.core.reasoning.reasoning_pipeline import (
    ReasoningPipeline,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)
from backend.core.reasoning.reasoning_result import (
    ReasoningResult,
)
from backend.core.reasoning.decision import Decision
from backend.core.reasoning.reasoning_trace import ReasoningTrace


class RecordingReasoningEngine(ReasoningEngine):
    """
    Test reasoning engine that records requests.
    """

    def __init__(self) -> None:
        super().__init__()

        self.calls = 0
        self.last_request: ReasoningRequest | None = None
        self.last_context: ReasoningContext | None = None

    async def reason(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
        *,
        strategy: str | None = None,
    ) -> ReasoningResult:
        self.calls += 1

        self.last_request = request
        self.last_context = context

        return ReasoningResult(
            strategy="test",
            decision=Decision(
                name="test",
                outcome="continue",
                confidence=1.0,
            ),
            trace=ReasoningTrace(),
            confidence=1.0,
            rationale="pipeline test",
        )


def create_context() -> AgentContext:
    """
    Create a minimal runtime context.
    """

    return AgentContext(
        event_bus=EventBus(),
    )


async def test_pipeline_invokes_reasoning_engine() -> None:
    """
    Pipeline should invoke the reasoning engine exactly once.
    """

    engine = RecordingReasoningEngine()

    pipeline = ReasoningPipeline(
        engine=engine,
    )

    goal = Goal(
        description="Search the web",
    )

    result = await pipeline.run(
        goal=goal,
        context=create_context(),
    )

    assert engine.calls == 1

    assert result.strategy == "test"


async def test_pipeline_builds_request() -> None:
    """
    Pipeline should build a reasoning request from the goal.
    """

    engine = RecordingReasoningEngine()

    pipeline = ReasoningPipeline(
        engine=engine,
    )

    goal = Goal(
        description="Open browser",
    )

    await pipeline.run(
        goal=goal,
        context=create_context(),
    )

    assert engine.last_request is not None

    assert (
        engine.last_request.goal
        == "Open browser"
    )


async def test_pipeline_creates_reasoning_context() -> None:
    """
    Pipeline should create a reasoning context.
    """

    engine = RecordingReasoningEngine()

    pipeline = ReasoningPipeline(
        engine=engine,
    )

    await pipeline.run(
        goal=Goal(
            description="Generate report",
        ),
        context=create_context(),
    )

    assert engine.last_context is not None

    assert isinstance(
        engine.last_context.memory,
        Memory,
    )


async def test_pipeline_returns_reasoning_result() -> None:
    """
    Pipeline should return the engine result unchanged.
    """

    pipeline = ReasoningPipeline(
        engine=RecordingReasoningEngine(),
    )

    result = await pipeline.run(
        goal=Goal(
            description="Create workflow",
        ),
        context=create_context(),
    )

    assert result.strategy == "test"

    assert result.confidence == 1.0

    assert result.rationale == "pipeline test"


def test_pipeline_diagnostics() -> None:
    """
    Diagnostics should expose the configured engine.
    """

    pipeline = ReasoningPipeline(
        engine=RecordingReasoningEngine(),
    )

    diagnostics = pipeline.diagnostics()

    assert diagnostics["engine"] == "RecordingReasoningEngine"

    assert "engine_diagnostics" in diagnostics