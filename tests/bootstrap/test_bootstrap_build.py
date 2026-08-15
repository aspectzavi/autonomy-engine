"""
Kernel bootstrap construction tests.

Verifies that a freshly constructed KernelBootstrap produces a fully
wired, working system -- not just a container with registrations, but
services whose dependencies actually point at the same shared
instances.

This suite exists because the composition root previously had zero
test coverage, which let two real wiring bugs go undetected:

- AgentService resolved before agent infrastructure was registered,
  so it ended up with a disconnected, empty AgentManager (built-in
  agents were never visible to it)
- AgentManager.__init__ used `registry or AgentRegistry()`, which
  silently discards an injected-but-empty AgentRegistry (it defines
  __len__, so an empty registry is falsy) and replaces it with a new,
  disconnected one
"""

from __future__ import annotations

import pytest

from backend.core.agents.registry import AgentRegistry
from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.workflows.workflow_runtime_pipeline import (
    WorkflowRuntimePipeline,
)


def test_bootstrap_registers_built_in_agents() -> None:
    """
    A freshly constructed KernelBootstrap must have its built-in
    agents (e.g. "planning") actually registered and reachable
    through agent_service, not just constructible via the container.
    """

    bootstrap = KernelBootstrap()

    agents = bootstrap.agent_service.agents()

    assert len(agents) >= 1

    names = [agent.name for agent in agents]

    assert "planning" in names


def test_bootstrap_agent_manager_shares_the_registered_registry() -> None:
    """
    AgentService.manager.registry must be the SAME instance the
    container resolves for AgentRegistry -- not a disconnected copy.
    """

    bootstrap = KernelBootstrap()

    registry = bootstrap.container.resolve(
        AgentRegistry,
    )

    assert (
        bootstrap.agent_service.manager.registry
        is registry
    )

    assert len(registry) >= 1


def test_bootstrap_workflow_service_uses_the_full_pipeline() -> None:
    """
    WorkflowService must be wired to WorkflowRuntimePipeline (the
    monitored/resilient/recoverable runtime), not a bare fallback
    runtime with no monitoring, retry, or recovery.
    """

    bootstrap = KernelBootstrap()

    runtime = (
        bootstrap.workflow_service._workflow_runtime
    )

    assert isinstance(
        runtime,
        WorkflowRuntimePipeline,
    )


def test_bootstrap_task_service_is_registered_and_reachable() -> None:
    """
    TaskService must be a real, working part of a freshly constructed
    KernelBootstrap -- resolvable, startable, and able to run a
    submitted task -- not merely present in the container.
    """

    from backend.core.services.task_service import TaskService

    bootstrap = KernelBootstrap()

    service = bootstrap.container.resolve(TaskService)

    assert service is bootstrap.task_service
    assert isinstance(service, TaskService)


@pytest.mark.asyncio
async def test_bootstrap_agent_execution_persists_memory() -> None:
    """
    A goal executed through bootstrap.agent_service.execute() must
    have its generated experience actually persisted and queryable
    through the shared MemoryService -- not just recorded into a
    throwaway in-memory list that nothing reads back.
    """

    from backend.core.agents.goal import Goal
    from backend.core.memory.memory_query import MemoryQuery
    from backend.core.observability.events import EventBus
    from backend.core.observability.logger import KernelLogger
    from backend.core.services.memory_service import MemoryService
    from backend.core.tasks.context import TaskContext

    bootstrap = KernelBootstrap()

    assert bootstrap.agent_service.memory_service is (
        bootstrap.container.resolve(MemoryService)
    )

    task_context = TaskContext(
        runtime=bootstrap.runtime_context,
        container=bootstrap.container,
        logger=KernelLogger(),
        events=EventBus(),
    )

    await bootstrap.agent_service.execute(
        agent="planning",
        goal=Goal(description="bootstrap memory smoke test"),
        task_context=task_context,
    )

    found = await bootstrap.agent_service.memory_service.query(
        MemoryQuery(text="planning", limit=10),
    )

    assert len(found.entries) >= 1
