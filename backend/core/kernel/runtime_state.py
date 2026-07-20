"""
Kernel runtime states.
"""

from __future__ import annotations

from enum import StrEnum


class RuntimeState(StrEnum):
    """
    Runtime lifecycle state.
    """

    CREATED = "created"

    STARTING = "starting"

    RUNNING = "running"

    STOPPING = "stopping"

    STOPPED = "stopped"

    FAILED = "failed"