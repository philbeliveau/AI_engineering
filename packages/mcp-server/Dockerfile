# =============================================================================
# Knowledge MCP Server Dockerfile
# =============================================================================
# Multi-stage build optimized for production deployment
#
# Environment Variables (required at runtime):
#   MONGODB_URI    - MongoDB connection string (e.g., mongodb+srv://...)
#   QDRANT_URL     - Qdrant server URL (e.g., https://xxx.cloud.qdrant.io:6333)
#   QDRANT_API_KEY - Qdrant Cloud API key (optional for local)
#
# Optional Environment Variables:
#   PORT           - Server port (default: 8000, Railway sets dynamically)
#   ENVIRONMENT    - Deployment environment (default: production)
#   PROJECT_ID     - Multi-tenant project isolation (default: default)
#   LOG_LEVEL      - Logging level: DEBUG|INFO|WARNING|ERROR (default: INFO)
#
# Build: docker build -t knowledge-mcp .
# Run:   docker run -p 8000:8000 -e MONGODB_URI=... -e QDRANT_URL=... knowledge-mcp
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install uv and dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Install uv (fast Python package manager)
# Using official install script for latest version
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (cache optimization)
# Include README.md as hatchling requires it for the build
COPY pyproject.toml uv.lock README.md ./

# Create virtualenv and install production dependencies only
# --frozen: Use exact versions from uv.lock
# --no-dev: Exclude development dependencies
# --no-cache: Don't cache packages (smaller layer)
# --no-install-project: Skip installing the local project (we copy src separately)
RUN uv sync --frozen --no-dev --no-cache --no-install-project

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Set environment variables
# - PYTHONDONTWRITEBYTECODE: Prevent .pyc files (smaller image)
# - PYTHONUNBUFFERED: Ensure logs are immediately flushed
# - PYTHONFAULTHANDLER: Enable faulthandler for debugging crashes
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Default environment variables for Railway compatibility
# PORT can be overridden at runtime (Railway sets this dynamically)
ENV PORT=8000 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy virtualenv from builder (contains all dependencies)
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ /app/src/

# Set ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Add virtualenv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose default port (Railway will set PORT dynamically)
EXPOSE 8000

# Health check for container orchestration
# - interval: Check every 30 seconds
# - timeout: Fail if no response in 10 seconds
# - retries: Mark unhealthy after 3 consecutive failures
# - start-period: Allow 40s for initial startup
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health', timeout=5)" || exit 1

# Run uvicorn with exec form for proper signal handling
# --host 0.0.0.0: Bind to all interfaces for container networking
# --proxy-headers: Trust X-Forwarded-* headers from Railway's reverse proxy
# Note: PORT is read from environment variable at runtime
CMD ["sh", "-c", "uvicorn src.server:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]
