"""Tests for error handler middleware.

Story 4.6: Tests for centralized exception handlers.
"""

import pytest
from unittest.mock import MagicMock


class TestKnowledgeErrorHandler:
    """Tests for knowledge_error_handler."""

    @pytest.mark.asyncio
    async def test_handles_knowledge_error(self):
        """Test that KnowledgeError is converted to JSON response."""
        from fastapi import Request
        from src.middleware.error_handlers import knowledge_error_handler
        from src.exceptions import KnowledgeError
        from src.models.errors import ErrorCode

        # Create mock request
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        exc = KnowledgeError(
            code=ErrorCode.INTERNAL_ERROR,
            message="Test error",
            status_code=500,
            details={"test": "value"},
        )

        response = await knowledge_error_handler(request, exc)

        assert response.status_code == 500
        data = response.body.decode()
        assert "INTERNAL_ERROR" in data
        assert "Test error" in data

    @pytest.mark.asyncio
    async def test_handles_not_found_error(self):
        """Test that NotFoundError returns 404."""
        from fastapi import Request
        from src.middleware.error_handlers import knowledge_error_handler
        from src.exceptions import NotFoundError

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        exc = NotFoundError(resource="source", resource_id="test-123")

        response = await knowledge_error_handler(request, exc)

        assert response.status_code == 404
        data = response.body.decode()
        assert "NOT_FOUND" in data

    @pytest.mark.asyncio
    async def test_handles_validation_error(self):
        """Test that ValidationError returns 400."""
        from fastapi import Request
        from src.middleware.error_handlers import knowledge_error_handler
        from src.exceptions import ValidationError

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        exc = ValidationError(
            message="Invalid input",
            details={"field": "error message"},
        )

        response = await knowledge_error_handler(request, exc)

        assert response.status_code == 400
        data = response.body.decode()
        assert "VALIDATION_ERROR" in data

    @pytest.mark.asyncio
    async def test_handles_rate_limit_error_with_retry_after(self):
        """Test that RateLimitError includes Retry-After header."""
        from fastapi import Request
        from src.middleware.error_handlers import knowledge_error_handler
        from src.exceptions import RateLimitError

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        exc = RateLimitError(retry_after=60, limit=100, window="hour")

        response = await knowledge_error_handler(request, exc)

        assert response.status_code == 429
        assert response.headers.get("Retry-After") == "60"


class TestValidationExceptionHandler:
    """Tests for validation_exception_handler."""

    @pytest.mark.asyncio
    async def test_handles_pydantic_validation_error(self):
        """Test that Pydantic validation errors are converted to 400 response."""
        from fastapi import Request
        from src.middleware.error_handlers import validation_exception_handler

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "POST"

        # Create a mock RequestValidationError
        class MockError:
            def errors(self):
                return [
                    {"loc": ("body", "name"), "msg": "field required"},
                    {"loc": ("query", "limit"), "msg": "value is not a valid integer"},
                ]

        exc = MockError()

        response = await validation_exception_handler(request, exc)

        assert response.status_code == 400
        data = response.body.decode()
        assert "VALIDATION_ERROR" in data
        assert "Invalid request parameters" in data


class TestGenericExceptionHandler:
    """Tests for generic_exception_handler."""

    @pytest.mark.asyncio
    async def test_handles_uncaught_exception(self):
        """Test that uncaught exceptions return 500 with correlation_id."""
        from fastapi import Request
        from src.middleware.error_handlers import generic_exception_handler

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        exc = Exception("Unexpected error")

        response = await generic_exception_handler(request, exc)

        assert response.status_code == 500
        import json
        data = json.loads(response.body.decode())
        assert data["error"]["code"] == "INTERNAL_ERROR"
        assert "correlation_id" in data["error"]["details"]
        # Message should be safe (not expose original error)
        assert "Unexpected error" not in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_generates_unique_correlation_ids(self):
        """Test that each error gets a unique correlation_id."""
        from fastapi import Request
        from src.middleware.error_handlers import generic_exception_handler

        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"

        exc1 = Exception("Error 1")
        exc2 = Exception("Error 2")

        response1 = await generic_exception_handler(request, exc1)
        response2 = await generic_exception_handler(request, exc2)

        import json
        data1 = json.loads(response1.body.decode())
        data2 = json.loads(response2.body.decode())

        correlation_id1 = data1["error"]["details"]["correlation_id"]
        correlation_id2 = data2["error"]["details"]["correlation_id"]

        assert correlation_id1 != correlation_id2


class TestErrorHandlerIntegration:
    """Integration tests for error handlers with FastAPI."""

    @pytest.mark.asyncio
    async def test_validation_error_returns_400_with_error_format(self):
        """Test that validation errors return standardized error format."""
        from httpx import ASGITransport, AsyncClient
        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send invalid request
            response = await client.get("/get_decisions", params={"limit": -1})

            assert response.status_code == 400
            data = response.json()
            assert "error" in data
            assert data["error"]["code"] == "VALIDATION_ERROR"
            assert "message" in data["error"]
            assert "details" in data["error"]

    @pytest.mark.asyncio
    async def test_auth_error_returns_401(self):
        """Test that authentication errors return 401."""
        from httpx import ASGITransport, AsyncClient
        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send request with invalid API key
            response = await client.get(
                "/get_methodologies",
                headers={"X-API-Key": "invalid-key-format"},
            )

            assert response.status_code == 401
            data = response.json()
            assert data["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_forbidden_error_returns_403(self):
        """Test that authorization errors return 403."""
        from httpx import ASGITransport, AsyncClient
        from src.server import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Send request without auth to restricted endpoint
            response = await client.get("/get_methodologies")

            assert response.status_code == 403
            data = response.json()
            assert data["error"]["code"] == "FORBIDDEN"
