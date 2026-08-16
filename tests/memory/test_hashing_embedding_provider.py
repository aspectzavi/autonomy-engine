"""
Hashing embedding provider tests.
"""

from __future__ import annotations

import pytest

from backend.core.memory.hashing_embedding_provider import (
    HashingEmbeddingProvider,
)
from backend.core.memory.similarity import cosine_similarity


@pytest.mark.asyncio
async def test_embed_is_deterministic() -> None:
    provider = HashingEmbeddingProvider()

    first = await provider.embed("hello world")
    second = await provider.embed("hello world")

    assert first == second


@pytest.mark.asyncio
async def test_embed_has_configured_dimensions() -> None:
    provider = HashingEmbeddingProvider(dimensions=32)

    embedding = await provider.embed("some text")

    assert len(embedding) == 32
    assert provider.dimensions == 32


@pytest.mark.asyncio
async def test_embed_is_normalized() -> None:
    provider = HashingEmbeddingProvider()

    embedding = await provider.embed("some reasonably long piece of text")

    magnitude = sum(value * value for value in embedding) ** 0.5

    assert magnitude == pytest.approx(1.0, abs=1e-6)


@pytest.mark.asyncio
async def test_shared_vocabulary_is_more_similar_than_unrelated_text() -> None:
    provider = HashingEmbeddingProvider()

    a = await provider.embed(
        "cat sitting by a sunny window watching birds outside",
    )
    b = await provider.embed(
        "cat sitting by a sunny window watching sparrows",
    )
    c = await provider.embed(
        "quarterly revenue grew twelve percent this fiscal year",
    )

    assert cosine_similarity(a, b) > cosine_similarity(a, c)


@pytest.mark.asyncio
async def test_empty_text_returns_zero_vector() -> None:
    provider = HashingEmbeddingProvider(dimensions=16)

    embedding = await provider.embed("")

    assert embedding == [0.0] * 16


@pytest.mark.asyncio
async def test_embed_many() -> None:
    provider = HashingEmbeddingProvider()

    embeddings = await provider.embed_many(["a", "b", "c"])

    assert len(embeddings) == 3


def test_rejects_non_positive_dimensions() -> None:
    with pytest.raises(ValueError):
        HashingEmbeddingProvider(dimensions=0)
