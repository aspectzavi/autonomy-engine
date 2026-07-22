"""
Default runtime middleware.

Registers the built-in middleware that ships with the autonomy engine.

This module is the composition point for the runtime middleware stack.
The registry itself is responsible only for storing middleware, while
this module defines which middleware are enabled by default.
"""

from __future__ import annotations


from backend.core.observability.tracing import Tracing

from backend.core.runtime.middleware_registry import (
    MiddlewareRegistry,
)

from backend.core.runtime.builtins.validation_middleware import (
    ValidationMiddleware,
)

from backend.core.runtime.builtins.logging_middleware import (
    LoggingMiddleware,
)

from backend.core.runtime.builtins.metrics_middleware import (
    MetricsMiddleware,
)

from backend.core.runtime.builtins.event_middleware import (
    EventMiddleware,
)

from backend.core.runtime.builtins.tracing_middleware import (
    TracingMiddleware,
)


def register_default_middleware(
    registry: MiddlewareRegistry,
    *,
    tracing: Tracing,
) -> None:
    """
    Register the built-in runtime middleware.

    Middleware execute in the order they are registered.
    """

    #
    # Validate execution requests first.
    #
    registry.register(
        ValidationMiddleware(),
    )

    #
    # Create execution trace.
    #
    registry.register(
        TracingMiddleware(
            tracing,
        ),
    )

    #
    # Runtime logging.
    #
    registry.register(
        LoggingMiddleware(),
    )

    #
    # Runtime metrics.
    #
    registry.register(
        MetricsMiddleware(),
    )

    #
    # Runtime event publishing.
    #
    registry.register(
        EventMiddleware(),
    )
    