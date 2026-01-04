"""Embedding model wrapper for nomic-embed-text-v1.5.

This module provides a unified interface for generating embeddings using the
nomic-embed-text-v1.5 model, which supports 8,192 token context and produces
768-dimensional vectors.

The model uses instruction prefixes to optimize embeddings for different tasks:
- search_document: for documents being indexed
- search_query: for search queries
- clustering: for clustering tasks
- classification: for classification tasks

Example:
    from src.processors.embedder import NomicEmbedder

    embedder = NomicEmbedder()

    # Embed documents for indexing
    doc_vectors = embedder.embed_documents(["Document 1 text", "Document 2 text"])

    # Embed query for search
    query_vector = embedder.embed_query("What is RAG?")

    # Count tokens (useful for chunking decisions)
    token_count = embedder.count_tokens("Some text to count")
"""

from __future__ import annotations

import structlog
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_CONFIG

logger = structlog.get_logger()


class NomicEmbedder:
    """Wrapper for nomic-embed-text-v1.5 with instruction prefixes.

    Provides methods to embed documents and queries with the appropriate
    instruction prefixes for optimal retrieval performance.

    Attributes:
        model: The underlying SentenceTransformer model.
        prefixes: Dictionary of instruction prefixes for different tasks.
        vector_size: Output dimension of embeddings (768).
        max_tokens: Maximum context window (8,192).
    """

    def __init__(self):
        """Initialize the nomic-embed-text-v1.5 model.

        Downloads the model on first use (~550MB). Subsequent calls use cached version.
        """
        logger.info(
            "loading_embedding_model",
            model_id=EMBEDDING_CONFIG["model_id"],
        )
        self.model = SentenceTransformer(
            EMBEDDING_CONFIG["model_id"],
            trust_remote_code=EMBEDDING_CONFIG["trust_remote_code"],
        )
        self.prefixes = EMBEDDING_CONFIG["prefixes"]
        self.vector_size = EMBEDDING_CONFIG["vector_size"]
        self.max_tokens = EMBEDDING_CONFIG["max_tokens"]

        logger.info(
            "embedding_model_loaded",
            model_id=EMBEDDING_CONFIG["model_id"],
            vector_size=self.vector_size,
            max_tokens=self.max_tokens,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents for indexing.

        Applies the 'search_document:' prefix to each text for optimal
        document embedding in retrieval scenarios.

        Sync function - CPU-bound embedding operation.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of 768-dimensional embedding vectors.
        """
        if not texts:
            return []

        prefixed = [self.prefixes["document"] + t for t in texts]
        embeddings = self.model.encode(prefixed, show_progress_bar=len(texts) > 10)

        logger.debug(
            "documents_embedded",
            count=len(texts),
            vector_size=len(embeddings[0]) if len(embeddings) > 0 else 0,
        )

        return embeddings.tolist()

    def embed_document(self, text: str) -> list[float]:
        """Embed a single document for indexing.

        Convenience method for single document embedding.

        Sync function - CPU-bound embedding operation.

        Args:
            text: Document text to embed.

        Returns:
            768-dimensional embedding vector.
        """
        return self.embed_documents([text])[0]

    def embed_query(self, query: str) -> list[float]:
        """Embed query for search.

        Applies the 'search_query:' prefix for optimal query embedding
        in retrieval scenarios.

        Sync function - CPU-bound embedding operation.

        Args:
            query: Search query text.

        Returns:
            768-dimensional embedding vector.
        """
        prefixed = self.prefixes["query"] + query
        embedding = self.model.encode([prefixed])[0]

        logger.debug(
            "query_embedded",
            query_length=len(query),
            vector_size=len(embedding),
        )

        return embedding.tolist()

    def embed_for_clustering(self, texts: list[str]) -> list[list[float]]:
        """Embed texts for clustering tasks.

        Applies the 'clustering:' prefix for optimal clustering embeddings.

        Sync function - CPU-bound embedding operation.

        Args:
            texts: List of texts to embed for clustering.

        Returns:
            List of 768-dimensional embedding vectors.
        """
        if not texts:
            return []

        prefixed = [self.prefixes["clustering"] + t for t in texts]
        embeddings = self.model.encode(prefixed, show_progress_bar=len(texts) > 10)

        return embeddings.tolist()

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using the model's tokenizer.

        Useful for determining if text exceeds the model's context window
        or for chunking decisions.

        Sync function - CPU-bound tokenization operation.

        Args:
            text: Text to count tokens for.

        Returns:
            Number of tokens in the text.
        """
        # Use the model's tokenizer for accurate token counting
        tokens = self.model.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)

    def get_max_tokens(self) -> int:
        """Get the maximum token context window.

        Returns:
            Maximum tokens supported (8,192).
        """
        return self.max_tokens

    def get_vector_size(self) -> int:
        """Get the output embedding dimension.

        Returns:
            Vector dimension (768).
        """
        return self.vector_size


# Module-level singleton for reuse (model loading is expensive)
_embedder_instance: NomicEmbedder | None = None


def get_embedder() -> NomicEmbedder:
    """Get or create the singleton NomicEmbedder instance.

    Lazily initializes the embedder on first call to avoid loading
    the model when the module is imported.

    Returns:
        Shared NomicEmbedder instance.
    """
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = NomicEmbedder()
    return _embedder_instance
