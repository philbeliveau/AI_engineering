"""Configuration module for Knowledge MCP Server.

Uses Pydantic Settings for type-safe configuration loaded from environment variables
and .env files. Follow project-context.md:59-64 configuration pattern.
"""

import json
from pathlib import Path
from typing import Any

import structlog
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger()


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings can be overridden via environment variables or a .env file.
    Supports cloud database configuration for MongoDB Atlas and Qdrant Cloud.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment: local | staging | production
    environment: str = Field(
        default="local",
        description="Deployment environment (local, staging, production)",
    )

    # MongoDB Configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI. Use mongodb+srv:// for Atlas.",
    )
    mongodb_database: str = Field(
        default="knowledge_db",
        description="MongoDB database name",
    )

    # Qdrant Configuration
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant URL. Use https://<cluster>.cloud.qdrant.io for Cloud.",
    )
    qdrant_api_key: str | None = Field(
        default=None,
        description="Qdrant Cloud API key (required for Qdrant Cloud)",
    )

    # Connection Settings
    ssl_enabled: bool = Field(
        default=True,
        description="Enable SSL/TLS for database connections",
    )
    connection_timeout_ms: int = Field(
        default=5000,
        description="Database connection timeout in milliseconds",
    )
    max_pool_size: int = Field(
        default=10,
        description="MongoDB connection pool size",
    )

    # Server Configuration
    server_host: str = "0.0.0.0"
    # Accept both PORT (Railway) and SERVER_PORT for backward compatibility
    server_port: int = Field(
        default=8000,
        validation_alias=AliasChoices("PORT", "SERVER_PORT"),
    )

    # Logging
    log_level: str = "INFO"

    # Project namespacing
    project_id: str = Field(
        default="default",
        description="Project identifier for collection namespacing",
    )

    # Authentication configuration
    api_keys_file: str | None = Field(
        default=None,
        description="Path to JSON file containing API keys",
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

    def get_api_keys(self) -> list[dict[str, Any]]:
        """Load API keys from configured file.

        Returns:
            List of API key dictionaries with keys: key, tier, created_at, expires_at, metadata

        Example file format:
            {
              "keys": [
                {
                  "key": "kp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
                  "tier": "REGISTERED",
                  "created_at": "2025-12-30T00:00:00Z",
                  "expires_at": null,
                  "metadata": {"user_id": "user_123"}
                }
              ]
            }
        """
        if not self.api_keys_file:
            logger.debug("api_keys_file_not_configured")
            return []

        path = Path(self.api_keys_file)
        if not path.exists():
            logger.warning("api_keys_file_not_found", path=str(path))
            return []

        try:
            with open(path) as f:
                data = json.load(f)
                keys = data.get("keys", [])
                logger.info("api_keys_loaded", count=len(keys))
                return keys
        except json.JSONDecodeError as e:
            logger.error("api_keys_file_invalid_json", path=str(path), error=str(e))
            return []
        except Exception as e:
            logger.error("api_keys_file_load_error", path=str(path), error=str(e))
            return []


# Unified Qdrant collection for single-collection architecture
# All chunks and extractions stored in one collection with payload-based filtering
KNOWLEDGE_VECTORS_COLLECTION = "knowledge_vectors"

# Export singleton instance for use throughout the application
settings = Settings()
