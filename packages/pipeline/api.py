"""Knowledge Pipeline API.

FastAPI service exposing ingestion and extraction endpoints with project namespace isolation.

Endpoints:
    POST /ingest - Upload and ingest a file
    POST /ingest/url - Ingest a document from URL
    POST /extract/{source_id} - Run extraction on an ingested source
    GET /sources/{source_id} - Get source metadata and status
    DELETE /sources/{source_id} - Delete source and all associated data
    GET /health - Health check endpoint

All endpoints support project namespacing via X-Project-ID header (defaults to "default").
"""

import tempfile
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import structlog
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.config import settings
from src.exceptions import KnowledgeError, NotFoundError, ValidationError
from src.extraction.pipeline import ExtractionPipeline
from src.ingestion.pipeline import IngestionPipeline, PipelineConfig
from src.storage.mongodb import MongoDBClient
from src.storage.qdrant import QdrantStorageClient

logger = structlog.get_logger()


# =============================================================================
# Response Models
# =============================================================================


class IngestResponse(BaseModel):
    """Response model for file/URL ingestion."""

    source_id: str
    title: str
    chunk_count: int
    total_tokens: int
    duration: float
    project_id: str
    status: str = "complete"


class ExtractResponse(BaseModel):
    """Response model for extraction endpoint."""

    source_id: str
    total_extractions: int
    extraction_counts: dict[str, int]
    duration: float
    project_id: str


class SourceResponse(BaseModel):
    """Response model for source status endpoint."""

    source_id: str
    title: str
    status: str
    chunk_count: int
    extraction_count: int
    project_id: str


class DeletedCounts(BaseModel):
    """Counts of deleted items per storage layer."""

    sources: int
    chunks: int
    extractions: int
    vectors: str


class DeleteResponse(BaseModel):
    """Response model for source deletion."""

    deleted: DeletedCounts
    project_id: str


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    mongodb: bool
    qdrant: bool


class IngestURLRequest(BaseModel):
    """Request model for URL ingestion."""

    url: str
    category: Optional[str] = Field(default="reference", description="Source category")
    tags: list[str] = Field(default_factory=list, description="Source tags")
    year: Optional[int] = Field(default=None, ge=1900, le=2100, description="Publication year")


class ErrorDetail(BaseModel):
    """Structured error detail."""

    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Structured error response."""

    error: ErrorDetail


# =============================================================================
# Lifespan Handler
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events."""
    logger.info("pipeline_api_starting")
    yield
    logger.info("pipeline_api_shutdown")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Knowledge Pipeline API",
    description="API for ingesting documents and extracting knowledge",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# Helper Functions
# =============================================================================


