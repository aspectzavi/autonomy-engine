"""
Tests for runtime dependency cycle detection.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.exceptions import RegistryError
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.service import KernelService


class DummyService(KernelService):
    """
    Minimal kernel service used for dependency graph testing.
    """

    def __init__(
        self,
        name: str,
    ) -> None:
        super().__init__(
            ServiceMetadata(
                name=name,
                version="1.0.0",
            )
        )

    async def on_start(self) -> None:
        pass

    async def on_stop(self) -> None:
        pass


def test_runtime_dependency_cycle() -> None:
    """
    Building the runtime should fail when a circular
    dependency exists.
    """

    bootstrap = KernelBootstrap()

    #
    # Register three services.
    #
    bootstrap.register_service(
        DummyService("service-a"),
    )

    bootstrap.register_service(
        DummyService("service-b"),
    )

    bootstrap.register_service(
        DummyService("service-c"),
    )

    #
    # Create a dependency cycle:
    #
    # service-a -> service-b
    # service-b -> service-c
    # service-c -> service-a
    #
    bootstrap.depends_on(
        "service-a",
        "service-b",
    )

    bootstrap.depends_on(
        "service-b",
        "service-c",
    )

    bootstrap.depends_on(
        "service-c",
        "service-a",
    )

    with pytest.raises(
        RegistryError,
        match="Circular dependency detected",
    ):
        bootstrap.build()