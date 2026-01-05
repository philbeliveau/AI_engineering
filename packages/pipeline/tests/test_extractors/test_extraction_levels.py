"""Tests for extraction level configuration."""

import pytest
from pydantic import ValidationError

from src.extractors.extraction_levels import (
    EXTRACTION_LEVEL_CONFIG,
    ExtractionLevel,
    ExtractionLevelConfig,
    get_extraction_types_for_level,
    get_level_for_extraction_type,
    get_max_tokens_for_level,
)


class TestExtractionLevel:
    """Tests for ExtractionLevel enum."""

    def test_enum_values(self):
        """All extraction levels should have correct string values."""
        assert ExtractionLevel.CHAPTER.value == "chapter"
        assert ExtractionLevel.SECTION.value == "section"
        assert ExtractionLevel.CHUNK.value == "chunk"

    def test_enum_count(self):
        """Should have exactly 3 levels."""
        assert len(ExtractionLevel) == 3

    def test_enum_string_comparison(self):
        """Enum should support string comparison."""
        assert ExtractionLevel.CHAPTER == "chapter"
        assert ExtractionLevel.SECTION == "section"
        assert ExtractionLevel.CHUNK == "chunk"


class TestExtractionLevelConfig:
    """Tests for ExtractionLevelConfig model."""

    def test_valid_config_creation(self):
        """Should create valid config with all fields."""
        config = ExtractionLevelConfig(
            level=ExtractionLevel.CHAPTER,
            extraction_types=["methodology", "workflow"],
            max_tokens=8000,
            combination_strategy="truncate",
        )
        assert config.level == ExtractionLevel.CHAPTER
        assert config.extraction_types == ["methodology", "workflow"]
        assert config.max_tokens == 8000
        assert config.combination_strategy == "truncate"

    def test_default_combination_strategy(self):
        """Should default to 'truncate' strategy."""
        config = ExtractionLevelConfig(
            level=ExtractionLevel.SECTION,
            extraction_types=["decision"],
            max_tokens=4000,
        )
        assert config.combination_strategy == "truncate"

    def test_invalid_max_tokens_zero(self):
        """Should reject max_tokens of 0."""
        with pytest.raises(ValidationError):
            ExtractionLevelConfig(
                level=ExtractionLevel.CHUNK,
                extraction_types=["warning"],
                max_tokens=0,
            )

    def test_invalid_max_tokens_negative(self):
        """Should reject negative max_tokens."""
        with pytest.raises(ValidationError):
            ExtractionLevelConfig(
                level=ExtractionLevel.CHUNK,
                extraction_types=["warning"],
                max_tokens=-100,
            )

    def test_invalid_combination_strategy(self):
        """Should reject invalid combination strategy."""
        with pytest.raises(ValidationError):
            ExtractionLevelConfig(
                level=ExtractionLevel.CHUNK,
                extraction_types=["warning"],
                max_tokens=512,
                combination_strategy="invalid_strategy",  # type: ignore
            )

    def test_repr(self):
        """Should have human-readable repr."""
        config = ExtractionLevelConfig(
            level=ExtractionLevel.CHAPTER,
            extraction_types=["methodology"],
            max_tokens=8000,
        )
        repr_str = repr(config)
        assert "CHAPTER" in repr_str or "chapter" in repr_str
        assert "methodology" in repr_str
        assert "8000" in repr_str

    def test_empty_extraction_types_allowed(self):
        """Empty extraction_types list should be allowed."""
        config = ExtractionLevelConfig(
            level=ExtractionLevel.CHUNK,
            extraction_types=[],
            max_tokens=512,
        )
        assert config.extraction_types == []


