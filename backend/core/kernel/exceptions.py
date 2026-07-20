"""
Kernel exception hierarchy.

This module defines the exception hierarchy used by the framework kernel.

All kernel-related exceptions derive from ``KernelError`` so callers may
either catch specific exceptions or handle all kernel failures through
the common base class.
"""

from __future__ import annotations


class KernelError(Exception):
    """
    Base exception for all kernel-related errors.
    """


# ============================================================================
# Configuration
# ============================================================================


class ConfigurationError(KernelError):
    """
    Raised when kernel configuration is invalid.
    """


# ============================================================================
# Services
# ============================================================================


class ServiceError(KernelError):
    """
    Base exception for service-related failures.
    """


class ServiceAlreadyRegisteredError(ServiceError):
    """
    Raised when attempting to register a service that already exists.
    """


class ServiceNotFoundError(ServiceError):
    """
    Raised when a requested service cannot be found.
    """


class ServiceDisabledError(ServiceError):
    """
    Raised when attempting to use a disabled service.
    """


class ServiceInitializationError(ServiceError):
    """
    Raised when a service fails during initialization.
    """


# ============================================================================
# Dependencies
# ============================================================================


class DependencyError(KernelError):
    """
    Base exception for dependency-related failures.
    """


class DependencyResolutionError(DependencyError):
    """
    Raised when dependencies cannot be resolved.
    """


class CircularDependencyError(DependencyError):
    """
    Raised when a circular dependency is detected.
    """


class MissingDependencyError(DependencyError):
    """
    Raised when a required dependency is missing.
    """


# ============================================================================
# Lifecycle
# ============================================================================


class LifecycleError(KernelError):
    """
    Base exception for lifecycle failures.
    """


class StartupError(LifecycleError):
    """
    Raised when a service fails during startup.
    """


class ShutdownError(LifecycleError):
    """
    Raised when a service fails during shutdown.
    """


class RestartError(LifecycleError):
    """
    Raised when a service restart fails.
    """


class InvalidLifecycleTransitionError(LifecycleError):
    """
    Raised when an invalid lifecycle transition is attempted.
    """


# ============================================================================
# Registry
# ============================================================================


class RegistryError(KernelError):
    """
    Raised when the service registry encounters an error.
    """


# ============================================================================
# Runtime
# ============================================================================


class RuntimeError(KernelError):
    """
    Raised when the kernel runtime encounters an unrecoverable error.
    """


class BootstrapError(RuntimeError):
    """
    Raised when the kernel bootstrap process fails.
    """


class HealthCheckError(RuntimeError):
    """
    Raised when a service health check fails.
    """