"""Cloud database connection handlers for Knowledge MCP Server.

Provides factory functions for creating MongoDB and Qdrant clients
configured for cloud (Atlas/Qdrant Cloud) or local development.

Follows project-context.md:59-64 (configuration via pydantic-settings)
and project-context.md:152-164 (structured logging).
"""

import asyncio
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import structlog
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from qdrant_client import QdrantClient

from src.config import Settings

if TYPE_CHECKING:
    from src.storage.mongodb import MongoDBClient
    from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()

T = TypeVar("T")


class ValidationResult:
    """Result of environment validation."""

    def __init__(self) -> None:
        self.is_valid: bool = True
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str) -> None:
        """Add a validation error (makes result invalid)."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a validation warning (does not affect validity)."""
        self.warnings.append(message)


def _is_local_uri(uri: str) -> bool:
    """Check if a URI points to localhost or 127.0.0.1."""
    return "localhost" in uri or "127.0.0.1" in uri


def _validate_mongodb_uri_format(uri: str) -> bool:
    """Validate MongoDB URI format."""
    return uri.startswith("mongodb://") or uri.startswith("mongodb+srv://")


def _validate_qdrant_url_format(url: str) -> bool:
    """Validate Qdrant URL format."""
    return url.startswith("http://") or url.startswith("https://")


def validate_environment(
    environment: str,
    mongodb_uri: str,
    qdrant_url: str,
) -> ValidationResult:
    """Validate environment configuration for database connections.

    Checks:
    - URI/URL format validity
    - Production requires cloud databases (not localhost)
    - Warns about local databases in development

    Args:
        environment: Deployment environment (local, staging, production)
        mongodb_uri: MongoDB connection URI
        qdrant_url: Qdrant server URL

    Returns:
        ValidationResult with is_valid, errors, and warnings
    """
    result = ValidationResult()

    # Validate URI formats
    if not _validate_mongodb_uri_format(mongodb_uri):
        result.add_error(
            "MongoDB URI has invalid format. Must start with 'mongodb://' or 'mongodb+srv://'"
        )

    if not _validate_qdrant_url_format(qdrant_url):
        result.add_error(
            "Qdrant URL has invalid format. Must start with 'http://' or 'https://'"
        )

    # If format validation failed, skip further checks
    if not result.is_valid:
        return result

    mongodb_is_local = _is_local_uri(mongodb_uri)
    qdrant_is_local = _is_local_uri(qdrant_url)

    if environment == "production":
        # Production MUST use cloud databases
        if mongodb_is_local:
            result.add_error(
                "Production environment cannot use localhost MongoDB. "
                "Configure MongoDB Atlas connection string."
            )
        if qdrant_is_local:
            result.add_error(
                "Production environment cannot use localhost Qdrant. "
                "Configure Qdrant Cloud connection string."
            )
    elif environment in ("local", "staging"):
        # Local and staging can use local databases, but warn
        if mongodb_is_local:
            result.add_warning(
                f"Using local MongoDB in {environment} environment. "
                "Consider using cloud database for staging."
            )
        if qdrant_is_local:
            result.add_warning(
                f"Using local Qdrant in {environment} environment. "
                "Consider using cloud database for staging."
            )

    # Log validation result
    if result.is_valid:
        if result.warnings:
            logger.warning(
                "environment_validation_passed_with_warnings",
                environment=environment,
                warnings=result.warnings,
            )
        else:
            logger.info(
                "environment_validation_passed",
                environment=environment,
            )
    else:
        logger.error(
            "environment_validation_failed",
            environment=environment,
            errors=result.errors,
        )

    return result


def is_cloud_mongodb(uri: str) -> bool:
    """Detect if MongoDB URI points to MongoDB Atlas.

    Atlas connections use either:
    - mongodb+srv:// protocol (DNS-based discovery)
    - .mongodb.net domain

    Args:
        uri: MongoDB connection URI

    Returns:
        True if URI points to Atlas, False for local MongoDB
    """
    return "mongodb+srv://" in uri or "mongodb.net" in uri


def is_cloud_qdrant(url: str) -> bool:
    """Detect if Qdrant URL points to Qdrant Cloud.

    Qdrant Cloud URLs contain the .cloud.qdrant.io domain.

    Args:
        url: Qdrant server URL

    Returns:
        True if URL points to Qdrant Cloud, False for local Qdrant
    """
    return "cloud.qdrant.io" in url


def create_mongodb_client(settings: Settings | None = None) -> MongoClient:
    """Create MongoDB client configured for the current environment.

    For MongoDB Atlas (cloud):
    - Uses ServerApi '1' for versioned API compatibility
    - Enables retryWrites and w=majority via connection string
    - SSL/TLS is automatic with mongodb+srv://

    For local MongoDB:
    - Uses simpler configuration without ServerApi
    - No SSL by default

    Args:
        settings: Optional settings override (uses singleton if None)

    Returns:
        Configured MongoClient instance

    Raises:
        Exception: If connection fails (should be caught by caller)
    """
    if settings is None:
        from src.config import settings as default_settings
        settings = default_settings

    uri = settings.mongodb_uri
    is_cloud = is_cloud_mongodb(uri)

    if is_cloud:
        logger.info(
            "creating_mongodb_client",
            connection_type="atlas",
            timeout_ms=settings.connection_timeout_ms,
            max_pool_size=settings.max_pool_size,
        )
        return MongoClient(
            uri,
            server_api=ServerApi("1"),
            serverSelectionTimeoutMS=settings.connection_timeout_ms,
            connectTimeoutMS=settings.connection_timeout_ms * 2,  # 2x for initial connect
            maxPoolSize=settings.max_pool_size,
        )
    else:
        logger.info(
            "creating_mongodb_client",
            connection_type="local",
            timeout_ms=settings.connection_timeout_ms,
        )
        return MongoClient(
            uri,
            serverSelectionTimeoutMS=settings.connection_timeout_ms,
        )


