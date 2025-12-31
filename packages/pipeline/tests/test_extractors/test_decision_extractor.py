"""Tests for DecisionExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    Decision,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
)
from src.extractors.decision_extractor import DecisionExtractor


class TestDecisionExtractorProperties:
    """Test DecisionExtractor properties and configuration."""

    def test_instantiation(self):
        """DecisionExtractor can be instantiated."""
        extractor = DecisionExtractor()
        assert extractor is not None

    def test_extraction_type_is_decision(self):
        """DecisionExtractor has DECISION extraction type."""
        extractor = DecisionExtractor()
        assert extractor.extraction_type == ExtractionType.DECISION

    def test_model_class_is_decision(self):
        """DecisionExtractor uses Decision model class."""
        extractor = DecisionExtractor()
        assert extractor.model_class == Decision

    def test_uses_default_config(self):
        """DecisionExtractor uses default config when none provided."""
        extractor = DecisionExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """DecisionExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = DecisionExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestDecisionExtractorGetPrompt:
    """Test DecisionExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = DecisionExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_decision_instructions(self):
        """get_prompt contains decision-specific instructions."""
        extractor = DecisionExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain decision-specific content
        assert "decision" in prompt.lower()
        assert "question" in prompt.lower()
        assert "options" in prompt.lower()


class TestDecisionExtractorAutoTagTopics:
    """Test DecisionExtractor topic auto-tagging."""

    def test_auto_tag_topics_from_question(self):
        """auto_tag_topics extracts topics from decision question."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="Which embedding model should I use?",
            options=["OpenAI ada-002", "all-MiniLM-L6-v2"],
            considerations=["Cost vs quality trade-off"],
        )
        topics = extractor.auto_tag_topics(decision)
        assert "embeddings" in topics

    def test_auto_tag_topics_from_options(self):
        """auto_tag_topics extracts topics from options."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="What approach should I use?",
            options=["Use RAG with retrieval", "Use fine-tuning"],
            considerations=["Accuracy needed"],
        )
        topics = extractor.auto_tag_topics(decision)
        assert "rag" in topics or "fine-tuning" in topics

    def test_auto_tag_topics_from_considerations(self):
        """auto_tag_topics extracts topics from considerations."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="How to improve accuracy?",
            options=["Option A", "Option B"],
            considerations=["LLM latency matters", "Prompting quality"],
        )
        topics = extractor.auto_tag_topics(decision)
        assert "llm" in topics or "prompting" in topics

    def test_auto_tag_topics_limits_to_five(self):
        """auto_tag_topics returns at most 5 topics."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="RAG vs fine-tuning for embeddings?",
            options=["RAG with LLM", "Fine-tuning with training"],
            considerations=[
                "Deployment latency for agents",
                "Evaluation and inference costs",
                "Prompting complexity",
            ],
        )
        topics = extractor.auto_tag_topics(decision)
        assert len(topics) <= 5

    def test_auto_tag_topics_returns_empty_when_no_matches(self):
        """auto_tag_topics returns empty list when no topics match."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="Should we use blue or green?",
            options=["Blue", "Green"],
            considerations=["Color preference"],
        )
        topics = extractor.auto_tag_topics(decision)
        assert isinstance(topics, list)

    def test_auto_tag_topics_from_context_and_recommended_approach(self):
        """auto_tag_topics extracts topics from context and recommended_approach."""
        extractor = DecisionExtractor()
        decision = Decision(
            source_id="src-1",
            chunk_id="chunk-1",
            question="What should we do?",
            options=["Option A", "Option B"],
            considerations=["Some consideration"],
            context="When deploying LLM agents to production",
            recommended_approach="Use RAG for better retrieval performance",
        )
        topics = extractor.auto_tag_topics(decision)
        # Should find topics from context (deployment, agents) or recommended_approach (rag)
        assert any(t in topics for t in ["deployment", "agents", "rag", "llm"])


