"""FastAPI server for Knowledge MCP Server.

Main application entry point providing:
- Health check endpoint at /health
- MCP protocol endpoint at /mcp (mounted via fastapi-mcp)
- Database connections to MongoDB and Qdrant

Follows project-context.md:54-57 (all endpoints MUST be async) and
project-context.md:152-164 (structured logging).
"""

from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP

from src import __version__
from src.config import settings
from fastapi.exceptions import RequestValidationError

from src.exceptions import KnowledgeError
from src.middleware.error_handlers import (
    generic_exception_handler,
    knowledge_error_handler,
    validation_exception_handler,
)
from src.middleware.auth import AuthMiddleware, get_validator
from src.models.auth import APIKey, UserTier
from src.storage import validate_environment
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient
from src.tools.health import health_check as check_health
from src.tools.search import router as search_router, set_clients
from src.tools.decisions import router as decisions_router, set_qdrant_client as set_decisions_client
from src.tools.patterns import router as patterns_router, set_qdrant_client as set_patterns_client
from src.tools.warnings import router as warnings_router, set_qdrant_client as set_warnings_client
from src.tools.methodologies import router as methodologies_router, set_clients as set_methodologies_clients
from src.tools.sources import router as sources_router, set_clients as set_sources_clients

logger = structlog.get_logger()

# Global storage clients (initialized during startup)
mongodb_client: MongoDBClient | None = None
qdrant_client: QdrantStorageClient | None = None


