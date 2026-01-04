"""Tests for exception classes."""



class TestKnowledgeError:
    """Test cases for base KnowledgeError exception."""

    def test_knowledge_error_has_code(self):
        """Test that KnowledgeError has a code attribute."""
        from src.exceptions import KnowledgeError

        error = KnowledgeError(code="TEST_ERROR", message="Test message")
        assert error.code == "TEST_ERROR"

    def test_knowledge_error_has_message(self):
        """Test that KnowledgeError has a message attribute."""
        from src.exceptions import KnowledgeError

        error = KnowledgeError(code="TEST_ERROR", message="Test message")
        assert error.message == "Test message"

    def test_knowledge_error_has_details(self):
        """Test that KnowledgeError has a details attribute."""
        from src.exceptions import KnowledgeError

        error = KnowledgeError(
            code="TEST_ERROR", message="Test message", details={"key": "value"}
        )
        assert error.details == {"key": "value"}

    def test_knowledge_error_default_details(self):
        """Test that details defaults to empty dict."""
        from src.exceptions import KnowledgeError

        error = KnowledgeError(code="TEST_ERROR", message="Test message")
        assert error.details == {}

    def test_knowledge_error_is_exception(self):
        """Test that KnowledgeError is an Exception."""
        from src.exceptions import KnowledgeError

        error = KnowledgeError(code="TEST_ERROR", message="Test message")
        assert isinstance(error, Exception)


class TestNotFoundError:
    """Test cases for NotFoundError exception."""

    def test_not_found_error_inherits_knowledge_error(self):
        """Test that NotFoundError inherits from KnowledgeError."""
        from src.exceptions import KnowledgeError, NotFoundError

        error = NotFoundError(resource="source", resource_id="test-123")
        assert isinstance(error, KnowledgeError)

    def test_not_found_error_has_not_found_code(self):
        """Test that NotFoundError has NOT_FOUND code."""
        from src.exceptions import NotFoundError

        error = NotFoundError(resource="source", resource_id="test-123")
        assert error.code == "NOT_FOUND"

    def test_not_found_error_has_status_code(self):
        """Test that NotFoundError has status_code 404."""
        from src.exceptions import NotFoundError

        error = NotFoundError(resource="source", resource_id="test-123")
        assert error.status_code == 404

    def test_not_found_error_has_details(self):
        """Test that NotFoundError has correct details."""
        from src.exceptions import NotFoundError

        error = NotFoundError(resource="source", resource_id="test-123")
        assert error.details == {"resource": "source", "id": "test-123"}

    def test_not_found_error_has_auto_generated_message(self):
        """Test that NotFoundError auto-generates message."""
        from src.exceptions import NotFoundError

        error = NotFoundError(resource="source", resource_id="test-123")
        assert error.message == "source with id 'test-123' not found"


class TestValidationError:
    """Test cases for ValidationError exception."""

    def test_validation_error_inherits_knowledge_error(self):
        """Test that ValidationError inherits from KnowledgeError."""
        from src.exceptions import KnowledgeError, ValidationError

        error = ValidationError(message="Invalid input")
        assert isinstance(error, KnowledgeError)

    def test_validation_error_has_validation_error_code(self):
        """Test that ValidationError has VALIDATION_ERROR code."""
        from src.exceptions import ValidationError

        error = ValidationError(message="Invalid input")
        assert error.code == "VALIDATION_ERROR"


class TestDatabaseError:
    """Test cases for DatabaseError exception."""

    def test_database_error_inherits_knowledge_error(self):
        """Test that DatabaseError inherits from KnowledgeError."""
        from src.exceptions import DatabaseError, KnowledgeError

        error = DatabaseError(message="Database connection failed")
        assert isinstance(error, KnowledgeError)

    def test_database_error_has_internal_error_code(self):
        """Test that DatabaseError has INTERNAL_ERROR code."""
        from src.exceptions import DatabaseError

        error = DatabaseError(message="Database connection failed")
        assert error.code == "INTERNAL_ERROR"


class TestRateLimitError:
    """Test cases for RateLimitError exception."""

    def test_rate_limit_error_inherits_knowledge_error(self):
        """Test that RateLimitError inherits from KnowledgeError."""
        from src.exceptions import KnowledgeError, RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert isinstance(error, KnowledgeError)

    def test_rate_limit_error_has_rate_limited_code(self):
        """Test that RateLimitError has RATE_LIMITED code."""
        from src.exceptions import RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert error.code == "RATE_LIMITED"

    def test_rate_limit_error_has_status_code(self):
        """Test that RateLimitError has status_code 429."""
        from src.exceptions import RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert error.status_code == 429

    def test_rate_limit_error_has_retry_after(self):
        """Test that RateLimitError has retry_after attribute."""
        from src.exceptions import RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert error.retry_after == 60

    def test_rate_limit_error_has_details(self):
        """Test that RateLimitError has correct details."""
        from src.exceptions import RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert error.details == {"limit": 100, "window": "hour", "retry_after": 60}

    def test_rate_limit_error_has_auto_generated_message(self):
        """Test that RateLimitError auto-generates message."""
        from src.exceptions import RateLimitError

        error = RateLimitError(retry_after=60, limit=100, window="hour")
        assert "60 seconds" in error.message
