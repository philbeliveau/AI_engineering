"""Tests for PatternExtractor class."""

from unittest.mock import AsyncMock, patch

import pytest

from src.extractors import (
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    Pattern,
    extractor_registry,
)
from src.extractors.pattern_extractor import PatternExtractor


class TestPatternExtractorProperties:
    """Test PatternExtractor properties and configuration."""

    def test_instantiation(self):
        """PatternExtractor can be instantiated."""
        extractor = PatternExtractor()
        assert extractor is not None

    def test_extraction_type_is_pattern(self):
        """PatternExtractor has PATTERN extraction type."""
        extractor = PatternExtractor()
        assert extractor.extraction_type == ExtractionType.PATTERN

    def test_model_class_is_pattern(self):
        """PatternExtractor uses Pattern model class."""
        extractor = PatternExtractor()
        assert extractor.model_class == Pattern

    def test_uses_default_config(self):
        """PatternExtractor uses default config when none provided."""
        extractor = PatternExtractor()
        assert extractor.config.max_extractions_per_chunk == 5
        assert extractor.config.min_confidence == 0.5
        assert extractor.config.auto_tag_topics is True

    def test_accepts_custom_config(self):
        """PatternExtractor accepts custom configuration."""
        config = ExtractorConfig(
            max_extractions_per_chunk=10,
            min_confidence=0.8,
            auto_tag_topics=False,
        )
        extractor = PatternExtractor(config=config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.8


class TestPatternExtractorGetPrompt:
    """Test PatternExtractor.get_prompt method."""

    def test_get_prompt_returns_string(self):
        """get_prompt returns prompt string."""
        extractor = PatternExtractor()
        prompt = extractor.get_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_get_prompt_contains_pattern_instructions(self):
        """get_prompt contains pattern-specific instructions."""
        extractor = PatternExtractor()
        prompt = extractor.get_prompt()
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        # Should contain pattern-specific content
        assert "pattern" in prompt.lower()
        assert "problem" in prompt.lower()
        assert "solution" in prompt.lower()

    def test_get_prompt_includes_code_example_guidance(self):
        """get_prompt includes guidance for code_example field."""
        extractor = PatternExtractor()
        prompt = extractor.get_prompt()
        assert "code" in prompt.lower()
        assert "example" in prompt.lower()

    def test_get_prompt_includes_trade_offs_guidance(self):
        """get_prompt includes guidance for trade_offs field."""
        extractor = PatternExtractor()
        prompt = extractor.get_prompt()
        assert "trade" in prompt.lower()


class TestPatternModel:
    """Test Pattern Pydantic model."""

    def test_pattern_required_fields(self):
        """Pattern requires source_id, chunk_id, name, problem, solution."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Caching",
            problem="High API costs",
            solution="Cache using embedding similarity",
        )
        assert pattern.source_id == "src-123"
        assert pattern.chunk_id == "chunk-456"
        assert pattern.type == ExtractionType.PATTERN
        assert pattern.schema_version == "1.0.0"

    def test_pattern_optional_fields(self):
        """Pattern allows optional code_example, context, trade_offs."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test Pattern",
            problem="Test problem",
            solution="Test solution",
            code_example="def example(): pass",
            context="Test context",
            trade_offs=["Pro 1", "Con 1"],
        )
        assert pattern.code_example == "def example(): pass"
        assert pattern.context == "Test context"
        assert len(pattern.trade_offs) == 2

    def test_pattern_code_example_preserves_formatting(self):
        """Code example preserves multiline formatting."""
        code = """def semantic_cache(query: str) -> str:
    embedding = get_embedding(query)
    cached = find_similar(embedding)
    if cached:
        return cached.response
    return None"""

        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Cache",
            problem="Cost",
            solution="Cache",
            code_example=code,
        )
        assert "\n" in pattern.code_example
        assert "def semantic_cache" in pattern.code_example
        assert "    embedding" in pattern.code_example  # Indentation preserved

    def test_pattern_has_source_attribution(self):
        """Pattern includes source attribution fields."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
            problem="Test",
            solution="Test",
        )
        assert hasattr(pattern, "source_id")
        assert hasattr(pattern, "chunk_id")
        assert hasattr(pattern, "topics")
        assert hasattr(pattern, "schema_version")

    def test_pattern_confidence_bounds(self):
        """Pattern confidence must be between 0.0 and 1.0."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Test",
            problem="Test",
            solution="Test",
            confidence=0.85,
        )
        assert 0.0 <= pattern.confidence <= 1.0


