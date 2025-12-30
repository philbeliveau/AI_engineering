"""Test fixtures for adapters module."""

from pathlib import Path

import pytest

from src.adapters import AdapterConfig, AdapterResult, SourceAdapter


class ConcreteTestAdapter(SourceAdapter):
    """Minimal concrete adapter for testing purposes."""

    SUPPORTED_EXTENSIONS = [".txt", ".text"]

    def extract_text(self, file_path: Path) -> AdapterResult:
        self._validate_file_exists(file_path)
        self._validate_file_extension(file_path)
        return AdapterResult(
            text=file_path.read_text(),
            metadata=self.get_metadata(file_path),
        )

    def get_metadata(self, file_path: Path) -> dict:
        return {
            "title": self._extract_title_from_path(file_path),
            "path": str(file_path),
            "type": "text",
        }

    def supports_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS


class MinimalTestAdapter(SourceAdapter):
    """Minimal adapter with stub implementations for utility testing."""

    SUPPORTED_EXTENSIONS = [".txt"]

    def extract_text(self, file_path: Path) -> AdapterResult:
        return AdapterResult(text="", metadata={})

    def get_metadata(self, file_path: Path) -> dict:
        return {}

    def supports_file(self, file_path: Path) -> bool:
        return True


@pytest.fixture
def concrete_adapter() -> ConcreteTestAdapter:
    """Create a concrete test adapter instance."""
    return ConcreteTestAdapter()


@pytest.fixture
def minimal_adapter() -> MinimalTestAdapter:
    """Create a minimal test adapter for utility method testing."""
    return MinimalTestAdapter()


@pytest.fixture
def sample_text_file(tmp_path: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello, World!\n\nThis is a test document.")
    return file_path


@pytest.fixture
def custom_config() -> AdapterConfig:
    """Create a custom adapter config for testing."""
    return AdapterConfig(
        preserve_structure=False,
        include_metadata=True,
        max_section_depth=2,
    )
