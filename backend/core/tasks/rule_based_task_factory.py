"""
Rule-based task factory.

Default deterministic implementation of the TaskFactory interface.

The factory maps planning capabilities to executable Task
implementations. When a ToolManager is supplied and a capability
matches a registered tool's name, the capability resolves to a real
ToolTask that actually calls that tool. Otherwise it falls back to a
PlaceholderTask, exactly as before -- this is a strict superset of
the prior behavior, never a regression, and mirrors the same
swap-to-the-real-thing-when-available pattern used for
CapabilityRegistry (ToolCapabilityProvider) in the Agents subsystem.

Tool availability is checked live via `tool_manager.contains()` at
create() time, not snapshotted at construction time, since tools
aren't registered into the manager until ToolService.on_start() runs
-- which may happen after this factory is constructed.
"""

from __future__ import annotations

from backend.core.tasks.placeholder_task import (
    PlaceholderTask,
)
from backend.core.tasks.task import (
    Task,
)
from backend.core.tasks.task_factory import (
    TaskFactory,
)
from backend.core.tasks.tool_task import (
    ToolTask,
)
from backend.core.tools.manager import ToolManager


class RuleBasedTaskFactory(
    TaskFactory,
):
    """
    Default deterministic task factory.
    """

    def __init__(
        self,
        *,
        tool_manager: ToolManager | None = None,
    ) -> None:
        self._tool_manager = tool_manager

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def tool_manager(
        self,
    ) -> ToolManager | None:
        """
        The tool manager real capabilities are resolved against, if
        one was supplied.
        """

        return self._tool_manager

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        capability: str,
        name: str | None = None,
    ) -> Task:
        """
        Create a task for a capability.

        Resolves to a real ToolTask when the capability matches a
        registered tool; falls back to a PlaceholderTask otherwise.
        """

        if (
            self._tool_manager is not None
            and self._tool_manager.contains(capability)
        ):
            return ToolTask(
                name=name or capability,
                tool=capability,
                tool_manager=self._tool_manager,
            )

        return PlaceholderTask(
            capability=capability,
            name=name or capability,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "type": "rule-based",
                "tool_manager_attached": (
                    self._tool_manager is not None
                ),
            },
        )

        return diagnostics