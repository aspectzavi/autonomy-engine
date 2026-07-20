"""
Lifecycle manager.

This module provides lifecycle state management for kernel-managed
services.
"""

from __future__ import annotations

from backend.core.kernel.lifecycle.state import LifecycleState


class LifecycleManager:
    """
    Manages the lifecycle state of a kernel service.
    """

    def __init__(self) -> None:
        self._state = LifecycleState.INITIALIZED

    @property
    def state(self) -> LifecycleState:
        """
        Return the current lifecycle state.
        """
        return self._state

    @property
    def is_running(self) -> bool:
        """
        Whether the service is running.
        """
        return self._state == LifecycleState.RUNNING

    @property
    def is_stopped(self) -> bool:
        """
        Whether the service is stopped.
        """
        return self._state == LifecycleState.STOPPED

    @property
    def is_failed(self) -> bool:
        """
        Whether the service has failed.
        """
        return self._state == LifecycleState.FAILED

    def transition_to(self, state: LifecycleState) -> None:
        """
        Transition to a new lifecycle state.

        Args:
            state:
                The target lifecycle state.
        """
        self._state = state