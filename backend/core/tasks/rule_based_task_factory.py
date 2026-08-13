"""
Rule-based task factory.

Default deterministic implementation of the TaskFactory interface.

The factory maps planning capabilities to executable Task
implementations.

Initially only a placeholder task is produced.

Future versions will resolve real tasks such as:

- browser.open
- browser.click
- desktop.click
- memory.search
- reasoning.analyze
- goal.execute
- goal.verify
- user.ask
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


class RuleBasedTaskFactory(
    TaskFactory,
):
    """
    Default deterministic task factory.
    """

    def create(
        self,
        *,
        capability: str,
        name: str | None = None,
    ) -> Task:
        """
        Create a task for a capability.

        Until concrete task implementations exist, every capability
        resolves to a PlaceholderTask.
        """

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
                "placeholder_resolution": True,
            },
        )

        return diagnostics