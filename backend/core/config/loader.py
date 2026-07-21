"""
Configuration loader.

Constructs the engine configuration.

Future versions may support environment variables, TOML, YAML,
JSON, secrets managers, or remote configuration providers.
"""

from __future__ import annotations

from backend.core.config.config import EngineConfig


class ConfigurationLoader:
    """
    Loads engine configuration.
    """

    def load(
        self,
    ) -> EngineConfig:
        """
        Load the engine configuration.
        """
        return EngineConfig()