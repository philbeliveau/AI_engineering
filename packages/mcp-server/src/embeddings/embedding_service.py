"""Embedding service for Knowledge MCP Server.

Provides embedding generation using sentence-transformers with nomic-embed-text-v1.5 model.
This model produces 768-dimensional embeddings with 8K token context.

Uses instruction prefixes for optimal retrieval:
- search_query: for search queries (used by MCP server)
- search_document: for documents (used by pipeline during ingestion)

Follows project-context.md:33-36 (embedding configuration) and
project-context.md:54-57 (CPU-bound helpers can be sync).
"""

import structlog
from sentence_transformers import SentenceTransformer

logger = structlog.get_logger()

# Embedding configuration for nomic-embed-text-v1.5
EMBEDDING_MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_VECTOR_SIZE = 768
QUERY_PREFIX = "search_query: "

# Singleton embedding model instance
_embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Get or create the embedding model singleton.

    Returns the singleton SentenceTransformer instance, creating it on first call.
    Uses nomic-embed-text-v1.5 model which produces 768-dimensional embeddings.

    Returns:
        SentenceTransformer model instance
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info("embedding_model_loading", model=EMBEDDING_MODEL_ID)
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_ID,
            trust_remote_code=True,
        )
        logger.info(
            "embedding_model_loaded",
            model=EMBEDDING_MODEL_ID,
            vector_size=EMBEDDING_VECTOR_SIZE,
        )
    return _embedding_model


def embed_query(text: str) -> list[float]:
    """Generate embedding vector for a search query.

    Applies the 'search_query:' prefix for optimal retrieval.
    Sync function - CPU-bound embedding generation.
    Per project-context.md:54-57, CPU-bound helpers can be sync.

    Args:
        text: Text to embed

    Returns:
        768-dimensional embedding vector as list of floats
    """
    model = get_embedding_model()
    # Apply query prefix for search
    prefixed_text = QUERY_PREFIX + text
    embedding = model.encode(prefixed_text, normalize_embeddings=True)
    return embedding.tolist()


class EmbeddingService:
    """Embedding service wrapper class.

    Provides object-oriented interface to embedding generation.
    Uses the singleton model internally for efficiency.
    """

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding vector for a search query.

        Applies the 'search_query:' prefix for optimal retrieval.
        Sync function - CPU-bound embedding generation.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector as list of floats
        """
        return embed_query(text)
