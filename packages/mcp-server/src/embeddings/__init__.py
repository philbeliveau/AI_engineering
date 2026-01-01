"""Embedding service module.

Provides embedding generation using fastembed with all-MiniLM-L6-v2 model.
"""

from src.embeddings.embedding_service import EmbeddingService, embed_query, get_embedding_model

__all__ = ["EmbeddingService", "embed_query", "get_embedding_model"]
