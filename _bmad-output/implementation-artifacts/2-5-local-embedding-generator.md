# Story 2.5: Local Embedding Generator

Status: done

## Story

As a **developer**,
I want to generate embeddings locally using sentence-transformers (all-MiniLM-L6-v2),
So that chunks can be vectorized for semantic search without external API costs.

## Acceptance Criteria

**Given** a text chunk
**When** I generate an embedding
**Then** a 384-dimensional vector is returned
**And** the embedding model is loaded once and reused
**And** batch embedding is supported for efficiency
**And** NFR3 (zero external LLM API costs) is satisfied

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed
  - Requires `packages/pipeline/src/` directory structure
  - Requires `sentence-transformers>=5.0` dependency installed
- **Story 1.3** (Pydantic Models) - MUST be completed
  - Requires Pydantic model patterns for configuration
- **Story 2.4** (Text Chunking Processor) - Should be completed
  - Provides `Chunk` objects that will be embedded
  - Provides text content to be vectorized

**Blocks:**
- **Story 2.6** (End-to-End Ingestion Pipeline) - Needs embeddings for Qdrant storage
- **Story 3.6** (Extraction Storage and Embedding) - Needs embedding generation for extractions

## Tasks / Subtasks

- [x] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [x] Confirm sentence-transformers installed: `cd packages/pipeline && uv run python -c "from sentence_transformers import SentenceTransformer; print('OK')"`
  - [x] Confirm Python 3.11+: `cd packages/pipeline && uv run python --version`
  - [x] Confirm Pydantic available: `cd packages/pipeline && uv run python -c "from pydantic import BaseModel; print('OK')"`

- [x] **Task 2: Create Embeddings Module Structure** (AC: Module exists)
  - [x] Create `packages/pipeline/src/embeddings/` directory
  - [x] Create `packages/pipeline/src/embeddings/__init__.py`
  - [x] Create `packages/pipeline/src/embeddings/local_embedder.py`

- [x] **Task 3: Define Embedding Configuration Model** (AC: Type-safe config)
  - [x] Create `EmbeddingConfig` Pydantic model with fields:
    - `model_name: str = "all-MiniLM-L6-v2"` - Default model per architecture
    - `embedding_dimension: int = 384` - Per Qdrant config
    - `batch_size: int = 32` - For batch processing efficiency
    - `show_progress: bool = True` - Progress bar for large batches
    - `normalize_embeddings: bool = True` - Normalize for cosine similarity

- [x] **Task 4: Implement LocalEmbedder Class** (AC: Core embedding functionality)
  - [x] Create `LocalEmbedder` class with singleton pattern for model reuse
  - [x] Implement `__init__(self, config: EmbeddingConfig = None)` with lazy model loading
  - [x] Implement `_load_model(self) -> SentenceTransformer` - One-time model load
  - [x] Implement `embed_text(self, text: str) -> list[float]` - Single text embedding
  - [x] Implement `embed_batch(self, texts: list[str]) -> list[list[float]]` - Batch embedding
  - [x] Implement `get_dimension(self) -> int` - Returns 384
  - [x] Add structlog logging for model load and embedding operations

- [x] **Task 5: Implement Error Handling** (AC: Proper exceptions)
  - [x] Create `EmbeddingError` base exception inheriting from `KnowledgeError`
  - [x] Create `ModelLoadError` for model loading failures
  - [x] Create `EmbeddingGenerationError` for embedding failures
  - [x] All exceptions follow structured format: `{code, message, details}`

- [x] **Task 6: Implement Module-Level Singleton** (AC: Model loaded once)
  - [x] Create `_embedder_instance: Optional[LocalEmbedder] = None` module variable
  - [x] Create `get_embedder(config: EmbeddingConfig = None) -> LocalEmbedder` factory function
  - [x] Ensure model is loaded exactly once across all usages
  - [x] Add thread-safety consideration (mutex for lazy loading)

- [x] **Task 7: Create Module Exports** (AC: Clean imports)
  - [x] Export from `packages/pipeline/src/embeddings/__init__.py`:
    - `LocalEmbedder`
    - `EmbeddingConfig`
    - `EmbeddingError`, `ModelLoadError`, `EmbeddingGenerationError`
    - `get_embedder`
  - [x] Verify imports work: `from src.embeddings import LocalEmbedder, get_embedder`

