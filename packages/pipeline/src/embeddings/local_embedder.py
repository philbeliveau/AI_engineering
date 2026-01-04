"""Local embedding generation using sentence-transformers.

This module provides zero-API-cost embedding generation using the
nomic-embed-text-v1.5 model for semantic search in Qdrant.

Uses instruction prefixes for optimal retrieval performance:
- search_document: for documents being indexed
- search_query: for search queries

Example:
    from src.embeddings import get_embedder

    embedder = get_embedder()
    vector = embedder.embed_text("Hello world")
    # Returns 768-dimensional vector (nomic-embed-text-v1.5)

    vectors = embedder.embed_batch(["Hello", "World"])
    # Returns list of 768-dimensional vectors
"""

from typing import Optional
import threading

from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import structlog

from src.config import EMBEDDING_CONFIG
from src.exceptions import KnowledgeError

logger = structlog.get_logger()


class EmbeddingConfig(BaseModel):
    """Configuration for local embedding generation.

    Defaults are set from centralized EMBEDDING_CONFIG for nomic-embed-text-v1.5.
    """

    model_name: str = Field(
        default=EMBEDDING_CONFIG["model_id"],
        description="Sentence-transformers model name"
    )
    embedding_dimension: int = Field(
        default=EMBEDDING_CONFIG["vector_size"],
        description="Expected embedding vector dimension"
    )
    batch_size: int = Field(
        default=32,
        description="Batch size for encoding"
    )
    show_progress: bool = Field(
        default=True,
        description="Show progress bar for batch encoding"
    )
    normalize_embeddings: bool = Field(
        default=True,
        description="Normalize vectors for cosine similarity"
    )
    max_tokens: int = Field(
        default=EMBEDDING_CONFIG["max_tokens"],
        description="Model's max token limit (for truncation warnings)"
    )
    trust_remote_code: bool = Field(
        default=EMBEDDING_CONFIG["trust_remote_code"],
        description="Allow remote code execution for model loading"
    )
    document_prefix: str = Field(
        default=EMBEDDING_CONFIG["prefixes"]["document"],
        description="Instruction prefix for document embeddings"
    )
    query_prefix: str = Field(
        default=EMBEDDING_CONFIG["prefixes"]["query"],
        description="Instruction prefix for query embeddings"
    )


class EmbeddingError(KnowledgeError):
    """Base exception for embedding errors."""

    pass


class ModelLoadError(EmbeddingError):
    """Raised when model loading fails."""

    def __init__(self, model_name: str, reason: str):
        super().__init__(
            code="MODEL_LOAD_ERROR",
            message=f"Failed to load embedding model '{model_name}': {reason}",
            details={"model_name": model_name, "reason": reason}
        )


class EmbeddingGenerationError(EmbeddingError):
    """Raised when embedding generation fails."""

    def __init__(self, reason: str, text_length: Optional[int] = None):
        super().__init__(
            code="EMBEDDING_GENERATION_ERROR",
            message=f"Failed to generate embedding: {reason}",
            details={"reason": reason, "text_length": text_length}
        )


