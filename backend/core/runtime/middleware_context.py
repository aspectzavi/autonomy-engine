"""
Runtime middleware context.

Carries state shared across the runtime middleware pipeline during a
single execution request.

The context provides access to runtime-level dependencies while keeping
middleware execution state isolated per request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from backend.core.kernel.runtime_context import RuntimeContext


@dataclass(slots=True)
class MiddlewareContext:
    """
    Shared middleware execution context.
    """

    runtime: RuntimeContext | None = None

    correlation_id: str = field(
        default_factory=lambda: str(
            uuid4(),
        ),
    )

    started_at: datetime = field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    items: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def set(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store a value.
        """
        self.items[key] = value

    def get(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a stored value.
        """
        return self.items.get(
            key,
            default,
        )

    def contains(
        self,
        key: str,
    ) -> bool:
        """
        Return whether a value exists.
        """
        return key in self.items

    # ------------------------------------------------------------------
    # Runtime Access
    # ------------------------------------------------------------------

    @property
    def has_runtime(
        self,
    ) -> bool:
        """
        Whether runtime context is attached.
        """
        return self.runtime is not None

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return middleware diagnostics.
        """
        return {
            "correlation_id": (
                self.correlation_id
            ),
            "started_at": (
                self.started_at.isoformat()
            ),
            "runtime_attached": (
                self.has_runtime
            ),
            "item_count": len(
                self.items,
            ),
            "keys": tuple(
                sorted(
                    self.items.keys(),
                ),
            ),
        }