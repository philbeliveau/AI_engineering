# Story 3.1: Base Extractor Interface and Extraction Models

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **developer**,
I want an abstract base class for extractors and Pydantic models for each extraction type,
So that all extractors follow a consistent pattern and extraction outputs are validated.

## Acceptance Criteria

**Given** the extractors module exists
**When** I create a new extractor by extending BaseExtractor
**Then** the extractor must implement `extract()` and `get_prompt()` methods
**And** type-specific Pydantic models exist for Decision, Pattern, Warning, Methodology, Checklist, Persona, Workflow
**And** all extraction models include `source_id`, `chunk_id`, `topics[]`, and `schema_version`
**And** the pattern follows NFR6 (Extensibility for Extractors)

## Dependency Analysis

**Depends On:**
- **Story 1.1** (Initialize Monorepo Structure) - MUST be completed first
  - Requires `packages/pipeline/src/` directory structure
  - Requires Python 3.11+ environment with uv
- **Story 1.3** (Pydantic Models for Core Entities) - MUST be completed first
  - Requires base `Extraction` model for extraction schema
  - Requires schema version pattern for document evolution
- **Story 1.4** (MongoDB Storage Client) - Recommended completed
  - Provides storage patterns for extraction persistence
- **Story 2.1** (Base Source Adapter Interface) - Recommended pattern reference
  - Demonstrates ABC pattern, registry pattern, exception hierarchy

**Blocks:**
- **Story 3.2** (Decision Extractor) - Needs base class to extend
- **Story 3.3** (Pattern Extractor) - Needs base class to extend
- **Story 3.4** (Warning Extractor) - Needs base class to extend
- **Story 3.5** (Methodology and Process Extractors) - Needs base class to extend
- **Story 3.6** (Extraction Storage and Embedding) - Uses extraction models
- **Story 3.7** (Extraction Pipeline CLI) - Uses extractors and registry

## Tasks / Subtasks

- [ ] **Task 1: Verify Prerequisites** (AC: Dependencies available)
  - [ ] Confirm Story 1.1 complete: `ls packages/pipeline/pyproject.toml`
  - [ ] Confirm Story 1.3 complete: `cd packages/pipeline && uv run python -c "from src.models import Source, Chunk, Extraction; print('OK')"`
  - [ ] Confirm Python 3.11+: `cd packages/pipeline && uv run python --version`
  - [ ] Confirm adapters module exists (Story 2.1 pattern reference): `ls packages/pipeline/src/adapters/base.py`

- [ ] **Task 2: Create Extractors Module Structure** (AC: Module exists)
  - [ ] Create `packages/pipeline/src/extractors/` directory
  - [ ] Create `packages/pipeline/src/extractors/__init__.py`
  - [ ] Create `packages/pipeline/src/extractors/base.py`
  - [ ] Create `packages/pipeline/src/extractors/prompts/` directory for extraction prompts

- [ ] **Task 3: Define Base Extraction Models** (AC: Common fields validated)
  - [ ] Create `ExtractionBase` Pydantic model with common fields:
    - `id: str` - Unique extraction ID (MongoDB ObjectId compatible)
    - `source_id: str` - Reference to source document
    - `chunk_id: str` - Reference to chunk extracted from
    - `type: ExtractionType` - Enum for extraction type
    - `topics: list[str]` - Topic tags for filtering
    - `schema_version: str` - Schema version for evolution
    - `extracted_at: datetime` - Extraction timestamp
    - `confidence: float` - Extraction confidence score (0.0-1.0)
  - [ ] Create `ExtractionType` enum: DECISION, PATTERN, WARNING, METHODOLOGY, CHECKLIST, PERSONA, WORKFLOW
  - [ ] Create `ExtractionResult` model for extractor output with validation status

