"""
Agent service memory-persistence tests.

Verifies AgentService.execute() closes the loop between Agent
execution and MemoryService: context.memory is auto-populated so
experience recording has somewhere to land during the run, and
whatever gets generated is actually persisted afterward -- not just
appended to a throwaway in-memory list that nothing reads back.
"""

from __future__ import annotations

import pytest

from backend.core.agents.agent import Agent
from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry
from backend.core.agents.result import AgentResult
from backend.core.agents.state import AgentState
from backend.core.memory.memory_entry import MemoryEntry
from backend.core.memory.memory_query import MemoryQuery
from backend.core.memory.memory_store import MemoryStore
from backend.core.observability.events import EventBus
from backend.core.services.agent_service import AgentService
from backend.core.services.memory_service import MemoryService
from backend.core.tasks.context import TaskContext


def _memory_service() -> MemoryService:
    return MemoryService(provider=MemoryStore())


def _task_context() -> TaskContext:
    from unittest.mock import Mock

    return TaskContext(
        runtime=Mock(),
        container=Mock(),
        logger=Mock(),
        events=EventBus(),
    )


class _FakeAgent(Agent):
    """
    Minimal agent that bypasses reasoning/planning/execution entirely
    and just records one experience, to isolate AgentService.execute()'s
    memory-wiring behavior from the rest of the planning stack.
    """

    def __init__(self, *, should_succeed: bool) -> None:
        from unittest.mock import Mock

        super().__init__(
            name="fake",
            planner=Mock(),
            optimizer=Mock(),
            compiler=Mock(),
            workflow_service=Mock(),
            experience_recorder=Mock(),
        )
        self._should_succeed = should_succeed

    async def reason(self, goal, context):  # type: ignore[override]
        raise NotImplementedError

    async def execute(  # type: ignore[override]
        self,
        goal: Goal,
        task_context: TaskContext,
        context: AgentContext | None = None,
    ) -> AgentResult:
        assert context is not None
        assert context.memory is not None

        self._state = AgentState.EXECUTING

        context.memory.remember(
            MemoryEntry(
                id="entry-1",
                content=f"ran goal: {goal.description}",
            ),
        )

        if self._should_succeed:
            self._state = AgentState.COMPLETED
            return AgentResult.ok(
                agent=self.name,
                goal=goal.description,
            )

        self._state = AgentState.FAILED
        return AgentResult.failure(
            agent=self.name,
            goal=goal.description,
            error="boom",
        )


def _service(agent: Agent, memory_service: MemoryService | None) -> AgentService:
    registry = AgentRegistry()
    registry.register(agent)
    manager = AgentManager(registry=registry)
    return AgentService(manager=manager, memory_service=memory_service)


@pytest.mark.asyncio
async def test_execute_auto_populates_context_memory_when_none() -> None:
    service = _service(_FakeAgent(should_succeed=True), memory_service=None)

    result = await service.execute(
        agent="fake",
        goal=Goal(description="hello"),
        task_context=_task_context(),
    )

    assert result.success


@pytest.mark.asyncio
async def test_execute_persists_generated_memory_on_success() -> None:
    memory_service = _memory_service()
    service = _service(_FakeAgent(should_succeed=True), memory_service)

    await service.execute(
        agent="fake",
        goal=Goal(description="hello"),
        task_context=_task_context(),
    )

    found = await memory_service.query(
        MemoryQuery(text="hello", limit=10),
    )

    assert len(found.entries) == 1
    assert found.entries[0].content == "ran goal: hello"


@pytest.mark.asyncio
async def test_execute_persists_generated_memory_on_failure() -> None:
    memory_service = _memory_service()
    service = _service(_FakeAgent(should_succeed=False), memory_service)

    result = await service.execute(
        agent="fake",
        goal=Goal(description="hello"),
        task_context=_task_context(),
    )

    assert not result.success

    found = await memory_service.query(
        MemoryQuery(text="hello", limit=10),
    )

    assert len(found.entries) == 1


@pytest.mark.asyncio
async def test_execute_without_memory_service_does_not_persist_or_crash() -> None:
    service = _service(_FakeAgent(should_succeed=True), memory_service=None)

    result = await service.execute(
        agent="fake",
        goal=Goal(description="hello"),
        task_context=_task_context(),
    )

    assert result.success
    assert service.memory_service is None


@pytest.mark.asyncio
async def test_execute_reuses_a_caller_supplied_context_memory() -> None:
    from backend.core.runtime.execution_memory import ExecutionMemory

    memory_service = _memory_service()
    service = _service(_FakeAgent(should_succeed=True), memory_service)

    context = AgentContext(
        event_bus=EventBus(),
        memory=ExecutionMemory(),
    )

    await service.execute(
        agent="fake",
        goal=Goal(description="hello"),
        task_context=_task_context(),
        context=context,
    )

    #
    # The service must not replace an already-attached memory object.
    #
    assert len(context.memory.generated) == 1
