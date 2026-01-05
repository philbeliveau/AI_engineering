"""Unit tests for DoclingChunker processor."""

from pathlib import Path

import pytest

from src.adapters import DoclingAdapter
from src.processors import (
    DoclingChunker,
    ChunkerConfig,
    ChunkOutput,
    ChunkerError,
    EmptyContentError,
    ChunkSizeError,
    MissingDoclingDocumentError,
    EMBED_MODEL_ID,
)


class TestChunkerConfig:
    """Tests for ChunkerConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ChunkerConfig()
        assert config.chunk_size == 512
        assert config.merge_peers is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ChunkerConfig(chunk_size=256, merge_peers=False)
        assert config.chunk_size == 256
        assert config.merge_peers is False

    def test_config_validation_min_chunk_size(self):
        """Test that chunk_size has minimum validation."""
        with pytest.raises(ValueError):
            ChunkerConfig(chunk_size=10)  # Below minimum of 50

    def test_config_validation_max_chunk_size(self):
        """Test that chunk_size has maximum validation."""
        with pytest.raises(ValueError):
            ChunkerConfig(chunk_size=3000)  # Above maximum of 2048


class TestChunkOutput:
    """Tests for ChunkOutput model."""

    def test_default_id_generation(self):
        """Test that ID is auto-generated as UUID."""
        chunk = ChunkOutput(
            source_id="test-source",
            content="Test content",
            token_count=5,
        )
        assert chunk.id is not None
        assert len(chunk.id) == 36  # UUID format
        assert "-" in chunk.id

    def test_chunk_fields(self):
        """Test that all fields are set correctly."""
        chunk = ChunkOutput(
            id="custom-id",
            source_id="source-123",
            content="Test content here",
            position={"chunk_index": 0, "section": "intro"},
            token_count=10,
        )
        assert chunk.id == "custom-id"
        assert chunk.source_id == "source-123"
        assert chunk.content == "Test content here"
        assert chunk.position == {"chunk_index": 0, "section": "intro"}
        assert chunk.token_count == 10
        assert chunk.schema_version == "1.0"

    def test_chunk_mongodb_compatible(self):
        """Test that ChunkOutput can be serialized for MongoDB."""
        chunk = ChunkOutput(
            source_id="source-123",
            content="Test content",
            token_count=5,
        )
        # Should be serializable to dict
        chunk_dict = chunk.model_dump()
        assert "id" in chunk_dict
        assert "source_id" in chunk_dict
        assert "content" in chunk_dict
        assert "position" in chunk_dict
        assert "token_count" in chunk_dict
        assert "schema_version" in chunk_dict


class TestDoclingChunkerInit:
    """Tests for DoclingChunker initialization."""

    def test_default_initialization(self, chunker):
        """Test default chunker initialization."""
        assert chunker.config.chunk_size == 512
        assert chunker.config.merge_peers is True

    def test_custom_config_initialization(self):
        """Test chunker with custom config."""
        config = ChunkerConfig(chunk_size=256, merge_peers=False)
        chunker = DoclingChunker(config)
        assert chunker.config.chunk_size == 256
        assert chunker.config.merge_peers is False

    def test_tokenizer_initialized(self, chunker):
        """Test that tokenizer is properly initialized."""
        assert chunker._hf_tokenizer is not None
        assert chunker._tokenizer is not None
        assert chunker._chunker is not None


class TestDoclingChunkerTokenCounting:
    """Tests for accurate token counting."""

    def test_count_tokens_simple(self, chunker):
        """Test token counting for simple text."""
        text = "Hello world"
        token_count = chunker.count_tokens(text)
        assert token_count > 0
        assert isinstance(token_count, int)

    def test_count_tokens_longer_text(self, chunker):
        """Test token counting for longer text."""
        text = "The quick brown fox jumps over the lazy dog. " * 10
        token_count = chunker.count_tokens(text)
        # Should be proportional to text length
        assert token_count > 50

    def test_count_tokens_consistent(self, chunker):
        """Test that token counting is consistent."""
        text = "Consistent token counting test"
        count1 = chunker.count_tokens(text)
        count2 = chunker.count_tokens(text)
        assert count1 == count2

    def test_count_tokens_uses_embedding_model(self, chunker):
        """Test that we're using the correct embedding model tokenizer."""
        # This is the model specified in the architecture (updated to nomic-embed-text-v1.5)
        assert EMBED_MODEL_ID == "nomic-ai/nomic-embed-text-v1.5"


