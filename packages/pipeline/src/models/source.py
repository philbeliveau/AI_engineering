"""Source model for books, papers, and case studies."""

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# MongoDB ObjectId validation pattern (24 hex characters)
OBJECTID_PATTERN = re.compile(r"^[a-f0-9]{24}$")

# Current schema version for all documents
CURRENT_SCHEMA_VERSION = "1.1"

# Valid source categories for categorization
SourceCategory = Literal["foundational", "advanced", "reference", "case_study"]


class Source(BaseModel):
    """Source document model for books, papers, and case studies.

    Represents metadata about ingested documents in the knowledge base.
    All sources are stored in MongoDB's 'sources' collection.

    Attributes:
        id: MongoDB ObjectId as string (24 hex characters).
        type: Document type - book, paper, or case_study.
        title: Title of the source document.
        authors: List of author names.
        path: File system path to the source document.
        ingested_at: Timestamp when the document was ingested.
        status: Processing status of the source.
        metadata: Arbitrary JSON metadata for extensibility.
        schema_version: Version of the document schema.
        project_id: Project identifier for multi-project isolation.
        year: Publication year of the source (optional, 1900-2100).
        category: Source category for classification.
        tags: List of tags for filtering and search.
    """

    id: str = Field(..., description="MongoDB ObjectId as string")
    type: Literal["book", "paper", "case_study"]
    title: str = Field(..., min_length=1, max_length=500)
    authors: list[str] = Field(default_factory=list)
    path: str = Field(..., min_length=1, max_length=1000)
    ingested_at: datetime
    status: Literal["pending", "processing", "complete", "failed"]
    metadata: dict = Field(default_factory=dict)
    schema_version: str = CURRENT_SCHEMA_VERSION
    # v1.1 fields for multi-project support and rich metadata
    project_id: str = Field(default="default", description="Project identifier for isolation")
    year: Optional[int] = Field(default=None, ge=1900, le=2100, description="Publication year")
    category: SourceCategory = Field(default="foundational", description="Source category")
    tags: list[str] = Field(default_factory=list, description="Tags for filtering")

    @field_validator("id")
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        """Validate that id is a valid MongoDB ObjectId format."""
        if not OBJECTID_PATTERN.match(v):
            raise ValueError("Invalid MongoDB ObjectId format (expected 24 hex characters)")
        return v

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, v: list[str]) -> list[str]:
        """Filter out empty or whitespace-only author names."""
        return [author.strip() for author in v if author and author.strip()]

    @field_validator("ingested_at")
    @classmethod
    def validate_ingested_at_not_future(cls, v: datetime) -> datetime:
        """Validate that ingested_at is not in the future (with 5 minute tolerance for clock skew)."""
        from datetime import timedelta

        max_allowed = datetime.now() + timedelta(minutes=5)
        if v > max_allowed:
            raise ValueError("ingested_at cannot be in the future")
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "type": "book",
                "title": "LLM Engineer's Handbook",
                "authors": ["Paul Iusztin", "Maxime Labonne"],
                "path": "/data/raw/llm-handbook.pdf",
                "ingested_at": "2025-12-30T10:30:00Z",
                "status": "complete",
                "metadata": {"pages": 800},
                "schema_version": "1.1",
                "project_id": "ai_engineering",
                "year": 2024,
                "category": "foundational",
                "tags": ["llm", "production", "rag"],
            }
        },
    )
