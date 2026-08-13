"""
LLM configuration.

Defines configuration for language model providers.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LLMConfig:
    """
    Language model configuration.

    Describes the default provider and inference settings used by
    autonomous agents.
    """

    provider: str = "openai"

    model: str = "gpt-5.5"

    api_key: str | None = None

    base_url: str | None = None

    temperature: float = 0.2

    max_tokens: int = 4096

    timeout_seconds: int = 120

    max_retries: int = 3

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return LLM configuration diagnostics.

        Sensitive values such as API keys are intentionally omitted.
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "api_key_configured": (
                self.api_key is not None
            ),
        }