class TestDoclingChunkerExceptions:
    """Tests for chunker exception handling."""

    def test_missing_docling_document_error(self, chunker):
        """Test MissingDoclingDocumentError when document is None."""
        with pytest.raises(MissingDoclingDocumentError) as exc_info:
            chunker.chunk_document(None, "test-source")

        error = exc_info.value
        assert error.code == "MISSING_DOCLING_DOCUMENT"
        assert "test-source" in str(error.details)

    def test_missing_docling_document_from_adapter_result(self, chunker):
        """Test error when adapter result lacks DoclingDocument."""

        class MockAdapterResult:
            metadata = {}

        with pytest.raises(MissingDoclingDocumentError):
            chunker.chunk_from_adapter_result(MockAdapterResult(), "test-source")

    def test_empty_content_error_format(self):
        """Test EmptyContentError structure."""
        error = EmptyContentError("test-source")
        assert error.code == "EMPTY_CONTENT"
        assert "test-source" in str(error.details)

    def test_chunk_size_error_format(self):
        """Test ChunkSizeError structure."""
        config = ChunkerConfig()
        error = ChunkSizeError("test reason", config)
        assert error.code == "INVALID_CHUNK_SIZE"
        assert "test reason" in error.message
        assert "config" in error.details

    def test_chunker_error_inheritance(self):
        """Test that all chunker errors inherit from ChunkerError."""
        assert issubclass(EmptyContentError, ChunkerError)
        assert issubclass(ChunkSizeError, ChunkerError)
        assert issubclass(MissingDoclingDocumentError, ChunkerError)


class TestDoclingChunkerWithDocuments:
    """Integration tests for chunking actual documents."""

    def test_chunk_markdown_document(self, chunker, sample_markdown_for_chunking):
        """Test chunking a markdown document via DoclingAdapter."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)

        # Get DoclingDocument from metadata
        docling_doc = result.metadata.get("_docling_document")
        assert docling_doc is not None

        # Chunk the document
        chunks = chunker.chunk_document(docling_doc, source_id="md-test-001")

        # Should produce multiple chunks
        assert len(chunks) > 0

        # All chunks should have required fields
        for chunk in chunks:
            assert isinstance(chunk, ChunkOutput)
            assert chunk.source_id == "md-test-001"
            assert chunk.content
            assert chunk.token_count > 0
            assert "chunk_index" in chunk.position
            assert chunk.schema_version == "1.0"

    def test_chunk_short_document(self, chunker, sample_short_markdown):
        """Test chunking a short document that fits in one chunk."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_short_markdown)

        docling_doc = result.metadata.get("_docling_document")
        chunks = chunker.chunk_document(docling_doc, source_id="short-doc")

        # Short document might produce 1 or a few chunks
        assert len(chunks) >= 1

        # Content should be preserved
        total_content = " ".join(c.content for c in chunks)
        assert "Quick Note" in total_content or "brief note" in total_content

    def test_chunk_from_adapter_result_convenience(
        self, chunker, sample_markdown_for_chunking
    ):
        """Test the convenience method chunk_from_adapter_result."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)

        # Use convenience method
        chunks = chunker.chunk_from_adapter_result(result, source_id="conv-test")

        assert len(chunks) > 0
        assert all(c.source_id == "conv-test" for c in chunks)

    def test_token_counts_accurate(self, chunker, sample_markdown_for_chunking):
        """Test that token counts match actual tokenizer output."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)

        docling_doc = result.metadata.get("_docling_document")
        chunks = chunker.chunk_document(docling_doc, source_id="token-test")

        # Verify token counts match
        for chunk in chunks:
            actual_tokens = chunker.count_tokens(chunk.content)
            assert (
                chunk.token_count == actual_tokens
            ), f"Token count mismatch: {chunk.token_count} vs {actual_tokens}"

    def test_chunk_position_metadata(self, chunker, sample_markdown_for_chunking):
        """Test that position metadata is preserved."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)

        docling_doc = result.metadata.get("_docling_document")
        chunks = chunker.chunk_document(docling_doc, source_id="pos-test")

        # Check chunk indices are sequential
        indices = [c.position.get("chunk_index") for c in chunks]
        expected_indices = list(range(len(chunks)))
        assert indices == expected_indices


class TestDoclingChunkerConfiguration:
    """Tests for different chunker configurations."""

    def test_small_chunk_size_more_chunks(self, sample_markdown_for_chunking):
        """Test that smaller chunk size produces more chunks."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)
        docling_doc = result.metadata.get("_docling_document")

        # Default chunker (512 tokens)
        default_chunker = DoclingChunker()
        default_chunks = default_chunker.chunk_document(docling_doc, "test")

        # Small chunker (128 tokens)
        small_chunker = DoclingChunker(ChunkerConfig(chunk_size=128))
        small_chunks = small_chunker.chunk_document(docling_doc, "test")

        # Smaller chunk size should produce more chunks (if document is large enough)
        # Note: This depends on document size and HybridChunker behavior
        assert len(small_chunks) >= len(default_chunks)

    def test_merge_peers_configuration(self, sample_markdown_for_chunking):
        """Test merge_peers configuration affects chunking."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)
        docling_doc = result.metadata.get("_docling_document")

        # With merge_peers=True (default)
        chunker_merge = DoclingChunker(ChunkerConfig(merge_peers=True))
        chunks_merge = chunker_merge.chunk_document(docling_doc, "test")

        # With merge_peers=False
        chunker_no_merge = DoclingChunker(ChunkerConfig(merge_peers=False))
        chunks_no_merge = chunker_no_merge.chunk_document(docling_doc, "test")

        # Both should produce valid chunks
        assert len(chunks_merge) > 0
        assert len(chunks_no_merge) > 0


class TestDoclingChunkerPdfDocument:
    """Tests for PDF document chunking."""

    def test_chunk_pdf_document(self, chunker, sample_pdf_for_chunking):
        """Test chunking a PDF document."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_pdf_for_chunking)

        docling_doc = result.metadata.get("_docling_document")
        assert docling_doc is not None, "DoclingDocument should be in metadata"

        chunks = chunker.chunk_document(docling_doc, source_id="pdf-test")

        # Minimal PDFs may produce no text content, which raises EmptyContentError
        # If we get here, we have chunks - validate them properly
        assert isinstance(chunks, list), "Should return a list of chunks"

        for chunk in chunks:
            assert chunk.source_id == "pdf-test"
            assert chunk.token_count > 0, "Each chunk should have positive token count"
            assert chunk.content, "Each chunk should have content"