def get_project_id(request: Request) -> str:
    """Extract project_id from X-Project-ID header or use default.

    Args:
        request: FastAPI request object.

    Returns:
        Project ID string.
    """
    return request.headers.get("X-Project-ID", "default")


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(KnowledgeError)
async def knowledge_error_handler(request: Request, exc: KnowledgeError) -> JSONResponse:
    """Handle KnowledgeError exceptions with structured response.

    Args:
        request: FastAPI request object.
        exc: KnowledgeError exception.

    Returns:
        JSONResponse with structured error format.
    """
    status_code = 500
    if exc.code == "NOT_FOUND":
        status_code = 404
    elif exc.code == "VALIDATION_ERROR":
        status_code = 400

    logger.warning(
        "knowledge_error",
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle ValidationError exceptions.

    Args:
        request: FastAPI request object.
        exc: ValidationError exception.

    Returns:
        JSONResponse with validation error format.
    """
    logger.warning(
        "validation_error",
        message=exc.message,
        details=exc.details,
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle NotFoundError exceptions.

    Args:
        request: FastAPI request object.
        exc: NotFoundError exception.

    Returns:
        JSONResponse with not found error format.
    """
    logger.warning(
        "not_found_error",
        message=exc.message,
        details=exc.details,
    )

    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with structured response.

    Args:
        request: FastAPI request object.
        exc: Generic exception.

    Returns:
        JSONResponse with internal error format.
    """
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error_type": type(exc).__name__},
            }
        },
    )


# =============================================================================
# Endpoints
# =============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check health of API and backend services.

    Returns:
        HealthResponse with service status.
    """
    mongodb_healthy = False
    qdrant_healthy = False

    # Check MongoDB
    try:
        mongodb = MongoDBClient()
        mongodb.connect()
        mongodb_healthy = mongodb.ping()
        mongodb.close()
    except Exception as e:
        logger.warning("mongodb_health_check_failed", error=str(e))

    # Check Qdrant
    try:
        qdrant = QdrantStorageClient()
        qdrant_healthy = qdrant.health_check()
    except Exception as e:
        logger.warning("qdrant_health_check_failed", error=str(e))

    overall_status = "healthy" if (mongodb_healthy and qdrant_healthy) else "degraded"

    return HealthResponse(
        status=overall_status,
        mongodb=mongodb_healthy,
        qdrant=qdrant_healthy,
    )


@app.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(default="reference"),
    tags: str = Form(default=""),
    year: Optional[int] = Form(default=None),
) -> IngestResponse:
    """Ingest a file into the knowledge base.

    Args:
        request: FastAPI request object.
        file: Uploaded file.
        category: Source category (foundational, advanced, reference, case_study).
        tags: Comma-separated tags.
        year: Publication year.

    Returns:
        IngestResponse with ingestion results.

    Raises:
        HTTPException: If ingestion fails.
    """
    project_id = get_project_id(request)
    tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    logger.info(
        "ingest_file_started",
        filename=file.filename,
        project_id=project_id,
        category=category,
    )

    # Save uploaded file to temp location
    suffix = Path(file.filename).suffix if file.filename else ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        config = PipelineConfig(
            project_id=project_id,
            category=category,
            tags=tags_list,
            year=year,
        )

        with IngestionPipeline(config=config) as pipeline:
            result = pipeline.ingest(temp_path)

        logger.info(
            "ingest_file_complete",
            source_id=result.source_id,
            chunk_count=result.chunk_count,
            project_id=project_id,
        )

        return IngestResponse(
            source_id=result.source_id,
            title=result.title,
            chunk_count=result.chunk_count,
            total_tokens=result.total_tokens,
            duration=result.duration,
            project_id=project_id,
            status="complete",
        )

    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@app.post("/ingest/url", response_model=IngestResponse)
async def ingest_url(
    request: Request,
    body: IngestURLRequest,
) -> IngestResponse:
    """Ingest a document from URL.

    Args:
        request: FastAPI request object.
        body: IngestURLRequest with URL and metadata.

    Returns:
        IngestResponse with ingestion results.

    Raises:
        HTTPException: If ingestion fails.
    """
    project_id = get_project_id(request)

    logger.info(
        "ingest_url_started",
        url=body.url,
        project_id=project_id,
        category=body.category,
    )

    config = PipelineConfig(
        project_id=project_id,
        category=body.category,
        tags=body.tags,
        year=body.year,
    )

    with IngestionPipeline(config=config) as pipeline:
        result = pipeline.ingest_url(body.url)

    logger.info(
        "ingest_url_complete",
        source_id=result.source_id,
        chunk_count=result.chunk_count,
        project_id=project_id,
    )

    return IngestResponse(
        source_id=result.source_id,
        title=result.title,
        chunk_count=result.chunk_count,
        total_tokens=result.total_tokens,
        duration=result.duration,
        project_id=project_id,
        status="complete",
    )