class LocalEmbedder:
    """Local embedding generator using sentence-transformers.

    Uses nomic-embed-text-v1.5 model to generate 768-dimensional embeddings
    for semantic search. Model is loaded lazily on first use.

    Supports instruction prefixes for optimal retrieval:
    - embed_text() applies document prefix for indexing
    - embed_query() applies query prefix for search

    Attributes:
        config: Embedding configuration settings.

    Example:
        embedder = LocalEmbedder()
        vector = embedder.embed_text("Sample text")
        assert len(vector) == 768  # nomic-embed-text-v1.5
    """

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """Initialize embedder with configuration.

        Args:
            config: Embedding configuration. Uses defaults if not provided.
        """
        self.config = config or EmbeddingConfig()
        self._model: Optional[SentenceTransformer] = None
        self._lock = threading.Lock()

        logger.debug(
            "embedder_initialized",
            model_name=self.config.model_name,
            dimension=self.config.embedding_dimension
        )

    def _load_model(self) -> SentenceTransformer:
        """Load the sentence-transformers model.

        Returns:
            Loaded SentenceTransformer model.

        Raises:
            ModelLoadError: If model loading fails.
        """
        with self._lock:
            if self._model is not None:
                return self._model

            try:
                logger.info(
                    "loading_embedding_model",
                    model_name=self.config.model_name
                )
                self._model = SentenceTransformer(
                    self.config.model_name,
                    trust_remote_code=self.config.trust_remote_code,
                )

                # Verify dimension matches expected
                actual_dim = self._model.get_sentence_embedding_dimension()
                if actual_dim != self.config.embedding_dimension:
                    logger.warning(
                        "dimension_mismatch",
                        expected=self.config.embedding_dimension,
                        actual=actual_dim
                    )

                logger.info(
                    "embedding_model_loaded",
                    model_name=self.config.model_name,
                    dimension=actual_dim
                )
                return self._model

            except Exception as e:
                raise ModelLoadError(self.config.model_name, str(e))

    @property
    def model(self) -> SentenceTransformer:
        """Get or load the embedding model.

        Returns:
            Loaded SentenceTransformer model.
        """
        # _load_model handles the already-loaded case with proper locking
        return self._load_model()

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text (document).

        Applies the document instruction prefix for optimal retrieval.

        Args:
            text: Text to embed.

        Returns:
            768-dimensional embedding vector (nomic-embed-text-v1.5).

        Raises:
            EmbeddingGenerationError: If embedding fails.
        """
        if not text or not text.strip():
            raise EmbeddingGenerationError(
                "Cannot embed empty text",
                text_length=len(text) if text else 0
            )

        # Warn if text may be truncated (rough estimate: ~4 chars per token)
        estimated_tokens = len(text) // 4
        if estimated_tokens > self.config.max_tokens:
            logger.warning(
                "text_may_be_truncated",
                text_length=len(text),
                estimated_tokens=estimated_tokens,
                max_tokens=self.config.max_tokens,
            )

        try:
            # Apply document prefix for indexing
            prefixed_text = self.config.document_prefix + text
            embedding = self.model.encode(
                prefixed_text,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=False
            )
            return embedding.tolist()

        except ModelLoadError:
            raise
        except Exception as e:
            raise EmbeddingGenerationError(str(e), len(text))

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a search query.

        Applies the query instruction prefix for optimal retrieval.

        Args:
            query: Query text to embed.

        Returns:
            768-dimensional embedding vector (nomic-embed-text-v1.5).

        Raises:
            EmbeddingGenerationError: If embedding fails.
        """
        if not query or not query.strip():
            raise EmbeddingGenerationError(
                "Cannot embed empty query",
                text_length=len(query) if query else 0
            )

        try:
            # Apply query prefix for search
            prefixed_query = self.config.query_prefix + query
            embedding = self.model.encode(
                prefixed_query,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=False
            )
            return embedding.tolist()

        except ModelLoadError:
            raise
        except Exception as e:
            raise EmbeddingGenerationError(str(e), len(query))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts (documents).

        Applies the document instruction prefix for optimal retrieval.

        Args:
            texts: List of texts to embed. All texts must be non-empty.

        Returns:
            List of 768-dimensional embedding vectors, one per input text.

        Raises:
            EmbeddingGenerationError: If embedding fails or any text is empty.
        """
        if not texts:
            return []

        # Validate all texts are non-empty (consistent with embed_text behavior)
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise EmbeddingGenerationError(
                    f"Cannot embed empty text at index {i}",
                    text_length=len(text) if text else 0
                )

        try:
            logger.debug(
                "batch_embedding_start",
                batch_size=len(texts)
            )

            # Apply document prefix to all texts
            prefixed_texts = [self.config.document_prefix + t for t in texts]

            embeddings = self.model.encode(
                prefixed_texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=self.config.show_progress
            )

            logger.debug(
                "batch_embedding_complete",
                batch_size=len(texts)
            )

            return [emb.tolist() for emb in embeddings]

        except ModelLoadError:
            raise
        except Exception as e:
            raise EmbeddingGenerationError(
                str(e),
                text_length=sum(len(t) for t in texts)
            )

    def get_dimension(self) -> int:
        """Get the embedding dimension.

        Returns:
            Embedding dimension (768 for nomic-embed-text-v1.5).
        """
        return self.config.embedding_dimension


# Module-level singleton
_embedder_instance: Optional[LocalEmbedder] = None
_instance_lock = threading.Lock()


def get_embedder(config: Optional[EmbeddingConfig] = None) -> LocalEmbedder:
    """Get or create the singleton embedder instance.

    Args:
        config: Configuration for first initialization.
                Ignored with warning if instance already exists.

    Returns:
        LocalEmbedder singleton instance.
    """
    global _embedder_instance

    with _instance_lock:
        if _embedder_instance is None:
            _embedder_instance = LocalEmbedder(config)
        elif config is not None:
            logger.warning(
                "get_embedder_config_ignored",
                message="Config parameter ignored - singleton already initialized",
                existing_model=_embedder_instance.config.model_name,
            )
        return _embedder_instance


def reset_embedder() -> None:
    """Reset the singleton instance (for testing).

    Warning: This is primarily for testing purposes.
    """
    global _embedder_instance
    with _instance_lock:
        _embedder_instance = None
