"""Tests for WarningExtractor implementation."""

import pytest

from src.extractors import (
    ExtractionResult,
    ExtractionType,
    Warning,
    WarningExtractor,
    extractor_registry,
)


class TestWarningExtractor:
    """Test WarningExtractor implementation."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        """Create warning extractor instance."""
        return WarningExtractor()

    def test_extraction_type_is_warning(self, extractor: WarningExtractor):
        """Extractor returns WARNING extraction type."""
        assert extractor.extraction_type == ExtractionType.WARNING

    def test_model_class_is_warning(self, extractor: WarningExtractor):
        """Extractor uses Warning model class."""
        assert extractor.model_class == Warning

    def test_get_prompt_loads_warning_md(self, extractor: WarningExtractor):
        """Prompt is loaded from warning.md file."""
        prompt = extractor.get_prompt()
        assert "warning" in prompt.lower()
        assert len(prompt) > 100
        # Check for key sections
        assert "symptoms" in prompt.lower()
        assert "consequences" in prompt.lower()
        assert "prevention" in prompt.lower()

    def test_extract_returns_list(self, extractor: WarningExtractor):
        """Extract method returns list of results."""
        results = extractor.extract(
            chunk_content="Sample warning text about common mistakes",
            chunk_id="chunk-123",
            source_id="source-456",
        )
        assert isinstance(results, list)

    def test_registry_contains_warning_extractor(self):
        """Warning extractor is registered in global registry."""
        assert extractor_registry.is_supported(ExtractionType.WARNING)
        extractor = extractor_registry.get_extractor(ExtractionType.WARNING)
        assert isinstance(extractor, WarningExtractor)

    def test_extractor_has_prompts_dir(self, extractor: WarningExtractor):
        """Extractor has prompts_dir attribute set."""
        assert extractor.prompts_dir is not None
        assert extractor.prompts_dir.exists()

    def test_extractor_has_config(self, extractor: WarningExtractor):
        """Extractor has config attribute with defaults."""
        assert extractor.config is not None
        assert extractor.config.auto_tag_topics is True
        assert extractor.config.max_extractions_per_chunk == 5


class TestWarningModel:
    """Test Warning Pydantic model."""

    def test_warning_required_fields(self):
        """Warning requires source_id, chunk_id, title, description."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Context Window Overflow",
            description="Sending too many tokens causes truncation",
        )
        assert warning.source_id == "src-123"
        assert warning.chunk_id == "chunk-456"
        assert warning.title == "Context Window Overflow"
        assert warning.description == "Sending too many tokens causes truncation"
        assert warning.type == ExtractionType.WARNING
        assert warning.schema_version == "1.0.0"

    def test_warning_optional_fields(self):
        """Warning allows optional symptoms, consequences, prevention."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Cold Start Latency",
            description="First inference is slow due to model loading",
            symptoms=["Long initial response time", "Timeout on first request"],
            consequences=["Poor user experience", "Failed health checks"],
            prevention="Use model warming or keep-alive requests",
        )
        assert len(warning.symptoms) == 2
        assert len(warning.consequences) == 2
        assert warning.prevention == "Use model warming or keep-alive requests"

    def test_warning_empty_lists_valid(self):
        """Warning allows empty symptoms and consequences lists."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test Warning",
            description="Test description",
        )
        assert warning.symptoms == []
        assert warning.consequences == []
        assert warning.prevention == ""

    def test_warning_has_source_attribution(self):
        """Warning includes source attribution fields."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
        )
        assert hasattr(warning, "source_id")
        assert hasattr(warning, "chunk_id")
        assert hasattr(warning, "topics")
        assert hasattr(warning, "schema_version")

    def test_warning_multiple_symptoms(self):
        """Warning can have multiple symptoms."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Rate Limiting Issues",
            description="Hitting API rate limits causes failures",
            symptoms=[
                "429 Too Many Requests errors",
                "Exponential backoff triggered",
                "Request queue growing",
                "Response latency increasing",
            ],
        )
        assert len(warning.symptoms) == 4

    def test_warning_multiple_consequences(self):
        """Warning can have multiple consequences."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Missing Input Validation",
            description="Not validating prompt inputs exposes security risks",
            consequences=[
                "Prompt injection attacks",
                "Data exfiltration",
                "Cost explosion from long inputs",
                "Service disruption",
            ],
        )
        assert len(warning.consequences) == 4

    def test_warning_default_confidence(self):
        """Warning has default confidence score."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
        )
        assert warning.confidence == 0.8

    def test_warning_custom_confidence(self):
        """Warning allows custom confidence score."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
            confidence=0.95,
        )
        assert warning.confidence == 0.95

    def test_warning_topics_default_empty(self):
        """Warning has empty topics list by default."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
        )
        assert warning.topics == []

    def test_warning_with_topics(self):
        """Warning can have topics assigned."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
            topics=["embeddings", "rag", "deployment"],
        )
        assert len(warning.topics) == 3
        assert "embeddings" in warning.topics


class TestTopicAutoTagging:
    """Test topic auto-tagging for warnings."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        return WarningExtractor()

    def test_generates_topics_from_content(self, extractor: WarningExtractor):
        """Topics are generated from warning content."""
        topics = extractor._generate_topics(
            "This warning about embedding model changes affects RAG systems"
        )
        assert isinstance(topics, list)
        # Should detect rag, embeddings, or related topics
        assert len(topics) > 0

    def test_limits_topics_to_five(self, extractor: WarningExtractor):
        """Topic generation limits to 5 topics max."""
        content = (
            "RAG embedding fine-tuning LLM prompting "
            "evaluation deployment training inference agents"
        )
        topics = extractor._generate_topics(content)
        assert len(topics) <= 5

    def test_detects_rag_topic(self, extractor: WarningExtractor):
        """Detects RAG-related content."""
        topics = extractor._generate_topics("This RAG system retrieval pipeline")
        assert "rag" in topics

    def test_detects_embedding_topic(self, extractor: WarningExtractor):
        """Detects embedding-related content."""
        topics = extractor._generate_topics("Vector embeddings are crucial")
        assert "embeddings" in topics

    def test_detects_llm_topic(self, extractor: WarningExtractor):
        """Detects LLM-related content."""
        topics = extractor._generate_topics("Using Claude or GPT for inference")
        assert "llm" in topics

    def test_empty_content_returns_empty_topics(self, extractor: WarningExtractor):
        """Empty content returns empty topics."""
        topics = extractor._generate_topics("")
        assert topics == []


