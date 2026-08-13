"""
Vector memory.

Provides the foundation for semantic memory retrieval.

Currently this class inherits the in-memory implementation provided by
MemoryStore. Future revisions will extend it with embedding generation
and vector similarity search.

Examples of future backends:

- ChromaDB
- FAISS
- Pinecone
- Weaviate
- Milvus
"""

from __future__ import annotations

from backend.core.memory.memory_store import MemoryStore


class VectorMemory(MemoryStore):
    """
    Semantic vector memory.

    Placeholder implementation.

    Future versions will support:

    - embedding generation
    - cosine similarity search
    - nearest-neighbor retrieval
    - persistent vector databases
    """

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Vector memory diagnostics.
        """

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "memory_type": "vector",
                "embeddings": False,
            },
        )

        return diagnostics