- [ ] **Task 4: Define Type-Specific Extraction Models** (AC: All 7 types defined)
  - [ ] Create `Decision` model extending ExtractionBase:
    - `question: str` - The decision point question
    - `options: list[str]` - Available options
    - `considerations: list[str]` - Factors to consider
    - `recommended_approach: str | None` - Recommended choice if stated
    - `context: str` - Surrounding context
  - [ ] Create `Pattern` model extending ExtractionBase:
    - `name: str` - Pattern name
    - `problem: str` - Problem it solves
    - `solution: str` - Solution approach
    - `code_example: str | None` - Code snippet if applicable
    - `context: str` - When to use
    - `trade_offs: list[str]` - Pros/cons
  - [ ] Create `Warning` model extending ExtractionBase:
    - `title: str` - Warning title
    - `description: str` - What the warning is about
    - `symptoms: list[str]` - How to recognize the problem
    - `consequences: list[str]` - What happens if ignored
    - `prevention: str` - How to avoid
  - [ ] Create `Methodology` model extending ExtractionBase:
    - `name: str` - Methodology name
    - `steps: list[MethodologyStep]` - Ordered steps
    - `prerequisites: list[str]` - Required before starting
    - `outputs: list[str]` - Expected deliverables
  - [ ] Create `MethodologyStep` model:
    - `order: int` - Step number
    - `title: str` - Step title
    - `description: str` - Step details
    - `tips: list[str]` - Optional tips
  - [ ] Create `Checklist` model extending ExtractionBase:
    - `name: str` - Checklist name
    - `items: list[ChecklistItem]` - Checklist items
    - `context: str` - When to use this checklist
  - [ ] Create `ChecklistItem` model:
    - `item: str` - Checklist item text
    - `required: bool` - Whether mandatory
  - [ ] Create `Persona` model extending ExtractionBase:
    - `role: str` - Role title
    - `responsibilities: list[str]` - What they do
    - `expertise: list[str]` - Domain expertise
    - `communication_style: str` - How they communicate
  - [ ] Create `Workflow` model extending ExtractionBase:
    - `name: str` - Workflow name
    - `trigger: str` - What starts the workflow
    - `steps: list[WorkflowStep]` - Workflow steps
    - `decision_points: list[str]` - Key decision points
  - [ ] Create `WorkflowStep` model:
    - `order: int` - Step number
    - `action: str` - What to do
    - `outputs: list[str]` - Step outputs

- [ ] **Task 5: Implement BaseExtractor ABC** (AC: Abstract methods defined)
  - [ ] Create `BaseExtractor` abstract base class
  - [ ] Define abstract method: `extract(chunk_content: str, chunk_id: str, source_id: str) -> list[ExtractionResult]`
  - [ ] Define abstract method: `get_prompt() -> str`
  - [ ] Define abstract property: `extraction_type: ExtractionType`
  - [ ] Define abstract property: `model_class: Type[ExtractionBase]`
  - [ ] Add `__init__(self, config: ExtractorConfig = None)` constructor
  - [ ] Implement `_parse_llm_response(response: str) -> list[dict]` for JSON parsing
  - [ ] Implement `_validate_extraction(data: dict) -> ExtractionResult` using Pydantic model
  - [ ] Implement `_generate_topics(content: str) -> list[str]` for auto-tagging

- [ ] **Task 6: Implement ExtractorConfig** (AC: Configuration available)
  - [ ] Create `ExtractorConfig` Pydantic model:
    - `max_extractions_per_chunk: int = 5` - Limit extractions per chunk
    - `min_confidence: float = 0.5` - Minimum confidence threshold
    - `auto_tag_topics: bool = True` - Enable auto-tagging
    - `include_context: bool = True` - Include surrounding context

- [ ] **Task 7: Implement Extractor Exceptions** (AC: Error handling)
  - [ ] Create `ExtractorError` base exception inheriting from `KnowledgeError`
  - [ ] Create `PromptLoadError` for prompt file loading failures
  - [ ] Create `ExtractionParseError` for LLM response parsing failures
  - [ ] Create `ExtractionValidationError` for Pydantic validation failures
  - [ ] Create `UnsupportedExtractionTypeError` for unknown extraction types
  - [ ] All exceptions follow structured format: `{code, message, details}`