class TestTopicAutoTagging:
    """Test topic auto-tagging for patterns."""

    def test_generates_topics_from_content(self):
        """Topics are generated from pattern content."""
        extractor = PatternExtractor()
        topics = extractor._generate_topics(
            "This pattern uses embedding similarity for semantic caching in RAG systems"
        )
        assert isinstance(topics, list)
        # Should detect rag, embeddings, or caching
        assert len(topics) > 0

    def test_auto_tag_topics_method(self):
        """auto_tag_topics extracts topics from Pattern model."""
        extractor = PatternExtractor()
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Semantic Caching",
            problem="High API costs from LLM calls",
            solution="Cache using embedding similarity in RAG pipeline",
            context="High-traffic applications",
            trade_offs=["Pro: Cost reduction", "Con: Latency"],
        )
        topics = extractor.auto_tag_topics(pattern)
        assert isinstance(topics, list)
        assert len(topics) > 0
        # Should detect rag, embeddings, or llm from content
        assert any(t in topics for t in ["rag", "embeddings", "llm"])

    def test_generates_topics_for_rag(self):
        """Topics detect RAG-related content."""
        extractor = PatternExtractor()
        topics = extractor._generate_topics("Build a RAG pipeline with retrieval")
        assert "rag" in topics

    def test_generates_topics_for_embeddings(self):
        """Topics detect embedding-related content."""
        extractor = PatternExtractor()
        topics = extractor._generate_topics("Use vector embeddings for search")
        assert "embeddings" in topics

    def test_generates_topics_for_llm(self):
        """Topics detect LLM-related content."""
        extractor = PatternExtractor()
        topics = extractor._generate_topics("This LLM approach uses Claude")
        assert "llm" in topics

    def test_limits_topics_to_five(self):
        """Topic generation limits to 5 topics max."""
        extractor = PatternExtractor()
        topics = extractor._generate_topics(
            "RAG embedding fine-tuning LLM prompting evaluation deployment training inference agents"
        )
        assert len(topics) <= 5


