"""Configuration management for the knowledge pipeline."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Single Qdrant collection for all vectors (following Qdrant multitenancy best practices)
KNOWLEDGE_VECTORS_COLLECTION = "knowledge_vectors"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"

    # Qdrant settings
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_grpc_port: int = 6334

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"

    # LLM settings
    anthropic_api_key: str = ""
    llm_model: str = "claude-3-haiku-20240307"
    llm_max_tokens: int = 1024

    # Environment
    environment: str = "local"

    # Project namespacing
    project_id: str = Field(
        default="default",
        description="Project identifier for collection namespacing",
    )

    # CLI metadata fields (optional, for source ingestion)
    source_category: Optional[str] = Field(
        default=None,
        description="Source category (foundational/advanced/reference/case_study)",
    )
    source_tags: Optional[str] = Field(
        default=None,
        description="Comma-separated tags for the source",
    )
    source_year: Optional[int] = Field(
        default=None,
        description="Publication year of the source",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def sources_collection(self) -> str:
        """MongoDB collection name for sources."""
        return f"{self.project_id}_sources"

    @property
    def chunks_collection(self) -> str:
        """MongoDB/Qdrant collection name for chunks."""
        return f"{self.project_id}_chunks"

    @property
    def extractions_collection(self) -> str:
        """MongoDB/Qdrant collection name for extractions."""
        return f"{self.project_id}_extractions"

    @property
    def qdrant_collection(self) -> str:
        """Single Qdrant collection for all vectors.

        Uses a single collection with payload-based filtering
        following Qdrant multitenancy best practices.
        """
        return KNOWLEDGE_VECTORS_COLLECTION


# Singleton instance
settings = Settings()