class TestDecisionExtractorExtract:
    """Test DecisionExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a decision point."""
        return """
        When choosing a chunking strategy for RAG, you should consider
        three main approaches: fixed-size chunking (simple, 512 tokens),
        semantic chunking (respects boundaries, variable size), and
        recursive chunking (hierarchical, preserves structure). Fixed-size
        is fastest but may split concepts. Semantic preserves meaning but
        slower. For technical documentation, semantic chunking is recommended.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid decision JSON."""
        return """
        [
            {
                "question": "Which chunking strategy should I use for RAG?",
                "options": [
                    "Fixed-size chunking (512 tokens)",
                    "Semantic chunking (respects boundaries)",
                    "Recursive chunking (hierarchical)"
                ],
                "considerations": [
                    "Fixed-size is fastest but may split concepts",
                    "Semantic preserves meaning but slower",
                    "Recursive preserves document structure"
                ],
                "recommended_approach": "Semantic chunking for technical documentation",
                "context": "RAG systems with technical documentation",
                "confidence": 0.9
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = DecisionExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
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
        extractor = DecisionExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results[0].success is True
            decision = results[0].extraction
            assert decision.source_id == "source-456"
            assert decision.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_sets_schema_version(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract sets schema_version on extraction."""
        extractor = DecisionExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results[0].extraction.schema_version == "1.0.0"

    @pytest.mark.asyncio
    async def test_extract_auto_tags_topics(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract auto-tags topics when enabled."""
        config = ExtractorConfig(auto_tag_topics=True)
        extractor = DecisionExtractor(config=config)

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            decision = results[0].extraction
            assert isinstance(decision.topics, list)

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_decisions(self):
        """extract returns empty list when no decisions found."""
        extractor = DecisionExtractor()
        no_decision_response = "[]"

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = no_decision_response

            results = await extractor.extract(
                chunk_content="The sky is blue.",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_extract_handles_parse_error(self):
        """extract returns error result for unparseable response."""
        extractor = DecisionExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = "This is not valid JSON"

            results = await extractor.extract(
                chunk_content="Some content",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "parse" in results[0].error.lower()

    @pytest.mark.asyncio
    async def test_extract_handles_validation_error(self):
        """extract returns error result for invalid schema."""
        extractor = DecisionExtractor()
        # Missing required 'question' field
        invalid_response = '[{"options": ["A", "B"]}]'

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = invalid_response

            results = await extractor.extract(
                chunk_content="Some content",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False

    @pytest.mark.asyncio
    async def test_extract_handles_unexpected_exception(self):
        """extract returns error result when LLM client raises unexpected exception."""
        extractor = DecisionExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            # Simulate an unexpected error from the LLM client
            mock_client.extract.side_effect = RuntimeError("Unexpected network failure")

            results = await extractor.extract(
                chunk_content="Some content about decisions",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "Extraction failed" in results[0].error
            assert "Unexpected network failure" in results[0].error


class TestDecisionExtractorIntegration:
    """Integration tests for DecisionExtractor (require LLM client mock)."""

    @pytest.mark.asyncio
    async def test_full_extraction_pipeline(self):
        """Test full extraction pipeline with mocked LLM."""
        extractor = DecisionExtractor()
        chunk_content = """
        When building an LLM application, you need to decide between
        using RAG (Retrieval Augmented Generation) or fine-tuning.
        RAG is cheaper and more flexible, while fine-tuning offers
        better domain-specific performance but requires more data.
        For most applications, RAG is the recommended starting point.
        """
        mock_response = """
        [
            {
                "question": "Should I use RAG or fine-tuning for my LLM application?",
                "options": ["RAG (Retrieval Augmented Generation)", "Fine-tuning"],
                "considerations": [
                    "RAG is cheaper and more flexible",
                    "Fine-tuning offers better domain-specific performance",
                    "Fine-tuning requires more data"
                ],
                "recommended_approach": "RAG for most applications as starting point",
                "context": "Building an LLM application",
                "confidence": 0.95
            }
        ]
        """

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_response

            results = await extractor.extract(
                chunk_content=chunk_content,
                chunk_id="chunk-001",
                source_id="book-ai-engineering",
            )

            # Verify successful extraction
            assert len(results) == 1
            assert results[0].success is True

            decision = results[0].extraction
            assert decision.question == "Should I use RAG or fine-tuning for my LLM application?"
            assert len(decision.options) == 2
            assert len(decision.considerations) == 3
            assert "RAG" in decision.recommended_approach
            assert decision.source_id == "book-ai-engineering"
            assert decision.chunk_id == "chunk-001"
            assert decision.type == ExtractionType.DECISION


class TestDecisionExtractorRegistration:
    """Test DecisionExtractor registration with ExtractorRegistry."""

    def test_extractor_can_be_registered(self):
        """DecisionExtractor can be registered with registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.DECISION, DecisionExtractor)

        assert registry.is_supported(ExtractionType.DECISION)

    def test_extractor_retrieved_from_registry(self):
        """DecisionExtractor can be retrieved from registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.DECISION, DecisionExtractor)

        extractor = registry.get_extractor(ExtractionType.DECISION)
        assert isinstance(extractor, DecisionExtractor)
