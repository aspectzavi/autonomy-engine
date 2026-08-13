"""
Container diagnostics tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from backend.app.container.container import Container
from backend.app.container.lifetime import ServiceLifetime


class SingletonService:
    """
    Dummy singleton service.
    """


class TransientService:
    """
    Dummy transient service.
    """


def test_container_diagnostics() -> None:
    """
    diagnostics() should accurately describe the
    registered services.
    """

    container = Container()

    container.register_singleton(
        SingletonService,
    )

    container.register_transient(
        TransientService,
    )

    diagnostics = container.diagnostics()

    assert diagnostics["service_count"] == 2

    services = cast(
        list[Mapping[str, Any]],
        diagnostics["services"],
    )

    assert len(services) == 2

    services_by_name = {
        cast(str, service["service"]): service
        for service in services
    }

    singleton = services_by_name[
        "SingletonService"
    ]

    assert singleton["provider"] == "ClassProvider"

    assert (
        singleton["lifetime"]
        == ServiceLifetime.SINGLETON.value
    )

    transient = services_by_name[
        "TransientService"
    ]

    assert transient["provider"] == "ClassProvider"

    assert (
        transient["lifetime"]
        == ServiceLifetime.TRANSIENT.value
    )