- [ ] **Task 8: Implement Extractor Registry** (AC: Extensibility pattern)
  - [ ] Create `ExtractorRegistry` class for managing extractors
  - [ ] Implement `register(extraction_type: ExtractionType, extractor_class: Type[BaseExtractor])` method
  - [ ] Implement `get_extractor(extraction_type: ExtractionType) -> BaseExtractor` method
  - [ ] Implement `list_extraction_types() -> list[ExtractionType]` method
  - [ ] Implement `get_all_extractors() -> list[BaseExtractor]` method
  - [ ] Create module-level registry instance: `extractor_registry = ExtractorRegistry()`

- [ ] **Task 9: Create Prompt Templates Directory** (AC: Prompts structure ready)
  - [ ] Create `packages/pipeline/src/extractors/prompts/` directory
  - [ ] Create `_base.md` with common extraction instructions
  - [ ] Create placeholder files for each extraction type (to be filled in Stories 3.2-3.5):
    - `decision.md`, `pattern.md`, `warning.md`, `methodology.md`
    - `checklist.md`, `persona.md`, `workflow.md`
  - [ ] Implement `_load_prompt(prompt_name: str) -> str` utility method in base class

- [ ] **Task 10: Create Module Exports** (AC: Clean imports)
  - [ ] Export from `packages/pipeline/src/extractors/__init__.py`:
    - `BaseExtractor`
    - `ExtractionType`, `ExtractionBase`, `ExtractionResult`
    - All type-specific models: `Decision`, `Pattern`, `Warning`, `Methodology`, `Checklist`, `Persona`, `Workflow`
    - `ExtractorConfig`
    - All exceptions
    - `ExtractorRegistry`, `extractor_registry`
  - [ ] Verify imports work: `from src.extractors import BaseExtractor, Decision, extractor_registry`

- [ ] **Task 11: Create Unit Tests** (AC: ABC works correctly)
  - [ ] Create `packages/pipeline/tests/test_extractors/` directory
  - [ ] Create `packages/pipeline/tests/test_extractors/conftest.py` with test fixtures
  - [ ] Create `packages/pipeline/tests/test_extractors/test_base.py`
  - [ ] Create `packages/pipeline/tests/test_extractors/test_models.py`
  - [ ] Test that BaseExtractor cannot be instantiated directly
  - [ ] Test that concrete implementation must define abstract methods
  - [ ] Test all Pydantic models validate correctly
  - [ ] Test all models include required common fields (source_id, chunk_id, topics, schema_version)
  - [ ] Test registry registers and retrieves extractors
  - [ ] Test exception hierarchy and structured error format
  - [ ] Test prompt loading utility
  - [ ] Document test results in completion notes

## Dev Notes

### NFR6 Extensibility Pattern Requirement

**From Architecture Document (architecture.md:80):**

> NFR6: Extensibility (Extractors) - Abstract extractor patterns enabling new extraction types

This story implements the core extractor pattern that enables easy addition of new extraction types without modifying existing code. Follow the same ABC + Registry pattern established in Story 2.1 for adapters.

### Architecture-Specified Directory Structure

**From Architecture Document (architecture.md:623-636):**

```
packages/pipeline/
├── src/
│   ├── extractors/            # FR-2: Knowledge Extraction <-- YOUR WORK HERE
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── decision_extractor.py   # Story 3.2
│   │   ├── pattern_extractor.py    # Story 3.3
│   │   ├── warning_extractor.py    # Story 3.4
│   │   ├── methodology_extractor.py # Story 3.5
│   │   └── prompts/
│   │       ├── decision.md
│   │       ├── pattern.md
│   │       ├── warning.md
│   │       └── methodology.md
```

### Extraction Types from Requirements

**From Epics Document (epics.md:62-73) and Architecture (architecture.md:62-73):**

| Type | Audience | Purpose | FR |
|------|----------|---------|-----|
| Decision | End User | Choice points with options and considerations | FR2.1 |
| Pattern | End User | Reusable code/architecture implementations | FR2.2 |
| Warning | End User | Gotchas, anti-patterns, failure modes | FR2.3 |
| Methodology | Builder | Step-by-step processes from books | FR2.4 |
| Checklist | Builder | Verification criteria for workflow steps | FR2.5 |
| Persona | Builder | Role definitions for agent creation | FR2.6 |
| Workflow | Builder | Process sequences for BMAD workflow design | FR2.7 |

