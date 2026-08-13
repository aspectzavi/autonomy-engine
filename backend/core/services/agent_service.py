"""
Agent service.

Runtime-managed service responsible for the autonomous agent subsystem.
"""

from __future__ import annotations

from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.agents.agent import Agent

class AgentService(KernelService):
    """
    Runtime-managed agent subsystem.
    """

    def __init__(
        self,
        *,
        manager: AgentManager | None = None,
    ) -> None:
        super().__init__(
            metadata=ServiceMetadata(
                name="agent-service",
                version="1.0.0",
                description=(
                    "Runtime-managed autonomous agent subsystem."
                ),
            ),
        )

        self._manager = manager or AgentManager()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def manager(
        self,
    ) -> AgentManager:
        """
        Return the managed agent manager.
        """
        return self._manager

    @property
    def registry(
        self,
    ) -> AgentRegistry:
        """
        Return the managed agent registry.
        """
        return self.manager.registry

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def on_start(
        self,
    ) -> None:
        """
        Start the agent subsystem.
        """
        self.logger.info(
            "Agent subsystem started with %d registered agent(s).",
            len(self.registry),
        )

    async def on_stop(
        self,
    ) -> None:
        """
        Stop the agent subsystem.
        """
        self.registry.clear()

        self.logger.info(
            "Agent registry cleared."
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return agent service diagnostics.
        """
        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "manager": (
                    self.manager.diagnostics()
                ),
            }
        )

        return diagnostics
    
    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Agent:
        """
        Return a registered agent.
        """
        return self.manager.get(
            name,
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Whether an agent is registered.
        """
        return self.manager.registry.contains(
            name,
        )

    def agents(
        self,
    ) -> tuple[Agent, ...]:
        """
        Return all registered agents.
        """
        return self.manager.agents()