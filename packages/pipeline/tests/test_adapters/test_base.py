"""Tests for base adapter module.

Tests cover:
- SourceAdapter ABC behavior
- Concrete adapter implementations
- Utility methods
- Adapter registry
- Exception classes
"""

from pathlib import Path

import pytest

from src.adapters import (
    AdapterConfig,
    AdapterError,
    AdapterRegistry,
    AdapterResult,
    FileParseError,
    MetadataExtractionError,
    Section,
    SourceAdapter,
    UnsupportedFileError,
)
from src.exceptions import KnowledgeError


class TestSourceAdapterABC:
    """Test that SourceAdapter is properly abstract."""

    def test_cannot_instantiate_directly(self):
        """SourceAdapter cannot be instantiated without implementing abstract methods."""
        with pytest.raises(TypeError) as exc_info:
            SourceAdapter()
        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_class_must_implement_abstract_methods(self):
        """Concrete class must implement all abstract methods."""

        class IncompleteAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".txt"]
            # Missing extract_text, get_metadata, supports_file

        with pytest.raises(TypeError):
            IncompleteAdapter()

    def test_partial_implementation_fails(self):
        """Class with only some abstract methods implemented still fails."""

        class PartialAdapter(SourceAdapter):
            SUPPORTED_EXTENSIONS = [".txt"]

            def extract_text(self, file_path):
                pass

            # Missing get_metadata, supports_file

        with pytest.raises(TypeError):
            PartialAdapter()


class TestConcreteAdapter:
    """Test a concrete adapter implementation."""

    def test_extract_text_file_not_found(self, concrete_adapter, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        fake_path = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            concrete_adapter.extract_text(fake_path)

    def test_extract_text_unsupported_extension(self, concrete_adapter, tmp_path):
        """Should raise UnsupportedFileError for wrong extension."""
        wrong_file = tmp_path / "file.pdf"
        wrong_file.touch()
        with pytest.raises(UnsupportedFileError) as exc_info:
            concrete_adapter.extract_text(wrong_file)
        assert exc_info.value.code == "UNSUPPORTED_FILE"

    def test_extract_text_success(self, concrete_adapter, sample_text_file):
        """Should extract text from valid file."""
        result = concrete_adapter.extract_text(sample_text_file)

        assert isinstance(result, AdapterResult)
        assert "Hello, World!" in result.text
        assert result.metadata["title"] == "Sample"
        assert result.metadata["type"] == "text"

    def test_supports_file_true(self, concrete_adapter):
        """Should correctly identify supported files."""
        assert concrete_adapter.supports_file(Path("doc.txt")) is True
        assert concrete_adapter.supports_file(Path("doc.text")) is True

    def test_supports_file_false(self, concrete_adapter):
        """Should correctly reject unsupported files."""
        assert concrete_adapter.supports_file(Path("doc.pdf")) is False
        assert concrete_adapter.supports_file(Path("doc.md")) is False

    def test_adapter_with_custom_config(self, custom_config):
        """Should accept custom configuration."""
        from tests.test_adapters.conftest import ConcreteTestAdapter

        adapter = ConcreteTestAdapter(config=custom_config)
        assert adapter.config.preserve_structure is False
        assert adapter.config.max_section_depth == 2


class TestUtilityMethods:
    """Test utility methods on SourceAdapter."""

    def test_normalize_whitespace_multiple_spaces(self, minimal_adapter):
        """Should collapse multiple spaces to single space."""
        input_text = "Hello   World"
        result = minimal_adapter._normalize_whitespace(input_text)
        assert result == "Hello World"

    def test_normalize_whitespace_multiple_newlines(self, minimal_adapter):
        """Should collapse multiple newlines to max two."""
        input_text = "Hello\n\n\n\nWorld"
        result = minimal_adapter._normalize_whitespace(input_text)
        assert result == "Hello\n\nWorld"

    def test_normalize_whitespace_mixed(self, minimal_adapter):
        """Should handle mixed whitespace issues."""
        input_text = "  Hello   World  \n\n\n\n  Test  "
        result = minimal_adapter._normalize_whitespace(input_text)
        # Note: space before newline is collapsed but preserved
        assert result == "Hello World \n\n Test"

    def test_normalize_whitespace_tabs(self, minimal_adapter):
        """Should collapse tabs to single space."""
        input_text = "Hello\t\tWorld"
        result = minimal_adapter._normalize_whitespace(input_text)
        assert result == "Hello World"

    def test_extract_title_from_path_basic(self, minimal_adapter):
        """Should extract clean title from filename."""
        path = Path("my-document_file.txt")
        title = minimal_adapter._extract_title_from_path(path)
        assert title == "My Document File"

    def test_extract_title_from_path_simple(self, minimal_adapter):
        """Should handle simple filename."""
        path = Path("readme.md")
        title = minimal_adapter._extract_title_from_path(path)
        assert title == "Readme"

    def test_extract_title_from_path_complex(self, minimal_adapter):
        """Should handle complex filenames."""
        path = Path("2025-01-01_project-notes_v2.txt")
        title = minimal_adapter._extract_title_from_path(path)
        assert title == "2025 01 01 Project Notes V2"

    def test_calculate_token_estimate(self, minimal_adapter):
        """Should estimate token count using 4-char heuristic."""
        text = "Hello World"  # 11 chars
        estimate = minimal_adapter._calculate_token_estimate(text)
        assert estimate == 2  # 11 // 4 = 2

    def test_calculate_token_estimate_empty(self, minimal_adapter):
        """Should handle empty text."""
        estimate = minimal_adapter._calculate_token_estimate("")
        assert estimate == 0

    def test_calculate_token_estimate_long(self, minimal_adapter):
        """Should scale with longer text."""
        text = "a" * 100  # 100 chars
        estimate = minimal_adapter._calculate_token_estimate(text)
        assert estimate == 25  # 100 // 4 = 25

    def test_validate_file_exists_missing(self, minimal_adapter, tmp_path):
        """Should raise FileNotFoundError for missing file."""
        fake_path = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError) as exc_info:
            minimal_adapter._validate_file_exists(fake_path)
        assert "not found" in str(exc_info.value).lower()

    def test_validate_file_exists_directory(self, minimal_adapter, tmp_path):
        """Should raise FileNotFoundError for directory path."""
        with pytest.raises(FileNotFoundError) as exc_info:
            minimal_adapter._validate_file_exists(tmp_path)
        assert "not a file" in str(exc_info.value).lower()

    def test_validate_file_exists_success(self, minimal_adapter, sample_text_file):
        """Should not raise for existing file."""
        # Should not raise
        minimal_adapter._validate_file_exists(sample_text_file)

    def test_validate_file_extension_unsupported(self, minimal_adapter, tmp_path):
        """Should raise UnsupportedFileError for wrong extension."""
        wrong_file = tmp_path / "file.pdf"
        wrong_file.touch()
        with pytest.raises(UnsupportedFileError):
            minimal_adapter._validate_file_extension(wrong_file)

    def test_validate_file_extension_success(self, minimal_adapter, tmp_path):
        """Should not raise for supported extension."""
        valid_file = tmp_path / "file.txt"
        valid_file.touch()
        # Should not raise
        minimal_adapter._validate_file_extension(valid_file)


