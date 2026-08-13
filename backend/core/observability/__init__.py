"""
Kernel observability subsystem.

Provides logging, metrics, and runtime telemetry.
"""

from backend.core.observability.logger import (
    KernelLogger,
)
from backend.core.observability.events import (
    EventBus,
)
from backend.core.observability.container import (
    ObservabilityContainer,
)

__all__ = [
    "KernelLogger",
    "EventBus",
    "ObservabilityContainer",
]