class TestWarningValidation:
    """Test warning validation via extractor utilities."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        return WarningExtractor()

    def test_validate_extraction_success(self, extractor: WarningExtractor):
        """Valid warning data passes validation."""
        data = {
            "title": "Context Window Overflow",
            "description": "Sending too many tokens causes truncation",
            "symptoms": ["API errors", "Truncated responses"],
            "consequences": ["Data loss", "Incorrect outputs"],
            "prevention": "Count tokens before sending",
        }
        result = extractor._validate_extraction(data, "chunk-123", "src-456")
        assert result.success is True
        assert result.extraction is not None
        assert result.extraction.title == "Context Window Overflow"

    def test_validate_extraction_adds_source_attribution(
        self, extractor: WarningExtractor
    ):
        """Validation adds source_id and chunk_id."""
        data = {
            "title": "Test Warning",
            "description": "Test description",
        }
        result = extractor._validate_extraction(data, "chunk-123", "src-456")
        assert result.success is True
        assert result.extraction.source_id == "src-456"
        assert result.extraction.chunk_id == "chunk-123"

    def test_validate_extraction_missing_required_field(
        self, extractor: WarningExtractor
    ):
        """Missing required field fails validation."""
        data = {
            "title": "Test Warning",
            # Missing description
        }
        result = extractor._validate_extraction(data, "chunk-123", "src-456")
        assert result.success is False
        assert result.error is not None


class TestPromptLoading:
    """Test prompt loading functionality."""

    @pytest.fixture
    def extractor(self) -> WarningExtractor:
        return WarningExtractor()

    def test_prompt_contains_schema(self, extractor: WarningExtractor):
        """Prompt contains output schema."""
        prompt = extractor.get_prompt()
        assert "title" in prompt
        assert "description" in prompt
        assert "symptoms" in prompt
        assert "consequences" in prompt
        assert "prevention" in prompt

    def test_prompt_contains_example(self, extractor: WarningExtractor):
        """Prompt contains extraction example."""
        prompt = extractor.get_prompt()
        assert "example" in prompt.lower()

    def test_prompt_contains_categories(self, extractor: WarningExtractor):
        """Prompt contains warning categories."""
        prompt = extractor.get_prompt()
        # Check for common warning categories
        assert "performance" in prompt.lower() or "cost" in prompt.lower()


class TestExtractionResult:
    """Test ExtractionResult handling."""

    def test_successful_extraction_result(self):
        """Successful extraction has success=True and extraction."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Test",
            description="Test",
        )
        result = ExtractionResult(success=True, extraction=warning)
        assert result.success is True
        assert result.extraction is not None
        assert result.error is None

    def test_failed_extraction_result(self):
        """Failed extraction has success=False and error."""
        result = ExtractionResult(success=False, error="Parsing failed")
        assert result.success is False
        assert result.extraction is None
        assert result.error == "Parsing failed"

    def test_extraction_result_with_raw_response(self):
        """ExtractionResult can store raw LLM response."""
        result = ExtractionResult(
            success=False,
            error="Invalid JSON",
            raw_response='{"invalid": json}',
        )
        assert result.raw_response == '{"invalid": json}'
