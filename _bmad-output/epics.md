---
stepsCompleted: [1, 2, 3, 4]
status: complete
completedAt: '2025-12-30'
inputDocuments:
  - prd.md
  - architecture.md
totalEpics: 5
totalStories: 29
---

# Knowledge Pipeline - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Knowledge Pipeline, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**FR-1: Source Ingestion (5 requirements)**
- FR1.1: PDF document intake via PDF adapter
- FR1.2: Markdown document intake via Markdown adapter
- FR1.3: arXiv paper intake via arXiv adapter (post-MVP)
- FR1.4: Status tracking for ingestion process
- FR1.5: Source metadata storage (title, authors, path, type)

**FR-2: Knowledge Extraction (9 requirements)**
- FR2.1: Decision extraction (choice points with options and considerations)
- FR2.2: Pattern extraction (reusable code/architecture implementations)
- FR2.3: Warning extraction (gotchas, anti-patterns, failure modes)
- FR2.4: Methodology extraction (step-by-step processes from books)
- FR2.5: Checklist extraction (verification criteria)
- FR2.6: Persona extraction (role definitions for agents)
- FR2.7: Workflow extraction (process sequences)
- FR2.8: Topic tagging for all extractions
- FR2.9: Source attribution (every extraction traces back to source -> chunk -> file)

**FR-3: Storage (6 requirements)**
- FR3.1: MongoDB storage for sources collection
- FR3.2: MongoDB storage for chunks collection
- FR3.3: MongoDB storage for extractions collection
- FR3.4: Qdrant vector storage for chunks (semantic search)
- FR3.5: Qdrant vector storage for extractions (semantic search)
- FR3.6: Schema versioning support for all documents

**FR-4: MCP Interface (7 requirements - 7 tools)**
- FR4.1: `search_knowledge` - Semantic search across all content (Public tier)
- FR4.2: `get_decisions` - Query decision extractions by topic (Public tier)
- FR4.3: `get_patterns` - Query code pattern extractions (Public tier)
- FR4.4: `get_warnings` - Query warning extractions (Public tier)
- FR4.5: `get_methodologies` - Query methodology extractions (Registered tier)
- FR4.6: `list_sources` - List available knowledge sources (Public tier)
- FR4.7: `compare_sources` - Compare extractions across sources (Registered tier)

### NonFunctional Requirements

- NFR1: Performance - <500ms search latency for all MCP tool queries
- NFR2: Batch Efficiency - Single-session batch ingestion completion for source processing
- NFR3: Cost - Zero external LLM API costs using Claude-as-extractor pattern during ingestion
- NFR4: Scalability - Support 100k+ chunks across multiple knowledge sources
- NFR5: Extensibility (Adapters) - Abstract adapter patterns enabling new source types
- NFR6: Extensibility (Extractors) - Abstract extractor patterns enabling new extraction types

### Additional Requirements

**Infrastructure & Deployment:**
- Monorepo structure with two packages: `knowledge-pipeline` + `knowledge-mcp`
- Package manager: `uv` (Astral) for all Python dependency management
- MCP framework: `fastapi-mcp` for MCP protocol layer
- Local development via Docker Compose (MongoDB + Qdrant containers)
- Cloud deployment stack: Railway (~$5/mo) + MongoDB Atlas + Qdrant Cloud

**Data Architecture:**
- MongoDB collections: `sources`, `chunks`, `extractions` (hybrid model with references)
- Qdrant configuration: 384d vectors, Cosine distance metric, `all-MiniLM-L6-v2` embedding model
- Compound indexes on `extractions.type` + `extractions.topics`
- Payload fields in Qdrant: `{source_id, chunk_id, type, topics}` for filtered search

**Authentication & Security:**
- Tiered authentication model with three tiers:
  - Public: No auth, 100 req/hr per IP, core search access
  - Registered: API Key (`X-API-Key` header), 1000 req/hr, full access
  - Premium: API Key + Subscription, unlimited access (future implementation)
- Rate limiting middleware for all tiers
- API Key authentication via FastAPI middleware

**Implementation Patterns:**
- Python 3.11+ runtime
- Async FastAPI endpoints for all MCP tools
- Pydantic models for all data validation
- Structured logging via structlog
- Tests in separate `tests/` directory mirroring `src/` structure

