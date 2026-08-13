from __future__ import annotations

from typing import cast

from backend.app.container.container import Container
from backend.core.kernel.runtime import Runtime
from backend.core.kernel.runtime_context import RuntimeContext
from backend.core.memory.memory_store import MemoryStore
from backend.core.observability.events import EventBus
from backend.core.observability.logger import KernelLogger
from backend.core.runtime.coordinator import RuntimeCoordinator
from backend.core.runtime.dispatcher import RuntimeDispatcher
from backend.core.services.memory_service import MemoryService


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


class DummyLogger:
    pass


class DummyEvents:
    def diagnostics(self) -> dict[str, object]:
        return {
            "events": "ok",
        }


def test_runtime_coordinator_diagnostics() -> None:
    context = RuntimeContext(
        runtime=cast(Runtime, DummyRuntime()),
        container=Container(),
        logger=cast(KernelLogger, DummyLogger()),
        events=cast(EventBus, DummyEvents()),
    )

    memory_service = MemoryService(
        provider=MemoryStore(),
    )

    coordinator = RuntimeCoordinator(
        dispatcher=cast(RuntimeDispatcher, DummyDispatcher()),
        runtime_context=context,
        memory_service=memory_service,
    )

    diagnostics = coordinator.diagnostics()

    assert diagnostics["dispatcher"] == {
        "dispatcher": "ok",
    }

    runtime = cast(
        dict[str, object],
        diagnostics["runtime_context"],
    )

    assert runtime["runtime"] == {
        "runtime": "ok",
    }

    assert runtime["logger"] == "DummyLogger"

    assert runtime["events"] == {
        "events": "ok",
    }

    assert "container" in runtime
    assert "memory_service" in diagnostics