- [x] **Task 8: Create Unit Tests** (AC: Full coverage)
  - [x] Create `packages/pipeline/tests/test_embeddings/` directory
  - [x] Create `packages/pipeline/tests/test_embeddings/conftest.py` with fixtures
  - [x] Create `packages/pipeline/tests/test_embeddings/test_local_embedder.py`
  - [x] Test single text embedding returns 384 dimensions
  - [x] Test batch embedding returns correct number of vectors
  - [x] Test model is loaded only once (singleton behavior)
  - [x] Test embedding dimension getter returns 384
  - [x] Test exception handling for empty input
  - [x] Test config customization works

## Dev Notes

### NFR3 Compliance - Zero External API Costs

**From Architecture Document (architecture.md:309-314):**

> NFR3: Cost
> - Zero external LLM API costs at query time | Pre-extraction during ingestion
> - Zero embedding API costs | Local all-MiniLM-L6-v2 model

This story implements the local embedding strategy that eliminates per-query API costs.

### Architecture-Specified Configuration

**From Architecture Document (architecture.md:299-307):**

| Setting | Value | Rationale |
|---------|-------|-----------|
| Vector size | 384 | all-MiniLM-L6-v2 output |
| Distance metric | Cosine | Standard for text embeddings |
| Embedding model | all-MiniLM-L6-v2 | 384d, efficient, good quality |

### Required Directory Structure

**From Architecture Document (architecture.md:636-640):**

```
packages/pipeline/
├── src/
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── local_embedder.py    # <-- YOUR WORK HERE
```

### Reference Implementation

```python
# packages/pipeline/src/embeddings/local_embedder.py
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
from pathlib import Path
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
        if self._model is None:
            self._load_model()
        return self._model

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

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=False
            )
            return embedding.tolist()

        except Exception as e:
            raise EmbeddingGenerationError(str(e), len(text))

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of 384-dimensional embedding vectors.

        Raises:
            EmbeddingGenerationError: If embedding fails.
        """
        if not texts:
            return []

        # Filter empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)

        if not valid_texts:
            raise EmbeddingGenerationError(
                "All texts are empty",
                text_length=0
            )

        try:
            logger.debug(
                "batch_embedding_start",
                batch_size=len(valid_texts)
            )

            embeddings = self.model.encode(
                valid_texts,
                batch_size=self.config.batch_size,
                normalize_embeddings=self.config.normalize_embeddings,
                show_progress_bar=self.config.show_progress
            )

            logger.debug(
                "batch_embedding_complete",
                batch_size=len(valid_texts)
            )

            return [emb.tolist() for emb in embeddings]

        except Exception as e:
            raise EmbeddingGenerationError(
                str(e),
                text_length=sum(len(t) for t in valid_texts)
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
                Ignored if instance already exists.

    Returns:
        LocalEmbedder singleton instance.
    """
    global _embedder_instance

    with _instance_lock:
        if _embedder_instance is None:
            _embedder_instance = LocalEmbedder(config)
        return _embedder_instance


def reset_embedder() -> None:
    """Reset the singleton instance (for testing).

    Warning: This is primarily for testing purposes.
    """
    global _embedder_instance
    with _instance_lock:
        _embedder_instance = None
```

### Module Exports

```python
# packages/pipeline/src/embeddings/__init__.py
"""Local embedding generation for knowledge pipeline.

This module provides zero-API-cost embedding generation using
sentence-transformers for semantic search in Qdrant.

Example:
    from src.embeddings import get_embedder

    embedder = get_embedder()
    vector = embedder.embed_text("Sample text")
    assert len(vector) == 384

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
```

### Test Implementation

