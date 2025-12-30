"""Shared fixtures for model tests."""

from datetime import datetime

import pytest

# Valid MongoDB ObjectId examples for testing
VALID_OBJECT_ID = "507f1f77bcf86cd799439011"
VALID_OBJECT_ID_2 = "507f1f77bcf86cd799439012"
VALID_OBJECT_ID_3 = "507f1f77bcf86cd799439013"


@pytest.fixture
def valid_object_id() -> str:
    """Return a valid MongoDB ObjectId string."""
    return VALID_OBJECT_ID


@pytest.fixture
def valid_object_id_2() -> str:
    """Return another valid MongoDB ObjectId string."""
    return VALID_OBJECT_ID_2


@pytest.fixture
def valid_object_id_3() -> str:
    """Return a third valid MongoDB ObjectId string."""
    return VALID_OBJECT_ID_3


@pytest.fixture
def sample_datetime() -> datetime:
    """Return a sample datetime for testing."""
    return datetime(2025, 12, 30, 10, 30, 0)