@app.post("/extract/{source_id}", response_model=ExtractResponse)
async def extract_source(
    request: Request,
    source_id: str,
) -> ExtractResponse:
    """Run extraction pipeline on an ingested source.

    Args:
        request: FastAPI request object.
        source_id: MongoDB source document ID.

    Returns:
        ExtractResponse with extraction results.

    Raises:
        HTTPException: If extraction fails.
    """
    project_id = get_project_id(request)

    logger.info(
        "extraction_started",
        source_id=source_id,
        project_id=project_id,
    )

    start_time = time.time()

    with ExtractionPipeline() as pipeline:
        result = pipeline.extract_hierarchical(source_id, quiet=True)

    duration = time.time() - start_time

    logger.info(
        "extraction_complete",
        source_id=source_id,
        total_extractions=result.total_extractions,
        duration=f"{duration:.2f}s",
    )

    return ExtractResponse(
        source_id=source_id,
        total_extractions=result.total_extractions,
        extraction_counts=result.extraction_counts,
        duration=duration,
        project_id=project_id,
    )


@app.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source_status(
    request: Request,
    source_id: str,
) -> SourceResponse:
    """Get source metadata and status.

    Args:
        request: FastAPI request object.
        source_id: MongoDB source document ID.

    Returns:
        SourceResponse with source information.

    Raises:
        HTTPException: If source not found.
    """
    project_id = get_project_id(request)

    logger.info(
        "get_source_status",
        source_id=source_id,
        project_id=project_id,
    )

    mongodb = MongoDBClient()
    mongodb.connect()

    try:
        source = mongodb.get_source(source_id, project_id=project_id)
        chunk_count = mongodb.count_chunks_by_source(source_id, project_id=project_id)
        extractions = mongodb.get_extractions_by_source(source_id, project_id=project_id)
        extraction_count = len(extractions)

        return SourceResponse(
            source_id=source_id,
            title=source.title,
            status=source.status,
            chunk_count=chunk_count,
            extraction_count=extraction_count,
            project_id=source.project_id or project_id,
        )
    finally:
        mongodb.close()


@app.delete("/sources/{source_id}", response_model=DeleteResponse)
async def delete_source(
    request: Request,
    source_id: str,
) -> DeleteResponse:
    """Delete a source and all associated data (chunks, extractions, vectors).

    Args:
        request: FastAPI request object.
        source_id: MongoDB source document ID.

    Returns:
        DeleteResponse with counts of deleted items per storage layer.

    Raises:
        HTTPException: If source not found (404).
    """
    project_id = get_project_id(request)

    logger.info(
        "delete_source_started",
        source_id=source_id,
        project_id=project_id,
    )

    mongodb = MongoDBClient()
    mongodb.connect()

    try:
        # Check source exists first — raises NotFoundError if missing
        mongodb.get_source(source_id, project_id=project_id)

        # Delete from all 4 storage layers; log failures but continue
        sources_deleted = 0
        chunks_deleted = 0
        extractions_deleted = 0
        vectors_status = "skipped"

        try:
            deleted = mongodb.delete_source(source_id, project_id=project_id)
            sources_deleted = 1 if deleted else 0
        except Exception as e:
            logger.error("delete_source_mongodb_failed", source_id=source_id, error=str(e))

        try:
            chunks_deleted = mongodb.delete_chunks_by_source(source_id, project_id=project_id)
        except Exception as e:
            logger.error("delete_chunks_mongodb_failed", source_id=source_id, error=str(e))

        try:
            extractions_deleted = mongodb.delete_extractions_by_source(
                source_id, project_id=project_id
            )
        except Exception as e:
            logger.error("delete_extractions_mongodb_failed", source_id=source_id, error=str(e))

        try:
            qdrant = QdrantStorageClient()
            qdrant.delete_by_source("knowledge_vectors", source_id, project_id=project_id)
            vectors_status = "deleted"
        except Exception as e:
            logger.error("delete_vectors_qdrant_failed", source_id=source_id, error=str(e))
            vectors_status = "failed"

        logger.info(
            "delete_source_complete",
            source_id=source_id,
            project_id=project_id,
            sources=sources_deleted,
            chunks=chunks_deleted,
            extractions=extractions_deleted,
            vectors=vectors_status,
        )

        return DeleteResponse(
            deleted=DeletedCounts(
                sources=sources_deleted,
                chunks=chunks_deleted,
                extractions=extractions_deleted,
                vectors=vectors_status,
            ),
            project_id=project_id,
        )
    finally:
        mongodb.close()


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
