"""Base extractor interface and supporting classes for knowledge extraction.

This module defines the abstract base class for all extractors,
supporting data models, exceptions, and the extractor registry pattern.

Follows NFR6: Extensibility for Extractors pattern from architecture.
"""

import json
import re
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Type

import structlog
from pydantic import BaseModel, Field

from src.exceptions import KnowledgeError

logger = structlog.get_logger()


# ============================================================================
# Enums
# ============================================================================


class ExtractionType(str, Enum):
    """Types of knowledge extractions.

    Each type represents a different category of knowledge that can be
    extracted from source documents.
    """

    DECISION = "decision"
    PATTERN = "pattern"
    WARNING = "warning"
    METHODOLOGY = "methodology"
    CHECKLIST = "checklist"
    PERSONA = "persona"
    WORKFLOW = "workflow"


# ============================================================================
# Base Models
# ============================================================================


class ExtractionBase(BaseModel):
    """Base model for all extraction types.

    All extractions MUST include source attribution for traceability.

    Attributes:
        id: Unique extraction ID (MongoDB ObjectId compatible).
        source_id: Reference to source document.
        chunk_id: Reference to chunk extracted from.
        type: Enum for extraction type.
        topics: Topic tags for filtering.
        schema_version: Schema version for evolution.
        extracted_at: Extraction timestamp.
        confidence: Extraction confidence score (0.0-1.0).
    """

    id: str = ""  # Set by storage layer
    source_id: str
    chunk_id: str
    type: ExtractionType
    topics: list[str] = Field(default_factory=list)
    schema_version: str = "1.0.0"
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ExtractionResult(BaseModel):
    """Result of an extraction attempt.

    Attributes:
        success: Whether extraction succeeded.
        extraction: The extracted data if successful.
        error: Error message if failed.
        raw_response: Raw LLM response for debugging.
    """

    success: bool
    extraction: Optional[ExtractionBase] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


class ExtractorConfig(BaseModel):
    """Configuration for extractor behavior.

    Attributes:
        max_extractions_per_chunk: Limit extractions per chunk.
        min_confidence: Minimum confidence threshold.
        auto_tag_topics: Enable auto-tagging.
        include_context: Include surrounding context.
    """

    max_extractions_per_chunk: int = 5
    min_confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    auto_tag_topics: bool = True
    include_context: bool = True


# ============================================================================
# Type-Specific Extraction Models
# ============================================================================


class Decision(ExtractionBase):
    """Decision point extraction.

    Captures choice points with options and considerations.
    Used by end users for AI engineering guidance.

    Attributes:
        question: The decision point question.
        options: Available options.
        considerations: Factors to consider.
        recommended_approach: Recommended choice if stated.
        context: Surrounding context.
    """

    type: ExtractionType = ExtractionType.DECISION
    question: str
    options: list[str] = Field(default_factory=list)
    considerations: list[str] = Field(default_factory=list)
    recommended_approach: Optional[str] = None
    context: str = ""


class Pattern(ExtractionBase):
    """Reusable pattern extraction.

    Captures code/architecture patterns with examples.
    Used by end users for implementation reference.

    Attributes:
        name: Pattern name.
        problem: Problem it solves.
        solution: Solution approach.
        code_example: Code snippet if applicable.
        context: When to use.
        trade_offs: Pros/cons.
    """

    type: ExtractionType = ExtractionType.PATTERN
    name: str
    problem: str
    solution: str
    code_example: Optional[str] = None
    context: str = ""
    trade_offs: list[str] = Field(default_factory=list)


class Warning(ExtractionBase):
    """Warning/gotcha extraction.

    Captures anti-patterns, failure modes, gotchas.
    Used by end users to avoid common mistakes.

    Attributes:
        title: Warning title.
        description: What the warning is about.
        symptoms: How to recognize the problem.
        consequences: What happens if ignored.
        prevention: How to avoid.
    """

    type: ExtractionType = ExtractionType.WARNING
    title: str
    description: str
    symptoms: list[str] = Field(default_factory=list)
    consequences: list[str] = Field(default_factory=list)
    prevention: str = ""


