"""
Lifecycle state definitions.

This module defines the lifecycle states used by all kernel-managed
services.
"""

from __future__ import annotations

from enum import StrEnum


class LifecycleState(StrEnum):
    """
    Lifecycle states for kernel services.
    """

    INITIALIZED = "initialized"

    STARTING = "starting"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"