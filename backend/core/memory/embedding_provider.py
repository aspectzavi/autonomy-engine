"""
Embedding provider.

Defines the interface responsible for converting text into numerical
vector embeddings.

Embedding providers are intentionally independent of any specific model
or vendor. Implementations may use:

- OpenAI
- Ollama
- SentenceTransformers
- HuggingFace
- Gemini
- Azure OpenAI
- Local GGUF models

The rest of the memory subsystem depends only on this abstraction.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class EmbeddingProvider(ABC):
    """
    Base interface for embedding providers.
    """

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for a single text.
        """
        raise NotImplementedError

    @abstractmethod
    async def embed_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def dimensions(
        self,
    ) -> int:
        """
        Return the dimensionality of produced embeddings.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(
        self,
    ) -> str:
        """
        Human-readable model identifier.
        """
        raise NotImplementedError

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return provider diagnostics.
        """

        return {
            "provider": type(self).__name__,
            "model": self.model_name,
            "dimensions": self.dimensions,
        }