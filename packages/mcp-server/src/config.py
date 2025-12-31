"""Configuration module for Knowledge MCP Server.

Uses Pydantic Settings for type-safe configuration loaded from environment variables
and .env files. Follow project-context.md:59-64 configuration pattern.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings can be overridden via environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: str = "local"

    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"

    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Logging
    log_level: str = "INFO"


# Export singleton instance for use throughout the application
settings = Settings()
