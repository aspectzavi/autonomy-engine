"""
Kernel dependency graph.

The dependency graph models relationships between runtime services.

Responsibilities:

- Store service dependencies.
- Validate graph integrity.
- Detect missing dependencies.
- Detect circular dependencies.
- Produce deterministic startup order.
- Produce shutdown order.

The graph is intentionally independent of the runtime.
"""

from __future__ import annotations

from collections import defaultdict, deque

from backend.core.kernel.exceptions import RegistryError
from backend.core.kernel.registry import ServiceRegistry


class DependencyGraph:
    """
    Directed acyclic graph of service dependencies.
    """

    def __init__(
        self,
        registry: ServiceRegistry,
    ) -> None:
        self._registry = registry

        # service -> dependencies
        self._dependencies: dict[str, set[str]] = defaultdict(set)

        # dependency -> dependents
        self._reverse: dict[str, set[str]] = defaultdict(set)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def add(
        self,
        service: str,
        *dependencies: str,
    ) -> None:
        """
        Register dependencies for a service.
        """
        if service not in self._registry:
            raise RegistryError(
                f"Unknown service '{service}'."
            )

        for dependency in dependencies:
            if dependency not in self._registry:
                raise RegistryError(
                    f"Unknown dependency '{dependency}'."
                )

            self._dependencies[service].add(dependency)
            self._reverse[dependency].add(service)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def dependencies(
        self,
        service: str,
    ) -> tuple[str, ...]:
        """
        Return direct dependencies.
        """
        return tuple(sorted(self._dependencies.get(service, set())))

    def dependents(
        self,
        service: str,
    ) -> tuple[str, ...]:
        """
        Return direct dependents.
        """
        return tuple(sorted(self._reverse.get(service, set())))

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate the dependency graph.

        Raises:
            RegistryError:
                If a circular dependency exists.
        """
        self.startup_order()

    # ------------------------------------------------------------------
    # Ordering
    # ------------------------------------------------------------------

    def startup_order(self) -> tuple[str, ...]:
        """
        Compute startup order using Kahn's algorithm.
        """
        indegree: dict[str, int] = {
            name: len(self._dependencies.get(name, set()))
            for name in self._registry.names()
        }

        queue: deque[str] = deque(
            sorted(
                name
                for name, degree in indegree.items()
                if degree == 0
            )
        )

        order: list[str] = []

        while queue:
            current = queue.popleft()

            order.append(current)

            for dependent in sorted(
                self._reverse.get(current, set())
            ):
                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(indegree):
            raise RegistryError(
                "Circular dependency detected."
            )

        return tuple(order)

    def shutdown_order(self) -> tuple[str, ...]:
        """
        Compute shutdown order.

        Shutdown order is the reverse of startup order.
        """
        return tuple(reversed(self.startup_order()))

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return graph diagnostics.
        """
        return {
            "services": len(self._registry),
            "edges": sum(
                len(dependencies)
                for dependencies in self._dependencies.values()
            ),
            "startup_order": self.startup_order(),
            "shutdown_order": self.shutdown_order(),
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Remove all dependency edges.
        """
        self._dependencies.clear()
        self._reverse.clear()

    def __len__(self) -> int:
        """
        Number of dependency edges.
        """
        return sum(
            len(dependencies)
            for dependencies in self._dependencies.values()
        )

    def __contains__(
        self,
        service: object,
    ) -> bool:
        """
        Membership test.
        """
        if not isinstance(service, str):
            return False

        return service in self._dependencies