"""
Runtime coordinator.

Coordinates autonomous runtime execution.

The coordinator is the primary entry point for executing user requests.
It orchestrates agent selection and execution without implementing
planning or workflow execution itself.
"""

from __future__ import annotations

from backend.core.agents.context import AgentContext
from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.runtime.dispatcher import RuntimeDispatcher
from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.execution_session import (
    ExecutionSession,
)
from backend.core.runtime.execution_state import (
    ExecutionState,
)
from backend.core.memory.memory_query import MemoryQuery
from backend.core.services.memory_service import MemoryService
from backend.core.runtime.execution_memory import (
    ExecutionMemory,
)


class RuntimeCoordinator:
    """
    Coordinates autonomous runtime execution.
    """

    def __init__(
        self,
        *,
        dispatcher: RuntimeDispatcher,
        runtime_context: RuntimeContext,
        memory_service: MemoryService,
    ) -> None:
        self._dispatcher = dispatcher
        self._runtime_context = runtime_context
        self._memory_service = memory_service

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dispatcher(
        self,
    ) -> RuntimeDispatcher:
        """
        Runtime dispatcher.
        """
        return self._dispatcher

    @property
    def runtime_context(
        self,
    ) -> RuntimeContext:
        """
        Shared runtime execution context.
        """
        return self._runtime_context

    @property
    def memory_service(
        self,
    ) -> MemoryService:
        """
        Runtime memory service.
        """
        return self._memory_service

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """
        Execute an autonomous runtime request.
        """

        session = ExecutionSession(
            request=request,
        )

        execution_memory = ExecutionMemory()

        session.record(
            "Execution created.",
        )

        try:
            session.transition(
                ExecutionState.EXECUTING,
            )

            #
            # Select the appropriate agent.
            #
            agent = self.dispatcher.dispatch(
                request,
            )

            session.record(
                f"Selected agent '{agent.name}'.",
            )

            #
            # Create task execution context.
            #
            task_context = (
                self.runtime_context.task_context()
            )

            #
            # Retrieve relevant long-term memories.
            #
            memory_result = await self.memory_service.recall(
                MemoryQuery(
                    text=request.goal.description,
                    limit=10,
                ),
            )

            execution_memory.attach(
                memory_result,
            )

            session.record(
                (
                    f"Retrieved "
                    f"{len(memory_result.entries)} "
                    "relevant memories."
                ),
            )

            #
            # Shared execution context.
            #
            agent_context = AgentContext(
                event_bus=self.runtime_context.events,
                runtime=self.runtime_context,
                session=session,
                memory=execution_memory,
            )

            #
            # Execute the selected agent.
            #
            agent_result = await agent.execute(
                goal=request.goal,
                task_context=task_context,
                context=agent_context,
            )

            #
            # Update execution state.
            #
            if agent_result.success:
                session.transition(
                    ExecutionState.COMPLETED,
                )

                session.record(
                    "Execution completed.",
                )

            else:
                session.transition(
                    ExecutionState.FAILED,
                )

                session.record(
                    "Execution failed.",
                )

            #
            # Persist any memories generated during execution.
            #
            for entry in execution_memory.generated:
                await self.memory_service.store(
                    entry,
                )

            if execution_memory.generated:
                session.record(
                    (
                        f"Stored "
                        f"{len(execution_memory.generated)} "
                        "new memories."
                    ),
                )

            return ExecutionResult(
                success=agent_result.success,
                workflow_result=agent_result.workflow_result,
                started_at=session.started_at,
                finished_at=(
                    session.completed_at
                    or session.updated_at
                ),
                errors=(
                    (agent_result.error,)
                    if agent_result.error
                    else ()
                ),
                metadata={
                    "request_id": request.request_id,
                    "agent": agent.name,
                    "events": tuple(
                        session.events,
                    ),
                },
            )

        except Exception as exc:
            session.transition(
                ExecutionState.FAILED,
            )

            session.record(
                str(exc),
            )

            return ExecutionResult(
                success=False,
                started_at=session.started_at,
                finished_at=(
                    session.completed_at
                    or session.updated_at
                ),
                errors=(
                    str(exc),
                ),
                metadata={
                    "request_id": request.request_id,
                    "events": tuple(
                        session.events,
                    ),
                },
            )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return coordinator diagnostics.
        """

        return {
            "dispatcher": (
                self.dispatcher.diagnostics()
            ),
            "runtime_context": (
                self.runtime_context.diagnostics()
            ),
            "memory_service": (
                self.memory_service.diagnostics()
            ),
        }