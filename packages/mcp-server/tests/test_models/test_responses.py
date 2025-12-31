"""Tests for response models."""

from pydantic import BaseModel


class TestResponseMetadata:
    """Test cases for ResponseMetadata model."""

    def test_response_metadata_has_query(self):
        """Test that ResponseMetadata has query field."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test query",
            sources_cited=["source1"],
            result_count=5,
            search_type="semantic",
        )
        assert meta.query == "test query"

    def test_response_metadata_has_sources_cited(self):
        """Test that ResponseMetadata has sources_cited field."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=["source1", "source2"],
            result_count=5,
            search_type="semantic",
        )
        assert meta.sources_cited == ["source1", "source2"]

    def test_response_metadata_has_result_count(self):
        """Test that ResponseMetadata has result_count field."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=[],
            result_count=10,
            search_type="semantic",
        )
        assert meta.result_count == 10

    def test_response_metadata_has_search_type(self):
        """Test that ResponseMetadata has search_type field."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=[],
            result_count=5,
            search_type="filtered",
        )
        assert meta.search_type == "filtered"

    def test_response_metadata_is_pydantic_model(self):
        """Test that ResponseMetadata is a Pydantic model."""
        from src.models.responses import ResponseMetadata

        assert issubclass(ResponseMetadata, BaseModel)


class TestApiResponse:
    """Test cases for ApiResponse model."""

    def test_api_response_has_results(self):
        """Test that ApiResponse has results field."""
        from src.models.responses import ApiResponse, ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=[],
            result_count=2,
            search_type="semantic",
        )
        response = ApiResponse(results=["item1", "item2"], metadata=meta)
        assert response.results == ["item1", "item2"]

    def test_api_response_has_metadata(self):
        """Test that ApiResponse has metadata field."""
        from src.models.responses import ApiResponse, ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=["source1"],
            result_count=1,
            search_type="exact",
        )
        response = ApiResponse(results=["item"], metadata=meta)
        assert response.metadata.query == "test"
        assert response.metadata.sources_cited == ["source1"]

    def test_api_response_is_generic(self):
        """Test that ApiResponse works with different types."""
        from src.models.responses import ApiResponse, ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=[],
            result_count=1,
            search_type="semantic",
        )
        # Test with dict results
        response = ApiResponse(results=[{"key": "value"}], metadata=meta)
        assert response.results[0]["key"] == "value"


class TestErrorDetail:
    """Test cases for ErrorDetail model."""

    def test_error_detail_has_code(self):
        """Test that ErrorDetail has code field."""
        from src.models.responses import ErrorDetail

        error = ErrorDetail(
            code="VALIDATION_ERROR",
            message="Invalid input",
            details={"field": "name"},
        )
        assert error.code == "VALIDATION_ERROR"

    def test_error_detail_has_message(self):
        """Test that ErrorDetail has message field."""
        from src.models.responses import ErrorDetail

        error = ErrorDetail(
            code="NOT_FOUND",
            message="Resource not found",
            details={},
        )
        assert error.message == "Resource not found"

    def test_error_detail_has_details(self):
        """Test that ErrorDetail has details field."""
        from src.models.responses import ErrorDetail

        error = ErrorDetail(
            code="INTERNAL_ERROR",
            message="Database error",
            details={"collection": "sources"},
        )
        assert error.details == {"collection": "sources"}


class TestErrorResponse:
    """Test cases for ErrorResponse model."""

    def test_error_response_has_error(self):
        """Test that ErrorResponse has error field."""
        from src.models.responses import ErrorDetail, ErrorResponse

        detail = ErrorDetail(
            code="NOT_FOUND",
            message="Not found",
            details={},
        )
        response = ErrorResponse(error=detail)
        assert response.error.code == "NOT_FOUND"
        assert response.error.message == "Not found"

    def test_error_response_is_pydantic_model(self):
        """Test that ErrorResponse is a Pydantic model."""
        from src.models.responses import ErrorResponse

        assert issubclass(ErrorResponse, BaseModel)


class TestModelExports:
    """Test that all models are exported from the package."""

    def test_response_metadata_exported(self):
        """Test ResponseMetadata is exported from models package."""
        from src.models import ResponseMetadata

        assert ResponseMetadata is not None

    def test_api_response_exported(self):
        """Test ApiResponse is exported from models package."""
        from src.models import ApiResponse

        assert ApiResponse is not None

    def test_error_detail_exported(self):
        """Test ErrorDetail is exported from models package."""
        from src.models import ErrorDetail

        assert ErrorDetail is not None

    def test_error_response_exported(self):
        """Test ErrorResponse is exported from models package."""
        from src.models import ErrorResponse

        assert ErrorResponse is not None