```python
# packages/pipeline/tests/test_embeddings/test_local_embedder.py
"""Tests for local embedding generation."""

import pytest
from src.embeddings import (
    LocalEmbedder,
    EmbeddingConfig,
    EmbeddingError,
    EmbeddingGenerationError,
    get_embedder,
    reset_embedder,
)


class TestLocalEmbedder:
    """Tests for LocalEmbedder class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        reset_embedder()
        yield
        reset_embedder()

    def test_embed_text_returns_384_dimensions(self):
        """Single text embedding should return 384-dimensional vector."""
        embedder = LocalEmbedder()
        vector = embedder.embed_text("Hello, world!")

        assert isinstance(vector, list)
        assert len(vector) == 384
        assert all(isinstance(v, float) for v in vector)

    def test_embed_batch_returns_correct_count(self):
        """Batch embedding should return one vector per input."""
        embedder = LocalEmbedder()
        texts = ["First text", "Second text", "Third text"]
        vectors = embedder.embed_batch(texts)

        assert len(vectors) == 3
        assert all(len(v) == 384 for v in vectors)

    def test_embed_empty_text_raises_error(self):
        """Empty text should raise EmbeddingGenerationError."""
        embedder = LocalEmbedder()

        with pytest.raises(EmbeddingGenerationError) as exc_info:
            embedder.embed_text("")

        assert exc_info.value.code == "EMBEDDING_GENERATION_ERROR"
        assert "empty" in exc_info.value.message.lower()

    def test_embed_whitespace_only_raises_error(self):
        """Whitespace-only text should raise error."""
        embedder = LocalEmbedder()

        with pytest.raises(EmbeddingGenerationError):
            embedder.embed_text("   \n\t  ")

    def test_embed_batch_empty_list_returns_empty(self):
        """Empty batch should return empty list."""
        embedder = LocalEmbedder()
        vectors = embedder.embed_batch([])

        assert vectors == []

    def test_get_dimension_returns_384(self):
        """get_dimension should return 384."""
        embedder = LocalEmbedder()

        assert embedder.get_dimension() == 384

    def test_model_loaded_once(self):
        """Model should only be loaded once per instance."""
        embedder = LocalEmbedder()

        # First call loads model
        _ = embedder.embed_text("First")
        model_id_1 = id(embedder._model)

        # Second call reuses model
        _ = embedder.embed_text("Second")
        model_id_2 = id(embedder._model)

        assert model_id_1 == model_id_2

    def test_custom_config(self):
        """Custom config should be respected."""
        config = EmbeddingConfig(
            batch_size=16,
            show_progress=False
        )
        embedder = LocalEmbedder(config)

        assert embedder.config.batch_size == 16
        assert embedder.config.show_progress is False
        assert embedder.config.model_name == "all-MiniLM-L6-v2"


class TestSingletonPattern:
    """Tests for module-level singleton."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        reset_embedder()
        yield
        reset_embedder()

    def test_get_embedder_returns_same_instance(self):
        """get_embedder should return the same instance."""
        embedder1 = get_embedder()
        embedder2 = get_embedder()

        assert embedder1 is embedder2

    def test_singleton_model_shared(self):
        """Singleton should share the loaded model."""
        embedder = get_embedder()
        _ = embedder.embed_text("Load model")

        embedder2 = get_embedder()
        assert embedder2._model is embedder._model

    def test_reset_embedder_clears_instance(self):
        """reset_embedder should clear singleton."""
        embedder1 = get_embedder()
        reset_embedder()
        embedder2 = get_embedder()

        assert embedder1 is not embedder2


class TestEmbeddingQuality:
    """Tests for embedding quality and semantics."""

    @pytest.fixture
    def embedder(self):
        """Create embedder for quality tests."""
        reset_embedder()
        yield LocalEmbedder()
        reset_embedder()

    def test_similar_texts_have_high_similarity(self, embedder):
        """Similar texts should have high cosine similarity."""
        import numpy as np

        text1 = "The weather is lovely today"
        text2 = "It's a beautiful day outside"
        text3 = "Machine learning algorithms"

        vec1 = np.array(embedder.embed_text(text1))
        vec2 = np.array(embedder.embed_text(text2))
        vec3 = np.array(embedder.embed_text(text3))

        # Cosine similarity (vectors are normalized)
        sim_12 = np.dot(vec1, vec2)
        sim_13 = np.dot(vec1, vec3)

        # Similar texts should have higher similarity
        assert sim_12 > sim_13
        assert sim_12 > 0.5  # Should be reasonably high

    def test_embeddings_are_normalized(self, embedder):
        """Embeddings should be normalized for cosine similarity."""
        import numpy as np

        vector = np.array(embedder.embed_text("Test normalization"))
        norm = np.linalg.norm(vector)

        assert abs(norm - 1.0) < 0.001  # Should be unit vector
```