class MethodologyStep(BaseModel):
    """Single step in a methodology.

    Attributes:
        order: Step number.
        title: Step title.
        description: Step details.
        tips: Optional tips.
    """

    order: int
    title: str
    description: str
    tips: list[str] = Field(default_factory=list)


class Methodology(ExtractionBase):
    """Methodology extraction.

    Captures step-by-step processes from books.
    Used by builder for BMAD workflow creation.

    Attributes:
        name: Methodology name.
        steps: Ordered steps.
        prerequisites: Required before starting.
        outputs: Expected deliverables.
    """

    type: ExtractionType = ExtractionType.METHODOLOGY
    name: str
    steps: list[MethodologyStep] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class ChecklistItem(BaseModel):
    """Single checklist item.

    Attributes:
        item: Checklist item text.
        required: Whether mandatory.
    """

    item: str
    required: bool = True


class Checklist(ExtractionBase):
    """Checklist extraction.

    Captures verification criteria.
    Used by builder for workflow validation steps.

    Attributes:
        name: Checklist name.
        items: Checklist items.
        context: When to use this checklist.
    """

    type: ExtractionType = ExtractionType.CHECKLIST
    name: str
    items: list[ChecklistItem] = Field(default_factory=list)
    context: str = ""


class Persona(ExtractionBase):
    """Persona extraction.

    Captures role definitions.
    Used by builder for BMAD agent creation.

    Attributes:
        role: Role title.
        responsibilities: What they do.
        expertise: Domain expertise.
        communication_style: How they communicate.
    """

    type: ExtractionType = ExtractionType.PERSONA
    role: str
    responsibilities: list[str] = Field(default_factory=list)
    expertise: list[str] = Field(default_factory=list)
    communication_style: str = ""


class WorkflowStep(BaseModel):
    """Single step in a workflow.

    Attributes:
        order: Step number.
        action: What to do.
        outputs: Step outputs.
    """

    order: int
    action: str
    outputs: list[str] = Field(default_factory=list)


class Workflow(ExtractionBase):
    """Workflow extraction.

    Captures process sequences.
    Used by builder for BMAD workflow design.

    Attributes:
        name: Workflow name.
        trigger: What starts the workflow.
        steps: Workflow steps.
        decision_points: Key decision points.
    """

    type: ExtractionType = ExtractionType.WORKFLOW
    name: str
    trigger: str = ""
    steps: list[WorkflowStep] = Field(default_factory=list)
    decision_points: list[str] = Field(default_factory=list)


# ============================================================================
# Exceptions
# ============================================================================


class ExtractorError(KnowledgeError):
    """Base exception for extractor errors."""

    pass


class PromptLoadError(ExtractorError):
    """Raised when prompt file cannot be loaded."""

    def __init__(self, prompt_name: str, reason: str):
        super().__init__(
            code="PROMPT_LOAD_ERROR",
            message=f"Failed to load prompt: {prompt_name}",
            details={"prompt_name": prompt_name, "reason": reason},
        )


class ExtractionParseError(ExtractorError):
    """Raised when LLM response cannot be parsed."""

    def __init__(self, extraction_type: str, reason: str):
        super().__init__(
            code="EXTRACTION_PARSE_ERROR",
            message="Failed to parse extraction response",
            details={"extraction_type": extraction_type, "reason": reason},
        )


class ExtractionValidationError(ExtractorError):
    """Raised when extraction fails Pydantic validation."""

    def __init__(self, extraction_type: str, errors: list[dict]):
        super().__init__(
            code="EXTRACTION_VALIDATION_ERROR",
            message="Extraction validation failed",
            details={"extraction_type": extraction_type, "validation_errors": errors},
        )


class UnsupportedExtractionTypeError(ExtractorError):
    """Raised when extraction type is not supported."""

    def __init__(self, extraction_type: str, supported: list[str]):
        super().__init__(
            code="UNSUPPORTED_EXTRACTION_TYPE",
            message=f"Extraction type not supported: {extraction_type}",
            details={"extraction_type": extraction_type, "supported": supported},
        )


