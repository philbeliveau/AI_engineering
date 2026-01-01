"""Embedding service for Knowledge MCP Server.

Provides embedding generation using fastembed with all-MiniLM-L6-v2 model.
Follows project-context.md:33-36 (embedding configuration) and
project-context.md:54-57 (CPU-bound helpers can be sync).
"""

import structlog
from fastembed import TextEmbedding

logger = structlog.get_logger()

# Singleton embedding model instance
_embedding_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    """Get or create the embedding model singleton.

    Returns the singleton TextEmbedding instance, creating it on first call.
    Uses all-MiniLM-L6-v2 model which produces 384-dimensional embeddings.

    Returns:
        TextEmbedding model instance
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info("embedding_model_loading", model="sentence-transformers/all-MiniLM-L6-v2")
        _embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        logger.info("embedding_model_loaded")
    return _embedding_model


def embed_query(text: str) -> list[float]:
    """Generate embedding vector for a text query.

    Sync function - CPU-bound embedding generation.
    Per project-context.md:54-57, CPU-bound helpers can be sync.

    Args:
        text: Text to embed

    Returns:
        384-dimensional embedding vector as list of floats
    """
    model = get_embedding_model()
    # fastembed returns generator, convert to list
    embeddings = list(model.embed([text]))
    return embeddings[0].tolist()


class EmbeddingService:
    """Embedding service wrapper class.

    Provides object-oriented interface to embedding generation.
    Uses the singleton model internally for efficiency.
    """

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for a text query.

        Sync function - CPU-bound embedding generation.

        Args:
            text: Text to embed

        Returns:
            384-dimensional embedding vector as list of floats
        """
        return embed_query(text)
