"""
Container instance registration tests.
"""

from __future__ import annotations

from backend.app.container.container import Container


class Configuration:
    """
    Example configuration object.
    """

    def __init__(
        self,
        value: str,
    ) -> None:
        self.value = value


def test_container_instance() -> None:
    """
    Registering an existing instance should always
    resolve that exact object.
    """

    container = Container()

    config = Configuration(
        "production",
    )

    container.register_instance(
        Configuration,
        config,
    )

    #
    # Container inspection.
    #
    assert container.contains(
        Configuration,
    )

    registration = container.registration(
        Configuration,
    )

    assert registration is not None
    assert registration.has_instance

    #
    # Resolve multiple times.
    #
    first = container.resolve(
        Configuration,
    )

    second = container.resolve(
        Configuration,
    )

    #
    # Exact same object.
    #
    assert first is config
    assert second is config
    assert first is second

    #
    # Values preserved.
    #
    assert first.value == "production"