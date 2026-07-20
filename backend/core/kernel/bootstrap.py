"""
Kernel bootstrap.

The bootstrap assembles the kernel runtime by wiring together the
service registry, dependency graph, and runtime.

It is intentionally responsible only for construction and registration,
not execution.
"""

from __future__ import annotations

from backend.core.kernel.dependency_graph import DependencyGraph
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.runtime import Runtime
from backend.core.kernel.service import KernelService


class KernelBootstrap:
    """
    Bootstrapper for the kernel runtime.

    Acts as the composition root responsible for constructing and wiring
    together the runtime infrastructure.
    """

    def __init__(self) -> None:
        self._registry = ServiceRegistry()
        self._graph = DependencyGraph(self._registry)
        self._runtime = Runtime(
            registry=self._registry,
            dependency_graph=self._graph,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def registry(self) -> ServiceRegistry:
        """
        Return the service registry.
        """
        return self._registry

    @property
    def dependency_graph(self) -> DependencyGraph:
        """
        Return the dependency graph.
        """
        return self._graph

    @property
    def runtime(self) -> Runtime:
        """
        Return the configured runtime.
        """
        return self._runtime

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        registration: ServiceRegistration,
    ) -> "KernelBootstrap":
        """
        Register a service.

        Returns:
            KernelBootstrap:
                The bootstrap instance for fluent registration.
        """
        self._registry.register(registration)
        return self

    def register_service(
        self,
        service: KernelService,
    ) -> "KernelBootstrap":
        """
        Register a service using its own metadata.

        Returns:
            KernelBootstrap:
                The bootstrap instance.
        """
        registration = ServiceRegistration(
            metadata=service.metadata,
            service=service,
        )

        self._registry.register(registration)

        return self

    def depends_on(
        self,
        service: str,
        *dependencies: str,
    ) -> "KernelBootstrap":
        """
        Register dependencies for a service.

        Returns:
            KernelBootstrap:
                The bootstrap instance.
        """
        self._graph.add(
            service,
            *dependencies,
        )

        return self

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> Runtime:
        """
        Validate and return the configured runtime.
        """
        self._registry.validate()
        self._graph.validate()

        return self._runtime

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return bootstrap diagnostics.
        """
        return {
            "registry": self._registry.diagnostics(),
            "dependency_graph": self._graph.diagnostics(),
            "runtime": self._runtime.diagnostics(),
        }