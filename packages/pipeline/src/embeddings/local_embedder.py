"""Local embedding generation using sentence-transformers.

This module provides zero-API-cost embedding generation using the
all-MiniLM-L6-v2 model for semantic search in Qdrant.

Example:
    from src.embeddings import get_embedder

    embedder = get_embedder()
    vector = embedder.embed_text("Hello world")
    # Returns 384-dimensional vector

    vectors = embedder.embed_batch(["Hello", "World"])
    # Returns list of 384-dimensional vectors
"""

from typing import Optional
import threading

from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import structlog

from src.exceptions import KnowledgeError

logger = structlog.get_logger()


class EmbeddingConfig(BaseModel):
    """Configuration for local embedding generation."""

    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence-transformers model name"
    )
    embedding_dimension: int = Field(
        default=384,
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
        default=256,
        description="Model's max token limit (for truncation warnings)"
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

    Uses all-MiniLM-L6-v2 model to generate 384-dimensional embeddings
    for semantic search. Model is loaded lazily on first use.

    Attributes:
        config: Embedding configuration settings.

    Example:
        embedder = LocalEmbedder()
        vector = embedder.embed_text("Sample text")
        assert len(vector) == 384
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
                self._model = SentenceTransformer(self.config.model_name)

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
        """Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            384-dimensional embedding vector.

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
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=False
            )
            return embedding.tolist()

        except ModelLoadError:
            raise
        except Exception as e:
            raise EmbeddingGenerationError(str(e), len(text))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed. All texts must be non-empty.

        Returns:
            List of 384-dimensional embedding vectors, one per input text.

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

            embeddings = self.model.encode(
                texts,
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
            Embedding dimension (384 for all-MiniLM-L6-v2).
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
