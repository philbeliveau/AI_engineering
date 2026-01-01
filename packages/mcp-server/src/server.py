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
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient
from src.tools.health import health_check as check_health

logger = structlog.get_logger()

# Global storage clients (initialized during startup)
mongodb_client: MongoDBClient | None = None
qdrant_client: QdrantStorageClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle (startup and shutdown).

    Initializes database connections on startup and closes them on shutdown.
    """
    global mongodb_client, qdrant_client

    # Startup
    logger.info(
        "server_starting",
        environment=settings.environment,
        host=settings.server_host,
        port=settings.server_port,
    )

    # Initialize MongoDB client
    mongodb_client = MongoDBClient(settings)
    try:
        await mongodb_client.connect()
    except Exception as e:
        logger.error("mongodb_connection_failed", error=str(e))
        mongodb_client = None

    # Initialize Qdrant client
    qdrant_client = QdrantStorageClient(settings)
    try:
        await qdrant_client.connect()
    except Exception as e:
        logger.error("qdrant_connection_failed", error=str(e))
        qdrant_client = None

    logger.info(
        "server_started",
        mongodb_connected=mongodb_client is not None,
        qdrant_connected=qdrant_client is not None,
    )

    yield

    # Shutdown
    logger.info("server_shutting_down")

    if mongodb_client:
        await mongodb_client.disconnect()

    if qdrant_client:
        await qdrant_client.disconnect()

    logger.info("server_shutdown_complete")


# Create FastAPI application
app = FastAPI(
    title="AI Engineering Knowledge MCP Server",
    description="MCP server providing access to AI engineering knowledge extracted from methodology books.",
    version=__version__,
    lifespan=lifespan,
)

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