**Project Initialization:**
```bash
# knowledge-pipeline
uv init && uv python pin 3.11
uv add fastapi uvicorn pymongo qdrant-client sentence-transformers pymupdf pydantic pydantic-settings
uv add --dev pytest pytest-asyncio ruff mypy

# knowledge-mcp
uv init && uv python pin 3.11
uv add fastapi fastapi-mcp uvicorn qdrant-client pymongo
uv add --dev pytest
```

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1.1 | Epic 2 | PDF document intake via PDF adapter |
| FR1.2 | Epic 2 | Markdown document intake via Markdown adapter |
| FR1.3 | Deferred | arXiv adapter (post-MVP) |
| FR1.4 | Epic 2 | Status tracking for ingestion process |
| FR1.5 | Epic 2 | Source metadata storage |
| FR2.1 | Epic 3 | Decision extraction |
| FR2.2 | Epic 3 | Pattern extraction |
| FR2.3 | Epic 3 | Warning extraction |
| FR2.4 | Epic 3 | Methodology extraction |
| FR2.5 | Epic 3 | Checklist extraction |
| FR2.6 | Epic 3 | Persona extraction |
| FR2.7 | Epic 3 | Workflow extraction |
| FR2.8 | Epic 3 | Topic tagging |
| FR2.9 | Epic 3 | Source attribution |
| FR3.1 | Epic 1 | MongoDB storage for sources |
| FR3.2 | Epic 1 | MongoDB storage for chunks |
| FR3.3 | Epic 1 | MongoDB storage for extractions |
| FR3.4 | Epic 1 | Qdrant vector storage for chunks |
| FR3.5 | Epic 1 | Qdrant vector storage for extractions |
| FR3.6 | Epic 1 | Schema versioning support |
| FR4.1 | Epic 4 | search_knowledge MCP tool |
| FR4.2 | Epic 4 | get_decisions MCP tool |
| FR4.3 | Epic 4 | get_patterns MCP tool |
| FR4.4 | Epic 4 | get_warnings MCP tool |
| FR4.5 | Epic 4 | get_methodologies MCP tool |
| FR4.6 | Epic 4 | list_sources MCP tool |
| FR4.7 | Epic 4 | compare_sources MCP tool |

**Coverage:** 26 of 27 FRs mapped (FR1.3 deferred to post-MVP per architecture)

---

## Epic List

### Epic 1: Project Foundation & Development Environment
Developer can initialize the project structure, run MongoDB and Qdrant locally via Docker Compose, and have a functioning development environment with all Pydantic models and storage clients ready.
**FRs covered:** FR3.1, FR3.2, FR3.3, FR3.4, FR3.5, FR3.6

### Epic 2: Document Ingestion Pipeline
Builder can ingest PDF and Markdown documents into the system, process them into chunks with embeddings, track ingestion status, and store source metadata.
**FRs covered:** FR1.1, FR1.2, FR1.4, FR1.5

### Epic 3: Knowledge Extraction System
Builder can extract structured knowledge (decisions, patterns, warnings, methodologies, checklists, personas, workflows) from ingested documents with full source attribution and topic tagging.
**FRs covered:** FR2.1, FR2.2, FR2.3, FR2.4, FR2.5, FR2.6, FR2.7, FR2.8, FR2.9

### Epic 4: Knowledge Query Interface (MCP Tools)
End users can connect to the MCP server and query for decisions, patterns, warnings, methodologies; search semantically across all content; list available sources; and compare extractions across sources.
**FRs covered:** FR4.1, FR4.2, FR4.3, FR4.4, FR4.5, FR4.6, FR4.7

### Epic 5: Production Deployment & Access Control
System is deployed to cloud (Railway + MongoDB Atlas + Qdrant Cloud) with rate limiting, tiered authentication (Public/Registered/Premium), and production-ready performance.
**NFRs addressed:** NFR1 (Performance), NFR3 (Cost), NFR4 (Scalability) + Authentication requirements

---

## Epic 1: Project Foundation & Development Environment

**Goal:** Developer can initialize the project structure, run MongoDB and Qdrant locally via Docker Compose, and have a functioning development environment with all Pydantic models and storage clients ready.

**FRs Covered:** FR3.1, FR3.2, FR3.3, FR3.4, FR3.5, FR3.6

---

### Story 1.1: Initialize Monorepo Structure

As a **developer**,
I want to initialize the monorepo with both `knowledge-pipeline` and `knowledge-mcp` packages using uv,
So that I have a properly structured project with all dependencies installed and ready for development.

**Acceptance Criteria:**

