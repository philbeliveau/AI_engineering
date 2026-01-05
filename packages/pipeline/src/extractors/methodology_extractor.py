"""Methodology extractor for step-by-step process extraction.

Extracts structured methodologies from document chunks for BMAD workflow creation.
Used by builder to transform book content into executable workflows.
"""

from typing import Optional, Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionBase,
    ExtractionLevel,
    ExtractionParseError,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    Methodology,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class MethodologyExtractor(BaseExtractor):
    """Extractor for step-by-step methodologies from books.

    Identifies and structures process methodologies for BMAD workflow
    creation. Used by builder to transform book content into executable
    workflows.

    Supports hierarchical extraction with chapter/section/chunk context levels.
    Note: Methodologies are typically extracted at CHAPTER level (8K tokens)
    to capture complete multi-step processes.

    Example methodologies:
    - RAG Implementation Methodology: Steps to build a RAG system
    - LLM Evaluation Framework: Process for evaluating model outputs
    - Fine-tuning Workflow: Steps for domain-specific fine-tuning

    Example:
        extractor = MethodologyExtractor()
        results = await extractor.extract(
            content="Building a RAG system requires...",
            source_id="source-456",
            context_level=ExtractionLevel.CHAPTER,
            context_id="chapter-123",
            chunk_ids=["chunk-1", "chunk-2", "chunk-3"],
        )

        for result in results:
            if result.success:
                methodology = result.extraction
                logger.debug("methodology_parsed", name=methodology.name)
                logger.debug("methodology_steps", step_count=len(methodology.steps))
    """

    def __init__(self, config: ExtractorConfig | None = None):
        """Initialize the MethodologyExtractor.

        Args:
            config: Optional extractor configuration.
        """
        super().__init__(config)
        self._llm_client = LLMClient()
        logger.debug(
            "methodology_extractor_initialized",
            auto_tag_topics=self.config.auto_tag_topics,
        )

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for methodologies."""
        return ExtractionType.METHODOLOGY

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Methodology model class."""
        return Methodology

    def get_prompt(self) -> str:
        """Load and return the methodology extraction prompt.

        Combines base extraction instructions with methodology-specific
        instructions from prompts/methodology.md.

        Returns:
            Combined prompt string for LLM extraction.
        """
        return self._load_full_prompt("methodology")

    def auto_tag_topics(self, methodology: Methodology) -> list[str]:
        """Auto-tag topics from methodology content.

        Extracts relevant AI/ML topics from the methodology's name,
        steps, prerequisites, and outputs fields.

        Args:
            methodology: Methodology model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        content_parts = [
            methodology.name,
            " ".join(step.title + " " + step.description for step in methodology.steps),
            " ".join(methodology.prerequisites),
            " ".join(methodology.outputs),
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
        """Extract methodologies from content with hierarchical context.

        Uses LLM to identify and extract structured methodologies from
        the content. Returns a list of ExtractionResult objects,
        each containing either a successful Methodology extraction or an error.

        Args:
            content: Text content to extract from (single chunk or combined).
            source_id: ID of the source document.
            context_level: Level at which extraction is performed.
            context_id: ID of the context (chapter_id, section_id, or chunk_id).
            chunk_ids: List of chunk IDs combined for this extraction.

        Returns:
            List of ExtractionResult with extracted methodologies or errors.
        """
        logger.debug(
            "methodology_extraction_start",
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
                    "methodology_parse_failed",
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
                    "no_methodologies_found",
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
                        methodology = result.extraction
                        if isinstance(methodology, Methodology):
                            topics = self.auto_tag_topics(methodology)
                            existing_topics = set(methodology.topics)
                            existing_topics.update(topics)
                            methodology.topics = list(existing_topics)[:5]

                    logger.info(
                        "methodology_extracted",
                        context_id=context_id,
                        context_level=context_level.value,
                        source_id=source_id,
                        name=result.extraction.name,
                        step_count=len(result.extraction.steps),
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "methodology_validation_failed",
                        context_id=context_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "methodology_extraction_complete",
                context_id=context_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "methodology_extraction_error",
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
extractor_registry.register(ExtractionType.METHODOLOGY, MethodologyExtractor)
