"""Tests for local embedding generation."""

import pytest
import numpy as np

from src.embeddings import (
    LocalEmbedder,
    EmbeddingConfig,
    EmbeddingError,
    EmbeddingGenerationError,
    ModelLoadError,
    get_embedder,
    reset_embedder,
)


class TestLocalEmbedder:
    """Tests for LocalEmbedder class."""

    def test_embed_text_returns_384_dimensions(self, embedder):
        """Single text embedding should return 384-dimensional vector."""
        vector = embedder.embed_text("Hello, world!")

        assert isinstance(vector, list)
        assert len(vector) == 384
        assert all(isinstance(v, float) for v in vector)

    def test_embed_batch_returns_correct_count(self, embedder):
        """Batch embedding should return one vector per input."""
        texts = ["First text", "Second text", "Third text"]
        vectors = embedder.embed_batch(texts)

        assert len(vectors) == 3
        assert all(len(v) == 384 for v in vectors)

    def test_embed_empty_text_raises_error(self, embedder):
        """Empty text should raise EmbeddingGenerationError."""
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            embedder.embed_text("")

        assert exc_info.value.code == "EMBEDDING_GENERATION_ERROR"
        assert "empty" in exc_info.value.message.lower()

    def test_embed_whitespace_only_raises_error(self, embedder):
        """Whitespace-only text should raise error."""
        with pytest.raises(EmbeddingGenerationError):
            embedder.embed_text("   \n\t  ")

    def test_embed_batch_empty_list_returns_empty(self, embedder):
        """Empty batch should return empty list."""
        vectors = embedder.embed_batch([])

        assert vectors == []

    def test_embed_batch_all_empty_texts_raises_error(self, embedder):
        """Batch with all empty texts should raise error at first empty."""
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            embedder.embed_batch(["", "   ", "\t\n"])

        assert "empty" in exc_info.value.message.lower()
        assert "index 0" in exc_info.value.message.lower()

    def test_embed_batch_with_mixed_empty_raises_error(self, embedder):
        """Batch with any empty text should raise error."""
        with pytest.raises(EmbeddingGenerationError) as exc_info:
            embedder.embed_batch(["hello", "", "world"])

        assert "empty" in exc_info.value.message.lower()
        assert "index 1" in exc_info.value.message.lower()

    def test_get_dimension_returns_384(self, embedder):
        """get_dimension should return 384."""
        assert embedder.get_dimension() == 384

    def test_model_loaded_once(self, embedder):
        """Model should only be loaded once per instance."""
        # First call loads model
        _ = embedder.embed_text("First")
        model_id_1 = id(embedder._model)

        # Second call reuses model
        _ = embedder.embed_text("Second")
        model_id_2 = id(embedder._model)

        assert model_id_1 == model_id_2

    def test_custom_config(self, custom_config):
        """Custom config should be respected."""
        embedder = LocalEmbedder(custom_config)

        assert embedder.config.batch_size == 16
        assert embedder.config.show_progress is False
        assert embedder.config.model_name == "all-MiniLM-L6-v2"


class TestSingletonPattern:
    """Tests for module-level singleton."""

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

    def test_similar_texts_have_high_similarity(self, embedder):
        """Similar texts should have high cosine similarity."""
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
        vector = np.array(embedder.embed_text("Test normalization"))
        norm = np.linalg.norm(vector)

        assert abs(norm - 1.0) < 0.001  # Should be unit vector


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig model."""

    def test_default_config_values(self):
        """Default config should have expected values."""
        config = EmbeddingConfig()

        assert config.model_name == "all-MiniLM-L6-v2"
        assert config.embedding_dimension == 384
        assert config.batch_size == 32
        assert config.show_progress is True
        assert config.normalize_embeddings is True

    def test_config_custom_values(self):
        """Custom config values should be applied."""
        config = EmbeddingConfig(
            model_name="custom-model",
            embedding_dimension=768,
            batch_size=64,
            show_progress=False,
            normalize_embeddings=False,
        )

        assert config.model_name == "custom-model"
        assert config.embedding_dimension == 768
        assert config.batch_size == 64
        assert config.show_progress is False
        assert config.normalize_embeddings is False

    def test_config_max_tokens_default(self):
        """Default max_tokens should be 256."""
        config = EmbeddingConfig()
        assert config.max_tokens == 256


class TestExceptionHierarchy:
    """Tests for exception classes and inheritance."""

    def test_embedding_error_inherits_from_knowledge_error(self):
        """EmbeddingError should inherit from KnowledgeError."""
        from src.exceptions import KnowledgeError
        assert issubclass(EmbeddingError, KnowledgeError)

    def test_model_load_error_inherits_from_embedding_error(self):
        """ModelLoadError should inherit from EmbeddingError."""
        assert issubclass(ModelLoadError, EmbeddingError)

    def test_embedding_generation_error_inherits_from_embedding_error(self):
        """EmbeddingGenerationError should inherit from EmbeddingError."""
        assert issubclass(EmbeddingGenerationError, EmbeddingError)

    def test_model_load_error_has_correct_attributes(self):
        """ModelLoadError should have code, message, and details."""
        error = ModelLoadError("test-model", "connection failed")

        assert error.code == "MODEL_LOAD_ERROR"
        assert "test-model" in error.message
        assert "connection failed" in error.message
        assert error.details["model_name"] == "test-model"
        assert error.details["reason"] == "connection failed"

    def test_model_load_error_to_dict(self):
        """ModelLoadError should serialize to API response format."""
        error = ModelLoadError("test-model", "timeout")
        result = error.to_dict()

        assert "error" in result
        assert result["error"]["code"] == "MODEL_LOAD_ERROR"
        assert "test-model" in result["error"]["message"]

    def test_embedding_generation_error_has_correct_attributes(self):
        """EmbeddingGenerationError should have code, message, and details."""
        error = EmbeddingGenerationError("encoding failed", text_length=100)

        assert error.code == "EMBEDDING_GENERATION_ERROR"
        assert "encoding failed" in error.message
        assert error.details["reason"] == "encoding failed"
        assert error.details["text_length"] == 100


class TestModelLoadError:
    """Tests for model loading failure scenarios."""

    def test_invalid_model_raises_model_load_error(self):
        """Invalid model name should raise ModelLoadError."""
        config = EmbeddingConfig(model_name="non-existent-model-xyz-123")
        embedder = LocalEmbedder(config)

        with pytest.raises(ModelLoadError) as exc_info:
            embedder.embed_text("test")

        assert exc_info.value.code == "MODEL_LOAD_ERROR"
        assert "non-existent-model-xyz-123" in exc_info.value.message

    def test_model_load_error_not_swallowed_in_embed_batch(self):
        """ModelLoadError should not be swallowed in embed_batch."""
        config = EmbeddingConfig(model_name="non-existent-model-xyz-456")
        embedder = LocalEmbedder(config)

        with pytest.raises(ModelLoadError) as exc_info:
            embedder.embed_batch(["test1", "test2"])

        assert exc_info.value.code == "MODEL_LOAD_ERROR"