class TestAdapterRegistry:
    """Test adapter registry functionality."""

    def test_register_and_get_adapter(self):
        """Should register and retrieve adapters."""
        from tests.test_adapters.conftest import ConcreteTestAdapter

        registry = AdapterRegistry()
        registry.register(".dummy", ConcreteTestAdapter)

        adapter = registry.get_adapter(Path("test.dummy"))
        assert isinstance(adapter, ConcreteTestAdapter)

    def test_get_adapter_unsupported_raises(self):
        """Should raise UnsupportedFileError for unregistered extension."""
        registry = AdapterRegistry()

        with pytest.raises(UnsupportedFileError) as exc_info:
            registry.get_adapter(Path("file.xyz"))
        assert exc_info.value.code == "UNSUPPORTED_FILE"

    def test_list_supported_extensions(self):
        """Should list all registered extensions."""
        from tests.test_adapters.conftest import ConcreteTestAdapter

        registry = AdapterRegistry()
        registry.register(".one", ConcreteTestAdapter)
        registry.register(".two", ConcreteTestAdapter)

        extensions = registry.list_supported_extensions()
        assert ".one" in extensions
        assert ".two" in extensions
        assert len(extensions) == 2

    def test_list_supported_extensions_empty(self):
        """Should return empty list for empty registry."""
        registry = AdapterRegistry()
        extensions = registry.list_supported_extensions()
        assert extensions == []

    def test_is_supported_true(self):
        """Should return True for supported extension."""
        from tests.test_adapters.conftest import ConcreteTestAdapter

        registry = AdapterRegistry()
        registry.register(".sup", ConcreteTestAdapter)

        assert registry.is_supported(Path("file.sup")) is True

    def test_is_supported_false(self):
        """Should return False for unsupported extension."""
        registry = AdapterRegistry()
        assert registry.is_supported(Path("file.unsup")) is False

    def test_case_insensitive_extension(self):
        """Should handle case-insensitive extensions."""
        from tests.test_adapters.conftest import ConcreteTestAdapter

        registry = AdapterRegistry()
        registry.register(".TXT", ConcreteTestAdapter)

        # Should work with lowercase
        assert registry.is_supported(Path("file.txt")) is True
        adapter = registry.get_adapter(Path("file.txt"))
        assert isinstance(adapter, ConcreteTestAdapter)

    def test_register_override_warning(self):
        """Should allow override of existing registration."""
        from tests.test_adapters.conftest import ConcreteTestAdapter, MinimalTestAdapter

        registry = AdapterRegistry()
        registry.register(".txt", ConcreteTestAdapter)
        # Should not raise, just warn
        registry.register(".txt", MinimalTestAdapter)

        # Should use the new adapter
        adapter = registry.get_adapter(Path("file.txt"))
        assert isinstance(adapter, MinimalTestAdapter)


