"""
Planning dependency registration.
"""

from __future__ import annotations

from backend.app.container.container import Container

from backend.core.capabilities.capability_factory import (
    CapabilityFactory,
)
from backend.core.capabilities.capability_registry import (
    CapabilityRegistry,
)

from backend.core.planning.plan_compiler import (
    PlanCompiler,
)
from backend.core.planning.plan_validator import (
    PlanValidator,
)


def register_planning(
    container: Container,
) -> None:
    """
    Register planning infrastructure.
    """

    if not container.contains(
        CapabilityRegistry,
    ):
        container.register_singleton(
            CapabilityRegistry,
        )

    if not container.contains(
        CapabilityFactory,
    ):
        container.register_singleton(
            CapabilityFactory,
        )

    if not container.contains(
        PlanValidator,
    ):
        container.register_singleton(
            PlanValidator,
        )

    if not container.contains(
        PlanCompiler,
    ):
        container.register_singleton(
            PlanCompiler,
        )