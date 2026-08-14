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
