"""
Middleware registry tests.
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


class FirstMiddleware(RuntimeMiddleware):
    """
    Test middleware.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        return await call_next(request)


class SecondMiddleware(RuntimeMiddleware):
    """
    Test middleware.
    """

    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        return await call_next(request)


def test_middleware_registry() -> None:
    """
    MiddlewareRegistry should correctly register,
    unregister, iterate and report diagnostics.
    """

    registry = MiddlewareRegistry()

    assert len(registry) == 0

    first = FirstMiddleware()
    second = SecondMiddleware()

    #
    # Register middleware.
    #
    registry.register(first)
    registry.register(second)

    assert len(registry) == 2

    assert registry.contains(
        FirstMiddleware,
    )

    assert registry.contains(
        SecondMiddleware,
    )

    assert registry.middleware() == (
        first,
        second,
    )

    assert tuple(registry) == (
        first,
        second,
    )

    diagnostics = registry.diagnostics()

    assert diagnostics["count"] == 2

    assert diagnostics["middleware"] == (
        "FirstMiddleware",
        "SecondMiddleware",
    )

    #
    # Remove middleware.
    #
    assert registry.unregister(
        FirstMiddleware,
    )

    assert len(registry) == 1

    assert not registry.contains(
        FirstMiddleware,
    )

    assert registry.contains(
        SecondMiddleware,
    )

    #
    # Removing again should fail.
    #
    assert not registry.unregister(
        FirstMiddleware,
    )

    #
    # Clear registry.
    #
    registry.clear()

    assert len(registry) == 0

    assert registry.middleware() == ()

    diagnostics = registry.diagnostics()

    assert diagnostics["count"] == 0

    assert diagnostics["middleware"] == ()