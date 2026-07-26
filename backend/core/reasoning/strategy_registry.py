"""
Strategy registry.

Maintains the collection of reasoning strategies available to the
reasoning engine.

Strategies are registered under a unique name and may later be selected
by configuration, heuristics, or policy.
"""

from __future__ import annotations

from backend.core.reasoning.strategy import Strategy


class StrategyRegistry:
    """
    Registry of reasoning strategies.
    """

    def __init__(
        self,
    ) -> None:
        self._strategies: dict[str, Strategy] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        name: str,
        strategy: Strategy,
    ) -> None:
        """
        Register a reasoning strategy.
        """

        self._strategies[name] = strategy

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove a reasoning strategy.
        """

        self._strategies.pop(
            name,
            None,
        )

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def strategy(
        self,
        name: str,
    ) -> Strategy:
        """
        Resolve a reasoning strategy.
        """

        try:
            return self._strategies[name]

        except KeyError as exc:
            raise ValueError(
                f"Unknown reasoning strategy: {name}"
            ) from exc

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a strategy exists.
        """

        return (
            name
            in self._strategies
        )

    @property
    def names(
        self,
    ) -> tuple[str, ...]:
        """
        Registered strategy names.
        """

        return tuple(
            sorted(
                self._strategies.keys(),
            ),
        )

    @property
    def count(
        self,
    ) -> int:
        """
        Number of registered strategies.
        """

        return len(
            self._strategies,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Registry diagnostics.
        """

        return {
            "count": self.count,
            "strategies": self.names,
        }