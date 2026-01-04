"""Tests for the NomicEmbedder wrapper class.

Tests verify:
- Correct model loading and configuration
- Document embedding with search_document prefix
- Query embedding with search_query prefix
- Token counting accuracy
- Vector dimension correctness (768d)
"""

import pytest

from src.config import EMBEDDING_CONFIG
from src.processors.embedder import NomicEmbedder, get_embedder


class TestNomicEmbedder:
    """Test suite for NomicEmbedder class."""

    @pytest.fixture
    def embedder(self):
        """Create a NomicEmbedder instance for testing."""
        return NomicEmbedder()

    def test_embedder_initialization(self, embedder):
        """Test that embedder initializes with correct configuration."""
        assert embedder.vector_size == 768
        assert embedder.max_tokens == 8192
        assert embedder.model is not None

    def test_embed_single_document(self, embedder):
        """Test embedding a single document produces 768d vector."""
        text = "RAG systems combine retrieval with generation for better AI responses."
        vector = embedder.embed_document(text)

        assert isinstance(vector, list)
        assert len(vector) == 768
        assert all(isinstance(v, float) for v in vector)

    def test_embed_multiple_documents(self, embedder):
        """Test embedding multiple documents produces correct vectors."""
        texts = [
            "Document about machine learning.",
            "Document about natural language processing.",
            "Document about vector databases.",
        ]
        vectors = embedder.embed_documents(texts)

        assert len(vectors) == 3
        for vector in vectors:
            assert len(vector) == 768

    def test_embed_empty_list(self, embedder):
        """Test embedding empty list returns empty list."""
        vectors = embedder.embed_documents([])
        assert vectors == []

    def test_embed_query(self, embedder):
        """Test query embedding produces 768d vector."""
        query = "What is RAG?"
        vector = embedder.embed_query(query)

        assert isinstance(vector, list)
        assert len(vector) == 768
        assert all(isinstance(v, float) for v in vector)

    def test_query_and_document_embeddings_different(self, embedder):
        """Test that query and document embeddings for same text differ.

        nomic-embed-text uses different prefixes for queries and documents,
        which should produce different embeddings for the same text.
        """
        text = "RAG architecture patterns"

        doc_vector = embedder.embed_document(text)
        query_vector = embedder.embed_query(text)

        # Vectors should be different due to different prefixes
        assert doc_vector != query_vector

    def test_count_tokens(self, embedder):
        """Test token counting returns positive integer."""
        text = "This is a test sentence for token counting."
        token_count = embedder.count_tokens(text)

        assert isinstance(token_count, int)
        assert token_count > 0
        # A simple sentence should be less than 20 tokens
        assert token_count < 20

    def test_count_tokens_empty_string(self, embedder):
        """Test token counting on empty string returns 0."""
        token_count = embedder.count_tokens("")
        assert token_count == 0

    def test_count_tokens_long_text(self, embedder):
        """Test token counting on longer text."""
        # Generate text that should be ~100 tokens
        text = "This is a test. " * 50
        token_count = embedder.count_tokens(text)

        # Should be roughly 50-200 tokens for this text
        assert token_count > 50
        assert token_count < 300

    def test_get_max_tokens(self, embedder):
        """Test max tokens returns 8192."""
        assert embedder.get_max_tokens() == 8192

    def test_get_vector_size(self, embedder):
        """Test vector size returns 768."""
        assert embedder.get_vector_size() == 768

    def test_embed_for_clustering(self, embedder):
        """Test clustering embeddings produce 768d vectors."""
        texts = ["Text for clustering A", "Text for clustering B"]
        vectors = embedder.embed_for_clustering(texts)

        assert len(vectors) == 2
        for vector in vectors:
            assert len(vector) == 768

    def test_embed_for_clustering_empty(self, embedder):
        """Test clustering embedding on empty list returns empty list."""
        vectors = embedder.embed_for_clustering([])
        assert vectors == []


class TestEmbedderSingleton:
    """Test suite for the get_embedder singleton function."""

    def test_get_embedder_returns_instance(self):
        """Test get_embedder returns a NomicEmbedder instance."""
        embedder = get_embedder()
        assert isinstance(embedder, NomicEmbedder)

    def test_get_embedder_returns_same_instance(self):
        """Test get_embedder returns the same instance on multiple calls."""
        embedder1 = get_embedder()
        embedder2 = get_embedder()
        assert embedder1 is embedder2


class TestEmbeddingConfig:
    """Test suite for embedding configuration."""

    def test_config_has_required_fields(self):
        """Test EMBEDDING_CONFIG has all required fields."""
        assert "model_id" in EMBEDDING_CONFIG
        assert "vector_size" in EMBEDDING_CONFIG
        assert "max_tokens" in EMBEDDING_CONFIG
        assert "trust_remote_code" in EMBEDDING_CONFIG
        assert "prefixes" in EMBEDDING_CONFIG

    def test_config_values(self):
        """Test EMBEDDING_CONFIG has correct values."""
        assert EMBEDDING_CONFIG["model_id"] == "nomic-ai/nomic-embed-text-v1.5"
        assert EMBEDDING_CONFIG["vector_size"] == 768
        assert EMBEDDING_CONFIG["max_tokens"] == 8192
        assert EMBEDDING_CONFIG["trust_remote_code"] is True

    def test_prefixes_defined(self):
        """Test instruction prefixes are defined."""
        prefixes = EMBEDDING_CONFIG["prefixes"]
        assert prefixes["document"] == "search_document: "
        assert prefixes["query"] == "search_query: "
        assert prefixes["clustering"] == "clustering: "
        assert prefixes["classification"] == "classification: "
