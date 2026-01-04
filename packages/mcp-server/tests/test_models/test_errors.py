"""Tests for error models.

Story 4.6: Tests for ErrorCode enum and ErrorDetail/ErrorResponse models.
"""



class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_error_code_values(self):
        """Test that ErrorCode has all expected values."""
        from src.models.errors import ErrorCode

        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.UNAUTHORIZED.value == "UNAUTHORIZED"
        assert ErrorCode.FORBIDDEN.value == "FORBIDDEN"
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.RATE_LIMITED.value == "RATE_LIMITED"
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"

    def test_error_code_is_string_enum(self):
        """Test that ErrorCode is a string enum."""
        from src.models.errors import ErrorCode

        assert isinstance(ErrorCode.NOT_FOUND, str)
        assert ErrorCode.NOT_FOUND == "NOT_FOUND"

    def test_error_code_to_status_mapping(self):
        """Test that error codes map to correct HTTP status codes."""
        from src.models.errors import ErrorCode, ERROR_CODE_TO_STATUS

        assert ERROR_CODE_TO_STATUS[ErrorCode.VALIDATION_ERROR] == 400
        assert ERROR_CODE_TO_STATUS[ErrorCode.UNAUTHORIZED] == 401
        assert ERROR_CODE_TO_STATUS[ErrorCode.FORBIDDEN] == 403
        assert ERROR_CODE_TO_STATUS[ErrorCode.NOT_FOUND] == 404
        assert ERROR_CODE_TO_STATUS[ErrorCode.RATE_LIMITED] == 429
        assert ERROR_CODE_TO_STATUS[ErrorCode.INTERNAL_ERROR] == 500


class TestErrorDetail:
    """Tests for ErrorDetail model."""

    def test_error_detail_with_code_enum(self):
        """Test ErrorDetail with ErrorCode enum."""
        from src.models.errors import ErrorCode, ErrorDetail

        detail = ErrorDetail(
            code=ErrorCode.NOT_FOUND,
            message="Resource not found",
        )

        assert detail.code == ErrorCode.NOT_FOUND
        assert detail.message == "Resource not found"
        assert detail.details == {}
        assert detail.retry_after is None

    def test_error_detail_with_retry_after(self):
        """Test ErrorDetail with retry_after for rate limit."""
        from src.models.errors import ErrorCode, ErrorDetail

        detail = ErrorDetail(
            code=ErrorCode.RATE_LIMITED,
            message="Rate limit exceeded",
            retry_after=60,
        )

        assert detail.code == ErrorCode.RATE_LIMITED
        assert detail.retry_after == 60

    def test_error_detail_with_details(self):
        """Test ErrorDetail with additional details."""
        from src.models.errors import ErrorCode, ErrorDetail

        detail = ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid input",
            details={"field": "name", "error": "required"},
        )

        assert detail.details == {"field": "name", "error": "required"}

    def test_error_detail_serialization(self):
        """Test ErrorDetail serializes correctly."""
        from src.models.errors import ErrorCode, ErrorDetail

        detail = ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message="Server error",
            details={"correlation_id": "abc-123"},
        )

        data = detail.model_dump()

        assert data["code"] == "INTERNAL_ERROR"
        assert data["message"] == "Server error"
        assert data["details"]["correlation_id"] == "abc-123"


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_wraps_detail(self):
        """Test ErrorResponse wraps ErrorDetail."""
        from src.models.errors import ErrorCode, ErrorDetail, ErrorResponse

        detail = ErrorDetail(
            code=ErrorCode.NOT_FOUND,
            message="Not found",
        )
        response = ErrorResponse(error=detail)

        assert response.error.code == ErrorCode.NOT_FOUND
        assert response.error.message == "Not found"

    def test_error_response_serialization(self):
        """Test ErrorResponse serializes correctly."""
        from src.models.errors import ErrorCode, ErrorDetail, ErrorResponse

        detail = ErrorDetail(
            code=ErrorCode.FORBIDDEN,
            message="Access denied",
            details={"required_tier": "REGISTERED"},
        )
        response = ErrorResponse(error=detail)

        data = response.model_dump()

        assert "error" in data
        assert data["error"]["code"] == "FORBIDDEN"
        assert data["error"]["message"] == "Access denied"
        assert data["error"]["details"]["required_tier"] == "REGISTERED"


class TestLatencyInMetadata:
    """Tests for latency_ms in metadata models."""

    def test_response_metadata_has_latency_ms(self):
        """Test ResponseMetadata includes latency_ms."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=["source1"],
            result_count=1,
            search_type="semantic",
            latency_ms=42,
        )

        assert meta.latency_ms == 42

    def test_response_metadata_latency_ms_optional(self):
        """Test latency_ms is optional (defaults to None)."""
        from src.models.responses import ResponseMetadata

        meta = ResponseMetadata(
            query="test",
            sources_cited=[],
            result_count=0,
            search_type="filtered",
        )

        assert meta.latency_ms is None

    def test_search_metadata_has_latency_ms(self):
        """Test SearchMetadata includes latency_ms."""
        from src.models.responses import SearchMetadata

        meta = SearchMetadata(
            query="test query",
            sources_cited=["Book 1"],
            result_count=5,
            search_type="semantic",
            latency_ms=100,
        )

        assert meta.latency_ms == 100

    def test_extraction_metadata_has_latency_ms(self):
        """Test ExtractionMetadata includes latency_ms."""
        from src.models.responses import ExtractionMetadata

        meta = ExtractionMetadata(
            query="all",
            sources_cited=["Book 1"],
            result_count=10,
            search_type="filtered",
            latency_ms=50,
        )

        assert meta.latency_ms == 50

    def test_source_list_metadata_has_latency_ms(self):
        """Test SourceListMetadata includes latency_ms."""
        from src.models.responses import SourceListMetadata

        meta = SourceListMetadata(
            query="all",
            result_count=3,
            latency_ms=25,
        )

        assert meta.latency_ms == 25

    def test_comparison_metadata_has_latency_ms(self):
        """Test ComparisonMetadata includes latency_ms."""
        from src.models.responses import ComparisonMetadata

        meta = ComparisonMetadata(
            query="rag",
            sources_cited=["Book 1", "Book 2"],
            result_count=2,
            latency_ms=150,
        )

        assert meta.latency_ms == 150