### Abstract Base Class Pattern

**Reference Implementation (following Story 2.1 adapter pattern):**

```python
# packages/pipeline/src/extractors/base.py
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Type
from pydantic import BaseModel, Field
import structlog

from src.exceptions import KnowledgeError

logger = structlog.get_logger()


class ExtractionType(str, Enum):
    """Types of knowledge extractions."""
    DECISION = "decision"
    PATTERN = "pattern"
    WARNING = "warning"
    METHODOLOGY = "methodology"
    CHECKLIST = "checklist"
    PERSONA = "persona"
    WORKFLOW = "workflow"


class ExtractionBase(BaseModel):
    """Base model for all extraction types.

    All extractions MUST include source attribution for traceability.
    """
    id: str = ""  # Set by storage layer
    source_id: str  # Reference to sources collection
    chunk_id: str  # Reference to chunks collection
    type: ExtractionType
    topics: list[str] = []
    schema_version: str = "1.0.0"
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ExtractionResult(BaseModel):
    """Result of an extraction attempt."""
    success: bool
    extraction: Optional[ExtractionBase] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


class ExtractorConfig(BaseModel):
    """Configuration for extractor behavior."""
    max_extractions_per_chunk: int = 5
    min_confidence: float = 0.5
    auto_tag_topics: bool = True
    include_context: bool = True


# Type-specific models
class Decision(ExtractionBase):
    """Decision point extraction.

    Captures choice points with options and considerations.
    Used by end users for AI engineering guidance.
    """
    type: ExtractionType = ExtractionType.DECISION
    question: str  # The decision point question
    options: list[str] = []  # Available options
    considerations: list[str] = []  # Factors to consider
    recommended_approach: Optional[str] = None  # If source recommends
    context: str = ""  # Surrounding context


class Pattern(ExtractionBase):
    """Reusable pattern extraction.

    Captures code/architecture patterns with examples.
    Used by end users for implementation reference.
    """
    type: ExtractionType = ExtractionType.PATTERN
    name: str  # Pattern name
    problem: str  # Problem it solves
    solution: str  # Solution approach
    code_example: Optional[str] = None  # Code snippet
    context: str = ""  # When to use
    trade_offs: list[str] = []  # Pros/cons


class Warning(ExtractionBase):
    """Warning/gotcha extraction.

    Captures anti-patterns, failure modes, gotchas.
    Used by end users to avoid common mistakes.
    """
    type: ExtractionType = ExtractionType.WARNING
    title: str  # Warning title
    description: str  # What the warning is about
    symptoms: list[str] = []  # How to recognize
    consequences: list[str] = []  # What happens if ignored
    prevention: str = ""  # How to avoid


class MethodologyStep(BaseModel):
    """Single step in a methodology."""
    order: int
    title: str
    description: str
    tips: list[str] = []


class Methodology(ExtractionBase):
    """Methodology extraction.

    Captures step-by-step processes from books.
    Used by builder for BMAD workflow creation.
    """
    type: ExtractionType = ExtractionType.METHODOLOGY
    name: str  # Methodology name
    steps: list[MethodologyStep] = []  # Ordered steps
    prerequisites: list[str] = []  # Required before starting
    outputs: list[str] = []  # Expected deliverables


class ChecklistItem(BaseModel):
    """Single checklist item."""
    item: str
    required: bool = True


class Checklist(ExtractionBase):
    """Checklist extraction.

    Captures verification criteria.
    Used by builder for workflow validation steps.
    """
    type: ExtractionType = ExtractionType.CHECKLIST
    name: str  # Checklist name
    items: list[ChecklistItem] = []  # Checklist items
    context: str = ""  # When to use


class Persona(ExtractionBase):
    """Persona extraction.

    Captures role definitions.
    Used by builder for BMAD agent creation.
    """
    type: ExtractionType = ExtractionType.PERSONA
    role: str  # Role title
    responsibilities: list[str] = []  # What they do
    expertise: list[str] = []  # Domain expertise
    communication_style: str = ""  # How they communicate


class WorkflowStep(BaseModel):
    """Single step in a workflow."""
    order: int
    action: str
    outputs: list[str] = []


class Workflow(ExtractionBase):
    """Workflow extraction.

    Captures process sequences.
    Used by builder for BMAD workflow design.
    """
    type: ExtractionType = ExtractionType.WORKFLOW
    name: str  # Workflow name
    trigger: str = ""  # What starts the workflow
    steps: list[WorkflowStep] = []  # Workflow steps
    decision_points: list[str] = []  # Key decision points


# Exception classes
class ExtractorError(KnowledgeError):
    """Base exception for extractor errors."""
    pass


class PromptLoadError(ExtractorError):
    """Raised when prompt file cannot be loaded."""
    def __init__(self, prompt_name: str, reason: str):
        super().__init__(
            code="PROMPT_LOAD_ERROR",
            message=f"Failed to load prompt: {prompt_name}",
            details={"prompt_name": prompt_name, "reason": reason}
        )


class ExtractionParseError(ExtractorError):
    """Raised when LLM response cannot be parsed."""
    def __init__(self, extraction_type: str, reason: str):
        super().__init__(
            code="EXTRACTION_PARSE_ERROR",
            message=f"Failed to parse extraction response",
            details={"extraction_type": extraction_type, "reason": reason}
        )


class ExtractionValidationError(ExtractorError):
    """Raised when extraction fails Pydantic validation."""
    def __init__(self, extraction_type: str, errors: list[dict]):
        super().__init__(
            code="EXTRACTION_VALIDATION_ERROR",
            message=f"Extraction validation failed",
            details={"extraction_type": extraction_type, "validation_errors": errors}
        )


class UnsupportedExtractionTypeError(ExtractorError):
    """Raised when extraction type is not supported."""
    def __init__(self, extraction_type: str, supported: list[str]):
        super().__init__(
            code="UNSUPPORTED_EXTRACTION_TYPE",
            message=f"Extraction type not supported: {extraction_type}",
            details={"extraction_type": extraction_type, "supported": supported}
        )


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
            extraction_type=self.extraction_type.value
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
        source_id: str
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

    # Utility methods

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
        import json
        import re

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
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
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
            "Could not parse JSON from response"
        )

    def _validate_extraction(self, data: dict, chunk_id: str, source_id: str) -> ExtractionResult:
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

            return ExtractionResult(
                success=True,
                extraction=extraction
            )
        except Exception as e:
            return ExtractionResult(
                success=False,
                error=str(e)
            )

    def _generate_topics(self, content: str) -> list[str]:
        """Auto-generate topic tags from content.

        Simple keyword extraction. Override for more sophisticated tagging.

        Args:
            content: Text content to extract topics from.

        Returns:
            List of topic tags.
        """
        # Basic implementation - extract key terms
        # In production, use NLP or LLM for better tagging
        import re

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
        extractor_class: Type[BaseExtractor]
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
                new=extractor_class.__name__
            )
        self._extractors[extraction_type] = extractor_class
        logger.info(
            "extractor_registered",
            extraction_type=extraction_type.value,
            extractor=extractor_class.__name__
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
                [t.value for t in self._extractors.keys()]
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
```

