"""
Capability factory.

The factory converts capability requests into executable Task
instances.

The planner produces capability names.

The registry resolves the appropriate provider.

The factory creates CapabilityTask instances that delegate execution
to capability providers.
"""

from __future__ import annotations

from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)
from backend.core.capabilities.capability_task import (
    CapabilityTask,
)
from backend.core.tasks.task import Task


class CapabilityFactory:
    """
    Factory responsible for creating executable tasks from capabilities.
    """

    def __init__(
        self,
        *,
        registry: CapabilityRegistry,
    ) -> None:
        self._registry = registry

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(
        self,
    ) -> CapabilityRegistry:
        """
        Capability registry.
        """

        return self._registry

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        capability: str,
        task_name: str,
        arguments: dict[str, object] | None = None,
    ) -> Task:
        """
        Create an executable task for a capability.
        """

        provider = self.registry.provider_for(
            capability,
        )

        return CapabilityTask(
            name=task_name,
            provider=provider,
            capability=capability,
            arguments=arguments,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Factory diagnostics.
        """

        return {
            "registry": self.registry.diagnostics(),
        }