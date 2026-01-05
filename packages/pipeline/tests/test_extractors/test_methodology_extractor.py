"""Tests for MethodologyExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    Methodology,
    MethodologyStep,
)
from src.extractors.base import ExtractionLevel
from src.extractors.methodology_extractor import MethodologyExtractor


class TestMethodologyExtractorProperties:
    """Test MethodologyExtractor properties and configuration."""

    def test_instantiation(self):
        """MethodologyExtractor can be instantiated."""
        extractor = MethodologyExtractor()
        assert extractor is not None

    def test_extraction_type_is_methodology(self):
        """MethodologyExtractor has METHODOLOGY extraction type."""
        extractor = MethodologyExtractor()
        assert extractor.extraction_type == ExtractionType.METHODOLOGY

    def test_model_class_is_methodology(self):
        """MethodologyExtractor uses Methodology model class."""
        extractor = MethodologyExtractor()
        assert extractor.model_class == Methodology

    def test_uses_default_config(self):
        """MethodologyExtractor uses default config when none provided."""
        extractor = MethodologyExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """MethodologyExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = MethodologyExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestMethodologyExtractorGetPrompt:
    """Test MethodologyExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = MethodologyExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_methodology_instructions(self):
        """get_prompt contains methodology-specific instructions."""
        extractor = MethodologyExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain methodology-specific content
        assert "methodology" in prompt.lower()
        assert "step" in prompt.lower()


class TestMethodologyExtractorAutoTagTopics:
    """Test MethodologyExtractor topic auto-tagging."""

    def test_auto_tag_topics_from_name(self):
        """auto_tag_topics extracts topics from methodology name."""
        extractor = MethodologyExtractor()
        methodology = Methodology(
            source_id="src-1",
            chunk_id="chunk-1",
            name="RAG Implementation Methodology",
            steps=[
                MethodologyStep(order=1, title="Step 1", description="First step"),
            ],
        )
        topics = extractor.auto_tag_topics(methodology)
        assert "rag" in topics

    def test_auto_tag_topics_from_steps(self):
        """auto_tag_topics extracts topics from steps."""
        extractor = MethodologyExtractor()
        methodology = Methodology(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Model Training",
            steps=[
                MethodologyStep(
                    order=1, title="Prepare embeddings", description="Generate embeddings"
                ),
                MethodologyStep(
                    order=2, title="Fine-tune model", description="Fine-tuning process"
                ),
            ],
        )
        topics = extractor.auto_tag_topics(methodology)
        assert "embeddings" in topics or "fine-tuning" in topics

    def test_auto_tag_topics_limits_to_five(self):
        """auto_tag_topics returns at most 5 topics."""
        extractor = MethodologyExtractor()
        methodology = Methodology(
            source_id="src-1",
            chunk_id="chunk-1",
            name="RAG Fine-tuning with Embeddings",
            steps=[
                MethodologyStep(order=1, title="LLM prompting", description="Prompt the LLM"),
                MethodologyStep(
                    order=2, title="Training", description="Train with evaluation"
                ),
            ],
            prerequisites=["Deployment ready", "Agent setup"],
            outputs=["Inference pipeline"],
        )
        topics = extractor.auto_tag_topics(methodology)
        assert len(topics) <= 5

    def test_auto_tag_topics_returns_empty_when_no_matches(self):
        """auto_tag_topics returns empty list when no topics match."""
        extractor = MethodologyExtractor()
        methodology = Methodology(
            source_id="src-1",
            chunk_id="chunk-1",
            name="General Process",
            steps=[
                MethodologyStep(order=1, title="Step 1", description="Do something"),
            ],
        )
        topics = extractor.auto_tag_topics(methodology)
        assert isinstance(topics, list)


class TestMethodologyExtractorExtract:
    """Test MethodologyExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a methodology."""
        return """
        Building a RAG system requires several key steps. First, prepare
        your document corpus by collecting and cleaning your source
        documents. Next, implement chunking - split documents into
        semantically coherent pieces. Third, generate embeddings using
        a model like all-MiniLM-L6-v2. Finally, store vectors in a
        database like Qdrant. Before starting, ensure you have access
        to your documents. The result is a working retrieval pipeline.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid methodology JSON."""
        return """
        [
            {
                "name": "RAG System Implementation",
                "steps": [
                    {
                        "order": 1,
                        "title": "Prepare Document Corpus",
                        "description": "Collect and clean source documents",
                        "tips": []
                    },
                    {
                        "order": 2,
                        "title": "Implement Chunking",
                        "description": "Split documents into semantic pieces",
                        "tips": ["Keep chunks coherent"]
                    },
                    {
                        "order": 3,
                        "title": "Generate Embeddings",
                        "description": "Use all-MiniLM-L6-v2 model",
                        "tips": []
                    },
                    {
                        "order": 4,
                        "title": "Store Vectors",
                        "description": "Store in Qdrant database",
                        "tips": []
                    }
                ],
                "prerequisites": ["Access to document corpus"],
                "outputs": ["Working retrieval pipeline"],
                "confidence": 0.9
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(self, sample_chunk_content, mock_llm_response):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = MethodologyExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                content=sample_chunk_content,
                source_id="source-456",
                context_level=ExtractionLevel.CHUNK,
                context_id="chunk-123",
                chunk_ids=["chunk-123"],
            )

            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, ExtractionResult) for r in results)

    @pytest.mark.asyncio
    async def test_extract_preserves_source_attribution(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract preserves source_id and chunk_id."""
        extractor = MethodologyExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                content=sample_chunk_content,
                source_id="source-456",
                context_level=ExtractionLevel.CHUNK,
                context_id="chunk-123",
                chunk_ids=["chunk-123"],
            )

            assert results[0].success is True
            methodology = results[0].extraction
            assert methodology.source_id == "source-456"
            assert methodology.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_sets_schema_version(self, sample_chunk_content, mock_llm_response):
        """extract sets schema_version on extraction."""
        extractor = MethodologyExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                content=sample_chunk_content,
                source_id="source-456",
                context_level=ExtractionLevel.CHUNK,
                context_id="chunk-123",
                chunk_ids=["chunk-123"],
            )

            assert results[0].extraction.schema_version == "1.1.0"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_methodologies(self):
        """extract returns empty list when no methodologies found."""
        extractor = MethodologyExtractor()
        no_methodology_response = "[]"

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = no_methodology_response

            results = await extractor.extract(
                content="The sky is blue.",
                source_id="source-456",
                context_level=ExtractionLevel.CHUNK,
                context_id="chunk-123",
                chunk_ids=["chunk-123"],
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_extract_handles_parse_error(self):
        """extract returns error result for unparseable response."""
        extractor = MethodologyExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = "This is not valid JSON"

            results = await extractor.extract(
                content="Some content",
                source_id="source-456",
                context_level=ExtractionLevel.CHUNK,
                context_id="chunk-123",
                chunk_ids=["chunk-123"],
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "parse" in results[0].error.lower()


class TestMethodologyModel:
    """Test Methodology Pydantic model."""

    def test_methodology_required_fields(self):
        """Methodology requires source_id, chunk_id, name."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Methodology",
        )
        assert methodology.source_id == "src-123"
        assert methodology.chunk_id == "chunk-456"
        assert methodology.type == ExtractionType.METHODOLOGY
        assert methodology.schema_version == "1.1.0"

    def test_methodology_with_steps(self):
        """Methodology can contain ordered steps."""
        methodology = Methodology(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Methodology",
            steps=[
                MethodologyStep(order=1, title="Step 1", description="Do first thing"),
                MethodologyStep(order=2, title="Step 2", description="Do second thing"),
            ],
            prerequisites=["Prereq 1"],
            outputs=["Output 1"],
        )
        assert len(methodology.steps) == 2
        assert methodology.steps[0].order == 1
        assert methodology.steps[1].title == "Step 2"

    def test_methodology_step_with_tips(self):
        """MethodologyStep can include tips."""
        step = MethodologyStep(
            order=1,
            title="Chunking",
            description="Split documents",
            tips=["Keep chunks semantic", "Use 500-1000 tokens"],
        )
        assert len(step.tips) == 2

    def test_methodology_has_source_attribution(self):
        """Methodology includes source attribution fields."""
        methodology = Methodology(source_id="src-123", chunk_id="chunk-456", name="Test")
        assert hasattr(methodology, "source_id")
        assert hasattr(methodology, "chunk_id")
        assert hasattr(methodology, "topics")
        assert hasattr(methodology, "schema_version")


class TestMethodologyExtractorRegistration:
    """Test MethodologyExtractor registration with ExtractorRegistry."""

    def test_extractor_can_be_registered(self):
        """MethodologyExtractor can be registered with registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.METHODOLOGY, MethodologyExtractor)

        assert registry.is_supported(ExtractionType.METHODOLOGY)

    def test_extractor_retrieved_from_registry(self):
        """MethodologyExtractor can be retrieved from registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.METHODOLOGY, MethodologyExtractor)

        extractor = registry.get_extractor(ExtractionType.METHODOLOGY)
        assert isinstance(extractor, MethodologyExtractor)

    def test_global_registry_contains_methodology(self):
        """Global extractor_registry contains MethodologyExtractor."""
        from src.extractors import extractor_registry

        assert extractor_registry.is_supported(ExtractionType.METHODOLOGY)
        extractor = extractor_registry.get_extractor(ExtractionType.METHODOLOGY)
        assert isinstance(extractor, MethodologyExtractor)