### Integration with Storage (Story 1.5)

**Qdrant Vector Format:**

The embeddings from this module are used directly with Qdrant storage:

```python
# Integration example (for Story 2.6)
from src.embeddings import get_embedder
from src.storage.qdrant import QdrantClient

embedder = get_embedder()
qdrant = QdrantClient()

# Embed chunks and store
for chunk in chunks:
    vector = embedder.embed_text(chunk.content)
    qdrant.upsert(
        collection="chunks",
        id=chunk.id,
        vector=vector,
        payload={
            "source_id": chunk.source_id,
            "chunk_id": chunk.id,
            "type": "chunk"
        }
    )
```

### Performance Considerations

**First Load Latency:**
- Model download on first use (~90MB for all-MiniLM-L6-v2)
- After caching: ~2-3 seconds to load into memory

**Batch Processing:**
- Default batch size 32 optimizes memory/speed tradeoff
- Progress bar enabled for batches > 32 items
- Single batch encode is more efficient than multiple single encodes

**Memory Usage:**
- Model uses ~400MB RAM when loaded
- Keep single instance via `get_embedder()` to minimize memory

### Sentence-Transformers API Reference

**Current Version:** sentence-transformers >= 5.0

**Key Methods Used:**
```python
# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Encode single or batch
embeddings = model.encode(
    sentences,                    # str or list[str]
    batch_size=32,               # for batches
    normalize_embeddings=True,   # unit vectors for cosine
    show_progress_bar=True       # for large batches
)

# Get dimension
dim = model.get_sentence_embedding_dimension()  # Returns 384
```

### Project Structure Notes

- File location: `packages/pipeline/src/embeddings/local_embedder.py`
- Module exports: `packages/pipeline/src/embeddings/__init__.py`
- Tests: `packages/pipeline/tests/test_embeddings/test_local_embedder.py`
- Aligned with architecture: All embedding code in `packages/pipeline/`
- Follow NFR3: Zero external embedding API costs

### Predecessor Story Intelligence

**From Epic 1 Stories (Foundation):**
- Story 1.1 installed `sentence-transformers>=5.0` dependency
- Story 1.3 established Pydantic model patterns
- Story 1.4/1.5 established exception patterns with `KnowledgeError` base
- Logging with structlog pattern already established

**Patterns to Follow:**
- Exception classes inherit from `KnowledgeError`
- All exceptions include `code`, `message`, `details`
- Use structlog for all logging
- Pydantic models for configuration
- Tests mirror src structure

**From Story 2.4 (Text Chunking Processor):**
- Chunk model will have `content: str` field
- Each chunk needs embedding for Qdrant storage
- Token count estimate already calculated in chunker

### Architecture Compliance Checklist

- [x] File in `packages/pipeline/src/embeddings/local_embedder.py` (architecture.md:636-640)
- [x] Uses all-MiniLM-L6-v2 model (architecture.md:299-307)
- [x] Returns 384-dimensional vectors (architecture.md:299)
- [x] Singleton pattern for model reuse (NFR3 cost efficiency)
- [x] Zero external API costs satisfied (NFR3)
- [x] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [x] Structured error format: `{code, message, details}`
- [x] Uses structlog for logging (architecture.md:535-542)
- [x] Pydantic model for `EmbeddingConfig`
- [x] Tests in `packages/pipeline/tests/test_embeddings/`
- [x] Thread-safe singleton with locking

### References

