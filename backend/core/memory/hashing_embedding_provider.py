"""
Hashing embedding provider.

Default deterministic implementation of EmbeddingProvider.

Uses feature hashing (the "hashing trick"): each token in the input
text is hashed into a fixed-size vector, so semantically overlapping
text (shared words) produces vectors with high cosine similarity,
without needing a trained model, network access, or an API key.

This is a real, standard technique (the same one behind scikit-learn's
HashingVectorizer) -- not a placeholder. It is intentionally simple
and local so the memory subsystem has a genuinely working default
before a real model-backed provider (OpenAI, SentenceTransformers,
Ollama, etc.) is wired in.

Future implementations may wrap:

- OpenAI
- Ollama
- SentenceTransformers
- HuggingFace
- Gemini
- Azure OpenAI
- Local GGUF models
"""

from __future__ import annotations

import re
from hashlib import blake2b
from math import sqrt

from backend.core.memory.embedding_provider import (
    EmbeddingProvider,
)

_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class HashingEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic, offline embedding provider using feature hashing.
    """

    def __init__(
        self,
        *,
        dimensions: int = 128,
    ) -> None:
        if dimensions <= 0:
            raise ValueError(
                "dimensions must be positive.",
            )

        self._dimensions = dimensions

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dimensions(
        self,
    ) -> int:
        """
        Return the dimensionality of produced embeddings.
        """

        return self._dimensions

    @property
    def model_name(
        self,
    ) -> str:
        """
        Human-readable model identifier.
        """

        return f"hashing-v1-{self._dimensions}d"

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate a hashed bag-of-words embedding for a single text.
        """

        vector = [0.0] * self._dimensions

        tokens = _TOKEN_PATTERN.findall(
            text.casefold(),
        )

        for token in tokens:
            digest = blake2b(
                token.encode("utf-8"),
                digest_size=8,
            ).digest()

            index = (
                int.from_bytes(digest, "big")
                % self._dimensions
            )

            #
            # Sign bucket derived from a second hash byte so
            # unrelated tokens partially cancel out, the same way
            # real hashing-trick vectorizers do, rather than every
            # token pushing the vector in a purely positive direction.
            #
            sign = (
                1.0
                if digest[0] % 2 == 0
                else -1.0
            )

            vector[index] += sign

        norm = sqrt(
            sum(value * value for value in vector),
        )

        if norm == 0.0:
            return vector

        return [value / norm for value in vector]

    async def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        return [
            await self.embed(text)
            for text in texts
        ]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "strategy": "feature_hashing",
            },
        )

        return diagnostics
