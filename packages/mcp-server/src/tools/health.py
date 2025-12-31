"""Health check endpoint for Knowledge MCP Server.

Provides a health check endpoint that monitors the status of all services
(MongoDB, Qdrant) and returns server status information.
"""

from datetime import datetime, timezone
from typing import Any

import structlog

from src import __version__
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()


async def health_check(
    mongodb_client: MongoDBClient | None,
    qdrant_client: QdrantStorageClient | None,
) -> dict[str, Any]:
    """Check health of all services.

    Args:
        mongodb_client: MongoDB client instance (or None if unavailable)
        qdrant_client: Qdrant client instance (or None if unavailable)

    Returns:
        Health status dictionary with:
        - status: "healthy" or "unhealthy"
        - timestamp: ISO-8601 formatted timestamp
        - version: Server version from package
        - services: Status of each service
    """
    services: dict[str, str] = {}
    all_healthy = True

    # Check MongoDB using public ping() method
    if mongodb_client is None:
        services["mongodb"] = "unavailable"
        all_healthy = False
    else:
        try:
            is_healthy = await mongodb_client.ping()
            if is_healthy:
                services["mongodb"] = "healthy"
                logger.debug("health_check_mongodb", status="healthy")
            else:
                services["mongodb"] = "unavailable"
                all_healthy = False
                logger.warning("health_check_mongodb_failed", error="ping returned False")
        except Exception as e:
            services["mongodb"] = "unavailable"
            all_healthy = False
            logger.warning("health_check_mongodb_failed", error=str(e))

    # Check Qdrant using public ping() method
    if qdrant_client is None:
        services["qdrant"] = "unavailable"
        all_healthy = False
    else:
        try:
            is_healthy = await qdrant_client.ping()
            if is_healthy:
                services["qdrant"] = "healthy"
                logger.debug("health_check_qdrant", status="healthy")
            else:
                services["qdrant"] = "unavailable"
                all_healthy = False
                logger.warning("health_check_qdrant_failed", error="ping returned False")
        except Exception as e:
            services["qdrant"] = "unavailable"
            all_healthy = False
            logger.warning("health_check_qdrant_failed", error=str(e))

    status = "healthy" if all_healthy else "unhealthy"
    timestamp = datetime.now(timezone.utc).isoformat()

    logger.info(
        "health_check_completed",
        status=status,
        mongodb=services["mongodb"],
        qdrant=services["qdrant"],
    )

    return {
        "status": status,
        "timestamp": timestamp,
        "version": __version__,
        "services": services,
    }
