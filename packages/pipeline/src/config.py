"""Configuration management for the knowledge pipeline."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "knowledge_db"

    # Qdrant settings
    qdrant_url: str = "http://localhost:6333"
    qdrant_grpc_port: int = 6334

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"

    # LLM settings
    anthropic_api_key: str = ""
    llm_model: str = "claude-3-haiku-20240307"
    llm_max_tokens: int = 1024

    # Environment
    environment: str = "local"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Singleton instance
settings = Settings()