# ============================================================================
# Base Extractor ABC
# ============================================================================


class BaseExtractor(ABC):
    """Abstract base class for knowledge extractors.

    All extractors must extend this class and implement the abstract
    methods for extraction and prompt retrieval.

    Follows NFR6: Extensibility for Extractors pattern.

    Attributes:
        config: Extractor configuration settings.
        prompts_dir: Directory containing extraction prompts.

    Example:
        class DecisionExtractor(BaseExtractor):
            @property
            def extraction_type(self) -> ExtractionType:
                return ExtractionType.DECISION

            @property
            def model_class(self) -> Type[ExtractionBase]:
                return Decision

            def extract(self, chunk_content, chunk_id, source_id):
                # Implementation here
                pass

            def get_prompt(self) -> str:
                return self._load_prompt("decision")
    """

    def __init__(self, config: Optional[ExtractorConfig] = None):
        """Initialize extractor with optional configuration.

        Args:
            config: Extractor configuration. Uses defaults if not provided.
        """
        self.config = config or ExtractorConfig()
        self.prompts_dir = Path(__file__).parent / "prompts"
        logger.debug(
            "extractor_initialized",
            extractor=self.__class__.__name__,
            extraction_type=self.extraction_type.value,
        )

    @property
    @abstractmethod
    def extraction_type(self) -> ExtractionType:
        """The type of extraction this extractor produces."""
        pass

    @property
    @abstractmethod
    def model_class(self) -> Type[ExtractionBase]:
        """The Pydantic model class for this extraction type."""
        pass

    @abstractmethod
    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        """Extract knowledge from a chunk.

        Args:
            chunk_content: Text content of the chunk.
            chunk_id: ID of the chunk being extracted from.
            source_id: ID of the source document.

        Returns:
            List of ExtractionResult with extracted knowledge.
        """
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """Get the extraction prompt for this extractor.

        Returns:
            Prompt string for LLM extraction.
        """
        pass

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt from prompts directory.

        Args:
            prompt_name: Name of prompt file (without .md extension).

        Returns:
            Prompt content as string.

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.md"
        try:
            return prompt_path.read_text()
        except FileNotFoundError:
            raise PromptLoadError(prompt_name, f"File not found: {prompt_path}")
        except Exception as e:
            raise PromptLoadError(prompt_name, str(e))

    def _load_full_prompt(self, prompt_name: str) -> str:
        """Load prompt with base instructions prepended.

        Combines the base extraction instructions (_base.md) with the
        extraction-type-specific prompt for complete LLM instructions.

        Args:
            prompt_name: Name of prompt file (without .md extension).

        Returns:
            Combined prompt content (base + specific).

        Raises:
            PromptLoadError: If prompt file cannot be loaded.
        """
        base_prompt = self._load_prompt("_base")
        specific_prompt = self._load_prompt(prompt_name)
        return f"{base_prompt}\n\n{specific_prompt}"

    def _parse_llm_response(self, response: str) -> list[dict]:
        """Parse LLM response into list of extraction dicts.

        Expects JSON array or single JSON object in response.

        Args:
            response: Raw LLM response string.

        Returns:
            List of parsed dictionaries.

        Raises:
            ExtractionParseError: If response cannot be parsed.
        """
        # Try to extract JSON from response
        try:
            # First try direct JSON parse
            data = json.loads(response)
            if isinstance(data, list):
                return data
            return [data]
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code block
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                if isinstance(data, list):
                    return data
                return [data]
            except json.JSONDecodeError:
                pass

        raise ExtractionParseError(
            self.extraction_type.value,
            "Could not parse JSON from response",
        )

    def _validate_extraction(
        self, data: dict, chunk_id: str, source_id: str
    ) -> ExtractionResult:
        """Validate extraction data against Pydantic model.

        Args:
            data: Parsed extraction dictionary.
            chunk_id: ID of source chunk.
            source_id: ID of source document.

        Returns:
            ExtractionResult with validated extraction or error.
        """
        try:
            # Add required fields
            data["source_id"] = source_id
            data["chunk_id"] = chunk_id
            data["type"] = self.extraction_type

            # Validate with Pydantic model
            extraction = self.model_class(**data)

            return ExtractionResult(success=True, extraction=extraction)
        except Exception as e:
            return ExtractionResult(success=False, error=str(e))

    def _generate_topics(self, content: str) -> list[str]:
        """Auto-generate topic tags from content.

        Simple keyword extraction. Override for more sophisticated tagging.

        Args:
            content: Text content to extract topics from.

        Returns:
            List of topic tags.
        """
        # Common AI/ML topics to look for
        topic_keywords = {
            "rag": ["rag", "retrieval", "augmented generation"],
            "fine-tuning": ["fine-tune", "fine-tuning", "finetune"],
            "embeddings": ["embedding", "embeddings", "vector"],
            "llm": ["llm", "large language model", "gpt", "claude"],
            "prompting": ["prompt", "prompting", "prompt engineering"],
            "evaluation": ["eval", "evaluation", "metrics", "benchmark"],
            "deployment": ["deploy", "deployment", "production", "serving"],
            "training": ["train", "training", "training data"],
            "inference": ["inference", "latency", "throughput"],
            "agents": ["agent", "agents", "autonomous"],
        }

        content_lower = content.lower()
        topics = []

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    topics.append(topic)
                    break

        return topics[:5]  # Limit to 5 topics


