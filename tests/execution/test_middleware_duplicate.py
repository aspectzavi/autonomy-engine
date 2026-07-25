"""
Middleware duplicate registration tests.
"""

from __future__ import annotations

from backend.core.runtime.execution_request import ExecutionRequest
from backend.core.runtime.execution_result import ExecutionResult
from backend.core.runtime.middleware import (
    NextMiddleware,
    RuntimeMiddleware,
)
from backend.core.runtime.middleware_context import MiddlewareContext
from backend.core.runtime.middleware_registry import (
    MiddlewareRegistry,
)


class TestMiddleware(RuntimeMiddleware):
    """
    Simple middleware used for duplicate registration testing.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        return await call_next(request)


def test_middleware_duplicate() -> None:
    """
    MiddlewareRegistry currently allows multiple instances
    of the same middleware type.
    """

    registry = MiddlewareRegistry()

    first = TestMiddleware()
    second = TestMiddleware()

    registry.register(first)
    registry.register(second)

    assert len(registry) == 2

    middleware = registry.middleware()

    assert middleware == (
        first,
        second,
    )

    #
    # contains() checks by type.
    #
    assert registry.contains(
        TestMiddleware,
    )

    diagnostics = registry.diagnostics()

    assert diagnostics["count"] == 2

    #
    # Diagnostics report both registrations.
    #
    assert diagnostics["middleware"] == (
        "TestMiddleware",
        "TestMiddleware",
    )

    #
    # unregister() removes only the first matching instance.
    #
    assert registry.unregister(
        TestMiddleware,
    )

    assert len(registry) == 1

    assert registry.contains(
        TestMiddleware,
    )

    assert registry.middleware() == (
        second,
    )

    #
    # Remove the remaining instance.
    #
    assert registry.unregister(
        TestMiddleware,
    )

    assert len(registry) == 0

    assert not registry.contains(
        TestMiddleware,
    )