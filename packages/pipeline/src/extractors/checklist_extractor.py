"""Checklist extractor for verification criteria extraction.

Extracts structured checklists from document chunks for workflow validation.
Used by builder to create BMAD workflow validation steps.
"""

from typing import Optional, Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    Checklist,
    ExtractionBase,
    ExtractionLevel,
    ExtractionParseError,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class ChecklistExtractor(BaseExtractor):
    """Extractor for verification checklists from books.

    Identifies and structures checklists for BMAD workflow validation.
    Used by builder to create validation steps in workflows.

    Supports hierarchical extraction with chapter/section/chunk context levels.
    Note: Checklists are typically extracted at SECTION level (4K tokens).

    Example checklists:
    - Production Deployment Checklist: Items to verify before deploying
    - Model Evaluation Checklist: Criteria for evaluating model quality
    - Security Review Checklist: Security items to verify

    Example:
        extractor = ChecklistExtractor()
        results = await extractor.extract(
            content="Before deploying, verify...",
            source_id="source-456",
            context_level=ExtractionLevel.SECTION,
            context_id="section-123",
            chunk_ids=["chunk-1", "chunk-2"],
        )

        for result in results:
            if result.success:
                checklist = result.extraction
                logger.debug("checklist_parsed", name=checklist.name)
                logger.debug("checklist_items", item_count=len(checklist.items))
    """

    def __init__(self, config: ExtractorConfig | None = None):
        """Initialize the ChecklistExtractor.

        Args:
            config: Optional extractor configuration.
        """
        super().__init__(config)
        self._llm_client = LLMClient()
        logger.debug(
            "checklist_extractor_initialized",
            auto_tag_topics=self.config.auto_tag_topics,
        )

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for checklists."""
        return ExtractionType.CHECKLIST

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Checklist model class."""
        return Checklist

    def get_prompt(self) -> str:
        """Load and return the checklist extraction prompt.

        Combines base extraction instructions with checklist-specific
        instructions from prompts/checklist.md.

        Returns:
            Combined prompt string for LLM extraction.
        """
        return self._load_full_prompt("checklist")

    def auto_tag_topics(self, checklist: Checklist) -> list[str]:
        """Auto-tag topics from checklist content.

        Extracts relevant AI/ML topics from the checklist's name,
        items, and context fields.

        Args:
            checklist: Checklist model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        content_parts = [
            checklist.name,
            " ".join(item.item for item in checklist.items),
            checklist.context or "",
        ]
        combined_content = " ".join(content_parts)

        return self._generate_topics(combined_content)

    async def extract(
        self,
        content: str,
        source_id: str,
        context_level: ExtractionLevel = ExtractionLevel.CHUNK,
        context_id: str = "",
        chunk_ids: Optional[list[str]] = None,
    ) -> list[ExtractionResult]:
        """Extract checklists from content with hierarchical context.

        Uses LLM to identify and extract structured checklists from
        the content. Returns a list of ExtractionResult objects,
        each containing either a successful Checklist extraction or an error.

        Args:
            content: Text content to extract from (single chunk or combined).
            source_id: ID of the source document.
            context_level: Level at which extraction is performed.
            context_id: ID of the context (chapter_id, section_id, or chunk_id).
            chunk_ids: List of chunk IDs combined for this extraction.

        Returns:
            List of ExtractionResult with extracted checklists or errors.
        """
        logger.debug(
            "checklist_extraction_start",
            context_id=context_id,
            context_level=context_level.value,
            source_id=source_id,
            content_length=len(content),
            chunk_count=len(chunk_ids) if chunk_ids else 1,
        )

        try:
            # Get prompt and call LLM
            prompt = self.get_prompt()
            response = await self._llm_client.extract(prompt, content)

            # Parse LLM response
            try:
                parsed_data = self._parse_llm_response(response)
            except ExtractionParseError as e:
                logger.warning(
                    "checklist_parse_failed",
                    context_id=context_id,
                    error=str(e),
                )
                return [
                    ExtractionResult(
                        success=False,
                        error=f"Failed to parse LLM response: {e.message}",
                        raw_response=response,
                    )
                ]

            # Handle empty results
            if not parsed_data:
                logger.debug(
                    "no_checklists_found",
                    context_id=context_id,
                )
                return []

            # Validate and build results
            results = []
            for i, data in enumerate(parsed_data):
                result = self._validate_extraction(
                    data, source_id, context_level, context_id, chunk_ids
                )

                if result.success and result.extraction:
                    # Apply auto-tagging if enabled
                    if self.config.auto_tag_topics:
                        checklist = result.extraction
                        if isinstance(checklist, Checklist):
                            topics = self.auto_tag_topics(checklist)
                            existing_topics = set(checklist.topics)
                            existing_topics.update(topics)
                            checklist.topics = list(existing_topics)[:5]

                    logger.info(
                        "checklist_extracted",
                        context_id=context_id,
                        context_level=context_level.value,
                        source_id=source_id,
                        name=result.extraction.name,
                        item_count=len(result.extraction.items),
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "checklist_validation_failed",
                        context_id=context_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "checklist_extraction_complete",
                context_id=context_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "checklist_extraction_error",
                context_id=context_id,
                source_id=source_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            return [
                ExtractionResult(
                    success=False,
                    error=f"Extraction failed: {e!s}",
                )
            ]


# Register extractor with global registry
extractor_registry.register(ExtractionType.CHECKLIST, ChecklistExtractor)
