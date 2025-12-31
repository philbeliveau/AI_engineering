"""Tests for BaseExtractor ABC and related functionality."""

import pytest

from src.extractors import (
    BaseExtractor,
    Decision,
    ExtractionParseError,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    PromptLoadError,
    UnsupportedExtractionTypeError,
)


class TestBaseExtractorABC:
    """Test that BaseExtractor is properly abstract."""

    def test_cannot_instantiate_directly(self):
        """BaseExtractor cannot be instantiated without implementing abstract methods."""
        with pytest.raises(TypeError) as exc_info:
            BaseExtractor()
        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_class_must_implement_abstract_methods(self):
        """Concrete class must implement all abstract methods and properties."""

        class IncompleteExtractor(BaseExtractor):
            pass  # Missing all required methods

        with pytest.raises(TypeError):
            IncompleteExtractor()

    def test_concrete_class_missing_extract_method(self):
        """Concrete class missing extract method raises TypeError."""

        class MissingExtract(BaseExtractor):
            @property
            def extraction_type(self):
                return ExtractionType.DECISION

            @property
            def model_class(self):
                return Decision

            def get_prompt(self):
                return "test"

        with pytest.raises(TypeError):
            MissingExtract()

    def test_concrete_class_missing_get_prompt(self):
        """Concrete class missing get_prompt raises TypeError."""

        class MissingGetPrompt(BaseExtractor):
            @property
            def extraction_type(self):
                return ExtractionType.DECISION

            @property
            def model_class(self):
                return Decision

            def extract(self, chunk_content, chunk_id, source_id):
                return []

        with pytest.raises(TypeError):
            MissingGetPrompt()


class TestConcreteExtractor:
    """Test concrete extractor implementation."""

    def test_dummy_extractor_instantiates(self, dummy_extractor):
        """DummyExtractor can be instantiated."""
        assert dummy_extractor is not None
        assert dummy_extractor.extraction_type == ExtractionType.DECISION
        assert dummy_extractor.model_class == Decision

    def test_extractor_uses_default_config(self, dummy_extractor):
        """Extractor uses default config if none provided."""
        assert dummy_extractor.config is not None
        assert dummy_extractor.config.max_extractions_per_chunk == 5
        assert dummy_extractor.config.min_confidence == 0.5

    def test_extractor_uses_custom_config(self, dummy_extractor_class, custom_config):
        """Extractor uses custom config when provided."""
        extractor = dummy_extractor_class(config=custom_config)
        assert extractor.config.max_extractions_per_chunk == 10
        assert extractor.config.min_confidence == 0.7

    def test_extractor_has_prompts_dir(self, dummy_extractor):
        """Extractor has prompts directory path."""
        assert dummy_extractor.prompts_dir is not None
        assert "prompts" in str(dummy_extractor.prompts_dir)


class TestExtractorUtilityMethods:
    """Test BaseExtractor utility methods."""

    def test_parse_llm_response_valid_json_array(self, dummy_extractor):
        """_parse_llm_response parses valid JSON array."""
        response = '[{"question": "test?", "options": ["a", "b"]}]'
        result = dummy_extractor._parse_llm_response(response)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["question"] == "test?"

    def test_parse_llm_response_valid_json_object(self, dummy_extractor):
        """_parse_llm_response wraps single JSON object in array."""
        response = '{"question": "test?", "options": ["a", "b"]}'
        result = dummy_extractor._parse_llm_response(response)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_llm_response_markdown_code_block(self, dummy_extractor):
        """_parse_llm_response extracts JSON from markdown code block."""
        response = """
        Here's the extraction:
        ```json
        [{"question": "test?"}]
        ```
        """
        result = dummy_extractor._parse_llm_response(response)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_parse_llm_response_invalid_json_raises(self, dummy_extractor):
        """_parse_llm_response raises ExtractionParseError for invalid JSON."""
        response = "This is not valid JSON at all"
        with pytest.raises(ExtractionParseError) as exc_info:
            dummy_extractor._parse_llm_response(response)
        assert exc_info.value.code == "EXTRACTION_PARSE_ERROR"

    def test_validate_extraction_success(self, dummy_extractor):
        """_validate_extraction creates successful result for valid data."""
        data = {
            "question": "Should I use RAG?",
            "options": ["Yes", "No"],
            "considerations": ["Cost"],
        }
        result = dummy_extractor._validate_extraction(data, "chunk-1", "src-1")
        assert result.success is True
        assert result.extraction is not None
        assert result.extraction.source_id == "src-1"
        assert result.extraction.chunk_id == "chunk-1"
        assert result.extraction.type == ExtractionType.DECISION

    def test_validate_extraction_failure(self, dummy_extractor):
        """_validate_extraction returns error result for invalid data."""
        data = {}  # Missing required 'question' field
        result = dummy_extractor._validate_extraction(data, "chunk-1", "src-1")
        assert result.success is False
        assert result.error is not None

    def test_generate_topics_finds_rag(self, dummy_extractor):
        """_generate_topics identifies RAG topic."""
        content = "This chapter covers RAG systems and retrieval mechanisms."
        topics = dummy_extractor._generate_topics(content)
        assert "rag" in topics

    def test_generate_topics_finds_embeddings(self, dummy_extractor):
        """_generate_topics identifies embeddings topic."""
        content = "Vector embeddings are crucial for semantic search."
        topics = dummy_extractor._generate_topics(content)
        assert "embeddings" in topics

    def test_generate_topics_limits_to_five(self, dummy_extractor):
        """_generate_topics returns at most 5 topics."""
        content = """
        RAG systems use embeddings and LLMs for prompting.
        Training and fine-tuning improve evaluation metrics.
        Agents handle deployment and inference.
        """
        topics = dummy_extractor._generate_topics(content)
        assert len(topics) <= 5

    def test_load_prompt_success(self, dummy_extractor):
        """_load_prompt loads existing prompt file."""
        prompt = dummy_extractor._load_prompt("decision")
        assert "decision" in prompt.lower()

    def test_load_prompt_not_found_raises(self, dummy_extractor):
        """_load_prompt raises PromptLoadError for missing file."""
        with pytest.raises(PromptLoadError) as exc_info:
            dummy_extractor._load_prompt("nonexistent")
        assert exc_info.value.code == "PROMPT_LOAD_ERROR"
        assert "nonexistent" in exc_info.value.details["prompt_name"]

    def test_load_full_prompt_combines_base_and_specific(self, dummy_extractor):
        """_load_full_prompt combines base instructions with specific prompt."""
        prompt = dummy_extractor._load_full_prompt("decision")
        # Should contain base instructions
        assert "knowledge extraction assistant" in prompt.lower()
        assert "confidence" in prompt.lower()
        # Should contain decision-specific content
        assert "decision" in prompt.lower()
        assert "question" in prompt.lower()

    def test_load_full_prompt_all_types(self, dummy_extractor):
        """_load_full_prompt works for all extraction types."""
        prompt_names = [
            "decision", "pattern", "warning", "methodology",
            "checklist", "persona", "workflow"
        ]
        for name in prompt_names:
            prompt = dummy_extractor._load_full_prompt(name)
            # All should contain base content
            assert "knowledge extraction assistant" in prompt.lower()
            # All should contain type-specific content
            assert name in prompt.lower()


