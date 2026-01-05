"""Tests for PersonaExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    Persona,
)
from src.extractors.base import ExtractionLevel
from src.extractors.persona_extractor import PersonaExtractor


class TestPersonaExtractorProperties:
    """Test PersonaExtractor properties and configuration."""

    def test_instantiation(self):
        """PersonaExtractor can be instantiated."""
        extractor = PersonaExtractor()
        assert extractor is not None

    def test_extraction_type_is_persona(self):
        """PersonaExtractor has PERSONA extraction type."""
        extractor = PersonaExtractor()
        assert extractor.extraction_type == ExtractionType.PERSONA

    def test_model_class_is_persona(self):
        """PersonaExtractor uses Persona model class."""
        extractor = PersonaExtractor()
        assert extractor.model_class == Persona

    def test_uses_default_config(self):
        """PersonaExtractor uses default config when none provided."""
        extractor = PersonaExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """PersonaExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = PersonaExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestPersonaExtractorGetPrompt:
    """Test PersonaExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = PersonaExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_persona_instructions(self):
        """get_prompt contains persona-specific instructions."""
        extractor = PersonaExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain persona-specific content
        assert "persona" in prompt.lower()
        assert "role" in prompt.lower()


class TestPersonaExtractorAutoTagTopics:
    """Test PersonaExtractor topic auto-tagging."""

    def test_auto_tag_topics_from_role(self):
        """auto_tag_topics extracts topics from persona role."""
        extractor = PersonaExtractor()
        persona = Persona(
            source_id="src-1",
            chunk_id="chunk-1",
            role="RAG Specialist",
            responsibilities=["Design systems"],
        )
        topics = extractor.auto_tag_topics(persona)
        assert "rag" in topics

    def test_auto_tag_topics_from_expertise(self):
        """auto_tag_topics extracts topics from expertise."""
        extractor = PersonaExtractor()
        persona = Persona(
            source_id="src-1",
            chunk_id="chunk-1",
            role="ML Engineer",
            responsibilities=["Train models"],
            expertise=["Embeddings", "Fine-tuning", "LLM"],
        )
        topics = extractor.auto_tag_topics(persona)
        assert "embeddings" in topics or "fine-tuning" in topics or "llm" in topics

    def test_auto_tag_topics_limits_to_five(self):
        """auto_tag_topics returns at most 5 topics."""
        extractor = PersonaExtractor()
        persona = Persona(
            source_id="src-1",
            chunk_id="chunk-1",
            role="Senior AI Engineer",
            responsibilities=[
                "RAG development",
                "LLM fine-tuning",
                "Prompt engineering",
            ],
            expertise=[
                "Embeddings",
                "Training",
                "Inference",
                "Evaluation",
                "Deployment",
            ],
            communication_style="Technical with agents",
        )
        topics = extractor.auto_tag_topics(persona)
        assert len(topics) <= 5


class TestPersonaExtractorExtract:
    """Test PersonaExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a persona."""
        return """
        The RAG Specialist is responsible for designing and implementing
        retrieval-augmented generation systems. They need deep expertise
        in embedding models, vector databases, and chunking strategies.
        They should also understand query optimization and reranking
        techniques. They communicate technically with development teams
        and translate complex concepts for stakeholders.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid persona JSON."""
        return """
        [
            {
                "role": "RAG Specialist",
                "responsibilities": [
                    "Design retrieval-augmented generation systems",
                    "Implement RAG pipelines",
                    "Optimize query and retrieval performance"
                ],
                "expertise": [
                    "Embedding models",
                    "Vector databases",
                    "Chunking strategies",
                    "Query optimization",
                    "Reranking techniques"
                ],
                "communication_style": "Technical with development teams, translates complex concepts for stakeholders",
                "confidence": 0.9
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(self, sample_chunk_content, mock_llm_response):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = PersonaExtractor()

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
        extractor = PersonaExtractor()

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
            persona = results[0].extraction
            assert persona.source_id == "source-456"
            assert persona.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_personas(self):
        """extract returns empty list when no personas found."""
        extractor = PersonaExtractor()
        no_persona_response = "[]"

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = no_persona_response

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
        extractor = PersonaExtractor()

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


class TestPersonaModel:
    """Test Persona Pydantic model."""

    def test_persona_required_fields(self):
        """Persona requires source_id, chunk_id, role."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="ML Engineer",
        )
        assert persona.source_id == "src-123"
        assert persona.chunk_id == "chunk-456"
        assert persona.type == ExtractionType.PERSONA
        assert persona.schema_version == "1.1.0"

    def test_persona_with_all_fields(self):
        """Persona can contain all optional fields."""
        persona = Persona(
            source_id="src-123",
            chunk_id="chunk-456",
            role="RAG Specialist",
            responsibilities=["Design systems", "Implement pipelines"],
            expertise=["Embeddings", "Vector databases"],
            communication_style="Technical and precise",
        )
        assert persona.role == "RAG Specialist"
        assert len(persona.responsibilities) == 2
        assert len(persona.expertise) == 2
        assert persona.communication_style == "Technical and precise"

    def test_persona_has_source_attribution(self):
        """Persona includes source attribution fields."""
        persona = Persona(source_id="src-123", chunk_id="chunk-456", role="Test")
        assert hasattr(persona, "source_id")
        assert hasattr(persona, "chunk_id")
        assert hasattr(persona, "topics")
        assert hasattr(persona, "schema_version")


class TestPersonaExtractorRegistration:
    """Test PersonaExtractor registration with ExtractorRegistry."""

    def test_extractor_can_be_registered(self):
        """PersonaExtractor can be registered with registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.PERSONA, PersonaExtractor)

        assert registry.is_supported(ExtractionType.PERSONA)

    def test_extractor_retrieved_from_registry(self):
        """PersonaExtractor can be retrieved from registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.PERSONA, PersonaExtractor)

        extractor = registry.get_extractor(ExtractionType.PERSONA)
        assert isinstance(extractor, PersonaExtractor)

    def test_global_registry_contains_persona(self):
        """Global extractor_registry contains PersonaExtractor."""
        from src.extractors import extractor_registry

        assert extractor_registry.is_supported(ExtractionType.PERSONA)
        extractor = extractor_registry.get_extractor(ExtractionType.PERSONA)
        assert isinstance(extractor, PersonaExtractor)
