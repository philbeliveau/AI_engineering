"""Decision extractor for extracting decision points from text chunks.

This module provides the DecisionExtractor class that identifies and extracts
structured decision points from document chunks using LLM-based extraction.

Decisions capture choice points where developers need to make choices,
including options, considerations, and recommended approaches.
"""

from typing import Optional, Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    Decision,
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


class DecisionExtractor(BaseExtractor):
    """Extractor for decision points from document chunks.

    Identifies and extracts structured decision points where developers
    need to make choices. Each decision includes the question being asked,
    available options, considerations, and recommended approach if stated.

    Supports hierarchical extraction with chapter/section/chunk context levels.

    Example:
        extractor = DecisionExtractor()
        results = await extractor.extract(
            content="When choosing between RAG and fine-tuning...",
            source_id="source-456",
            context_level=ExtractionLevel.SECTION,
            context_id="section-123",
            chunk_ids=["chunk-1", "chunk-2"],
        )

        for result in results:
            if result.success:
                decision = result.extraction
                logger.debug("decision_parsed", question=decision.question)
                logger.debug("decision_options", options=decision.options)
    """

    def __init__(self, config: ExtractorConfig | None = None):
        """Initialize the DecisionExtractor.

        Args:
            config: Optional extractor configuration.
        """
        super().__init__(config)
        self._llm_client = LLMClient()
        logger.debug(
            "decision_extractor_initialized",
            auto_tag_topics=self.config.auto_tag_topics,
        )

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for this extractor."""
        return ExtractionType.DECISION

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Pydantic model class for Decision extractions."""
        return Decision

    def get_prompt(self) -> str:
        """Load and return the decision extraction prompt.

        Combines base extraction instructions with decision-specific
        instructions from prompts/decision.md.

        Returns:
            Combined prompt string for LLM extraction.
        """
        return self._load_full_prompt("decision")

    def auto_tag_topics(self, decision: Decision) -> list[str]:
        """Auto-tag topics from decision content.

        Extracts relevant AI/ML topics from the decision's question,
        options, considerations, and context fields.

        Args:
            decision: Decision model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        # Combine all text content for topic extraction
        content_parts = [
            decision.question,
            " ".join(decision.options),
            " ".join(decision.considerations),
            decision.context or "",
            decision.recommended_approach or "",
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
        """Extract decision points from content with hierarchical context.

        Uses LLM to identify and extract structured decision points from
        the content. Returns a list of ExtractionResult objects,
        each containing either a successful Decision extraction or an error.

        Args:
            content: Text content to extract from (single chunk or combined).
            source_id: ID of the source document.
            context_level: Level at which extraction is performed.
            context_id: ID of the context (chapter_id, section_id, or chunk_id).
            chunk_ids: List of chunk IDs combined for this extraction.

        Returns:
            List of ExtractionResult with extracted decisions or errors.
        """
        logger.debug(
            "decision_extraction_start",
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
                    "decision_parse_failed",
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
                    "no_decisions_found",
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
                        decision = result.extraction
                        if isinstance(decision, Decision):
                            topics = self.auto_tag_topics(decision)
                            # Merge with any topics from LLM response
                            existing_topics = set(decision.topics)
                            existing_topics.update(topics)
                            decision.topics = list(existing_topics)[:5]

                    logger.info(
                        "decision_extracted",
                        context_id=context_id,
                        context_level=context_level.value,
                        source_id=source_id,
                        question_preview=result.extraction.question[:50] + "..."
                        if len(result.extraction.question) > 50
                        else result.extraction.question,
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "decision_validation_failed",
                        context_id=context_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "decision_extraction_complete",
                context_id=context_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "decision_extraction_error",
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
extractor_registry.register(ExtractionType.DECISION, DecisionExtractor)