### Module Exports

```python
# packages/pipeline/src/extractors/__init__.py
"""Knowledge extractors for the knowledge pipeline.

This module provides the base extractor interface and registry
for extracting structured knowledge from document chunks.

Example:
    from src.extractors import BaseExtractor, Decision, extractor_registry

    class MyExtractor(BaseExtractor):
        @property
        def extraction_type(self):
            return ExtractionType.DECISION

        @property
        def model_class(self):
            return Decision

        def extract(self, chunk_content, chunk_id, source_id):
            # Implementation
            pass

        def get_prompt(self):
            return self._load_prompt("decision")

    extractor_registry.register(ExtractionType.DECISION, MyExtractor)
"""

from src.extractors.base import (
    # Enums
    ExtractionType,
    # Base models
    ExtractionBase,
    ExtractionResult,
    ExtractorConfig,
    # Type-specific models
    Decision,
    Pattern,
    Warning,
    Methodology,
    MethodologyStep,
    Checklist,
    ChecklistItem,
    Persona,
    Workflow,
    WorkflowStep,
    # Base class
    BaseExtractor,
    # Exceptions
    ExtractorError,
    PromptLoadError,
    ExtractionParseError,
    ExtractionValidationError,
    UnsupportedExtractionTypeError,
    # Registry
    ExtractorRegistry,
    extractor_registry,
)

__all__ = [
    # Enums
    "ExtractionType",
    # Base models
    "ExtractionBase",
    "ExtractionResult",
    "ExtractorConfig",
    # Type-specific models
    "Decision",
    "Pattern",
    "Warning",
    "Methodology",
    "MethodologyStep",
    "Checklist",
    "ChecklistItem",
    "Persona",
    "Workflow",
    "WorkflowStep",
    # Base class
    "BaseExtractor",
    # Exceptions
    "ExtractorError",
    "PromptLoadError",
    "ExtractionParseError",
    "ExtractionValidationError",
    "UnsupportedExtractionTypeError",
    # Registry
    "ExtractorRegistry",
    "extractor_registry",
]
```

