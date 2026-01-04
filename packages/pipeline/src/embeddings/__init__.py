"""Local embedding generation for knowledge pipeline.

This module provides zero-API-cost embedding generation using
sentence-transformers for semantic search in Qdrant.

Uses nomic-embed-text-v1.5 (768 dimensions, 8K context window).

Example:
    from src.embeddings import get_embedder

    embedder = get_embedder()
    vector = embedder.embed_text("Sample text")
    assert len(vector) == 768  # nomic-embed-text-v1.5

    vectors = embedder.embed_batch(["Hello", "World"])
"""

from src.embeddings.local_embedder import (
    # Main class
    LocalEmbedder,
    # Configuration
    EmbeddingConfig,
    # Exceptions
    EmbeddingError,
    ModelLoadError,
    EmbeddingGenerationError,
    # Factory function
    get_embedder,
    reset_embedder,
)

__all__ = [
    "LocalEmbedder",
    "EmbeddingConfig",
    "EmbeddingError",
    "ModelLoadError",
    "EmbeddingGenerationError",
    "get_embedder",
    "reset_embedder",
]
