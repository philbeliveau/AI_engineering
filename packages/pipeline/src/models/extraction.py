"""Extraction models for structured knowledge extracted from sources."""

import re
from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# MongoDB ObjectId validation pattern (24 hex characters)
OBJECTID_PATTERN = re.compile(r"^[a-f0-9]{24}$")

# Current schema version for all documents
CURRENT_SCHEMA_VERSION = "1.1"

# Valid extraction types
ExtractionType = Literal[
    "decision", "pattern", "warning", "methodology", "checklist", "persona", "workflow"
]


# ============================================================================
# Type-Specific Content Models
# ============================================================================


class DecisionContent(BaseModel):
    """Content model for decision extractions.

    Represents an architectural or design decision with context.

    Attributes:
        question: The decision question being addressed.
        options: Available options or choices.
        considerations: Factors to consider when making the decision.
        recommended_approach: The recommended or chosen approach.
    """

    question: str = Field(..., min_length=1)
    options: list[str] = Field(default_factory=list)
    considerations: list[str] = Field(default_factory=list)
    recommended_approach: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class PatternContent(BaseModel):
    """Content model for pattern extractions.

    Represents a reusable design or implementation pattern.

    Attributes:
        name: Name of the pattern.
        problem: The problem this pattern solves.
        solution: How the pattern solves the problem.
        code_example: Example code demonstrating the pattern (optional).
        context: When to apply this pattern.
        trade_offs: Trade-offs and considerations when using this pattern.
    """

    name: str = Field(..., min_length=1)
    problem: str = Field(..., min_length=1)
    solution: str = Field(..., min_length=1)
    code_example: Optional[str] = None
    context: Optional[str] = None
    trade_offs: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class WarningContent(BaseModel):
    """Content model for warning extractions.

    Represents a warning, anti-pattern, or pitfall to avoid.

    Attributes:
        title: Brief title of the warning.
        description: Detailed description of the warning.
        symptoms: Signs that indicate this issue.
        consequences: What happens if this warning is ignored.
        prevention: How to prevent or address this issue.
    """

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    symptoms: list[str] = Field(default_factory=list)
    consequences: list[str] = Field(default_factory=list)
    prevention: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class MethodologyContent(BaseModel):
    """Content model for methodology extractions.

    Represents a process or methodology with defined steps.

    Attributes:
        name: Name of the methodology.
        steps: Ordered list of steps in the methodology.
        prerequisites: Requirements before starting the methodology.
        outputs: Expected outputs or deliverables.
    """

    name: str = Field(..., min_length=1)
    steps: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ChecklistContent(BaseModel):
    """Content model for checklist extractions.

    Represents a checklist for verification or review.

    Attributes:
        name: Name of the checklist.
        items: List of checklist items.
        context: When or where to use this checklist.
    """

    name: str = Field(..., min_length=1)
    items: list[str] = Field(default_factory=list)
    context: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class PersonaContent(BaseModel):
    """Content model for persona extractions.

    Represents a role or persona with defined characteristics.

    Attributes:
        role: The role or title of the persona.
        responsibilities: Key responsibilities of this persona.
        expertise: Areas of expertise or skills.
        communication_style: How this persona communicates.
    """

    role: str = Field(..., min_length=1)
    responsibilities: list[str] = Field(default_factory=list)
    expertise: list[str] = Field(default_factory=list)
    communication_style: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class WorkflowContent(BaseModel):
    """Content model for workflow extractions.

    Represents a workflow or process with decision points.

    Attributes:
        name: Name of the workflow.
        trigger: What triggers or starts this workflow.
        steps: Ordered list of steps in the workflow.
        decision_points: Key decision points in the workflow.
    """

    name: str = Field(..., min_length=1)
    trigger: Optional[str] = None
    steps: list[str] = Field(default_factory=list)
    decision_points: list[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


# Union type for all content models
ContentType = Union[
    DecisionContent,
    PatternContent,
    WarningContent,
    MethodologyContent,
    ChecklistContent,
    PersonaContent,
    WorkflowContent,
    dict,  # Allow raw dict for flexibility during extraction
]


# ============================================================================
# Base Extraction Model
# ============================================================================


class Extraction(BaseModel):
    """Base extraction model for all structured knowledge types.

    Represents extracted knowledge from source documents.
    All extractions are stored in MongoDB's 'extractions' collection.

    Attributes:
        id: MongoDB ObjectId as string (24 hex characters).
        source_id: Reference to the parent source document.
        chunk_id: Reference to the specific chunk this was extracted from.
        type: Type of extraction (decision, pattern, warning, etc.).
        content: Type-specific structured data.
        topics: Topic tags for categorization and search.
        schema_version: Version of the document schema.
        extracted_at: Timestamp when the extraction was created.
        project_id: Project identifier for multi-project isolation (denormalized).
        title: Human-readable extraction title.
        source_title: Title of the source document (denormalized).
        source_type: Type of the source document (denormalized).
        chapter: Chapter identifier from the source chunk (denormalized).
    """

    id: str = Field(..., description="MongoDB ObjectId as string")
    source_id: str = Field(..., description="Reference to sources._id")
    chunk_id: str = Field(..., description="Reference to chunks._id")
    type: ExtractionType
    content: ContentType = Field(..., description="Type-specific structured data")
    topics: list[str] = Field(default_factory=list)
    schema_version: str = CURRENT_SCHEMA_VERSION
    extracted_at: datetime
    # v1.1 fields for multi-project support and rich payload
    project_id: str = Field(default="default", description="Project identifier (denormalized)")
    title: str = Field(default="", description="Human-readable extraction title")
    source_title: str = Field(default="", description="Source document title (denormalized)")
    source_type: str = Field(default="", description="Source document type (denormalized)")
    chapter: Optional[str] = Field(default=None, description="Chapter from source chunk")

    @field_validator("id", "source_id", "chunk_id")
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        """Validate that id fields are valid MongoDB ObjectId format."""
        if not OBJECTID_PATTERN.match(v):
            raise ValueError("Invalid MongoDB ObjectId format (expected 24 hex characters)")
        return v

    @model_validator(mode="after")
    def validate_content_type_match(self) -> "Extraction":
        """Validate that content structure matches the extraction type.

        When using the base Extraction class, content can be a raw dict for flexibility.
        However, if a typed content model is provided, it must match the extraction type.
        For strict type enforcement, use typed extraction classes (DecisionExtraction, etc.).
        """
        # Map extraction types to their expected content model types
        type_to_content_class = {
            "decision": DecisionContent,
            "pattern": PatternContent,
            "warning": WarningContent,
            "methodology": MethodologyContent,
            "checklist": ChecklistContent,
            "persona": PersonaContent,
            "workflow": WorkflowContent,
        }

        # If content is a typed model (not raw dict), verify it matches the type
        if not isinstance(self.content, dict):
            expected_class = type_to_content_class.get(self.type)
            if expected_class and not isinstance(self.content, expected_class):
                raise ValueError(
                    f"Content type mismatch: extraction type '{self.type}' expects "
                    f"{expected_class.__name__}, got {type(self.content).__name__}"
                )
        return self

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "source_id": "507f1f77bcf86cd799439011",
                "chunk_id": "507f1f77bcf86cd799439012",
                "type": "decision",
                "content": {
                    "question": "Which embedding model should we use?",
                    "options": ["all-MiniLM-L6-v2", "text-embedding-ada-002", "bge-small-en"],
                    "considerations": ["Local vs API", "Cost", "Performance", "Latency"],
                    "recommended_approach": "all-MiniLM-L6-v2 for local inference",
                },
                "topics": ["embeddings", "architecture", "ml"],
                "schema_version": "1.1",
                "extracted_at": "2025-12-30T11:00:00Z",
                "project_id": "ai_engineering",
                "title": "Embedding Model Selection",
                "source_title": "LLM Engineer's Handbook",
                "source_type": "book",
                "chapter": "5",
            }
        },
    )


# ============================================================================
# Convenience Type-Specific Extraction Models
# ============================================================================


class DecisionExtraction(Extraction):
    """Extraction specifically for decisions with typed content."""

    type: Literal["decision"] = "decision"
    content: DecisionContent


class PatternExtraction(Extraction):
    """Extraction specifically for patterns with typed content."""

    type: Literal["pattern"] = "pattern"
    content: PatternContent


class WarningExtraction(Extraction):
    """Extraction specifically for warnings with typed content."""

    type: Literal["warning"] = "warning"
    content: WarningContent


class MethodologyExtraction(Extraction):
    """Extraction specifically for methodologies with typed content."""

    type: Literal["methodology"] = "methodology"
    content: MethodologyContent


class ChecklistExtraction(Extraction):
    """Extraction specifically for checklists with typed content."""

    type: Literal["checklist"] = "checklist"
    content: ChecklistContent


class PersonaExtraction(Extraction):
    """Extraction specifically for personas with typed content."""

    type: Literal["persona"] = "persona"
    content: PersonaContent


class WorkflowExtraction(Extraction):
    """Extraction specifically for workflows with typed content."""

    type: Literal["workflow"] = "workflow"
    content: WorkflowContent
