"""
Runtime middleware.

Defines the middleware interface used by the runtime execution pipeline.

Middleware provides extensibility around request execution without
modifying the execution engine itself.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.core.runtime.execution_request import (
    ExecutionRequest,
)
from backend.core.runtime.execution_result import (
    ExecutionResult,
)
from backend.core.runtime.middleware_context import (
    MiddlewareContext,
)
from collections.abc import Awaitable
from collections.abc import Callable


NextMiddleware = Callable[
    [ExecutionRequest],
    Awaitable[ExecutionResult],
]

class RuntimeMiddleware(ABC):
    """
    Base class for runtime middleware.
    """

    @property
    def name(
        self,
    ) -> str:
        """
        Middleware name.
        """
        return self.__class__.__name__

    @abstractmethod
    async def invoke(
        self,
        context: MiddlewareContext,
        request: ExecutionRequest,
        call_next: NextMiddleware,
    ) -> ExecutionResult:
        """
        Invoke the middleware with the given context and request.
        """
        raise NotImplementedError

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """
        return {
            "name": self.name,
        }