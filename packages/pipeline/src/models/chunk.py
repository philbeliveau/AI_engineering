"""Chunk model for raw text chunks extracted from sources."""

import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# MongoDB ObjectId validation pattern (24 hex characters)
OBJECTID_PATTERN = re.compile(r"^[a-f0-9]{24}$")

# Current schema version for all documents
CURRENT_SCHEMA_VERSION = "1.0"


class ChunkPosition(BaseModel):
    """Position information for a chunk within its source document.

    Attributes:
        chapter: Chapter number or name (optional).
        section: Section number or name (optional).
        page: Page number where the chunk is located (optional, must be >= 1).
    """

    chapter: Optional[str] = None
    section: Optional[str] = None
    page: Optional[int] = Field(default=None, ge=1)

    model_config = ConfigDict(populate_by_name=True)


class Chunk(BaseModel):
    """Raw text chunk extracted from a source document.

    Represents a portion of text from an ingested document.
    All chunks are stored in MongoDB's 'chunks' collection.

    Attributes:
        id: MongoDB ObjectId as string (24 hex characters).
        source_id: Reference to the parent source document.
        content: The actual text content of the chunk.
        position: Location information within the source document.
        token_count: Number of tokens in the chunk content.
        schema_version: Version of the document schema.
    """

    id: str = Field(..., description="MongoDB ObjectId as string")
    source_id: str = Field(..., description="Reference to sources._id")
    content: str = Field(..., min_length=1, max_length=50000)
    position: ChunkPosition = Field(default_factory=ChunkPosition)
    token_count: int = Field(..., ge=0)
    schema_version: str = CURRENT_SCHEMA_VERSION

    @field_validator("id", "source_id")
    @classmethod
    def validate_object_id(cls, v: str) -> str:
        """Validate that id fields are valid MongoDB ObjectId format."""
        if not OBJECTID_PATTERN.match(v):
            raise ValueError("Invalid MongoDB ObjectId format (expected 24 hex characters)")
        return v

    @model_validator(mode="after")
    def validate_token_count_consistency(self) -> "Chunk":
        """Validate that token_count is reasonable for content length."""
        # Simple sanity check: token count shouldn't be more than content length
        # (a token is at minimum 1 character)
        if self.token_count > len(self.content):
            raise ValueError("token_count cannot exceed content length")
        return self

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "source_id": "507f1f77bcf86cd799439011",
                "content": "Large Language Models (LLMs) are neural networks trained on massive text corpora...",
                "position": {"chapter": "1", "section": "Introduction", "page": 5},
                "token_count": 150,
                "schema_version": "1.0",
            }
        },
    )
