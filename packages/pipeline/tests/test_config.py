"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest

from src.config import Settings


class TestSettingsProjectNamespacing:
    """Tests for project namespacing configuration."""

    def test_default_project_id(self) -> None:
        """Default project_id should be 'default'."""
        settings = Settings()
        assert settings.project_id == "default"

    def test_custom_project_id_from_env(self) -> None:
        """project_id can be set via environment variable."""
        with patch.dict(os.environ, {"PROJECT_ID": "ai_engineering"}):
            settings = Settings()
            assert settings.project_id == "ai_engineering"

    def test_sources_collection_default(self) -> None:
        """sources_collection uses default project_id prefix."""
        settings = Settings()
        assert settings.sources_collection == "default_sources"

    def test_chunks_collection_default(self) -> None:
        """chunks_collection uses default project_id prefix."""
        settings = Settings()
        assert settings.chunks_collection == "default_chunks"

    def test_extractions_collection_default(self) -> None:
        """extractions_collection uses default project_id prefix."""
        settings = Settings()
        assert settings.extractions_collection == "default_extractions"

    def test_sources_collection_custom_project(self) -> None:
        """sources_collection uses custom project_id prefix."""
        settings = Settings(project_id="ai_engineering")
        assert settings.sources_collection == "ai_engineering_sources"

    def test_chunks_collection_custom_project(self) -> None:
        """chunks_collection uses custom project_id prefix."""
        settings = Settings(project_id="time_series")
        assert settings.chunks_collection == "time_series_chunks"

    def test_extractions_collection_custom_project(self) -> None:
        """extractions_collection uses custom project_id prefix."""
        settings = Settings(project_id="system_design")
        assert settings.extractions_collection == "system_design_extractions"

    def test_collection_properties_with_env_var(self) -> None:
        """Collection properties respect PROJECT_ID environment variable."""
        with patch.dict(os.environ, {"PROJECT_ID": "my_project"}):
            settings = Settings()
            assert settings.sources_collection == "my_project_sources"
            assert settings.chunks_collection == "my_project_chunks"
            assert settings.extractions_collection == "my_project_extractions"


class TestSettingsKnowledgeVectors:
    """Tests for single Qdrant collection configuration."""

    def test_knowledge_vectors_collection_exists(self) -> None:
        """KNOWLEDGE_VECTORS_COLLECTION constant should exist."""
        from src.config import KNOWLEDGE_VECTORS_COLLECTION
        assert KNOWLEDGE_VECTORS_COLLECTION == "knowledge_vectors"

    def test_qdrant_collection_property(self) -> None:
        """Settings should have qdrant_collection property."""
        settings = Settings()
        assert settings.qdrant_collection == "knowledge_vectors"

    def test_qdrant_collection_not_project_dependent(self) -> None:
        """qdrant_collection should NOT change with project_id."""
        settings_default = Settings(project_id="default")
        settings_custom = Settings(project_id="ai_engineering")
        assert settings_default.qdrant_collection == settings_custom.qdrant_collection
        assert settings_default.qdrant_collection == "knowledge_vectors"


class TestSettingsCliMetadata:
    """Tests for CLI metadata fields."""

    def test_source_category_default(self) -> None:
        """source_category should default to None."""
        settings = Settings()
        assert settings.source_category is None

    def test_source_category_from_env(self) -> None:
        """source_category can be set via environment."""
        with patch.dict(os.environ, {"SOURCE_CATEGORY": "advanced"}):
            settings = Settings()
            assert settings.source_category == "advanced"

    def test_source_tags_default(self) -> None:
        """source_tags should default to None."""
        settings = Settings()
        assert settings.source_tags is None

    def test_source_tags_from_env(self) -> None:
        """source_tags can be set via environment."""
        with patch.dict(os.environ, {"SOURCE_TAGS": "llm,rag,production"}):
            settings = Settings()
            assert settings.source_tags == "llm,rag,production"

    def test_source_year_default(self) -> None:
        """source_year should default to None."""
        settings = Settings()
        assert settings.source_year is None

    def test_source_year_from_env(self) -> None:
        """source_year can be set via environment."""
        with patch.dict(os.environ, {"SOURCE_YEAR": "2024"}):
            settings = Settings()
            assert settings.source_year == 2024
