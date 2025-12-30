"""Shared pytest fixtures for MCP server tests."""

import pytest


@pytest.fixture
def sample_mongodb_uri() -> str:
    """Return MongoDB URI for testing."""
    return "mongodb://localhost:27017"


@pytest.fixture
def sample_qdrant_url() -> str:
    """Return Qdrant URL for testing."""
    return "http://localhost:6333"
