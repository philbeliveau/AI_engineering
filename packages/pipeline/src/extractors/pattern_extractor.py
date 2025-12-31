"""Pattern extractor for reusable code/architecture patterns.

This module extracts implementation patterns from document chunks,
capturing problem-solution pairs with code examples and trade-offs.
"""

from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionBase,
    ExtractionResult,
    ExtractionType,
    Pattern,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class PatternExtractor(BaseExtractor):
    """Extractor for reusable code/architecture patterns.

    Identifies and structures implementation patterns from text chunks,
    including code examples when present. Used by end users for
    implementation reference via the get_patterns MCP tool.

    Example patterns:
    - Semantic Caching: Cache LLM responses based on semantic similarity
    - Chunking Strategy: Split documents for optimal retrieval
    - Prompt Template: Reusable prompt structure for specific tasks

    Attributes:
        llm_client: Client for LLM-based extraction.
    """

    def __init__(self, llm_client: LLMClient | None = None, **kwargs):
        """Initialize pattern extractor.

        Args:
            llm_client: Optional LLM client. Creates new instance if not provided.
            **kwargs: Additional arguments passed to BaseExtractor.
        """
        super().__init__(**kwargs)
        self._llm_client = llm_client

    @property
    def llm_client(self) -> LLMClient:
        """Get or create LLM client.

        Returns:
            LLM client instance for extraction.
        """
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for patterns.

        Returns:
            ExtractionType.PATTERN enum value.
        """
        return ExtractionType.PATTERN

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Pattern model class.

        Returns:
            Pattern Pydantic model class.
        """
        return Pattern

    async def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract patterns from chunk content.

        Uses LLM to identify reusable patterns in the text. Each pattern
        includes name, problem, solution, and optionally code examples
        and trade-offs.

        Args:
            chunk_content: Text content to extract patterns from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with Pattern extractions.
        """
        logger.info(
            "pattern_extraction_started",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content),
        )

        # Get extraction prompt
        prompt = self.get_prompt()

        # Call LLM for extraction
        try:
            raw_response = await self.llm_client.extract(
                prompt=prompt,
                content=chunk_content,
            )
        except Exception as e:
            logger.error(
                "pattern_extraction_llm_failed",
                chunk_id=chunk_id,
                error=str(e),
            )
            return [
                ExtractionResult(
                    success=False,
                    error=f"Extraction failed: {e!s}",
                    raw_response=None,
                )
            ]

        # Parse LLM response to list of dicts
        try:
            parsed_data = self._parse_llm_response(raw_response)
        except Exception as e:
            logger.warning(
                "pattern_extraction_parse_failed",
                chunk_id=chunk_id,
                error=str(e),
                raw_response=raw_response[:500] if raw_response else None,
            )
            return [
                ExtractionResult(
                    success=False,
                    error=f"Failed to parse LLM response: {e}",
                    raw_response=raw_response,
                )
            ]

        # Handle empty array response (no patterns found)
        if not parsed_data:
            logger.info(
                "pattern_extraction_no_patterns",
                chunk_id=chunk_id,
                source_id=source_id,
            )
            return []

        # Validate each extraction and generate topics
        results: list[ExtractionResult] = []
        for i, data in enumerate(parsed_data):
            # Validate with Pydantic model (confidence default handled by model)
            result = self._validate_extraction(data, chunk_id, source_id)

            if result.success and result.extraction:
                # Apply auto-tagging if enabled
                if self.config.auto_tag_topics:
                    pattern = result.extraction
                    if isinstance(pattern, Pattern):
                        topics = self.auto_tag_topics(pattern)
                        # Merge with any topics from LLM response
                        existing_topics = set(pattern.topics)
                        existing_topics.update(topics)
                        pattern.topics = list(existing_topics)[:5]

                logger.info(
                    "pattern_extracted",
                    chunk_id=chunk_id,
                    source_id=source_id,
                    pattern_name=result.extraction.name[:50] + "..."
                    if len(result.extraction.name) > 50
                    else result.extraction.name,
                    topics=result.extraction.topics,
                )
            else:
                logger.warning(
                    "pattern_validation_failed",
                    chunk_id=chunk_id,
                    extraction_index=i,
                    pattern_name=data.get("name"),
                    error=result.error,
                )

            results.append(result)

        successful = sum(1 for r in results if r.success)
        logger.info(
            "pattern_extraction_completed",
            chunk_id=chunk_id,
            source_id=source_id,
            pattern_count=successful,
            total_parsed=len(parsed_data),
        )

        return results

    def get_prompt(self) -> str:
        """Load pattern extraction prompt from file.

        Returns:
            Combined base + pattern-specific prompt for LLM extraction.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        return self._load_full_prompt("pattern")

    def auto_tag_topics(self, pattern: Pattern) -> list[str]:
        """Auto-tag topics from pattern content.

        Extracts relevant AI/ML topics from the pattern's name, problem,
        solution, and context fields.

        Args:
            pattern: Pattern model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        content_parts = [
            pattern.name,
            pattern.problem,
            pattern.solution,
            pattern.context or "",
            " ".join(pattern.trade_offs) if pattern.trade_offs else "",
        ]
        combined_content = " ".join(content_parts)

        return self._generate_topics(combined_content)


# Register extractor with global registry
extractor_registry.register(ExtractionType.PATTERN, PatternExtractor)
