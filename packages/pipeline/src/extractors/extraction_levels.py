"""Extraction level configuration for hierarchical knowledge extraction.

This module defines the extraction level enum and configuration for running
different extractors at different context window sizes (chapter/section/chunk).

The hierarchical extraction architecture addresses the 512-token chunk limitation
by matching extraction context to content scope:
- CHAPTER (8K tokens): methodology, workflow (span multiple pages)
- SECTION (4K tokens): decision, pattern, checklist, persona (span 1-3 pages)
- CHUNK (512 tokens): warning (single paragraph)
"""

from typing import Literal

from pydantic import BaseModel, Field

# Import the canonical ExtractionLevel from base to avoid duplicate definitions
from src.extractors.base import ExtractionLevel


class ExtractionLevelConfig(BaseModel):
    """Configuration for a specific extraction level.

    Defines which extractors run at this level and the token budget.

    Attributes:
        level: The extraction level this config applies to.
        extraction_types: List of extraction type strings (e.g., ["methodology", "workflow"]).
        max_tokens: Maximum token budget for combined content at this level.
        combination_strategy: How to handle content exceeding max_tokens.
    """

    level: ExtractionLevel
    extraction_types: list[str] = Field(
        description="Extraction types to run at this level (e.g., 'methodology', 'decision')"
    )
    max_tokens: int = Field(ge=1, description="Maximum token budget for combined content")
    combination_strategy: Literal["truncate", "summary_if_exceeded", "none"] = Field(
        default="truncate",
        description=(
            "Strategy when combined content exceeds max_tokens: "
            "'truncate' cuts at limit, 'summary_if_exceeded' summarizes (future), "
            "'none' means no combination needed (single chunk level)"
        ),
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"ExtractionLevelConfig(level={self.level.value}, "
            f"types={self.extraction_types}, max_tokens={self.max_tokens})"
        )


# =============================================================================
# Extraction Level Configuration
# =============================================================================
# This mapping defines which extractors run at each hierarchical level
# and the token budget for combined content.
#
# Based on content analysis:
# - methodology/workflow: 3-10 pages (need chapter-level context)
# - decision/pattern/checklist/persona: 1-3 pages (need section-level context)
# - warning: 0.5-1 page (fits in single chunk)

EXTRACTION_LEVEL_CONFIG: dict[ExtractionLevel, ExtractionLevelConfig] = {
    ExtractionLevel.CHAPTER: ExtractionLevelConfig(
        level=ExtractionLevel.CHAPTER,
        extraction_types=["methodology", "workflow"],
        max_tokens=8000,
        combination_strategy="summary_if_exceeded",
    ),
    ExtractionLevel.SECTION: ExtractionLevelConfig(
        level=ExtractionLevel.SECTION,
        extraction_types=["decision", "pattern", "checklist", "persona"],
        max_tokens=4000,
        combination_strategy="truncate",
    ),
    ExtractionLevel.CHUNK: ExtractionLevelConfig(
        level=ExtractionLevel.CHUNK,
        extraction_types=["warning"],
        max_tokens=512,
        combination_strategy="none",
    ),
}


def get_level_for_extraction_type(extraction_type: str) -> ExtractionLevel:
    """Get the extraction level for a given extraction type.

    Args:
        extraction_type: The extraction type (e.g., "methodology", "decision", "warning").

    Returns:
        The ExtractionLevel this type should run at.

    Raises:
        ValueError: If extraction_type is not found in any level configuration.
    """
    for level, config in EXTRACTION_LEVEL_CONFIG.items():
        if extraction_type in config.extraction_types:
            return level

    valid_types = []
    for config in EXTRACTION_LEVEL_CONFIG.values():
        valid_types.extend(config.extraction_types)

    raise ValueError(
        f"Unknown extraction type: '{extraction_type}'. "
        f"Valid types: {sorted(valid_types)}"
    )


def get_extraction_types_for_level(level: ExtractionLevel) -> list[str]:
    """Get all extraction types that run at a given level.

    Args:
        level: The extraction level to query.

    Returns:
        List of extraction type strings for that level.
    """
    config = EXTRACTION_LEVEL_CONFIG.get(level)
    return config.extraction_types if config else []


def get_max_tokens_for_level(level: ExtractionLevel) -> int:
    """Get the maximum token budget for a given level.

    Args:
        level: The extraction level to query.

    Returns:
        Maximum token count for that level.

    Raises:
        ValueError: If level is not found in configuration.
    """
    config = EXTRACTION_LEVEL_CONFIG.get(level)
    if config is None:
        raise ValueError(f"Unknown extraction level: {level}")
    return config.max_tokens