def create_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    """Create Qdrant client configured for the current environment.

    For Qdrant Cloud:
    - Uses HTTPS (automatic with cloud URLs)
    - Adds API key authentication
    - Sets longer timeout for network latency

    For local Qdrant:
    - Uses HTTP (no TLS)
    - No API key needed

    Args:
        settings: Optional settings override (uses singleton if None)

    Returns:
        Configured QdrantClient instance

    Raises:
        Exception: If connection fails (should be caught by caller)
    """
    if settings is None:
        from src.config import settings as default_settings
        settings = default_settings

    url = settings.qdrant_url
    is_cloud = is_cloud_qdrant(url)

    if is_cloud:
        logger.info(
            "creating_qdrant_client",
            connection_type="cloud",
            has_api_key=settings.qdrant_api_key is not None,
        )
        return QdrantClient(
            url=url,
            api_key=settings.qdrant_api_key,
            timeout=30,  # 30 second timeout for cloud operations
        )
    else:
        logger.info(
            "creating_qdrant_client",
            connection_type="local",
        )
        return QdrantClient(
            url=url,
            api_key=None,
            timeout=30,
        )


async def check_database_health(
    mongodb_client: "MongoDBClient | None",
    qdrant_client: "QdrantStorageClient | None",
) -> dict[str, Any]:
    """Check health of database connections.

    Tests MongoDB and Qdrant connections using their ping methods.
    Does not crash the application on connection failure.

    Args:
        mongodb_client: MongoDB client instance (or None if unavailable)
        qdrant_client: Qdrant client instance (or None if unavailable)

    Returns:
        Health status dictionary:
        {
            "mongodb": bool,  # True if healthy
            "qdrant": bool,   # True if healthy
            "details": {
                "mongodb_error": str | None,  # Error message if unhealthy
                "qdrant_error": str | None,   # Error message if unhealthy
            }
        }
    """
    result: dict[str, Any] = {
        "mongodb": False,
        "qdrant": False,
        "details": {
            "mongodb_error": None,
            "qdrant_error": None,
        },
    }

    # Check MongoDB
    if mongodb_client is None:
        result["details"]["mongodb_error"] = "Client not initialized"
        logger.warning("health_check_mongodb", status="unavailable", error="Client not initialized")
    else:
        try:
            is_healthy = await mongodb_client.ping()
            result["mongodb"] = is_healthy
            if not is_healthy:
                result["details"]["mongodb_error"] = "Ping returned False"
                logger.warning("health_check_mongodb", status="unhealthy", error="Ping returned False")
            else:
                logger.debug("health_check_mongodb", status="healthy")
        except Exception as e:
            result["details"]["mongodb_error"] = str(e)
            logger.warning("health_check_mongodb", status="error", error=str(e))

    # Check Qdrant
    if qdrant_client is None:
        result["details"]["qdrant_error"] = "Client not initialized"
        logger.warning("health_check_qdrant", status="unavailable", error="Client not initialized")
    else:
        try:
            is_healthy = await qdrant_client.ping()
            result["qdrant"] = is_healthy
            if not is_healthy:
                result["details"]["qdrant_error"] = "Ping returned False"
                logger.warning("health_check_qdrant", status="unhealthy", error="Ping returned False")
            else:
                logger.debug("health_check_qdrant", status="healthy")
        except Exception as e:
            result["details"]["qdrant_error"] = str(e)
            logger.warning("health_check_qdrant", status="error", error=str(e))

    logger.info(
        "database_health_check_completed",
        mongodb=result["mongodb"],
        qdrant=result["qdrant"],
    )

    return result


async def connect_with_retry(
    connect_func: Callable[[], T],
    max_retries: int = 5,
    base_delay: float = 1.0,
    operation_name: str = "connection",
) -> T:
    """Execute a connection function with exponential backoff retry.

    Implements exponential backoff with the following wait times:
    - Attempt 1: 0s (immediate)
    - Attempt 2: base_delay (1s default)
    - Attempt 3: base_delay * 2 (2s)
    - Attempt 4: base_delay * 4 (4s)
    - Attempt 5: base_delay * 8 (8s)

    Args:
        connect_func: Async function to execute (should raise on failure)
        max_retries: Maximum number of attempts (default 5)
        base_delay: Initial delay in seconds (default 1.0)
        operation_name: Name for logging purposes

    Returns:
        Result of successful connect_func call

    Raises:
        ConnectionError: After max_retries attempts with the last error
    """
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(
                "connection_attempt",
                operation=operation_name,
                attempt=attempt,
                max_retries=max_retries,
            )
            result = await connect_func()
            if attempt > 1:
                logger.info(
                    "connection_succeeded_after_retry",
                    operation=operation_name,
                    attempt=attempt,
                )
            return result
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                # Calculate exponential backoff delay
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "connection_failed_retrying",
                    operation=operation_name,
                    attempt=attempt,
                    max_retries=max_retries,
                    delay_seconds=delay,
                    error=str(e),
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "connection_failed_max_retries",
                    operation=operation_name,
                    attempts=attempt,
                    error=str(e),
                )

    # All retries exhausted
    raise ConnectionError(
        f"{operation_name} failed after {max_retries} attempts: {last_error}"
    ) from last_error