class TestExtractorConfig:
    """Test ExtractorConfig model."""

    def test_default_config_values(self, extractor_config):
        """ExtractorConfig has correct default values."""
        assert extractor_config.max_extractions_per_chunk == 5
        assert extractor_config.min_confidence == 0.5
        assert extractor_config.auto_tag_topics is True
        assert extractor_config.include_context is True

    def test_custom_config_values(self, custom_config):
        """ExtractorConfig accepts custom values."""
        assert custom_config.max_extractions_per_chunk == 10
        assert custom_config.min_confidence == 0.7
        assert custom_config.auto_tag_topics is False
        assert custom_config.include_context is False

    def test_config_validates_confidence_range(self):
        """ExtractorConfig validates confidence is between 0 and 1."""
        with pytest.raises(ValueError):
            ExtractorConfig(min_confidence=1.5)

        with pytest.raises(ValueError):
            ExtractorConfig(min_confidence=-0.1)


class TestExtractorRegistry:
    """Test ExtractorRegistry functionality."""

    def test_register_and_get_extractor(self, fresh_registry, dummy_extractor_class):
        """Registry registers and retrieves extractors."""
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        extractor = fresh_registry.get_extractor(ExtractionType.DECISION)
        assert isinstance(extractor, dummy_extractor_class)

    def test_get_extractor_unregistered_raises(self, fresh_registry):
        """Registry raises for unregistered extraction type."""
        with pytest.raises(UnsupportedExtractionTypeError) as exc_info:
            fresh_registry.get_extractor(ExtractionType.PATTERN)
        assert exc_info.value.code == "UNSUPPORTED_EXTRACTION_TYPE"
        assert "pattern" in exc_info.value.message

    def test_list_extraction_types(self, fresh_registry, dummy_extractor_class):
        """Registry lists registered extraction types."""
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        types = fresh_registry.list_extraction_types()
        assert ExtractionType.DECISION in types

    def test_list_extraction_types_empty(self, fresh_registry):
        """Registry returns empty list when no extractors registered."""
        types = fresh_registry.list_extraction_types()
        assert types == []

    def test_get_all_extractors(self, fresh_registry, dummy_extractor_class):
        """Registry returns all registered extractor instances."""
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        extractors = fresh_registry.get_all_extractors()
        assert len(extractors) == 1
        assert isinstance(extractors[0], dummy_extractor_class)

    def test_is_supported_true(self, fresh_registry, dummy_extractor_class):
        """Registry correctly identifies supported types."""
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        assert fresh_registry.is_supported(ExtractionType.DECISION) is True

    def test_is_supported_false(self, fresh_registry):
        """Registry correctly identifies unsupported types."""
        assert fresh_registry.is_supported(ExtractionType.PATTERN) is False

    def test_register_override_warns(self, fresh_registry, dummy_extractor_class):
        """Registry allows overriding registrations."""
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        # Should not raise, just log a warning
        fresh_registry.register(ExtractionType.DECISION, dummy_extractor_class)
        assert fresh_registry.is_supported(ExtractionType.DECISION)


class TestExtractionResult:
    """Test ExtractionResult model."""

    def test_successful_result(self, sample_decision):
        """ExtractionResult can hold successful extraction."""
        result = ExtractionResult(success=True, extraction=sample_decision)
        assert result.success is True
        assert result.extraction is not None
        assert result.error is None

    def test_failed_result(self):
        """ExtractionResult can hold failed extraction."""
        result = ExtractionResult(success=False, error="Parsing failed")
        assert result.success is False
        assert result.extraction is None
        assert result.error == "Parsing failed"

    def test_result_with_raw_response(self, sample_decision):
        """ExtractionResult can include raw LLM response."""
        result = ExtractionResult(
            success=True,
            extraction=sample_decision,
            raw_response='{"question": "test?"}',
        )
        assert result.raw_response is not None
