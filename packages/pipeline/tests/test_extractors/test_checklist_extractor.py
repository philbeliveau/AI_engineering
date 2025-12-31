"""Tests for ChecklistExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    Checklist,
    ChecklistItem,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
)
from src.extractors.checklist_extractor import ChecklistExtractor


class TestChecklistExtractorProperties:
    """Test ChecklistExtractor properties and configuration."""

    def test_instantiation(self):
        """ChecklistExtractor can be instantiated."""
        extractor = ChecklistExtractor()
        assert extractor is not None

    def test_extraction_type_is_checklist(self):
        """ChecklistExtractor has CHECKLIST extraction type."""
        extractor = ChecklistExtractor()
        assert extractor.extraction_type == ExtractionType.CHECKLIST

    def test_model_class_is_checklist(self):
        """ChecklistExtractor uses Checklist model class."""
        extractor = ChecklistExtractor()
        assert extractor.model_class == Checklist

    def test_uses_default_config(self):
        """ChecklistExtractor uses default config when none provided."""
        extractor = ChecklistExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """ChecklistExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = ChecklistExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestChecklistExtractorGetPrompt:
    """Test ChecklistExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = ChecklistExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_checklist_instructions(self):
        """get_prompt contains checklist-specific instructions."""
        extractor = ChecklistExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain checklist-specific content
        assert "checklist" in prompt.lower()
        assert "item" in prompt.lower()


class TestChecklistExtractorAutoTagTopics:
    """Test ChecklistExtractor topic auto-tagging."""

    def test_auto_tag_topics_from_name(self):
        """auto_tag_topics extracts topics from checklist name."""
        extractor = ChecklistExtractor()
        checklist = Checklist(
            source_id="src-1",
            chunk_id="chunk-1",
            name="LLM Deployment Checklist",
            items=[ChecklistItem(item="Test item", required=True)],
        )
        topics = extractor.auto_tag_topics(checklist)
        assert "llm" in topics or "deployment" in topics

    def test_auto_tag_topics_from_items(self):
        """auto_tag_topics extracts topics from items."""
        extractor = ChecklistExtractor()
        checklist = Checklist(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Quality Checklist",
            items=[
                ChecklistItem(item="Verify embedding dimensions", required=True),
                ChecklistItem(item="Test RAG retrieval", required=True),
            ],
        )
        topics = extractor.auto_tag_topics(checklist)
        assert "embeddings" in topics or "rag" in topics

    def test_auto_tag_topics_limits_to_five(self):
        """auto_tag_topics returns at most 5 topics."""
        extractor = ChecklistExtractor()
        checklist = Checklist(
            source_id="src-1",
            chunk_id="chunk-1",
            name="Complete LLM RAG Evaluation",
            items=[
                ChecklistItem(item="Check embeddings", required=True),
                ChecklistItem(item="Verify fine-tuning", required=True),
                ChecklistItem(item="Test prompting", required=True),
                ChecklistItem(item="Evaluate inference", required=True),
            ],
            context="For deployment of training pipeline",
        )
        topics = extractor.auto_tag_topics(checklist)
        assert len(topics) <= 5


class TestChecklistExtractorExtract:
    """Test ChecklistExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a checklist."""
        return """
        Before deploying your LLM to production, verify: model latency
        under 500ms, error rate below 1%, input validation in place,
        rate limiting configured, logging enabled. Also consider:
        A/B testing setup, rollback procedure documented.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid checklist JSON."""
        return """
        [
            {
                "name": "LLM Production Deployment Checklist",
                "items": [
                    {"item": "Model latency under 500ms", "required": true},
                    {"item": "Error rate below 1%", "required": true},
                    {"item": "Input validation in place", "required": true},
                    {"item": "Rate limiting configured", "required": true},
                    {"item": "Logging enabled", "required": true},
                    {"item": "A/B testing setup", "required": false},
                    {"item": "Rollback procedure documented", "required": false}
                ],
                "context": "Use before deploying LLM to production",
                "confidence": 0.9
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(self, sample_chunk_content, mock_llm_response):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = ChecklistExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert isinstance(results, list)
            assert len(results) > 0
            assert all(isinstance(r, ExtractionResult) for r in results)

    @pytest.mark.asyncio
    async def test_extract_preserves_source_attribution(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract preserves source_id and chunk_id."""
        extractor = ChecklistExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results[0].success is True
            checklist = results[0].extraction
            assert checklist.source_id == "source-456"
            assert checklist.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_checklists(self):
        """extract returns empty list when no checklists found."""
        extractor = ChecklistExtractor()
        no_checklist_response = "[]"

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = no_checklist_response

            results = await extractor.extract(
                chunk_content="The sky is blue.",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_extract_handles_parse_error(self):
        """extract returns error result for unparseable response."""
        extractor = ChecklistExtractor()

        with patch.object(extractor, "_llm_client", new_callable=AsyncMock) as mock_client:
            mock_client.extract.return_value = "This is not valid JSON"

            results = await extractor.extract(
                chunk_content="Some content",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "parse" in results[0].error.lower()


class TestChecklistModel:
    """Test Checklist Pydantic model."""

    def test_checklist_required_fields(self):
        """Checklist requires source_id, chunk_id, name."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Checklist",
        )
        assert checklist.source_id == "src-123"
        assert checklist.chunk_id == "chunk-456"
        assert checklist.type == ExtractionType.CHECKLIST
        assert checklist.schema_version == "1.0.0"

    def test_checklist_with_items(self):
        """Checklist can contain items."""
        checklist = Checklist(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Checklist",
            items=[
                ChecklistItem(item="Required item", required=True),
                ChecklistItem(item="Optional item", required=False),
            ],
            context="Before deployment",
        )
        assert len(checklist.items) == 2
        assert checklist.items[0].required is True
        assert checklist.items[1].required is False

    def test_checklist_item_defaults_required_true(self):
        """ChecklistItem defaults required to True."""
        item = ChecklistItem(item="Test item")
        assert item.required is True

    def test_checklist_has_source_attribution(self):
        """Checklist includes source attribution fields."""
        checklist = Checklist(source_id="src-123", chunk_id="chunk-456", name="Test")
        assert hasattr(checklist, "source_id")
        assert hasattr(checklist, "chunk_id")
        assert hasattr(checklist, "topics")
        assert hasattr(checklist, "schema_version")


class TestChecklistExtractorRegistration:
    """Test ChecklistExtractor registration with ExtractorRegistry."""

    def test_extractor_can_be_registered(self):
        """ChecklistExtractor can be registered with registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.CHECKLIST, ChecklistExtractor)

        assert registry.is_supported(ExtractionType.CHECKLIST)

    def test_extractor_retrieved_from_registry(self):
        """ChecklistExtractor can be retrieved from registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.CHECKLIST, ChecklistExtractor)

        extractor = registry.get_extractor(ExtractionType.CHECKLIST)
        assert isinstance(extractor, ChecklistExtractor)

    def test_global_registry_contains_checklist(self):
        """Global extractor_registry contains ChecklistExtractor."""
        from src.extractors import extractor_registry

        assert extractor_registry.is_supported(ExtractionType.CHECKLIST)
        extractor = extractor_registry.get_extractor(ExtractionType.CHECKLIST)
        assert isinstance(extractor, ChecklistExtractor)
