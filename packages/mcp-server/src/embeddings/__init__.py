"""Embedding service module.

Provides embedding generation using fastembed with nomic-embed-text-v1.5 model.
Import is lazy to avoid requiring fastembed in test environments.
"""

from src.embeddings.embedding_service import EmbeddingService, embed_query, get_embedding_model

__all__ = ["EmbeddingService", "embed_query", "get_embedding_model"]