### Prompt Templates Structure

```markdown
# packages/pipeline/src/extractors/prompts/_base.md
# Base Extraction Instructions

You are a knowledge extraction assistant. Your task is to extract
structured knowledge from the provided text chunk.

## Rules:
1. Only extract information explicitly stated in the text
2. Do not invent or hallucinate information
3. Return valid JSON matching the specified schema
4. If no relevant knowledge found, return an empty array []
5. Include confidence scores based on how clearly the information is stated

## Output Format:
Return a JSON array of extractions. Each extraction must include all required fields.
```

### Testing Pattern

**Test file structure:**

```python
# packages/pipeline/tests/test_extractors/test_base.py
import pytest
from datetime import datetime

from src.extractors import (
    BaseExtractor,
    ExtractionType,
    ExtractionBase,
    ExtractionResult,
    ExtractorConfig,
    Decision,
    Pattern,
    Warning,
    Methodology,
    ExtractorRegistry,
    ExtractorError,
    UnsupportedExtractionTypeError,
)


class TestBaseExtractorABC:
    """Test that BaseExtractor is properly abstract."""

    def test_cannot_instantiate_directly(self):
        """BaseExtractor cannot be instantiated without implementing abstract methods."""
        with pytest.raises(TypeError) as exc_info:
            BaseExtractor()
        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_class_must_implement_abstract_methods(self):
        """Concrete class must implement all abstract methods and properties."""
        class IncompleteExtractor(BaseExtractor):
            pass  # Missing all required methods

        with pytest.raises(TypeError):
            IncompleteExtractor()


class TestExtractionModels:
    """Test extraction Pydantic models."""

    def test_decision_model_required_fields(self):
        """Decision model requires source_id, chunk_id, question."""
        decision = Decision(
            source_id="src-123",
            chunk_id="chunk-456",
            question="Should I use RAG or fine-tuning?",
            options=["RAG", "Fine-tuning", "Both"],
        )
        assert decision.source_id == "src-123"
        assert decision.chunk_id == "chunk-456"
        assert decision.type == ExtractionType.DECISION
        assert decision.schema_version == "1.0.0"

    def test_pattern_model_fields(self):
        """Pattern model validates all fields."""
        pattern = Pattern(
            source_id="src-123",
            chunk_id="chunk-456",
            name="Retrieval-Augmented Generation",
            problem="LLM knowledge cutoff",
            solution="Retrieve relevant documents before generation",
        )
        assert pattern.type == ExtractionType.PATTERN
        assert pattern.name == "Retrieval-Augmented Generation"

    def test_warning_model_fields(self):
        """Warning model validates all fields."""
        warning = Warning(
            source_id="src-123",
            chunk_id="chunk-456",
            title="Context Window Overflow",
            description="Too many tokens in prompt",
            consequences=["Truncation", "Lost context"],
        )
        assert warning.type == ExtractionType.WARNING

    def test_all_models_have_common_fields(self):
        """All extraction models must have source attribution fields."""
        models = [Decision, Pattern, Warning, Methodology]

        for model_class in models:
            # Get model fields
            fields = model_class.model_fields
            assert "source_id" in fields
            assert "chunk_id" in fields
            assert "topics" in fields
            assert "schema_version" in fields


class TestExtractorRegistry:
    """Test extractor registry functionality."""

    @pytest.fixture
    def dummy_extractor_class(self):
        """Create a dummy extractor for testing."""
        class DummyExtractor(BaseExtractor):
            @property
            def extraction_type(self):
                return ExtractionType.DECISION

            @property
            def model_class(self):
                return Decision

            def extract(self, chunk_content, chunk_id, source_id):
                return []

            def get_prompt(self):
                return "Test prompt"

        return DummyExtractor

    def test_register_and_get_extractor(self, dummy_extractor_class):
        """Should register and retrieve extractors."""
        registry = ExtractorRegistry()
        registry.register(ExtractionType.DECISION, dummy_extractor_class)

        extractor = registry.get_extractor(ExtractionType.DECISION)
        assert isinstance(extractor, dummy_extractor_class)

    def test_get_extractor_unsupported_raises(self):
        """Should raise for unregistered extraction type."""
        registry = ExtractorRegistry()

        with pytest.raises(UnsupportedExtractionTypeError) as exc_info:
            registry.get_extractor(ExtractionType.PATTERN)
        assert exc_info.value.code == "UNSUPPORTED_EXTRACTION_TYPE"

    def test_list_extraction_types(self, dummy_extractor_class):
        """Should list registered extraction types."""
        registry = ExtractorRegistry()
        registry.register(ExtractionType.DECISION, dummy_extractor_class)

        types = registry.list_extraction_types()
        assert ExtractionType.DECISION in types


class TestExtractionExceptions:
    """Test exception classes."""

    def test_unsupported_extraction_type_error(self):
        """Should have structured error format."""
        error = UnsupportedExtractionTypeError(
            "unknown",
            ["decision", "pattern", "warning"]
        )
        assert error.code == "UNSUPPORTED_EXTRACTION_TYPE"
        assert "unknown" in error.message
        assert error.details["supported"] == ["decision", "pattern", "warning"]
```