class TestExtractionLevelConfigMapping:
    """Tests for EXTRACTION_LEVEL_CONFIG constant."""

    def test_all_levels_configured(self):
        """All extraction levels should have configuration."""
        for level in ExtractionLevel:
            assert level in EXTRACTION_LEVEL_CONFIG
            assert isinstance(EXTRACTION_LEVEL_CONFIG[level], ExtractionLevelConfig)

    def test_chapter_level_config(self):
        """Chapter level should have methodology and workflow."""
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.CHAPTER]
        assert config.level == ExtractionLevel.CHAPTER
        assert "methodology" in config.extraction_types
        assert "workflow" in config.extraction_types
        assert config.max_tokens == 8000
        assert config.combination_strategy == "summary_if_exceeded"

    def test_section_level_config(self):
        """Section level should have decision, pattern, checklist, persona."""
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.SECTION]
        assert config.level == ExtractionLevel.SECTION
        assert "decision" in config.extraction_types
        assert "pattern" in config.extraction_types
        assert "checklist" in config.extraction_types
        assert "persona" in config.extraction_types
        assert config.max_tokens == 4000
        assert config.combination_strategy == "truncate"

    def test_chunk_level_config(self):
        """Chunk level should have warning only."""
        config = EXTRACTION_LEVEL_CONFIG[ExtractionLevel.CHUNK]
        assert config.level == ExtractionLevel.CHUNK
        assert config.extraction_types == ["warning"]
        assert config.max_tokens == 512
        assert config.combination_strategy == "none"

    def test_no_extraction_type_overlap(self):
        """No extraction type should appear in multiple levels."""
        all_types = []
        for config in EXTRACTION_LEVEL_CONFIG.values():
            all_types.extend(config.extraction_types)
        assert len(all_types) == len(set(all_types)), "Extraction types should not overlap"

    def test_all_seven_extraction_types_covered(self):
        """All 7 extraction types should be configured."""
        all_types = []
        for config in EXTRACTION_LEVEL_CONFIG.values():
            all_types.extend(config.extraction_types)
        expected_types = {
            "methodology",
            "workflow",
            "decision",
            "pattern",
            "checklist",
            "persona",
            "warning",
        }
        assert set(all_types) == expected_types


class TestGetLevelForExtractionType:
    """Tests for get_level_for_extraction_type function."""

    def test_methodology_returns_chapter(self):
        """Methodology should be at chapter level."""
        assert get_level_for_extraction_type("methodology") == ExtractionLevel.CHAPTER

    def test_workflow_returns_chapter(self):
        """Workflow should be at chapter level."""
        assert get_level_for_extraction_type("workflow") == ExtractionLevel.CHAPTER

    def test_decision_returns_section(self):
        """Decision should be at section level."""
        assert get_level_for_extraction_type("decision") == ExtractionLevel.SECTION

    def test_pattern_returns_section(self):
        """Pattern should be at section level."""
        assert get_level_for_extraction_type("pattern") == ExtractionLevel.SECTION

    def test_checklist_returns_section(self):
        """Checklist should be at section level."""
        assert get_level_for_extraction_type("checklist") == ExtractionLevel.SECTION

    def test_persona_returns_section(self):
        """Persona should be at section level."""
        assert get_level_for_extraction_type("persona") == ExtractionLevel.SECTION

    def test_warning_returns_chunk(self):
        """Warning should be at chunk level."""
        assert get_level_for_extraction_type("warning") == ExtractionLevel.CHUNK

    def test_unknown_type_raises_value_error(self):
        """Unknown extraction type should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_level_for_extraction_type("unknown_type")
        assert "Unknown extraction type" in str(exc_info.value)
        assert "unknown_type" in str(exc_info.value)


class TestGetExtractionTypesForLevel:
    """Tests for get_extraction_types_for_level function."""

    def test_chapter_level_types(self):
        """Chapter level should return methodology and workflow."""
        types = get_extraction_types_for_level(ExtractionLevel.CHAPTER)
        assert "methodology" in types
        assert "workflow" in types
        assert len(types) == 2

    def test_section_level_types(self):
        """Section level should return decision, pattern, checklist, persona."""
        types = get_extraction_types_for_level(ExtractionLevel.SECTION)
        assert set(types) == {"decision", "pattern", "checklist", "persona"}

    def test_chunk_level_types(self):
        """Chunk level should return warning only."""
        types = get_extraction_types_for_level(ExtractionLevel.CHUNK)
        assert types == ["warning"]


class TestGetMaxTokensForLevel:
    """Tests for get_max_tokens_for_level function."""

    def test_chapter_level_tokens(self):
        """Chapter level should have 8000 tokens."""
        assert get_max_tokens_for_level(ExtractionLevel.CHAPTER) == 8000

    def test_section_level_tokens(self):
        """Section level should have 4000 tokens."""
        assert get_max_tokens_for_level(ExtractionLevel.SECTION) == 4000

    def test_chunk_level_tokens(self):
        """Chunk level should have 512 tokens."""
        assert get_max_tokens_for_level(ExtractionLevel.CHUNK) == 512

    def test_token_hierarchy(self):
        """Token budgets should follow chapter > section > chunk."""
        chapter_tokens = get_max_tokens_for_level(ExtractionLevel.CHAPTER)
        section_tokens = get_max_tokens_for_level(ExtractionLevel.SECTION)
        chunk_tokens = get_max_tokens_for_level(ExtractionLevel.CHUNK)
        assert chapter_tokens > section_tokens > chunk_tokens
