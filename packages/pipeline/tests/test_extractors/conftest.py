"""Test fixtures for extractor tests."""

from typing import Type

import pytest

from src.extractors import (
    BaseExtractor,
    Decision,
    ExtractionBase,
    ExtractionResult,
    ExtractionType,
    ExtractorConfig,
    ExtractorRegistry,
)


class DummyExtractor(BaseExtractor):
    """Concrete extractor for testing purposes."""

    @property
    def extraction_type(self) -> ExtractionType:
        return ExtractionType.DECISION

    @property
    def model_class(self) -> Type[ExtractionBase]:
        return Decision

    def extract(
        self,
        chunk_content: str,
        chunk_id: str,
        source_id: str,
    ) -> list[ExtractionResult]:
        return []

    def get_prompt(self) -> str:
        return "Test prompt"


@pytest.fixture
def dummy_extractor_class() -> Type[BaseExtractor]:
    """Provide the DummyExtractor class for testing."""
    return DummyExtractor


@pytest.fixture
def dummy_extractor() -> DummyExtractor:
    """Provide an instantiated DummyExtractor for testing."""
    return DummyExtractor()


@pytest.fixture
def extractor_config() -> ExtractorConfig:
    """Provide a default extractor config for testing."""
    return ExtractorConfig()


@pytest.fixture
def custom_config() -> ExtractorConfig:
    """Provide a custom extractor config for testing."""
    return ExtractorConfig(
        max_extractions_per_chunk=10,
        min_confidence=0.7,
        auto_tag_topics=False,
        include_context=False,
    )


@pytest.fixture
def fresh_registry() -> ExtractorRegistry:
    """Provide a fresh extractor registry for testing."""
    return ExtractorRegistry()


@pytest.fixture
def sample_decision() -> Decision:
    """Provide a sample Decision extraction for testing."""
    return Decision(
        source_id="src-123",
        chunk_id="chunk-456",
        question="Should I use RAG or fine-tuning?",
        options=["RAG", "Fine-tuning", "Both"],
        considerations=["Cost", "Accuracy", "Latency"],
        recommended_approach="RAG for most use cases",
        context="When building an LLM application",
    )