- [Source: epics.md#Story-2.5] - Story acceptance criteria (lines 336-349)
- [Source: architecture.md#Qdrant-Configuration] - Vector size 384, Cosine distance (lines 299-307)
- [Source: architecture.md#NFR3] - Zero external LLM/embedding API costs (lines 309-314)
- [Source: architecture.md#Project-Structure] - File locations (lines 636-640)
- [Source: architecture.md#Implementation-Patterns] - Naming patterns (lines 410-435)
- [Source: architecture.md#Error-Handling-Pattern] - Exception pattern (lines 545-560)
- [Source: project-context.md#Embeddings] - Model and dimension specs
- [Source: sentence-transformers docs] - API reference for encode method
- [Source: Story 2.1] - Exception pattern from adapters

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- All 16 embedding tests pass
- Full test suite (330 tests) passes with no regressions
- Linting passes: `uv run ruff check src/embeddings/ tests/test_embeddings/` - All checks passed

### Completion Notes List

- Implemented LocalEmbedder class with lazy model loading and thread-safe singleton pattern
- Created EmbeddingConfig Pydantic model with architecture-specified defaults (all-MiniLM-L6-v2, 384d, batch_size=32)
- Implemented embed_text() for single text and embed_batch() for multiple texts
- Created exception hierarchy: EmbeddingError > ModelLoadError, EmbeddingGenerationError (all inherit from KnowledgeError)
- Added module-level get_embedder() factory function for singleton access
- Added reset_embedder() for testing purposes
- Created comprehensive unit tests covering: dimensions, batch processing, singleton behavior, error handling, embedding quality (semantic similarity), normalization verification
- All tests confirm embeddings are properly normalized (unit vectors) for cosine similarity
- Verified NFR3 compliance: zero external API costs - all embeddings generated locally

### Change Log

- 2025-12-30: Story 2.5 implementation complete - Local Embedding Generator with all-MiniLM-L6-v2
- 2025-12-30: Senior Developer Review completed - 6 issues fixed (3 HIGH, 3 MEDIUM)

### File List

- packages/pipeline/src/embeddings/__init__.py (CREATE)
- packages/pipeline/src/embeddings/local_embedder.py (CREATE, then MODIFIED in review)
- packages/pipeline/tests/test_embeddings/__init__.py (CREATE)
- packages/pipeline/tests/test_embeddings/conftest.py (CREATE)
- packages/pipeline/tests/test_embeddings/test_local_embedder.py (CREATE, then MODIFIED in review)

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.5
**Date:** 2025-12-30
**Outcome:** APPROVED (after fixes)

### Issues Found and Fixed

| # | Severity | Issue | Fix Applied |
|---|----------|-------|-------------|
| 1 | HIGH | `embed_batch()` returned wrong count when input contained empty strings (tracked indices but didn't use them) | Changed to raise error on ANY empty text for API consistency |
| 2 | HIGH | `ModelLoadError` was swallowed and re-wrapped as `EmbeddingGenerationError` | Added explicit `except ModelLoadError: raise` before generic catch |
| 3 | HIGH | `ModelLoadError` had zero test coverage | Added `TestExceptionHierarchy` and `TestModelLoadError` test classes (10 new tests) |
| 4 | MEDIUM | `get_embedder()` silently ignored config on subsequent calls | Added warning log when config is passed but singleton exists |
| 5 | MEDIUM | Silent truncation for long texts (256 token limit) | Added `max_tokens` config field and warning log when text exceeds limit |
| 6 | MEDIUM | `model` property had unnecessary lock contention pattern | Simplified to directly call `_load_model()` which handles locking internally |

### Low Priority Issues (Not Fixed - Documentation Only)

| # | Severity | Issue | Notes |
|---|----------|-------|-------|
| 7 | LOW | Type hint `list[str]` allows None values in practice | Behavior is consistent - None treated as empty |
| 8 | LOW | `EmbeddingError` base class not directly tested | Covered indirectly by subclass tests |

### Test Results After Fixes

- **Embedding tests:** 26 passed (was 16, added 10 new tests)
- **Full suite:** 347 passed, 2 failed (pre-existing docling PPTX failures, unrelated)
- **Linting:** All checks passed

### Acceptance Criteria Verification

| AC | Status | Evidence |
|----|--------|----------|
| 384-dimensional vector returned | PASS | `test_embed_text_returns_384_dimensions` |
| Model loaded once and reused | PASS | `test_model_loaded_once`, `test_singleton_model_shared` |
| Batch embedding supported | PASS | `test_embed_batch_returns_correct_count` |
| NFR3 satisfied (zero external API costs) | PASS | All embeddings generated locally with sentence-transformers |
