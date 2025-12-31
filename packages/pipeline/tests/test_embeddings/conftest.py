"""Fixtures for embedding tests."""

import pytest
from src.embeddings import (
    LocalEmbedder,
    EmbeddingConfig,
    reset_embedder,
)


@pytest.fixture(autouse=True)
def reset_singleton_before_each_test():
    """Reset embedder singleton before and after each test."""
    reset_embedder()
    yield
    reset_embedder()


@pytest.fixture
def embedder() -> LocalEmbedder:
    """Create a fresh LocalEmbedder instance."""
    return LocalEmbedder()


@pytest.fixture
def custom_config() -> EmbeddingConfig:
    """Create a custom embedding configuration."""
    return EmbeddingConfig(
        batch_size=16,
        show_progress=False,
    )
