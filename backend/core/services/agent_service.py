"""
Agent service.

Runtime-managed service responsible for the autonomous agent subsystem.
"""

from __future__ import annotations

from backend.core.agents.agent import Agent
from backend.core.agents.context import AgentContext
from backend.core.agents.goal import Goal
from backend.core.agents.manager import AgentManager
from backend.core.agents.registry import AgentRegistry
from backend.core.agents.result import AgentResult
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService
from backend.core.runtime.execution_memory import ExecutionMemory
from backend.core.services.memory_service import MemoryService
from backend.core.tasks.context import TaskContext


class AgentService(KernelService):
    """
    Runtime-managed agent subsystem.
    """

    def __init__(
        self,
        *,
        manager: AgentManager | None = None,
        memory_service: MemoryService | None = None,
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

        #
        # NOTE: `is None`, not `manager or AgentManager()`. AgentManager
        # itself has no __len__, so this particular line was never at
        # risk of the empty-collection footgun -- but the explicit
        # check is kept consistent with every other optional
        # DI-injected dependency in this codebase.
        #
        self._manager = (
            manager
            if manager is not None
            else AgentManager()
        )

        #
        # Optional: if no MemoryService is available (e.g. this
        # service constructed standalone, outside the DI container),
        # execute() still runs goals correctly -- generated
        # experiences just are not persisted anywhere.
        #
        self._memory_service = memory_service

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

    @property
    def memory_service(
        self,
    ) -> MemoryService | None:
        """
        Return the memory service used to persist agent experiences,
        if one is attached.
        """
        return self._memory_service

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        *,
        agent: str,
        goal: Goal,
        task_context: TaskContext,
        context: AgentContext | None = None,
    ) -> AgentResult:
        """
        Execute a goal using the specified agent.

        This is the recommended entry point for running a goal (rather
        than calling `manager.execute()` directly), because it closes
        the loop that Agent.execute() otherwise leaves open:

        - ensures the context has working ExecutionMemory attached, so
          Agent.execute()'s experience recording has somewhere to land
        - after execution, persists every memory generated during the
          run through MemoryService, so future goals can recall past
          experience via memory_service.query()

        Without going through this method, Agent.execute()'s
        `context.memory.remember(...)` calls only ever write to a
        throwaway in-memory list that nothing reads back -- experience
        recording runs but is never actually durable.
        """

        if context is None:
            context = AgentContext(
                event_bus=self.events,
            )

        if context.memory is None:
            context.memory = ExecutionMemory()

        result = await self.manager.execute(
            agent=agent,
            goal=goal,
            task_context=task_context,
            context=context,
        )

        if self._memory_service is not None:
            for entry in context.memory.generated:
                await self._memory_service.store(
                    entry,
                )

        return result

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
                "memory_service_attached": (
                    self._memory_service is not None
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
