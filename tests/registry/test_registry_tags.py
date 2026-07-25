"""
ServiceRegistry tag lookup tests.
"""

from __future__ import annotations

from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.registry import (
    ServiceRegistration,
    ServiceRegistry,
)
from backend.core.kernel.service import KernelService


class DatabaseService(KernelService):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="database",
                version="1.0.0",
            )
        )


class ApiService(KernelService):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="api",
                version="1.0.0",
            )
        )


class CacheService(KernelService):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="cache",
                version="1.0.0",
            )
        )


def test_registry_tags() -> None:
    """
    Services should be discoverable by tag.
    """

    registry = ServiceRegistry()

    database = DatabaseService()
    api = ApiService()
    cache = CacheService()

    registry.register(
        ServiceRegistration(
            metadata=database.metadata,
            service=database,
            tags=frozenset({"database", "storage"}),
        )
    )

    registry.register(
        ServiceRegistration(
            metadata=api.metadata,
            service=api,
            tags=frozenset({"api", "http"}),
        )
    )

    registry.register(
        ServiceRegistration(
            metadata=cache.metadata,
            service=cache,
            tags=frozenset({"database", "cache"}),
        )
    )

    #
    # Database tag.
    #
    database_services = registry.find_by_tag("database")

    assert database_services == (
        database,
        cache,
    )

    #
    # API tag.
    #
    api_services = registry.find_by_tag("api")

    assert api_services == (
        api,
    )

    #
    # Cache tag.
    #
    cache_services = registry.find_by_tag("cache")

    assert cache_services == (
        cache,
    )

    #
    # Unknown tag.
    #
    assert registry.find_by_tag("missing") == ()