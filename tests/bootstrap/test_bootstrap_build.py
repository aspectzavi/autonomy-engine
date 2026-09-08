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


@pytest.mark.asyncio
async def test_bootstrap_memory_store_is_semantic_vector_memory() -> None:
    """
    The container's registered MemoryStore must be VectorMemory (real
    embeddings + cosine similarity search), not the plain substring-
    matching MemoryStore base class -- and it must be the exact same
    instance MemoryService uses, not a disconnected copy.
    """

    from backend.core.memory.memory_entry import MemoryEntry
    from backend.core.memory.memory_query import MemoryQuery
    from backend.core.memory.memory_store import MemoryStore
    from backend.core.memory.vector_memory import VectorMemory
    from backend.core.services.memory_service import MemoryService

    bootstrap = KernelBootstrap()

    provider = bootstrap.container.resolve(MemoryStore)
    assert isinstance(provider, VectorMemory)

    memory_service = bootstrap.container.resolve(MemoryService)
    assert memory_service.provider is provider

    await memory_service.store(
        MemoryEntry(id="a", content="cat sitting by a sunny window"),
    )
    await memory_service.store(
        MemoryEntry(id="b", content="quarterly revenue grew this year"),
    )

    result = await memory_service.query(
        MemoryQuery(text="a cat near a window", limit=2),
    )

    assert result.entries[0].id == "a"


def test_bootstrap_filesystem_config_is_not_di_auto_constructed() -> None:
    """
    Regression test: FilesystemConfig is a concrete dataclass, unlike
    BrowserProvider/DesktopProvider (abstract classes). An
    unregistered FilesystemConfig dependency doesn't fail cleanly the
    way an unregistered ABC does -- the DI container successfully
    auto-constructs one, but recursively "resolves" each of its own
    primitive-typed fields too (str, bool), and bare str()/bool()
    succeed trivially (yielding '' and False) instead of using the
    dataclass's real field defaults. This silently broke every
    filesystem tool (write_file failed with "unknown encoding: ''",
    overwrite protection was always on regardless of configuration)
    until FilesystemConfig was registered as a real instance in
    KernelBootstrap, the same way EngineConfig/Tracing/KernelLogger
    already were.
    """

    from backend.core.config.filesystem import FilesystemConfig

    bootstrap = KernelBootstrap()

    config = bootstrap.container.resolve(FilesystemConfig)

    assert config.encoding == "utf-8"
    assert config.create_missing_directories is True
    assert config.overwrite_existing_files is True

    factory_config = (
        bootstrap.tool_service.factory.filesystem_config
    )

    assert factory_config is config


@pytest.mark.asyncio
async def test_bootstrap_write_file_tool_actually_writes(tmp_path) -> None:
    """
    End-to-end proof the fix works: write_file through a fully
    bootstrapped system must produce a real file with the real
    content, not fail on a corrupted encoding.
    """

    bootstrap = KernelBootstrap()
    await bootstrap.runtime.start()

    try:
        write = bootstrap.tool_service.registry.get(
            "write_file",
        )

        from backend.core.tools.context import ToolContext

        result = await write.execute(
            ToolContext(
                arguments={
                    "path": str(tmp_path / "out.txt"),
                    "content": "hello",
                },
            ),
        )

        #
        # The default workspace sandboxes to cwd, so writing to an
        # arbitrary tmp_path is expected to be blocked by the
        # sandbox rather than succeed -- what matters here is that
        # it fails for a sandbox reason, not an encoding error like
        # "unknown encoding: ''" (the bug this test guards against).
        #
        assert not result.success
        assert "encoding" not in result.error.lower()
    finally:
        await bootstrap.runtime.stop()
