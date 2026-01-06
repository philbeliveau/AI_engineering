"""Tests for EmbeddingService.

Tests embedding generation using FastEmbed (ONNX) with nomic-embed-text-v1.5 model.
Produces 768-dimensional vectors with 8K token context.
"""


class TestEmbeddingService:
    """Tests for EmbeddingService class."""

    def test_embedding_service_import(self):
        """Test that EmbeddingService can be imported."""
        from src.embeddings.embedding_service import EmbeddingService

        assert EmbeddingService is not None

    def test_embedding_service_initialization(self):
        """Test that EmbeddingService can be initialized."""
        from src.embeddings.embedding_service import EmbeddingService

        service = EmbeddingService()
        assert service is not None

    def test_embed_query_returns_list(self):
        """Test that embed_query returns a list of floats."""
        from src.embeddings.embedding_service import EmbeddingService

        service = EmbeddingService()
        result = service.embed_query("test query")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(x, float) for x in result)

    def test_embed_query_returns_768_dimensions(self):
        """Test that embed_query returns exactly 768 dimensions (nomic-embed-text-v1.5)."""
        from src.embeddings.embedding_service import EmbeddingService

        service = EmbeddingService()
        result = service.embed_query("test query for embedding")
        assert len(result) == 768

    def test_embed_query_different_texts_produce_different_vectors(self):
        """Test that different texts produce different embedding vectors."""
        from src.embeddings.embedding_service import EmbeddingService

        service = EmbeddingService()
        result1 = service.embed_query("hello world")
        result2 = service.embed_query("completely different topic about databases")
        assert result1 != result2

    def test_embed_query_same_text_produces_same_vector(self):
        """Test that same text produces same embedding vector."""
        from src.embeddings.embedding_service import EmbeddingService

        service = EmbeddingService()
        result1 = service.embed_query("consistent embedding test")
        result2 = service.embed_query("consistent embedding test")
        assert result1 == result2


class TestGetEmbeddingModel:
    """Tests for get_embedding_model singleton function."""

    def test_get_embedding_model_import(self):
        """Test that get_embedding_model can be imported."""
        from src.embeddings.embedding_service import get_embedding_model

        assert get_embedding_model is not None
        assert callable(get_embedding_model)

    def test_get_embedding_model_returns_model(self):
        """Test that get_embedding_model returns a TextEmbedding model."""
        from fastembed import TextEmbedding

        from src.embeddings.embedding_service import get_embedding_model

        model = get_embedding_model()
        assert isinstance(model, TextEmbedding)

    def test_get_embedding_model_is_singleton(self):
        """Test that get_embedding_model returns the same instance."""
        from src.embeddings.embedding_service import get_embedding_model

        model1 = get_embedding_model()
        model2 = get_embedding_model()
        assert model1 is model2


class TestEmbedQueryFunction:
    """Tests for embed_query standalone function."""

    def test_embed_query_function_import(self):
        """Test that embed_query function can be imported."""
        from src.embeddings.embedding_service import embed_query

        assert embed_query is not None
        assert callable(embed_query)

    def test_embed_query_function_returns_768_dimensions(self):
        """Test that embed_query function returns 768 dimensions (nomic-embed-text-v1.5)."""
        from src.embeddings.embedding_service import embed_query

        result = embed_query("test query")
        assert len(result) == 768

    def test_embed_query_function_is_sync(self):
        """Test that embed_query is a sync function (not async)."""
        import inspect

        from src.embeddings.embedding_service import embed_query

        assert not inspect.iscoroutinefunction(embed_query)
