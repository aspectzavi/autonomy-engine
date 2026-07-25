"""
Runtime invalid dependency tests.
"""

from __future__ import annotations

import pytest

from backend.core.kernel.bootstrap import KernelBootstrap
from backend.core.kernel.exceptions import RegistryError


def test_runtime_invalid_dependency() -> None:
    """
    Registering a dependency on a non-existent service
    should fail immediately.
    """

    bootstrap = KernelBootstrap()

    with pytest.raises(
        RegistryError,
        match="Unknown dependency",
    ):
        bootstrap.depends_on(
            "agent-service",
            "database-service",  # not registered
        )