class TestPatternExtractorExtract:
    """Test PatternExtractor.extract method."""

    @pytest.fixture
    def sample_chunk_content(self) -> str:
        """Sample chunk containing a pattern."""
        return """
        For high-traffic LLM applications, implement semantic caching to reduce
        API costs. Instead of exact-match caching, use embedding similarity
        to find cached responses for semantically similar queries. This can
        reduce costs by 40-60% but adds latency for cache lookups.
        """

    @pytest.fixture
    def mock_llm_response(self) -> str:
        """Mock LLM response with valid pattern JSON."""
        return """
        [
            {
                "name": "Semantic Caching",
                "problem": "High API costs from repeated similar queries to LLM endpoints",
                "solution": "Cache responses using embedding similarity instead of exact match. Compare query embeddings to find cached responses.",
                "code_example": null,
                "context": "High-traffic LLM applications",
                "trade_offs": [
                    "Pro: 40-60% cost reduction",
                    "Con: Added latency for cache lookups"
                ],
                "confidence": 0.9
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_valid_chunk(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract returns ExtractionResult list for valid chunk."""
        extractor = PatternExtractor()

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
        extractor = PatternExtractor()

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
            pattern = results[0].extraction
            assert pattern.source_id == "source-456"
            assert pattern.chunk_id == "chunk-123"

    @pytest.mark.asyncio
    async def test_extract_sets_schema_version(
        self, sample_chunk_content, mock_llm_response
    ):
        """extract sets schema_version on extraction."""
        extractor = PatternExtractor()

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
        extractor = PatternExtractor(config=config)

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_llm_response

            results = await extractor.extract(
                chunk_content=sample_chunk_content,
                chunk_id="chunk-123",
                source_id="source-456",
            )

            pattern = results[0].extraction
            assert isinstance(pattern.topics, list)

    @pytest.mark.asyncio
    async def test_extract_returns_empty_list_for_no_patterns(self):
        """extract returns empty list when no patterns found."""
        extractor = PatternExtractor()
        no_pattern_response = "[]"

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = no_pattern_response

            results = await extractor.extract(
                chunk_content="The sky is blue.",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_extract_handles_parse_error(self):
        """extract returns error result for unparseable response."""
        extractor = PatternExtractor()

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
        extractor = PatternExtractor()
        # Missing required 'name' field
        invalid_response = '[{"problem": "test", "solution": "test"}]'

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
    async def test_extract_handles_llm_error(self):
        """extract returns error result when LLM call fails."""
        extractor = PatternExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.side_effect = Exception("API error")

            results = await extractor.extract(
                chunk_content="Some content",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            assert len(results) == 1
            assert results[0].success is False
            assert "Extraction failed" in results[0].error


class TestPatternExtractorWithCodeExample:
    """Test PatternExtractor with code examples."""

    @pytest.fixture
    def mock_response_with_code(self) -> str:
        """Mock LLM response with code example."""
        return """
        [
            {
                "name": "Retry with Backoff",
                "problem": "API calls fail intermittently due to rate limits or network issues",
                "solution": "Implement exponential backoff retry logic to handle transient failures gracefully",
                "code_example": "from tenacity import retry, stop_after_attempt, wait_exponential\\n\\n@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))\\ndef call_api():\\n    return requests.get(url)",
                "context": "External API integrations with unreliable networks",
                "trade_offs": [
                    "Pro: Handles transient failures automatically",
                    "Con: Increases overall request latency"
                ],
                "confidence": 0.95
            }
        ]
        """

    @pytest.mark.asyncio
    async def test_extract_with_code_example(self, mock_response_with_code):
        """extract captures code_example field."""
        extractor = PatternExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_response_with_code

            results = await extractor.extract(
                chunk_content="Implement retry logic with backoff",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            pattern = results[0].extraction
            assert pattern.code_example is not None
            assert "@retry" in pattern.code_example
            assert "tenacity" in pattern.code_example

    @pytest.mark.asyncio
    async def test_extract_preserves_code_formatting(self, mock_response_with_code):
        """extract preserves code_example newlines and formatting."""
        extractor = PatternExtractor()

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_response_with_code

            results = await extractor.extract(
                chunk_content="Implement retry logic",
                chunk_id="chunk-123",
                source_id="source-456",
            )

            pattern = results[0].extraction
            # Newlines should be preserved (escaped in JSON, unescaped in string)
            assert "\\n" in mock_response_with_code
            assert pattern.code_example is not None


class TestPatternExtractorIntegration:
    """Integration tests for PatternExtractor (require LLM client mock)."""

    @pytest.mark.asyncio
    async def test_full_extraction_pipeline(self):
        """Test full extraction pipeline with mocked LLM."""
        extractor = PatternExtractor()
        chunk_content = """
        When building RAG applications, implement semantic caching to reduce
        LLM API costs. Cache responses based on query embedding similarity
        rather than exact string match. This approach can reduce API costs
        by 40-60% for high-traffic applications, though it adds latency for
        computing embeddings and searching the cache.
        """
        mock_response = """
        [
            {
                "name": "Semantic Caching",
                "problem": "High LLM API costs in production applications",
                "solution": "Cache responses using embedding similarity. Compare query embeddings against cached entries to find semantically similar previous queries.",
                "code_example": null,
                "context": "RAG applications with high query volume",
                "trade_offs": [
                    "Pro: 40-60% cost reduction",
                    "Con: Added latency for embedding computation"
                ],
                "confidence": 0.9
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

            pattern = results[0].extraction
            assert pattern.name == "Semantic Caching"
            assert "cost" in pattern.problem.lower()
            assert "embedding" in pattern.solution.lower()
            assert len(pattern.trade_offs) == 2
            assert pattern.source_id == "book-ai-engineering"
            assert pattern.chunk_id == "chunk-001"
            assert pattern.type == ExtractionType.PATTERN

    @pytest.mark.asyncio
    async def test_multiple_patterns_extraction(self):
        """Test extraction of multiple patterns from single chunk."""
        extractor = PatternExtractor()
        mock_response = """
        [
            {
                "name": "Pattern One",
                "problem": "Problem one",
                "solution": "Solution one",
                "code_example": null,
                "context": "Context one",
                "trade_offs": [],
                "confidence": 0.8
            },
            {
                "name": "Pattern Two",
                "problem": "Problem two",
                "solution": "Solution two",
                "code_example": "print('hello')",
                "context": "Context two",
                "trade_offs": ["Pro: Fast"],
                "confidence": 0.85
            }
        ]
        """

        with patch.object(
            extractor, "_llm_client", new_callable=AsyncMock
        ) as mock_client:
            mock_client.extract.return_value = mock_response

            results = await extractor.extract(
                chunk_content="Multiple patterns in text",
                chunk_id="chunk-001",
                source_id="source-001",
            )

            assert len(results) == 2
            assert all(r.success for r in results)
            assert results[0].extraction.name == "Pattern One"
            assert results[1].extraction.name == "Pattern Two"
            assert results[1].extraction.code_example == "print('hello')"


class TestPatternExtractorRegistration:
    """Test PatternExtractor registration with ExtractorRegistry."""

    def test_extractor_registered_at_import(self):
        """PatternExtractor is registered in global registry at import."""
        # Registry should have PATTERN after importing pattern_extractor
        assert extractor_registry.is_supported(ExtractionType.PATTERN)

    def test_extractor_retrieved_from_registry(self):
        """PatternExtractor can be retrieved from registry."""
        extractor = extractor_registry.get_extractor(ExtractionType.PATTERN)
        assert isinstance(extractor, PatternExtractor)

    def test_extractor_can_be_manually_registered(self):
        """PatternExtractor can be registered with fresh registry."""
        from src.extractors import ExtractorRegistry

        registry = ExtractorRegistry()
        registry.register(ExtractionType.PATTERN, PatternExtractor)

        assert registry.is_supported(ExtractionType.PATTERN)
        extractor = registry.get_extractor(ExtractionType.PATTERN)
        assert isinstance(extractor, PatternExtractor)


class TestPatternExtractorDependencyInjection:
    """Test PatternExtractor LLMClient dependency injection."""

    def test_accepts_custom_llm_client(self):
        """PatternExtractor accepts custom LLMClient via constructor."""
        from unittest.mock import MagicMock

        mock_client = MagicMock()
        extractor = PatternExtractor(llm_client=mock_client)

        # Access the llm_client property to verify injection
        assert extractor.llm_client is mock_client

    def test_creates_default_llm_client_when_none_provided(self):
        """PatternExtractor creates LLMClient when none injected."""
        from src.extractors import LLMClient

        extractor = PatternExtractor()
        # Access property to trigger lazy creation
        client = extractor.llm_client

        assert isinstance(client, LLMClient)

    @pytest.mark.asyncio
    async def test_uses_injected_client_for_extraction(self):
        """PatternExtractor uses injected LLMClient for extraction."""
        mock_client = AsyncMock()
        mock_client.extract.return_value = "[]"

        extractor = PatternExtractor(llm_client=mock_client)
        await extractor.extract(
            chunk_content="Test content",
            chunk_id="chunk-123",
            source_id="source-456",
        )

        # Verify injected client was called
        mock_client.extract.assert_called_once()
