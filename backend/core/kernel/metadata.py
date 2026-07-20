"""
Kernel service metadata.

This module defines immutable metadata describing every managed service
within the framework.

Service metadata is used by the Kernel to:

- identify services
- resolve startup order
- validate dependencies
- generate diagnostics
- expose runtime information
- support plugin discovery

The metadata model is intentionally framework-agnostic and contains no
runtime behavior.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ServiceMetadata(BaseModel):
    """
    Immutable metadata describing a kernel-managed service.

    Every service registered with the Kernel should expose exactly one
    instance of this model.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=False,
    )

    name: str = Field(
        ...,
        min_length=1,
        description="Unique service identifier.",
    )

    version: str = Field(
        default="1.0.0",
        description="Semantic version of the service.",
    )

    description: str = Field(
        default="",
        description="Human-readable description.",
    )

    author: str = Field(
        default="Envisio",
        description="Service author.",
    )

    enabled: bool = Field(
        default=True,
        description="Whether the service is enabled.",
    )

    dependencies: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Required service dependencies.",
    )

    optional_dependencies: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Optional service dependencies.",
    )

    tags: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Service classification tags.",
    )

    provides: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Capabilities provided by the service.",
    )

    singleton: bool = Field(
        default=True,
        description="Whether only one instance may exist.",
    )

    auto_start: bool = Field(
        default=True,
        description="Whether the Kernel should start the service automatically.",
    )

    priority: int = Field(
        default=100,
        ge=0,
        description="Startup priority. Lower values start first.",
    )

    health_check_enabled: bool = Field(
        default=True,
        description="Whether health monitoring is enabled.",
    )

    restart_on_failure: bool = Field(
        default=True,
        description="Automatically restart after failure.",
    )

    timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        description="Startup/shutdown timeout in seconds.",
    )

    def has_dependency(self, service_name: str) -> bool:
        """
        Determine whether this service depends on another service.

        Args:
            service_name:
                Name of the dependency.

        Returns:
            True if the dependency exists.
        """
        return service_name in self.dependencies

    def has_tag(self, tag: str) -> bool:
        """
        Determine whether this service has a specific tag.

        Args:
            tag:
                Tag to search for.

        Returns:
            True if the tag exists.
        """
        return tag in self.tags

    def provides_capability(self, capability: str) -> bool:
        """
        Determine whether this service provides a capability.

        Args:
            capability:
                Capability identifier.

        Returns:
            True if supported.
        """
        return capability in self.provides

    @property
    def identifier(self) -> str:
        """
        Return the fully qualified service identifier.

        Returns:
            String in the format ``name@version``.
        """
        return f"{self.name}@{self.version}"