"""
Reasoning request.

Represents an immutable request submitted to the reasoning subsystem.

A ReasoningRequest is created from a user goal (or another planning
objective) and provides all information required by the reasoning
engine to determine an execution strategy.

The request itself contains no reasoning state.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ReasoningRequest:
    """
    Immutable reasoning request.
    """

    goal: str

    context: dict[str, object] = field(
        default_factory=dict,
    )

    constraints: dict[str, object] = field(
        default_factory=dict,
    )

    metadata: dict[str, object] = field(
        default_factory=dict,
    )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def has_context(
        self,
    ) -> bool:
        """
        Whether contextual information was supplied.
        """

        return bool(
            self.context,
        )

    @property
    def has_constraints(
        self,
    ) -> bool:
        """
        Whether execution constraints were supplied.
        """

        return bool(
            self.constraints,
        )

    @property
    def has_metadata(
        self,
    ) -> bool:
        """
        Whether metadata was supplied.
        """

        return bool(
            self.metadata,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def context_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a context value.
        """

        return self.context.get(
            key,
            default,
        )

    def constraint_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a constraint value.
        """

        return self.constraints.get(
            key,
            default,
        )

    def metadata_value(
        self,
        key: str,
        default: object | None = None,
    ) -> object | None:
        """
        Retrieve a metadata value.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return request diagnostics.
        """

        return {
            "goal": self.goal,
            "goal_length": len(
                self.goal,
            ),
            "context_keys": tuple(
                sorted(
                    self.context.keys(),
                ),
            ),
            "constraint_keys": tuple(
                sorted(
                    self.constraints.keys(),
                ),
            ),
            "metadata_keys": tuple(
                sorted(
                    self.metadata.keys(),
                ),
            ),
        }