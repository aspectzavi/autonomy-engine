"""
Kernel service base class.

This module defines the base class for every runtime-managed service.

The KernelService implements the Template Method Pattern. Public lifecycle
methods are owned by this class and delegate service-specific work to
protected hooks implemented by subclasses.

This guarantees consistent lifecycle management, logging, health
transitions, and runtime state across the framework.
"""

from __future__ import annotations

import asyncio
from abc import ABC
from logging import Logger

from backend.core.kernel.exceptions import LifecycleError
from backend.core.kernel.health import ServiceHealth
from backend.core.kernel.lifecycle import (
    Lifecycle,
    LifecycleManager,
    LifecycleState,
)
from backend.core.kernel.metadata import ServiceMetadata
from backend.core.kernel.runtime_info import ServiceRuntimeInfo
from backend.core.observability.logger import (
    KernelLogger,
)
from backend.core.observability.events import (
    EventBus,
)


class KernelService(Lifecycle, ABC):
    """
    Base class for every managed kernel service.

    Subclasses should override the protected lifecycle hooks
    (on_start, on_stop, on_restart) instead of overriding the public
    lifecycle methods.
    """

    def __init__(
        self,
        metadata: ServiceMetadata,
        event_bus: EventBus | None = None,
    ) -> None:
        self._metadata = metadata

        self._logger: Logger = KernelLogger().get(
            metadata.name,
        )

        self._events = event_bus or EventBus()

        self._health = ServiceHealth()

        self._runtime = ServiceRuntimeInfo()

        self._lifecycle = LifecycleManager()

        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Public Properties
    # ------------------------------------------------------------------

    @property
    def metadata(self) -> ServiceMetadata:
        """
        Immutable service metadata.
        """
        return self._metadata

    @property
    def logger(self) -> Logger:
        """
        Service logger.
        """
        return self._logger

    @property
    def health(self) -> ServiceHealth:
        """
        Current service health.
        """
        return self._health

    @property
    def runtime(self) -> ServiceRuntimeInfo:
        """
        Runtime information.
        """
        return self._runtime

    @property
    def lifecycle(self) -> LifecycleManager:
        """
        Lifecycle manager.
        """
        return self._lifecycle

    @property
    def is_running(self) -> bool:
        """
        Whether the service is currently running.
        """
        return self.lifecycle.is_running
    
    @property
    def events(self) -> EventBus:
        """
        Event bus used by the service.
        """
        return self._events
    
    def attach_event_bus(
        self,
        event_bus: EventBus,
    ) -> None:
        """
        Attach shared event bus.

        Used by the kernel bootstrap layer to inject
        the global runtime event stream.
        """
        self._events = event_bus    

    # ------------------------------------------------------------------
    # Public Lifecycle API
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """
        Start the service.
        """
        async with self._lock:
            await self._start_impl()

    async def stop(self) -> None:
        """
        Stop the service.
        """
        async with self._lock:
            await self._stop_impl()

    async def restart(self) -> None:
        """
        Restart the service.
        """
        async with self._lock:
            self.logger.info(
                "Restarting service '%s'.",
                self.metadata.name,
            )

            await self._stop_impl()

            self._health = self.health.restarted()

            await self.on_restart()

            await self._start_impl()

    # ------------------------------------------------------------------
    # Internal Lifecycle Implementation
    # ------------------------------------------------------------------

    async def _start_impl(self) -> None:
        """
        Internal start implementation.

        Assumes the lifecycle lock is already held.
        """
        if self.is_running:
            return

        self.logger.info(
            "Starting service '%s'.",
            self.metadata.name,
        )

        self.lifecycle.transition_to(LifecycleState.STARTING)

        self._runtime = self.runtime.with_state("starting")

        try:
            await self.on_start()

            self.lifecycle.transition_to(LifecycleState.RUNNING)

            self._runtime = self.runtime.with_state("running")

            self._health = self.health.recovered()

            self.logger.info(
                "Service '%s' started.",
                self.metadata.name,
            )

            self.events.publish(
                "service.started",
                {
                    "service": self.metadata.name,
                },
            )

        except Exception as exc:
            self.lifecycle.transition_to(LifecycleState.FAILED)

            self._health = self.health.with_error(str(exc))

            self.logger.exception(
                "Failed starting service '%s'.",
                self.metadata.name,
            )

            raise LifecycleError(
                f"Failed to start service '{self.metadata.name}'."
            ) from exc

    async def _stop_impl(self) -> None:
        """
        Internal stop implementation.

        Assumes the lifecycle lock is already held.
        """
        if self.lifecycle.is_stopped:
            return

        self.logger.info(
            "Stopping service '%s'.",
            self.metadata.name,
        )

        self.lifecycle.transition_to(LifecycleState.STOPPING)

        self._runtime = self.runtime.with_state("stopping")

        try:
            await self.on_stop()

            self.lifecycle.transition_to(LifecycleState.STOPPED)

            self._runtime = self.runtime.with_state("stopped")

            self.logger.info(
                "Service '%s' stopped.",
                self.metadata.name,
            )

            self.events.publish(
                "service.stopped",
                {
                    "service": self.metadata.name,
                },
            )

        except Exception as exc:
            self.lifecycle.transition_to(LifecycleState.FAILED)

            self._health = self.health.with_error(str(exc))

            self.logger.exception(
                "Failed stopping service '%s'.",
                self.metadata.name,
            )

            raise LifecycleError(
                f"Failed to stop service '{self.metadata.name}'."
            ) from exc

    # ------------------------------------------------------------------
    # Extension Hooks
    # ------------------------------------------------------------------

    async def on_start(self) -> None:
        """
        Service startup hook.

        Override in subclasses.
        """

    async def on_stop(self) -> None:
        """
        Service shutdown hook.

        Override in subclasses.
        """

    async def on_restart(self) -> None:
        """
        Optional restart hook.

        Override only when necessary.
        """

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(self) -> dict[str, object]:
        """
        Return a runtime diagnostics snapshot.
        """
        return {
            "metadata": self.metadata.model_dump(),
            "health": self.health.model_dump(),
            "runtime": self.runtime.model_dump(),
            "lifecycle": self.lifecycle.state.value,
        }