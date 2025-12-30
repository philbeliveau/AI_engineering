"""Custom exceptions for the knowledge pipeline."""


class KnowledgeError(Exception):
    """Base exception for all knowledge pipeline errors."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict:
        """Convert exception to dictionary format for API responses."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class NotFoundError(KnowledgeError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, id: str):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} with id '{id}' not found",
            details={"resource": resource, "id": id},
        )


class StorageError(KnowledgeError):
    """Raised when a database operation fails."""

    def __init__(self, operation: str, details: dict | None = None):
        super().__init__(
            code="STORAGE_ERROR",
            message=f"Storage operation '{operation}' failed",
            details=details or {},
        )


class ValidationError(KnowledgeError):
    """Raised when data validation fails."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details or {},
        )


# ============================================================================
# Qdrant-Specific Exceptions
# ============================================================================


class QdrantConnectionError(KnowledgeError):
    """Raised when Qdrant connection fails."""

    pass


class QdrantCollectionError(KnowledgeError):
    """Raised when Qdrant collection operations fail."""

    pass


class QdrantVectorError(KnowledgeError):
    """Raised when vector operations fail (wrong dimensions, etc.)."""

    pass