**Given** a fresh directory for the project
**When** I run the initialization commands from the architecture doc
**Then** both `knowledge-pipeline` and `knowledge-mcp` directories exist with `pyproject.toml` and `uv.lock`
**And** all dependencies are installed (fastapi, pymongo, qdrant-client, sentence-transformers, etc.)
**And** the project structure matches the architecture specification

---

### Story 1.2: Docker Compose Infrastructure Setup

As a **developer**,
I want to run MongoDB and Qdrant locally via Docker Compose,
So that I have a working development database environment without cloud dependencies.

**Acceptance Criteria:**

**Given** Docker is installed on my machine
**When** I run `docker-compose up -d`
**Then** MongoDB is running on port 27017
**And** Qdrant is running on port 6333
**And** both services are accessible from the Python application
**And** data persists across container restarts via volumes

---

### Story 1.3: Pydantic Models for Core Entities

As a **developer**,
I want Pydantic models for Source, Chunk, and Extraction entities,
So that I have type-safe data validation and serialization for all knowledge base operations.

**Acceptance Criteria:**

**Given** the Pydantic models module exists
**When** I create a Source, Chunk, or Extraction instance
**Then** all required fields are validated according to the architecture schema
**And** `schema_version` field is present on all models
**And** models serialize to JSON with snake_case field names
**And** MongoDB ObjectId fields are properly handled as strings

---

### Story 1.4: MongoDB Storage Client

As a **developer**,
I want a MongoDB client class with CRUD operations for sources, chunks, and extractions,
So that I can persist and retrieve knowledge base data from MongoDB.

**Acceptance Criteria:**

**Given** MongoDB is running (from Story 1.2)
**When** I use the MongoDB client to create/read/update/delete documents
**Then** documents are properly stored in the correct collections (sources, chunks, extractions)
**And** compound indexes on `extractions.type + extractions.topics` are created
**And** the client uses Pydantic models (from Story 1.3) for validation
**And** errors follow the structured error format from architecture

---

### Story 1.5: Qdrant Storage Client

As a **developer**,
I want a Qdrant client class for vector storage and semantic search operations,
So that I can store embeddings and perform similarity searches on chunks and extractions.

**Acceptance Criteria:**

**Given** Qdrant is running (from Story 1.2)
**When** I use the Qdrant client to create collections and upsert vectors
**Then** collections are created with 384d vectors and Cosine distance metric
**And** payload fields include `{source_id, chunk_id, type, topics}` for filtering
**And** semantic search returns ranked results with scores
**And** both `chunks` and `extractions` collections are supported

---

## Epic 2: Document Ingestion Pipeline

**Goal:** Builder can ingest PDF and Markdown documents into the system, process them into chunks with embeddings, track ingestion status, and store source metadata.

**FRs Covered:** FR1.1, FR1.2, FR1.4, FR1.5

---

### Story 2.1: Base Source Adapter Interface

As a **developer**,
I want an abstract base class (ABC) for source adapters,
So that all document adapters follow a consistent interface and new adapters can be easily added.

**Acceptance Criteria:**

**Given** the adapters module exists
**When** I create a new adapter by extending SourceAdapter
**Then** the adapter must implement `extract_text()` and `get_metadata()` methods
**And** the base class provides common utilities for text processing
**And** the pattern follows NFR5 (Extensibility for Adapters)

---

### Story 2.2: PDF Document Adapter

As a **builder**,
I want to ingest PDF documents using pymupdf,
So that I can extract text content from AI engineering books for knowledge extraction.

**Acceptance Criteria:**

**Given** a PDF file path is provided
**When** I use the PDF adapter to process the file
**Then** text is extracted from all pages with position metadata (chapter, section, page)
**And** source metadata (title, authors if detectable, path) is captured
**And** the adapter handles multi-column layouts gracefully
**And** errors are raised for corrupted or password-protected PDFs

---

### Story 2.3: Markdown Document Adapter

As a **builder**,
I want to ingest Markdown documents,
So that I can extract content from markdown-based documentation and notes.

**Acceptance Criteria:**

**Given** a Markdown file path is provided
**When** I use the Markdown adapter to process the file
**Then** text is extracted with structure preserved (headings become section markers)
**And** source metadata (title from H1, path) is captured
**And** code blocks are preserved with language annotations
**And** links and images are handled appropriately

---

### Story 2.4: Text Chunking Processor

As a **developer**,
I want a chunking processor that splits documents into semantic chunks,
So that extracted text is appropriately sized for embedding and extraction.

**Acceptance Criteria:**