class TestDoclingChunkerChunkSizeValidation:
    """Tests for ChunkSizeError being raised from DoclingChunker."""

    def test_chunk_size_error_raised_for_invalid_config(self):
        """Test that ChunkSizeError is raised when bypassing Pydantic validation."""
        # Use model_construct to bypass Pydantic validation
        invalid_config = ChunkerConfig.model_construct(chunk_size=10, merge_peers=True)

        with pytest.raises(ChunkSizeError) as exc_info:
            DoclingChunker(invalid_config)

        error = exc_info.value
        assert error.code == "INVALID_CHUNK_SIZE"
        assert "50" in error.message  # Should mention minimum

    def test_chunk_size_error_for_too_large(self):
        """Test that ChunkSizeError is raised for chunk_size > 2048."""
        invalid_config = ChunkerConfig.model_construct(chunk_size=5000, merge_peers=True)

        with pytest.raises(ChunkSizeError) as exc_info:
            DoclingChunker(invalid_config)

        error = exc_info.value
        assert error.code == "INVALID_CHUNK_SIZE"
        assert "2048" in error.message


class TestDoclingChunkerEmptyDocument:
    """Integration tests for empty document handling."""

    def test_empty_docling_document_raises_error(self, chunker):
        """Test that chunking an empty DoclingDocument raises EmptyContentError."""
        from docling_core.types.doc import DoclingDocument

        empty_doc = DoclingDocument(name="empty")

        with pytest.raises(EmptyContentError) as exc_info:
            chunker.chunk_document(empty_doc, source_id="empty-test")

        error = exc_info.value
        assert error.code == "EMPTY_CONTENT"
        assert "empty-test" in str(error.details)

    def test_empty_markdown_file_raises_error(self, chunker, tmp_path):
        """Test that an empty markdown file raises EmptyContentError."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        adapter = DoclingAdapter()
        result = adapter.extract_text(empty_file)

        docling_doc = result.metadata.get("_docling_document")
        if docling_doc is not None:
            with pytest.raises(EmptyContentError):
                chunker.chunk_document(docling_doc, source_id="empty-md")


class TestDoclingChunkerPositionMetadata:
    """Tests for architecture-compliant position metadata."""

    def test_position_includes_chapter_and_section(self, chunker, tmp_path):
        """Test that position metadata includes chapter and section fields."""
        content = """# Chapter One

Introduction text here.

## Section 1.1

Details about section 1.1.
"""
        md_file = tmp_path / "structured.md"
        md_file.write_text(content)

        adapter = DoclingAdapter()
        result = adapter.extract_text(md_file)
        docling_doc = result.metadata.get("_docling_document")

        chunks = chunker.chunk_document(docling_doc, source_id="pos-test")

        # Find a chunk that has section hierarchy
        chunks_with_section = [c for c in chunks if "section" in c.position]
        if chunks_with_section:
            chunk = chunks_with_section[0]
            assert "chapter" in chunk.position
            assert "section" in chunk.position
            assert chunk.position["chapter"] == "Chapter One"

    def test_position_always_has_chunk_index(self, chunker, sample_markdown_for_chunking):
        """Test that all chunks have chunk_index in position."""
        adapter = DoclingAdapter()
        result = adapter.extract_text(sample_markdown_for_chunking)
        docling_doc = result.metadata.get("_docling_document")

        chunks = chunker.chunk_document(docling_doc, source_id="idx-test")

        for i, chunk in enumerate(chunks):
            assert "chunk_index" in chunk.position
            assert chunk.position["chunk_index"] == i