class TestExceptions:
    """Test exception classes."""

    def test_adapter_error_inherits_from_knowledge_error(self):
        """AdapterError should inherit from KnowledgeError."""
        assert issubclass(AdapterError, KnowledgeError)

    def test_unsupported_file_error(self):
        """Should have structured error format."""
        error = UnsupportedFileError(Path("test.xyz"), [".pdf", ".md"])

        assert error.code == "UNSUPPORTED_FILE"
        assert ".xyz" in error.message
        assert error.details["supported"] == [".pdf", ".md"]
        assert "test.xyz" in error.details["path"]

    def test_file_parse_error(self):
        """Should have structured error format."""
        error = FileParseError(Path("corrupt.pdf"), "Invalid PDF structure")

        assert error.code == "FILE_PARSE_ERROR"
        assert "corrupt.pdf" in error.details["path"]
        assert error.details["reason"] == "Invalid PDF structure"

    def test_metadata_extraction_error(self):
        """Should have structured error format."""
        error = MetadataExtractionError(Path("doc.pdf"), "No title found")

        assert error.code == "METADATA_EXTRACTION_ERROR"
        assert "doc.pdf" in error.details["path"]
        assert error.details["reason"] == "No title found"

    def test_exception_hierarchy(self):
        """Exceptions should inherit from AdapterError."""
        assert issubclass(UnsupportedFileError, AdapterError)
        assert issubclass(FileParseError, AdapterError)
        assert issubclass(MetadataExtractionError, AdapterError)

    def test_exception_to_dict(self):
        """Should convert to dict format."""
        error = UnsupportedFileError(Path("test.xyz"), [".pdf"])
        error_dict = error.to_dict()

        assert "error" in error_dict
        assert error_dict["error"]["code"] == "UNSUPPORTED_FILE"
        assert "message" in error_dict["error"]
        assert "details" in error_dict["error"]


class TestDataModels:
    """Test Pydantic data models."""

    def test_section_model_defaults(self):
        """Section should have sensible defaults."""
        section = Section(title="Test", content="Content")

        assert section.title == "Test"
        assert section.content == "Content"
        assert section.level == 1
        assert section.position == {}

    def test_section_model_all_fields(self):
        """Section should accept all fields."""
        section = Section(
            title="Chapter 1",
            content="Introduction text",
            level=2,
            position={"page": 1, "chapter": 1},
        )

        assert section.level == 2
        assert section.position == {"page": 1, "chapter": 1}

    def test_section_level_validation(self):
        """Section level should be between 1-6."""
        with pytest.raises(ValueError):
            Section(title="Test", content="Content", level=0)

        with pytest.raises(ValueError):
            Section(title="Test", content="Content", level=7)

    def test_adapter_result_defaults(self):
        """AdapterResult should have sensible defaults."""
        result = AdapterResult(text="Hello", metadata={"title": "Test"})

        assert result.text == "Hello"
        assert result.metadata == {"title": "Test"}
        assert result.sections == []

    def test_adapter_result_with_sections(self):
        """AdapterResult should accept sections."""
        sections = [Section(title="Intro", content="Text")]
        result = AdapterResult(
            text="Full text",
            metadata={"title": "Doc"},
            sections=sections,
        )

        assert len(result.sections) == 1
        assert result.sections[0].title == "Intro"

    def test_adapter_config_defaults(self):
        """AdapterConfig should have sensible defaults."""
        config = AdapterConfig()

        assert config.preserve_structure is True
        assert config.include_metadata is True
        assert config.max_section_depth == 3

    def test_adapter_config_custom(self):
        """AdapterConfig should accept custom values."""
        config = AdapterConfig(
            preserve_structure=False,
            include_metadata=False,
            max_section_depth=5,
        )

        assert config.preserve_structure is False
        assert config.include_metadata is False
        assert config.max_section_depth == 5

    def test_adapter_config_depth_validation(self):
        """max_section_depth should be between 1-6."""
        with pytest.raises(ValueError):
            AdapterConfig(max_section_depth=0)

        with pytest.raises(ValueError):
            AdapterConfig(max_section_depth=7)
