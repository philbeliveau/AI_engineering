"""Methodology extractor for step-by-step process extraction.

Extracts structured methodologies from document chunks for BMAD workflow creation.
Used by builder to transform book content into executable workflows.
"""

from typing import Type

import structlog

from src.extractors.base import (
    BaseExtractor,
    ExtractionBase,
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

    Example methodologies:
    - RAG Implementation Methodology: Steps to build a RAG system
    - LLM Evaluation Framework: Process for evaluating model outputs
    - Fine-tuning Workflow: Steps for domain-specific fine-tuning

    Example:
        extractor = MethodologyExtractor()
        results = await extractor.extract(
            chunk_content="Building a RAG system requires...",
            chunk_id="chunk-123",
            source_id="source-456",
        )

        for result in results:
            if result.success:
                methodology = result.extraction
                print(f"Name: {methodology.name}")
                print(f"Steps: {len(methodology.steps)}")
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
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract methodologies from a text chunk.

        Uses LLM to identify and extract structured methodologies from
        the chunk content. Returns a list of ExtractionResult objects,
        each containing either a successful Methodology extraction or an error.

        Args:
            chunk_content: Text content of the chunk to extract from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with extracted methodologies or errors.
        """
        logger.debug(
            "methodology_extraction_start",
            chunk_id=chunk_id,
            source_id=source_id,
            content_length=len(chunk_content),
        )

        try:
            # Get prompt and call LLM
            prompt = self.get_prompt()
            response = await self._llm_client.extract(prompt, chunk_content)

            # Parse LLM response
            try:
                parsed_data = self._parse_llm_response(response)
            except ExtractionParseError as e:
                logger.warning(
                    "methodology_parse_failed",
                    chunk_id=chunk_id,
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
                    chunk_id=chunk_id,
                )
                return []

            # Validate and build results
            results = []
            for i, data in enumerate(parsed_data):
                result = self._validate_extraction(data, chunk_id, source_id)

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
                        chunk_id=chunk_id,
                        source_id=source_id,
                        name=result.extraction.name,
                        step_count=len(result.extraction.steps),
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "methodology_validation_failed",
                        chunk_id=chunk_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "methodology_extraction_complete",
                chunk_id=chunk_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "methodology_extraction_error",
                chunk_id=chunk_id,
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