**Given** extracted text from an adapter
**When** I process it through the chunker
**Then** text is split into chunks of configurable size (default based on architecture)
**And** chunks respect sentence boundaries where possible
**And** each chunk includes position metadata (source location)
**And** chunk token counts are calculated and stored

---

### Story 2.5: Local Embedding Generator

As a **developer**,
I want to generate embeddings locally using sentence-transformers (all-MiniLM-L6-v2),
So that chunks can be vectorized for semantic search without external API costs.

**Acceptance Criteria:**

**Given** a text chunk
**When** I generate an embedding
**Then** a 384-dimensional vector is returned
**And** the embedding model is loaded once and reused
**And** batch embedding is supported for efficiency
**And** NFR3 (zero external LLM API costs) is satisfied

---

### Story 2.6: End-to-End Ingestion Pipeline

As a **builder**,
I want to run a complete ingestion pipeline via CLI script,
So that I can ingest a document, chunk it, embed it, and store everything in one command.

**Acceptance Criteria:**

**Given** a document path (PDF or Markdown)
**When** I run `uv run scripts/ingest.py <file>`
**Then** source metadata is stored in MongoDB `sources` collection
**And** chunks are stored in MongoDB `chunks` collection with `source_id` reference
**And** chunk embeddings are stored in Qdrant `chunks` collection
**And** ingestion status is tracked (pending -> processing -> complete/failed)
**And** the script outputs a summary of chunks created

---

## Epic 3: Knowledge Extraction System

**Goal:** Builder can extract structured knowledge (decisions, patterns, warnings, methodologies, checklists, personas, workflows) from ingested documents with full source attribution and topic tagging.

**FRs Covered:** FR2.1, FR2.2, FR2.3, FR2.4, FR2.5, FR2.6, FR2.7, FR2.8, FR2.9

---

### Story 3.1: Base Extractor Interface and Extraction Models

As a **developer**,
I want an abstract base class for extractors and Pydantic models for each extraction type,
So that all extractors follow a consistent pattern and extraction outputs are validated.

**Acceptance Criteria:**

**Given** the extractors module exists
**When** I create a new extractor by extending BaseExtractor
**Then** the extractor must implement `extract()` and `get_prompt()` methods
**And** type-specific Pydantic models exist for Decision, Pattern, Warning, Methodology, Checklist, Persona, Workflow
**And** all extraction models include `source_id`, `chunk_id`, `topics[]`, and `schema_version`
**And** the pattern follows NFR6 (Extensibility for Extractors)
**And** LLMClient utility class exists at `src/extractors/llm_client.py`
**And** LLMClient provides `extract(prompt, content)` method for batch LLM extraction
**And** LLMClient uses `ANTHROPIC_API_KEY` from settings
**And** LLMClient includes retry logic with exponential backoff

---

### Story 3.2: Decision Extractor

As a **builder**,
I want to extract decision points from chunks,
So that end users can query for AI engineering choice points with options and considerations.

**Acceptance Criteria:**

**Given** a chunk of text containing a decision point
**When** I run the decision extractor
**Then** a structured Decision is extracted with: question, options[], considerations[], recommended_approach
**And** the extraction includes source attribution (source_id, chunk_id)
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/decision.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/decision.md` to LLMClient. Parse JSON response using Pydantic model validation.

---

### Story 3.3: Pattern Extractor

As a **builder**,
I want to extract reusable code/architecture patterns from chunks,
So that end users can query for implementation patterns with code examples.

**Acceptance Criteria:**

**Given** a chunk of text describing a pattern
**When** I run the pattern extractor
**Then** a structured Pattern is extracted with: name, problem, solution, code_example, context, trade_offs
**And** the extraction includes source attribution
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/pattern.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/pattern.md` to LLMClient. Parse JSON response using Pydantic model validation.

---

### Story 3.4: Warning Extractor

As a **builder**,
I want to extract warnings, gotchas, and anti-patterns from chunks,
So that end users can query for failure modes and things to avoid.

**Acceptance Criteria:**

**Given** a chunk of text describing a warning or anti-pattern
**When** I run the warning extractor
**Then** a structured Warning is extracted with: title, description, symptoms, consequences, prevention
**And** the extraction includes source attribution
**And** relevant topics are auto-tagged
**And** the extraction prompt is stored in `extractors/prompts/warning.md`

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompt from `prompts/warning.md` to LLMClient. Parse JSON response using Pydantic model validation.

---

