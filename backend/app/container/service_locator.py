"""
Application service locator.

Provides typed access to runtime-managed services registered in the
dependency injection container.

The service locator is a lightweight convenience wrapper around the
dependency injection container. It does not own service lifecycles or
construction.
"""

from __future__ import annotations

from backend.app.container.container import Container
from backend.core.config.config import EngineConfig
from backend.core.services.tool_service import ToolService


class ServiceLocator:
    """
    Typed access to runtime-managed services.
    """

    def __init__(
        self,
        container: Container,
    ) -> None:
        self._container = container

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def container(
        self,
    ) -> Container:
        """
        Return the underlying dependency injection container.
        """
        return self._container

    @property
    def config(
        self,
    ) -> EngineConfig:
        """
        Return the engine configuration.
        """
        return self.container.resolve(
            EngineConfig,
        )

    @property
    def tools(
        self,
    ) -> ToolService:
        """
        Return the runtime tool service.
        """
        return self.container.resolve(
            ToolService,
        )

    # ------------------------------------------------------------------
    # Generic Resolution
    # ------------------------------------------------------------------

    def resolve(
        self,
        service_type: type,
    ) -> object:
        """
        Resolve a service from the container.
        """
        return self.container.resolve(
            service_type,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return service locator diagnostics.
        """
        return {
            "container": self.container.diagnostics(),
            "services": {
                "config": type(
                    self.config,
                ).__name__,
                "tools": type(
                    self.tools,
                ).__name__,
            },
        }