"""
Concrete autonomous agent implementations.

This package contains production implementations built on top of the
core agent framework.

The core framework (backend.core.agents) defines reusable abstractions,
while this package provides concrete agents such as browser, desktop,
coding, planning, and research agents.
"""

from backend.agents.factory import AgentFactory

__all__ = [
    "AgentFactory",
]