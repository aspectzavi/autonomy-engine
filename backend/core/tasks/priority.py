"""
Task execution priorities.

Defines scheduling priorities for executable tasks.
"""

from __future__ import annotations

from enum import IntEnum


class TaskPriority(IntEnum):
    """
    Scheduling priority for tasks.

    Higher values indicate higher priority.
    """

    LOWEST = 0

    LOW = 25

    NORMAL = 50

    HIGH = 75

    CRITICAL = 100

    @property
    def is_high_priority(self) -> bool:
        """
        Whether this priority is considered high.
        """
        return self >= TaskPriority.HIGH

    @property
    def is_low_priority(self) -> bool:
        """
        Whether this priority is considered low.
        """
        return self <= TaskPriority.LOW