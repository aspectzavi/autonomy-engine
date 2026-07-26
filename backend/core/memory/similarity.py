"""
Similarity metrics.

Provides common vector similarity functions used by semantic memory.

Initially cosine similarity is implemented because it is the standard
metric for embedding models.

Future implementations may include:

- Euclidean distance
- Dot product
- Manhattan distance
- Angular similarity
"""

from __future__ import annotations

from math import sqrt


def cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns a value in the range [-1.0, 1.0].

    Identical vectors produce 1.0.

    Orthogonal vectors produce 0.0.
    """

    if len(left) != len(right):
        raise ValueError(
            "Vectors must have identical dimensions."
        )

    if not left:
        raise ValueError(
            "Vectors cannot be empty."
        )

    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0

    for left_value, right_value in zip(left, right):
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return dot / (
        sqrt(left_norm) * sqrt(right_norm)
    )


def cosine_distance(
    left: list[float],
    right: list[float],
) -> float:
    """
    Compute cosine distance.

    Lower values indicate greater similarity.
    """

    return 1.0 - cosine_similarity(
        left,
        right,
    )