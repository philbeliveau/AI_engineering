"""Workflow extractor for process sequence extraction.

Extracts structured workflows from document chunks for BMAD workflow design.
Used by builder to create executable process sequences.
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
    Workflow,
    extractor_registry,
)
from src.extractors.llm_client import LLMClient

logger = structlog.get_logger()


class WorkflowExtractor(BaseExtractor):
    """Extractor for process workflows from books.

    Identifies and structures process workflows for BMAD workflow design.
    Used by builder to create executable process sequences with triggers
    and decision points.

    Example workflows:
    - Document Ingestion Workflow: Steps for processing documents
    - Model Retraining Workflow: Triggered by performance degradation
    - Query Processing Workflow: Steps for handling user queries

    Example:
        extractor = WorkflowExtractor()
        results = await extractor.extract(
            chunk_content="When performance drops, trigger retraining...",
            chunk_id="chunk-123",
            source_id="source-456",
        )

        for result in results:
            if result.success:
                workflow = result.extraction
                print(f"Name: {workflow.name}")
                print(f"Trigger: {workflow.trigger}")
    """

    def __init__(self, config: ExtractorConfig | None = None):
        """Initialize the WorkflowExtractor.

        Args:
            config: Optional extractor configuration.
        """
        super().__init__(config)
        self._llm_client = LLMClient()
        logger.debug(
            "workflow_extractor_initialized",
            auto_tag_topics=self.config.auto_tag_topics,
        )

    @property
    def extraction_type(self) -> ExtractionType:
        """Return the extraction type for workflows."""
        return ExtractionType.WORKFLOW

    @property
    def model_class(self) -> Type[ExtractionBase]:
        """Return the Workflow model class."""
        return Workflow

    def get_prompt(self) -> str:
        """Load and return the workflow extraction prompt.

        Combines base extraction instructions with workflow-specific
        instructions from prompts/workflow.md.

        Returns:
            Combined prompt string for LLM extraction.
        """
        return self._load_full_prompt("workflow")

    def auto_tag_topics(self, workflow: Workflow) -> list[str]:
        """Auto-tag topics from workflow content.

        Extracts relevant AI/ML topics from the workflow's name,
        trigger, steps, and decision points fields.

        Args:
            workflow: Workflow model to extract topics from.

        Returns:
            List of topic tags (maximum 5).
        """
        content_parts = [
            workflow.name,
            workflow.trigger or "",
            " ".join(step.action for step in workflow.steps),
            " ".join(workflow.decision_points),
        ]
        combined_content = " ".join(content_parts)

        return self._generate_topics(combined_content)

    async def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract workflows from a text chunk.

        Uses LLM to identify and extract structured workflows from
        the chunk content. Returns a list of ExtractionResult objects,
        each containing either a successful Workflow extraction or an error.

        Args:
            chunk_content: Text content of the chunk to extract from.
            chunk_id: ID of the source chunk.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with extracted workflows or errors.
        """
        logger.debug(
            "workflow_extraction_start",
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
                    "workflow_parse_failed",
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
                    "no_workflows_found",
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
                        workflow = result.extraction
                        if isinstance(workflow, Workflow):
                            topics = self.auto_tag_topics(workflow)
                            existing_topics = set(workflow.topics)
                            existing_topics.update(topics)
                            workflow.topics = list(existing_topics)[:5]

                    logger.info(
                        "workflow_extracted",
                        chunk_id=chunk_id,
                        source_id=source_id,
                        name=result.extraction.name,
                        step_count=len(result.extraction.steps),
                        topics=result.extraction.topics,
                    )
                else:
                    logger.warning(
                        "workflow_validation_failed",
                        chunk_id=chunk_id,
                        extraction_index=i,
                        error=result.error,
                    )

                results.append(result)

            logger.debug(
                "workflow_extraction_complete",
                chunk_id=chunk_id,
                total_extractions=len(results),
                successful=sum(1 for r in results if r.success),
            )

            return results

        except Exception as e:
            logger.error(
                "workflow_extraction_error",
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
extractor_registry.register(ExtractionType.WORKFLOW, WorkflowExtractor)
