"""Warning extractor for knowledge extraction.

Extracts warnings, gotchas, and anti-patterns from document chunks.
Used by end users to avoid common mistakes via the get_warnings MCP tool.
"""

from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionBase,
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

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Sync extraction placeholder - use extract_async() for real extraction.

        This method satisfies the BaseExtractor ABC interface but returns an
        empty list. For actual LLM-based extraction, use the async method
        extract_async() which integrates with LLMClient.

        Note:
            Production pipelines should use extract_async() for real extraction.
            This sync method is provided for interface compliance and testing.

        Args:
            chunk_content: Text content to extract warnings from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            Empty list. Use extract_async() for actual extractions.
        """
        logger.info(
            "warning_extraction_started",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content),
            mode="sync_placeholder",
        )

        # Sync method returns empty - real extraction uses extract_async()
        results: list[ExtractionResult] = []

        logger.info(
            "warning_extraction_completed",
            chunk_id=chunk_id,
            warning_count=len(results),
            mode="sync_placeholder",
        )

        return results

    async def extract_async(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract warnings from chunk content asynchronously.

        Uses LLMClient for automated batch extraction. Parses JSON response
        and validates each warning against the Pydantic model.

        Args:
            chunk_content: Text content to extract warnings from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with Warning extractions.
        """
        logger.info(
            "warning_extraction_started",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content),
        )

        # Get the extraction prompt with base instructions
        prompt = self.get_prompt()

        results: list[ExtractionResult] = []

        async with LLMClient() as client:
            try:
                # Send chunk content to LLM for extraction
                response = await client.extract(prompt, chunk_content)

                # Parse JSON response
                parsed_items = self._parse_llm_response(response)

                # Validate each extraction
                for item in parsed_items:
                    # Auto-tag topics from content
                    if self.config.auto_tag_topics:
                        item["topics"] = self._generate_topics(chunk_content)

                    # Validate against Pydantic model
                    result = self._validate_extraction(item, chunk_id, source_id)
                    results.append(result)

            except Exception as e:
                logger.error(
                    "warning_extraction_failed",
                    chunk_id=chunk_id,
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
            chunk_id=chunk_id,
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