### Python Naming Conventions

**From Architecture Document (architecture.md:418-432):**

| Element | Convention | Example |
|---------|------------|---------|
| Files/modules | `snake_case.py` | `base.py`, `decision_extractor.py` |
| Classes | `PascalCase` | `BaseExtractor`, `Decision`, `ExtractionResult` |
| Functions | `snake_case` | `extract()`, `get_prompt()`, `_parse_llm_response()` |
| Variables | `snake_case` | `chunk_id`, `source_id`, `extraction_type` |
| Constants/Enums | `UPPER_SNAKE_CASE` | `ExtractionType.DECISION` |

### MongoDB Integration Pattern

**From Architecture Document (architecture.md:260-291):**

Extractions are stored in the `extractions` collection with:
- `source_id` reference to `sources` collection
- `chunk_id` reference to `chunks` collection
- `type` field for extraction type filtering
- `topics[]` for topic-based filtering
- Compound index on `type + topics`

```python
# Expected MongoDB document structure
{
    "_id": ObjectId("..."),
    "source_id": "src-123",
    "chunk_id": "chunk-456",
    "type": "decision",
    "content": {
        "question": "...",
        "options": ["..."],
        "considerations": ["..."],
        "recommended_approach": "..."
    },
    "topics": ["rag", "fine-tuning"],
    "schema_version": "1.0.0",
    "extracted_at": ISODate("2025-12-30T10:00:00Z"),
    "confidence": 0.85
}
```

### Logging Pattern

**From Architecture Document (architecture.md:535-542) and project-context.md:**

```python
import structlog
logger = structlog.get_logger()

# Good: structured with context
logger.info("extraction_completed",
    extraction_type="decision",
    chunk_id="chunk-456",
    count=3
)
logger.debug("extractor_initialized",
    extractor="DecisionExtractor",
    extraction_type="decision"
)
logger.error("extraction_failed",
    chunk_id="chunk-456",
    error=str(e)
)
```

**CRITICAL:** Use structlog, no print statements.

### Project Structure Notes

