from __future__ import annotations

from typing import cast

from backend.app.container.container import Container
from backend.core.kernel.runtime import Runtime
from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.dispatcher import RuntimeDispatcher


class DummyRuntime:
    def diagnostics(self) -> dict[str, object]:
        return {
            "runtime": "ok",
        }


class DummyDispatcher:
    def diagnostics(self) -> dict[str, object]:
        return {
            "dispatcher": "ok",
        }


def test_coordinator_diagnostics() -> None:
    """
    Coordinator diagnostics should expose dispatcher
    and runtime context diagnostics.
    """

    context = RuntimeContext(
        runtime=cast(
            Runtime,
            DummyRuntime(),
        ),
        container=Container(),
        logger=KernelLogger(),
        events=EventBus(),
    )

    coordinator = RuntimeCoordinator(
        dispatcher=cast(
            RuntimeDispatcher,
            DummyDispatcher(),
        ),
        runtime_context=context,
    )

    diagnostics = coordinator.diagnostics()

    dispatcher = cast(
        dict[str, object],
        diagnostics["dispatcher"],
    )

    runtime = cast(
        dict[str, object],
        diagnostics["runtime_context"],
    )

    #
    # Dispatcher diagnostics
    #

    assert dispatcher == {
        "dispatcher": "ok",
    }

    #
    # Runtime diagnostics
    #

    assert runtime["runtime"] == {
        "runtime": "ok",
    }

    assert runtime["logger"] == "KernelLogger"

    #
    # EventBus diagnostics
    #

    events = cast(
        dict[str, object],
        runtime["events"],
    )

    assert isinstance(
        events["events"],
        list,
    )

    assert isinstance(
        events["subscriptions"],
        dict,
    )

    #
    # Container diagnostics
    #

    container = cast(
        dict[str, object],
        runtime["container"],
    )

    assert "service_count" in container
    assert "services" in container