### Story 3.5: Methodology and Process Extractors

As a **builder**,
I want to extract methodologies, checklists, personas, and workflows from chunks,
So that I can use these to build BMAD workflows and agent prompts.

**Acceptance Criteria:**

**Given** chunks containing process-oriented content
**When** I run the methodology/checklist/persona/workflow extractors
**Then** structured extractions are created for each type:
- Methodology: name, steps[], prerequisites, outputs
- Checklist: name, items[], context
- Persona: role, responsibilities, expertise, communication_style
- Workflow: name, trigger, steps[], decision_points
**And** all extractions include source attribution and topic tags
**And** extraction prompts are stored in respective prompt files

**Implementation Note:** Use LLMClient from `src/extractors/llm_client.py` for extraction. Pass prompts from `prompts/{type}.md` to LLMClient. Parse JSON responses using Pydantic model validation.

---

### Story 3.6: Extraction Storage and Embedding

As a **developer**,
I want extractions to be stored in MongoDB and embedded in Qdrant,
So that they can be queried both by type/topic filters and semantic search.

**Acceptance Criteria:**

**Given** a completed extraction
**When** it is saved
**Then** the extraction document is stored in MongoDB `extractions` collection
**And** an embedding is generated from the extraction summary
**And** the embedding is stored in Qdrant `extractions` collection with payload `{source_id, chunk_id, type, topics}`
**And** source attribution chain is preserved (extraction -> chunk -> source)

---

### Story 3.7: Extraction Pipeline CLI

As a **builder**,
I want to run knowledge extraction on ingested sources via CLI,
So that I can extract all knowledge types from a book in one command.

**Acceptance Criteria:**

**Given** a source has been ingested (chunks exist)
**When** I run `uv run scripts/extract.py <source_id>`
**Then** all extractors are run against each chunk
**And** extractions are saved to MongoDB and Qdrant
**And** progress is displayed during extraction
**And** a summary shows extraction counts by type
**And** the Claude-as-extractor pattern is used (NFR3: zero external API costs)

---

## Epic 4: Knowledge Query Interface (MCP Tools)

**Goal:** End users can connect to the MCP server and query for decisions, patterns, warnings, methodologies; search semantically across all content; list available sources; and compare extractions across sources.

**FRs Covered:** FR4.1, FR4.2, FR4.3, FR4.4, FR4.5, FR4.6, FR4.7

---

### Story 4.1: FastAPI Server with MCP Integration

As a **developer**,
I want a FastAPI server with fastapi-mcp integration,
So that MCP tools can be exposed to Claude Code clients.

**Acceptance Criteria:**

**Given** the knowledge-mcp package exists
**When** I run `uv run uvicorn src.server:app`
**Then** the FastAPI server starts on the configured port
**And** the `/mcp` endpoint is available via fastapi-mcp mounting
**And** health check endpoint returns server status
**And** server connects to MongoDB and Qdrant on startup

---

### Story 4.2: Semantic Search Tool (search_knowledge)

As an **end user**,
I want to search across all knowledge content semantically,
So that I can find relevant information using natural language queries.

**Acceptance Criteria:**

**Given** I am connected to the MCP server
**When** I call `search_knowledge` with a query string
**Then** semantically similar chunks and extractions are returned
**And** results are ranked by relevance score
**And** source attribution is included in each result
**And** response follows the annotated format with `results` and `metadata`
**And** the tool is available at Public tier (FR4.1)

---

### Story 4.3: Extraction Query Tools (get_decisions, get_patterns, get_warnings)

As an **end user**,
I want to query specific extraction types by topic,
So that I can find decisions, patterns, or warnings relevant to my current problem.

**Acceptance Criteria:**

**Given** I am connected to the MCP server
**When** I call `get_decisions`, `get_patterns`, or `get_warnings` with optional topic filter
**Then** matching extractions of that type are returned
**And** results can be filtered by topic tags
**And** source attribution is included
**And** response follows the annotated format
**And** all three tools are available at Public tier (FR4.2, FR4.3, FR4.4)

---

### Story 4.4: Methodology Query Tool (get_methodologies)

As an **end user**,
I want to query methodology extractions,
So that I can find step-by-step processes for AI engineering tasks.

**Acceptance Criteria:**

**Given** I am connected to the MCP server
**When** I call `get_methodologies` with optional topic filter
**Then** matching methodology extractions are returned
**And** results include full steps and prerequisites
**And** source attribution is included
**And** response follows the annotated format
**And** the tool is available at Registered tier (FR4.5)

