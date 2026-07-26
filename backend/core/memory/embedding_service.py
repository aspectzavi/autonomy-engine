"""
Embedding service.

Provides the high-level interface used by the runtime to generate vector
embeddings.

The service delegates embedding generation to an EmbeddingProvider while
remaining independent of any concrete embedding model.

Future responsibilities include:

- batching
- caching
- retries
- rate limiting
- telemetry
- provider failover
"""

from __future__ import annotations

from backend.core.memory.embedding_provider import (
    EmbeddingProvider,
)


class EmbeddingService:
    """
    High-level embedding service.
    """

    def __init__(
        self,
        *,
        provider: EmbeddingProvider,
    ) -> None:
        self._provider = provider

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def provider(
        self,
    ) -> EmbeddingProvider:
        """
        Active embedding provider.
        """
        return self._provider

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """

        return await self.provider.embed(
            text,
        )

    async def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        return await self.provider.embed_many(
            texts,
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return embedding service diagnostics.
        """

        return {
            "provider": self.provider.diagnostics(),
        }