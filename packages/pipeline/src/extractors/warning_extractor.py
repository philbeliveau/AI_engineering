"""Warning extractor for knowledge extraction.

Extracts warnings, gotchas, and anti-patterns from document chunks.
Used by end users to avoid common mistakes via the get_warnings MCP tool.
"""

from typing import Optional, Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionBase,
    ExtractionLevel,
    ExtractionResult,
    ExtractionType,
    Warning,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class WarningExtractor(BaseExtractor):
    """Extractor for warnings, gotchas, and anti-patterns.

    Identifies and structures failure modes, common mistakes, and things
    to avoid from text chunks. Used by end users to prevent costly
    errors via the get_warnings MCP tool.

    Supports hierarchical extraction with chapter/section/chunk context levels.
    Note: Warnings are typically extracted at CHUNK level (512 tokens).

    Example warnings:
    - Context Window Overflow: Sending too many tokens causes truncation
    - Cold Start Latency: First inference is slow due to model loading
    - Embedding Drift: Changing embedding models breaks existing vectors
    """

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for warnings."""
        return ExtractionType.WARNING

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Warning model class."""
        return Warning

    async def extract(
        self,
        content: str,
        source_id: str,
        context_level: ExtractionLevel = ExtractionLevel.CHUNK,
        context_id: str = "",
        chunk_ids: Optional[list[str]] = None,
    ) -> list[ExtractionResult]:
        """Extract warnings from content with hierarchical context.

        Uses LLMClient for automated batch extraction. Parses JSON response
        and validates each warning against the Pydantic model.

        Args:
            content: Text content to extract from (single chunk or combined).
            source_id: ID of the source document.
            context_level: Level at which extraction is performed.
            context_id: ID of the context (chapter_id, section_id, or chunk_id).
            chunk_ids: List of chunk IDs combined for this extraction.

        Returns:
            List of ExtractionResult with Warning extractions.
        """
        logger.info(
            "warning_extraction_started",
            context_id=context_id,
            context_level=context_level.value,
            source_id=source_id,
            content_length=len(content),
            chunk_count=len(chunk_ids) if chunk_ids else 1,
        )

        # Get the extraction prompt with base instructions
        prompt = self.get_prompt()

        results: list[ExtractionResult] = []

        async with LLMClient() as client:
            try:
                # Send content to LLM for extraction
                response = await client.extract(prompt, content)

                # Parse JSON response
                parsed_items = self._parse_llm_response(response)

                # Validate each extraction
                for item in parsed_items:
                    # Auto-tag topics from content
                    if self.config.auto_tag_topics:
                        item["topics"] = self._generate_topics(content)

                    # Validate against Pydantic model with context fields
                    result = self._validate_extraction(
                        item, source_id, context_level, context_id, chunk_ids
                    )
                    results.append(result)

            except Exception as e:
                logger.error(
                    "warning_extraction_failed",
                    context_id=context_id,
                    error=str(e),
                )
                results.append(
                    ExtractionResult(
                        success=False,
                        error=str(e),
                    )
                )

        logger.info(
            "warning_extraction_completed",
            context_id=context_id,
            warning_count=len([r for r in results if r.success]),
            failed_count=len([r for r in results if not r.success]),
        )

        return results

    def get_prompt(self) -> str:
        """Load warning extraction prompt from file.

        Loads the combined prompt by concatenating:
        1. Base instructions from prompts/_base.md (common extraction rules)
        2. Warning-specific guidance from prompts/warning.md

        The prompt includes the {{chunk_content}} placeholder which should
        be replaced with actual chunk text before sending to LLM.

        Returns:
            Combined prompt string (base + warning-specific) for LLM extraction.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        return self._load_full_prompt("warning")


# Register extractor with global registry
extractor_registry.register(ExtractionType.WARNING, WarningExtractor)
