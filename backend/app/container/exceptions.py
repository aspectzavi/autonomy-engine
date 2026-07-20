"""
Dependency injection container exceptions.
"""

from __future__ import annotations


class ContainerError(Exception):
    """
    Base container exception.
    """


class ServiceAlreadyRegisteredError(ContainerError):
    """
    Raised when attempting to register an existing service.
    """


class ServiceNotRegisteredError(ContainerError):
    """
    Raised when resolving an unknown service.
    """


class CircularDependencyError(ContainerError):
    """
    Raised when dependency resolution detects a cycle.
    """