---

### Story 4.5: Source Management Tools (list_sources, compare_sources)

As an **end user**,
I want to list available knowledge sources and compare extractions across sources,
So that I can understand what knowledge is available and see different perspectives.

**Acceptance Criteria:**

**Given** I am connected to the MCP server
**When** I call `list_sources`
**Then** all available sources are returned with metadata (title, authors, type, extraction counts)
**And** the tool is available at Public tier (FR4.6)

**Given** I call `compare_sources` with a topic and source IDs
**When** the query executes
**Then** extractions from specified sources on that topic are returned side-by-side
**And** Claude can synthesize across conflicting recommendations
**And** the tool is available at Registered tier (FR4.7)

---

### Story 4.6: Response Models and Error Handling

As a **developer**,
I want standardized response models and error handling for all MCP tools,
So that clients receive consistent, well-structured responses.

**Acceptance Criteria:**

**Given** any MCP tool is called
**When** the response is returned
**Then** success responses follow the format: `{results: [...], metadata: {query, sources_cited, result_count, search_type}}`
**And** error responses follow the format: `{error: {code, message, details}}`
**And** appropriate HTTP status codes are used (400, 404, 429, 500)
**And** rate limit errors include `retry_after` information
**And** NFR1 (<500ms search latency) is achieved

---

## Epic 5: Production Deployment & Access Control

**Goal:** System is deployed to cloud (Railway + MongoDB Atlas + Qdrant Cloud) with rate limiting, tiered authentication (Public/Registered/Premium), and production-ready performance.

**NFRs Addressed:** NFR1 (Performance), NFR3 (Cost), NFR4 (Scalability) + Authentication requirements

---

### Story 5.1: Rate Limiting Middleware

As a **system operator**,
I want rate limiting middleware that enforces request limits by tier,
So that the system is protected from abuse and resources are fairly allocated.

**Acceptance Criteria:**

**Given** the middleware is configured
**When** requests arrive at the MCP server
**Then** Public tier is limited to 100 requests/hour per IP
**And** Registered tier is limited to 1000 requests/hour per API key
**And** Premium tier has unlimited requests
**And** rate limit errors return 429 status with `retry_after` header
**And** limits are tracked in-memory (Redis optional for future)

---

### Story 5.2: API Key Authentication Middleware

As a **system operator**,
I want API key authentication for Registered and Premium tiers,
So that users can access tier-appropriate features with their credentials.

**Acceptance Criteria:**

**Given** the auth middleware is configured
**When** a request includes `X-API-Key` header
**Then** the API key is validated against stored keys
**And** the user's tier (Registered/Premium) is determined
**And** tier-restricted tools (get_methodologies, compare_sources) check permissions
**And** invalid keys return 401 Unauthorized
**And** missing keys default to Public tier access

---

### Story 5.3: Dockerfile and Container Configuration

As a **developer**,
I want a Dockerfile for the knowledge-mcp server,
So that the application can be containerized and deployed to Railway.

**Acceptance Criteria:**

**Given** the Dockerfile exists in knowledge-mcp
**When** I build and run the container
**Then** the server starts and accepts connections
**And** environment variables configure MongoDB/Qdrant connections
**And** the image is optimized for size (multi-stage build)
**And** health check is configured for container orchestration

---

### Story 5.4: Cloud Database Configuration

As a **system operator**,
I want configuration for MongoDB Atlas and Qdrant Cloud,
So that production data is stored in managed cloud services.

**Acceptance Criteria:**

**Given** cloud database accounts are set up
**When** I configure the application with cloud connection strings
**Then** the application connects to MongoDB Atlas instead of local MongoDB
**And** the application connects to Qdrant Cloud instead of local Qdrant
**And** connection strings are configured via environment variables
**And** SSL/TLS is enabled for all database connections
**And** the application gracefully handles connection failures

---

### Story 5.5: Railway Deployment Pipeline

As a **system operator**,
I want the MCP server deployed to Railway with auto-deploy,
So that the service is publicly accessible and updates automatically.

**Acceptance Criteria:**

**Given** the Railway project is configured
**When** I push to the `main` branch
**Then** Railway automatically builds and deploys the new version
**And** the MCP endpoint is accessible at the configured URL
**And** environment variables are managed via Railway dashboard
**And** logs are accessible for debugging
**And** the deployment achieves NFR1 (<500ms search latency)
**And** estimated cost is ~$5/month for starter tier
