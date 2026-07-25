"""
Capability task.

A CapabilityTask adapts a CapabilityProvider to the Task execution
framework.

This allows planners and workflows to execute abstract capabilities
without knowing anything about their underlying implementation.

Architecture

ExecutionPlan
        │
        ▼
PlanCompiler
        │
        ▼
CapabilityFactory
        │
        ▼
CapabilityTask
        │
        ▼
CapabilityProvider
        │
        ▼
BrowserUse / Playwright / Python / Filesystem / Shell / ...
"""

from __future__ import annotations

from backend.core.capabilities.capability_provider import (
    CapabilityProvider,
)
from backend.core.tasks.context import TaskContext
from backend.core.tasks.task import Task


class CapabilityTask(Task):
    """
    Executable task backed by a capability provider.
    """

    def __init__(
        self,
        *,
        name: str,
        provider: CapabilityProvider,
        capability: str,
        arguments: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            name=name,
        )

        self._provider = provider
        self._capability = capability
        self._arguments = arguments or {}

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> CapabilityProvider:
        """
        Capability provider.
        """

        return self._provider

    @property
    def capability(
        self,
    ) -> str:
        """
        Capability name.
        """

        return self._capability

    @property
    def arguments(
        self,
    ) -> dict[str, object]:
        """
        Capability execution arguments.
        """

        return self._arguments

    # ------------------------------------------------------------------
    # Task Implementation
    # ------------------------------------------------------------------

    async def run(
        self,
        context: TaskContext,
    ) -> object:
        """
        Execute the capability through its provider.
        """

        result = await self.provider.execute(
            self.capability,
            arguments=self.arguments,
        )

        if result.failed:
            raise RuntimeError(
                result.error or "Capability execution failed."
            )

        return result.output

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Task diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "provider": self.provider.name,
                "capability": self.capability,
                "arguments": self.arguments,
            }
        )

        return diagnostics