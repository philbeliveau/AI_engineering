"""Persona extractor for role definition extraction.

Extracts structured personas from document chunks for BMAD agent creation.
Used by builder to define AI agent roles and behaviors.
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
    Persona,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class PersonaExtractor(BaseExtractor):
    """Extractor for role/persona definitions from books.

    Identifies and structures persona definitions for BMAD agent creation.
    Used by builder to define agent roles, responsibilities, and behaviors.

    Example personas:
    - RAG Specialist: Expert in retrieval-augmented generation systems
    - ML Engineer: Responsible for model training and evaluation
    - Prompt Engineer: Designs and optimizes prompts for LLM applications

    Example:
        extractor = PersonaExtractor()
        results = await extractor.extract(
            chunk_content="The ML Engineer is responsible for...",
            chunk_id="chunk-123",
            source_id="source-456",
        )

        for result in results:
            if result.success:
                persona = result.extraction
                logger.debug("persona_parsed", role=persona.role)
                logger.debug("persona_details", responsibilities=persona.responsibilities)
    """

    def __init__(self, config: ExtractorConfig | None = None):
        """Initialize the PersonaExtractor.

        Args:
            config: Optional extractor configuration.
        """
        super().__init__(config)
        self._llm_client = LLMClient()
        logger.debug(
            "persona_extractor_initialized",
            auto_tag_topics=self.config.auto_tag_topics,
        )

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for personas."""
        return ExtractionType.PERSONA

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Persona model class."""
        return Persona

    def get_prompt(self) -> str:
        """Load and return the persona extraction prompt.

        Combines base extraction instructions with persona-specific
        instructions from prompts/persona.md.

        Returns:
            Combined prompt string for LLM extraction.
        """
        return self._load_full_prompt("persona")

    def auto_tag_topics(self, persona: Persona) -> list[str]:
        """Auto-tag topics from persona content.

        Extracts relevant AI/ML topics from the persona's role,
        responsibilities, expertise, and communication style fields.

        Args:
            persona: Persona model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        content_parts = [
            persona.role,
            " ".join(persona.responsibilities),
            " ".join(persona.expertise),
            persona.communication_style or "",
        ]
        combined_content = " ".join(content_parts)

        return self._generate_topics(combined_content)

    async def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract personas from a text chunk.

        Uses LLM to identify and extract structured personas from
        the chunk content. Returns a list of ExtractionResult objects,
        each containing either a successful Persona extraction or an error.

        Args:
            chunk_content: Text content of the chunk to extract from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with extracted personas or errors.
        """
        logger.debug(
            "persona_extraction_start",
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
                    "persona_parse_failed",
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
                    "no_personas_found",
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
                        persona = result.extraction
                        if isinstance(persona, Persona):
                            topics = self.auto_tag_topics(persona)
                            existing_topics = set(persona.topics)
                            existing_topics.update(topics)
                            persona.topics = list(existing_topics)[:5]

                    logger.info(
                        "persona_extracted",
                        chunk_id=chunk_id,
                        source_id=source_id,
                        role=result.extraction.role,
                        responsibility_count=len(result.extraction.responsibilities),
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "persona_validation_failed",
                        chunk_id=chunk_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "persona_extraction_complete",
                chunk_id=chunk_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "persona_extraction_error",
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
extractor_registry.register(ExtractionType.PERSONA, PersonaExtractor)
