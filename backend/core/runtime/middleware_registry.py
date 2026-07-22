"""
Runtime middleware registry.

Maintains the collection of middleware participating in the runtime
execution pipeline.

The registry is responsible only for registration and discovery. It
does not execute middleware.
"""

from __future__ import annotations

from collections.abc import Iterator

from backend.core.runtime.middleware import RuntimeMiddleware
from backend.core.observability.tracing import Tracing


class MiddlewareRegistry:
    """
    Registry of runtime middleware.
    """

    def __init__(
        self,
        middleware: tuple[RuntimeMiddleware, ...] = (),
        *,
        tracing: Tracing | None = None,
    ) -> None:
        self._middleware = list(
            middleware,
        )

        if tracing is not None:
            from backend.core.runtime.default_middleware import (
                register_default_middleware,
            )

            register_default_middleware(
                self,
                tracing=tracing,
            )

   
    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        middleware: RuntimeMiddleware,
    ) -> None:
        """
        Register middleware.
        """
        self._middleware.append(
            middleware,
        )

    def unregister(
        self,
        middleware_type: type[RuntimeMiddleware],
    ) -> bool:
        """
        Remove middleware by type.

        Returns True if middleware was removed.
        """

        for middleware in tuple(
            self._middleware,
        ):
            if isinstance(
                middleware,
                middleware_type,
            ):
                self._middleware.remove(
                    middleware,
                )
                return True

        return False

    def clear(
        self,
    ) -> None:
        """
        Remove all registered middleware.
        """
        self._middleware.clear()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def middleware(
        self,
    ) -> tuple[RuntimeMiddleware, ...]:
        """
        Return registered middleware.
        """
        return tuple(
            self._middleware,
        )

    def contains(
        self,
        middleware_type: type[RuntimeMiddleware],
    ) -> bool:
        """
        Return whether middleware of the given type is registered.
        """
        return any(
            isinstance(
                middleware,
                middleware_type,
            )
            for middleware in self._middleware
        )

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered middleware.
        """
        return len(
            self._middleware,
        )

    def __iter__(
        self,
    ) -> Iterator[RuntimeMiddleware]:
        """
        Iterate over registered middleware.
        """
        return iter(
            self._middleware,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return registry diagnostics.
        """
        return {
            "count": len(
                self,
            ),
            "middleware": tuple(
                type(
                    middleware,
                ).__name__
                for middleware in self._middleware
            ),
        }