def load_api_keys() -> None:
    """Load API keys from configuration file into the global validator.

    Reads API keys from the file specified by API_KEYS_FILE environment variable
    and registers them with the global APIKeyValidator instance.
    """
    api_keys_data = settings.get_api_keys()
    if not api_keys_data:
        logger.info("no_api_keys_configured")
        return

    validator = get_validator()
    for key_data in api_keys_data:
        try:
            # Parse tier string to enum
            tier_str = key_data.get("tier", "REGISTERED").upper()
            tier = UserTier(tier_str)

            api_key = APIKey(
                key=key_data["key"],
                tier=tier,
                metadata=key_data.get("metadata", {}),
            )
            validator.register_key(api_key)
        except (KeyError, ValueError) as e:
            logger.warning(
                "api_key_load_failed",
                error=str(e),
                key_prefix=key_data.get("key", "unknown")[:8] + "...",
            )

    logger.info("api_keys_loaded", count=len(api_keys_data))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle (startup and shutdown).

    Initializes database connections on startup and closes them on shutdown.
    Validates environment configuration before connecting.
    """
    global mongodb_client, qdrant_client

    # Startup
    logger.info(
        "server_starting",
        environment=settings.environment,
        host=settings.server_host,
        port=settings.server_port,
        project_id=settings.project_id,
    )

    # Validate environment configuration (fail fast for production with invalid config)
    validation = validate_environment(
        environment=settings.environment,
        mongodb_uri=settings.mongodb_uri,
        qdrant_url=settings.qdrant_url,
    )

    if not validation.is_valid:
        logger.critical(
            "environment_validation_failed",
            errors=validation.errors,
        )
        if settings.environment == "production":
            # Fail fast in production with invalid configuration
            raise RuntimeError(
                f"Invalid production configuration: {'; '.join(validation.errors)}"
            )

    # Log startup configuration (without secrets)
    logger.info(
        "database_configuration",
        environment=settings.environment,
        mongodb_is_cloud="mongodb+srv://" in settings.mongodb_uri or "mongodb.net" in settings.mongodb_uri,
        qdrant_is_cloud="cloud.qdrant.io" in settings.qdrant_url,
        connection_timeout_ms=settings.connection_timeout_ms,
        max_pool_size=settings.max_pool_size,
    )

    # Load API keys from configuration
    load_api_keys()

    # Initialize MongoDB client
    mongodb_client = MongoDBClient(settings)
    try:
        await mongodb_client.connect()
        logger.info("mongodb_connected", database=settings.mongodb_database)
    except Exception as e:
        logger.error("mongodb_connection_failed", error=str(e))
        mongodb_client = None

    # Initialize Qdrant client
    qdrant_client = QdrantStorageClient(settings)
    try:
        await qdrant_client.connect()
        logger.info("qdrant_connected")
    except Exception as e:
        logger.error("qdrant_connection_failed", error=str(e))
        qdrant_client = None

    # Set clients for search module
    set_clients(qdrant=qdrant_client, mongodb=mongodb_client)

    # Set Qdrant client for extraction query tools (Story 4.3)
    set_decisions_client(qdrant_client)
    set_patterns_client(qdrant_client)
    set_warnings_client(qdrant_client)

    # Set clients for methodologies tool (Story 4.4)
    set_methodologies_clients(qdrant=qdrant_client, mongodb=mongodb_client)

    # Set clients for sources tools (Story 4.5)
    set_sources_clients(qdrant=qdrant_client, mongodb=mongodb_client)

    logger.info(
        "server_started",
        environment=settings.environment,
        mongodb_connected=mongodb_client is not None,
        qdrant_connected=qdrant_client is not None,
    )

    yield

    # Shutdown
    logger.info("server_shutting_down")

    if mongodb_client:
        await mongodb_client.disconnect()
        logger.info("mongodb_disconnected")

    if qdrant_client:
        await qdrant_client.disconnect()
        logger.info("qdrant_disconnected")

    logger.info("server_shutdown_complete")


# Create FastAPI application
app = FastAPI(
    title="AI Engineering Knowledge MCP Server",
    description="MCP server providing access to AI engineering knowledge extracted from methodology books.",
    version=__version__,
    lifespan=lifespan,
)

# Add authentication middleware
# Extracts X-API-Key header, validates key, sets request.state.auth_context
# Missing/invalid keys are handled per story 5.2 ACs:
# - No key = PUBLIC tier (no error)
# - Invalid key = 401 Unauthorized
app.add_middleware(AuthMiddleware)

# Include routers BEFORE MCP mount so endpoints are included
app.include_router(search_router, tags=["search"])
app.include_router(decisions_router, tags=["extractions"])
app.include_router(patterns_router, tags=["extractions"])
app.include_router(warnings_router, tags=["extractions"])
app.include_router(methodologies_router, tags=["extractions"])
app.include_router(sources_router, tags=["sources"])


# Register global exception handlers (Story 4.6)
# Follows architecture.md error response format
# Order matters: specific handlers first, then generic
app.add_exception_handler(KnowledgeError, knowledge_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Define health endpoint BEFORE MCP mount so it can be explicitly excluded
# Health is infrastructure, not a knowledge query tool
@app.get("/health", operation_id="health_check", tags=["infrastructure"])
async def health_endpoint() -> Response:
    """Health check endpoint.

    Returns server health status including MongoDB and Qdrant connectivity.
    Returns HTTP 200 if all services healthy, HTTP 503 if any service unavailable.
    """
    result = await check_health(
        mongodb_client=mongodb_client,
        qdrant_client=qdrant_client,
    )

    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


# Create and mount MCP server AFTER defining endpoints
# Follows architecture.md:169-189 (fastapi-mcp integration pattern)
# Using HTTP transport (recommended) per fastapi-mcp docs
# Exclude infrastructure endpoints from MCP tools (per context7 best practices)
mcp = FastApiMCP(
    app,
    name="AI Engineering Knowledge",
    description="Query AI engineering knowledge extracted from methodology books",
    exclude_tags=["infrastructure"],  # Health check is not a knowledge query tool
)
# Mount MCP at /mcp endpoint with HTTP transport
mcp.mount_http()


def main() -> None:
    """Entry point for the CLI command.

    Runs the uvicorn server with configuration from settings.
    """
    logger.info(
        "starting_uvicorn",
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
    )
    uvicorn.run(
        "src.server:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.environment == "local",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
