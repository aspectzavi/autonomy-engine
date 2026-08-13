"""
Dependency injection service lifetimes.

Defines how long resolved service instances live.
"""

from __future__ import annotations

from enum import StrEnum


class ServiceLifetime(StrEnum):
    """
    Lifetime of a registered service.

    SINGLETON:
        One instance for the entire container lifetime.

    TRANSIENT:
        New instance every resolution.

    SCOPED:
        One instance per scope.
    """

    SINGLETON = "singleton"

    TRANSIENT = "transient"

    SCOPED = "scoped"