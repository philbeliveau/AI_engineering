"""Global exception handlers for Knowledge MCP Server.

Follows architecture.md:478-497 (Error response format) and
project-context.md:152-160 (Error response format).

Story 4.6: Centralized exception handlers for consistent error responses.
"""

import uuid

import structlog
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions import InternalError, KnowledgeError, RateLimitError
from src.models.errors import ErrorCode, ErrorDetail, ErrorResponse

logger = structlog.get_logger()


async def knowledge_error_handler(request: Request, exc: KnowledgeError) -> JSONResponse:
    """Handle KnowledgeError exceptions.

    Converts KnowledgeError to standardized JSON error response.
    Uses the exception's status_code for HTTP response.

    Args:
        request: FastAPI request object
        exc: KnowledgeError exception

    Returns:
        JSONResponse with ErrorResponse body
    """
    # Log the error (warning for client errors, error for server errors)
    log_level = "warning" if exc.status_code < 500 else "error"
    getattr(logger, log_level)(
        "knowledge_error",
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
    )

    # Build response
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode(exc.code) if exc.code in ErrorCode.__members__.values() else ErrorCode.INTERNAL_ERROR,
            message=exc.message,
            details=exc.details,
            retry_after=getattr(exc, "retry_after", None),
        )
    )

    # Build headers (add Retry-After for rate limit errors)
    headers: dict[str, str] = {}
    if isinstance(exc, RateLimitError):
        headers["Retry-After"] = str(exc.retry_after)

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
        headers=headers if headers else None,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle Pydantic/FastAPI validation errors.

    Maps Pydantic validation errors to VALIDATION_ERROR format
    with field-level error details.

    Args:
        request: FastAPI request object
        exc: RequestValidationError exception

    Returns:
        JSONResponse with 400 status and validation error details
    """
    # Convert Pydantic errors to field-level messages
    errors: dict[str, str] = {}
    for error in exc.errors():
        # Build field path from location tuple
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]

    logger.warning(
        "validation_error",
        errors=errors,
        path=request.url.path,
        method=request.method,
    )

    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid request parameters",
            details=errors,
        )
    )

    return JSONResponse(status_code=400, content=response.model_dump())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions safely.

    Generates a correlation_id for log correlation and debugging.
    Never exposes sensitive error details to clients.

    Args:
        request: FastAPI request object
        exc: Uncaught exception

    Returns:
        JSONResponse with 500 status and correlation_id only
    """
    correlation_id = str(uuid.uuid4())

    # Log full error details for debugging (server-side only)
    logger.error(
        "internal_error",
        correlation_id=correlation_id,
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True,  # Include stack trace in logs
    )

    # Create safe error response with correlation ID only
    error = InternalError(correlation_id=correlation_id)
    response = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message=error.message,
            details=error.details,
        )
    )

    return JSONResponse(status_code=500, content=response.model_dump())
