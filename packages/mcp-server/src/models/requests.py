"""Request models for Knowledge MCP Server.

Follows architecture.md API request patterns for MCP tools.
"""

from pydantic import BaseModel, Field


class SearchKnowledgeRequest(BaseModel):
    """Request model for search_knowledge endpoint.

    Attributes:
        query: Natural language search query
        limit: Maximum number of results to return (1-100, default 10)
    """

    query: str = Field(
        ...,
        min_length=1,
        description="Natural language search query",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return",
    )
