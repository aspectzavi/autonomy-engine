"""
Task factory.

Defines the interface responsible for creating executable Task
instances from planning capabilities.

The planner and workflow compiler should depend only on this interface.

Concrete implementations may resolve tasks using:

- deterministic mappings
- dependency injection
- plugin registries
- capability discovery
- service containers
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.tasks.task import Task


class TaskFactory(ABC):
    """
    Base interface for task factories.
    """

    @abstractmethod
    def create(
        self,
        *,
        capability: str,
        name: str | None = None,
    ) -> Task:
        """
        Create a task for the supplied capability.

        Args:
            capability:
                Capability identifier.

            name:
                Optional task name override.

        Returns:
            Executable Task.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return factory diagnostics.
        """

        return {
            "factory": self.__class__.__name__,
        }