# ============================================================================
# Extractor Registry
# ============================================================================


class ExtractorRegistry:
    """Registry for managing knowledge extractors.

    Provides central location for registering and retrieving
    extractors based on extraction type.

    Example:
        registry = ExtractorRegistry()
        registry.register(ExtractionType.DECISION, DecisionExtractor)

        extractor = registry.get_extractor(ExtractionType.DECISION)
        results = extractor.extract(chunk_content, chunk_id, source_id)
    """

    def __init__(self):
        """Initialize empty registry."""
        self._extractors: dict[ExtractionType, Type[BaseExtractor]] = {}
        logger.debug("extractor_registry_initialized")

    def register(
        self,
        extraction_type: ExtractionType,
        extractor_class: Type[BaseExtractor],
    ) -> None:
        """Register an extractor for an extraction type.

        Args:
            extraction_type: Type of extraction to register.
            extractor_class: Extractor class to register.
        """
        if extraction_type in self._extractors:
            logger.warning(
                "extractor_override",
                extraction_type=extraction_type.value,
                old=self._extractors[extraction_type].__name__,
                new=extractor_class.__name__,
            )
        self._extractors[extraction_type] = extractor_class
        logger.info(
            "extractor_registered",
            extraction_type=extraction_type.value,
            extractor=extractor_class.__name__,
        )

    def get_extractor(self, extraction_type: ExtractionType) -> BaseExtractor:
        """Get an extractor instance for an extraction type.

        Args:
            extraction_type: Type to get extractor for.

        Returns:
            Instantiated extractor for the type.

        Raises:
            UnsupportedExtractionTypeError: If no extractor registered.
        """
        if extraction_type not in self._extractors:
            raise UnsupportedExtractionTypeError(
                extraction_type.value,
                [t.value for t in self._extractors.keys()],
            )
        return self._extractors[extraction_type]()

    def list_extraction_types(self) -> list[ExtractionType]:
        """List all registered extraction types.

        Returns:
            List of registered extraction types.
        """
        return list(self._extractors.keys())

    def get_all_extractors(self) -> list[BaseExtractor]:
        """Get instances of all registered extractors.

        Returns:
            List of all extractor instances.
        """
        return [cls() for cls in self._extractors.values()]

    def is_supported(self, extraction_type: ExtractionType) -> bool:
        """Check if an extraction type is supported.

        Args:
            extraction_type: Type to check.

        Returns:
            True if supported, False otherwise.
        """
        return extraction_type in self._extractors


# Module-level registry instance
extractor_registry = ExtractorRegistry()