- File location: `packages/pipeline/src/extractors/base.py`
- Module exports: `packages/pipeline/src/extractors/__init__.py`
- Prompts: `packages/pipeline/src/extractors/prompts/`
- Tests: `packages/pipeline/tests/test_extractors/`
- Aligned with architecture: All extraction code in `packages/pipeline/`
- Follow NFR6 extensibility pattern: ABC enables easy addition of new extractors

### Story Predecessor Intelligence

**From Epic 1 Stories (Foundation):**
- Story 1.1 established monorepo structure at `packages/pipeline/`
- Story 1.3 established Pydantic model patterns and `Extraction` model
- Story 1.4 established exception patterns with `KnowledgeError` base
- Story 1.5 established logging with structlog pattern

**From Epic 2 Stories (Ingestion - Pattern Reference):**
- Story 2.1 established ABC pattern with `SourceAdapter`
- Story 2.1 established registry pattern with `AdapterRegistry`
- Story 2.1 established exception hierarchy pattern
- Story 2.1 established testing patterns for ABCs

**Patterns to Follow:**
- Exception classes inherit from `KnowledgeError`
- All exceptions include `code`, `message`, `details`
- Use structlog for all logging
- Pydantic models for data validation
- Tests mirror src structure
- Registry pattern for extensibility

### Architecture Compliance Checklist

- [ ] File in `packages/pipeline/src/extractors/base.py` (architecture.md:623-636)
- [ ] ABC with abstract methods `extract()`, `get_prompt()` (NFR6)
- [ ] Abstract properties `extraction_type`, `model_class`
- [ ] All 7 extraction type Pydantic models defined
- [ ] All models include `source_id`, `chunk_id`, `topics[]`, `schema_version`
- [ ] Exceptions inherit from `KnowledgeError` (architecture.md:545-559)
- [ ] Structured error format: `{code, message, details}`
- [ ] Uses structlog for logging (architecture.md:535-542)
- [ ] Registry pattern for extensibility
- [ ] Prompts directory created for extraction prompts
- [ ] Tests in `packages/pipeline/tests/test_extractors/`

### Key Technical Decisions

1. **Extraction returns list[ExtractionResult]** - A single chunk may contain multiple extractable items
2. **Confidence score on all extractions** - Allows filtering by extraction quality
3. **Auto-topic tagging built-in** - Reduces manual tagging burden
4. **Prompt files in markdown** - Easy to read and modify prompts
5. **Registry pattern** - Easy to add new extraction types without modifying core code

### References

- [Source: epics.md#Story-3.1] - Story acceptance criteria (lines 379-393)
- [Source: epics.md#FR-2] - Knowledge Extraction requirements (lines 29-40)
- [Source: architecture.md#Project-Structure-&-Boundaries] - File locations (lines 623-636)
- [Source: architecture.md#NFR6] - Extensibility requirement (line 80)
- [Source: architecture.md#Data-Architecture] - Extraction schema (lines 260-291)
- [Source: architecture.md#Implementation-Patterns-&-Consistency-Rules] - Naming patterns (lines 410-435)
- [Source: architecture.md#Error-Handling-Pattern] - Exception pattern (lines 545-560)
- [Source: project-context.md#Critical-Implementation-Rules] - Error handling, logging rules
- [Source: Story 2.1] - Adapter ABC and Registry patterns to follow

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

_To be filled by dev agent - list all files created/modified:_
- packages/pipeline/src/extractors/__init__.py (CREATE)
- packages/pipeline/src/extractors/base.py (CREATE)
- packages/pipeline/src/extractors/prompts/_base.md (CREATE)
- packages/pipeline/src/extractors/prompts/decision.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/pattern.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/warning.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/methodology.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/checklist.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/persona.md (CREATE - placeholder)
- packages/pipeline/src/extractors/prompts/workflow.md (CREATE - placeholder)
- packages/pipeline/tests/test_extractors/__init__.py (CREATE)
- packages/pipeline/tests/test_extractors/conftest.py (CREATE)
- packages/pipeline/tests/test_extractors/test_base.py (CREATE)
- packages/pipeline/tests/test_extractors/test_models.py (CREATE)
