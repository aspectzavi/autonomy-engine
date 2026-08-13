"""
Failure classifier.

Defines the interface responsible for classifying execution failures.

A failure classifier determines the nature of an exception so that the
retry policy can make an informed decision.

Typical classifications include:

- transient
- permanent
- timeout
- cancellation
- resource exhaustion
- external service failure

Concrete implementations may use deterministic rules, exception
hierarchies, heuristics, or machine learning.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class FailureClassifier(ABC):
    """
    Base interface for failure classification.
    """

    @abstractmethod
    def classify(
        self,
        error: Exception,
    ) -> str:
        """
        Classify an execution failure.

        Returns:
            Stable classification string.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return classifier diagnostics.
        """

        return {
            "classifier": self.__class__.__name__,
        }