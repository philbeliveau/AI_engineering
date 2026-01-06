"""Embedding service for Knowledge MCP Server.

Provides embedding generation using FastEmbed (ONNX Runtime) with nomic-embed-text-v1.5 model.
This model produces 768-dimensional embeddings with 8K token context.

Uses instruction prefixes for optimal retrieval:
- search_query: for search queries (used by MCP server)
- search_document: for documents (used by pipeline during ingestion)

FastEmbed uses ONNX Runtime instead of PyTorch, reducing Docker image size from ~7.8GB to ~800MB
while producing identical embeddings (verified via compatibility test).

Follows project-context.md:33-36 (embedding configuration) and
project-context.md:54-57 (CPU-bound helpers can be sync).
"""

import structlog
from fastembed import TextEmbedding

logger = structlog.get_logger()

# Embedding configuration for nomic-embed-text-v1.5
EMBEDDING_MODEL_ID = "nomic-ai/nomic-embed-text-v1.5"
EMBEDDING_VECTOR_SIZE = 768
QUERY_PREFIX = "search_query: "

# Singleton embedding model instance
_embedding_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    """Get or create the embedding model singleton.

    Returns the singleton TextEmbedding instance, creating it on first call.
    Uses nomic-embed-text-v1.5 model which produces 768-dimensional embeddings.

    Returns:
        TextEmbedding model instance (FastEmbed/ONNX)
    """
    global _embedding_model
    if _embedding_model is None:
        logger.info("embedding_model_loading", model=EMBEDDING_MODEL_ID, runtime="onnx")
        _embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL_ID)
        logger.info(
            "embedding_model_loaded",
            model=EMBEDDING_MODEL_ID,
            vector_size=EMBEDDING_VECTOR_SIZE,
            runtime="onnx",
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
    # FastEmbed returns a generator, convert to list and get first result
    embeddings = list(model.embed([prefixed_text]))
    return embeddings[0].tolist()


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
