---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - AI-Engineering-Workflows-Brief.md
  - architecture.md
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 0
  projectDocs: 1
workflowType: 'prd'
lastStep: 11
status: 'complete'
completedAt: '2025-12-30'
project_name: 'Knowledge Pipeline'
user_name: 'Philippebeliveau'
date: '2025-12-30'
---

# Product Requirements Document - AI_engineering

**Author:** Philippebeliveau
**Date:** 2025-12-30

## Executive Summary

AI Engineering Workflows is a comprehensive knowledge system that transforms dense methodology books into interactive, executable workflows for AI engineering practitioners. The system addresses the fundamental problem of information overload and generalization gaps in AI engineering by providing context-aware, decision-tree-based guidance that reduces cognitive load and systematically narrows the solution space.

**Vision:** Create a living, executable knowledge system that encodes AI engineering methodologies as interactive workflows, guiding practitioners through structured decision trees while generating implementation-ready artifacts at each step.

**Core Problem:** AI engineering methodologies are trapped in 800+ page books that require practitioners to read, understand, and generalize to their specific context. This creates cognitive overwhelm, poor decisions, and paralysis. Knowledge is scattered across books, papers, articles, case studies, and repositories, requiring re-learning for each project. The rapid evolution of the AI landscape makes static knowledge quickly outdated.

**Target Users:**
- **Primary:** ML Engineers transitioning to LLM/AI engineering, Software Engineers building AI products, Data Scientists deploying to production, Technical Leads architecting AI systems
- **Secondary:** Startups needing rapid guidance, Enterprise Teams standardizing practices, Consultants delivering projects, Educators teaching modern AI engineering

### What Makes This Special

**Living, Executable Knowledge:** Unlike static books or documentation, this system encodes methodologies as interactive workflows that practitioners execute on their actual projects. Instead of reading and generalizing, users are guided through structured decision trees.

**Context-Aware Decision Reduction:** Built on the spec-forecasting philosophy where every decision is a function of previous decisions, project context, constraints, dataset characteristics, and business requirements. The system systematically reduces the solution space rather than providing generic answers.

**Structured Artifact Generation:** At each workflow step, the system generates implementation-ready artifacts (problem specs, solution approaches, architecture documents, evaluation plans) that persist context across decisions—similar to BMAD's PRD → Architecture → Stories flow.

**Multi-Source Synthesis:** Integrates multiple knowledge sources (books, research papers, case studies, GitHub code examples) via MCP servers. Claude synthesizes across sources at query time, weighing conflicting recommendations and applying user context rather than being limited to pre-extracted content.

**Continuous Evolution Model:** Monthly content updates as the AI landscape evolves, making rapid obsolescence a subscription advantage rather than a weakness. Pirated content becomes stale while subscribers receive current patterns for new models and techniques.

**Dual-Audience Architecture:** Serves both builders (creating BMAD workflows and agents from extracted methodologies) and end users (receiving contextual AI engineering guidance), with separate tool sets and query patterns optimized for each.

## Project Classification

**Technical Type:** Developer Tool / Framework
**Domain:** Scientific / AI Engineering
**Complexity:** Medium
**Project Context:** Brownfield - extending existing Knowledge Pipeline infrastructure

This project is a developer tool that provides a framework for AI engineering methodology execution. It operates in the scientific/AI engineering domain, requiring domain expertise in machine learning, LLM systems, and computational workflows. The medium complexity level reflects established technical patterns (FastAPI, MongoDB, Qdrant, MCP) combined with domain-specific knowledge extraction and synthesis requirements.

**Integration with Existing Infrastructure:**

The AI Engineering Workflows BMAD module will leverage the existing Knowledge Pipeline architecture:
- **knowledge-pipeline:** Ingests AI engineering books (LLM Engineer's Handbook, LLMs in Production) and extracts methodologies, decision trees, patterns, warnings, and checklists
- **knowledge-mcp:** Provides authenticated MCP server access to extracted knowledge for workflow execution
- **Dual-repo pattern:** Batch extraction pipeline separate from real-time query server
- **Technology alignment:** Python 3.11, FastAPI, MongoDB (extractions), Qdrant (semantic search), uv package management

## Success Criteria

### User Success

**Builder (Philippebeliveau) Success:**
- Successfully extract methodologies, personas, checklists, and workflows from source books
- Generate BMAD-compatible agents and workflows from extracted knowledge
- Query knowledge base to inform agent prompt development

**End User (Community) Success:**
- Receive contextual AI engineering guidance via MCP tools
- Find relevant decisions, patterns, and warnings for their specific context
- Access multi-source synthesized recommendations (Claude weighs conflicting sources)

### Business Success

| Timeframe | Target |
|-----------|--------|
| Phase 1 (Months 1-2) | 100 GitHub stars, 20 active users, 5 community contributions |
| Phase 2 (Month 3) | 50 paying subscribers, <5% churn |
| Phase 3 (Months 4-6) | 200 subscribers, >85% retention, 2 enterprise pilots |
| Phase 4 (Months 7-12) | 300 Pro subscribers, 10 Enterprise customers, $8-10K MRR |

**Core Business Metrics:**
- Conversion: Free → Pro (10% target)
- Churn: Monthly churn (<5% target)
- LTV: Customer lifetime value (>$300 target)

### Technical Success

| Metric | Target | Rationale |
|--------|--------|-----------|
| Search Performance | <500ms | Qdrant + indexed MongoDB |
| Batch Efficiency | Single-session ingestion | Complete book processing in one run |
| API Cost | Zero external LLM costs | Claude-as-extractor during ingestion, local embeddings |
| Scalability | 100k+ chunks | Support multiple books, papers, case studies |
| Extensibility | Adapter/extractor patterns | Easy addition of new source types and extraction types |

### Measurable Outcomes

**User Engagement Metrics:**
- Activation: User completes first workflow (70% target)
- Engagement: 8+ workflows run per month = engaged user
- Retention: 80% monthly active users

**Content Quality Metrics:**
- Quality: User rating of workflows (4.5+ / 5)
- Coverage: 2+ new workflows added monthly
- Freshness: Bi-weekly content updates

## Product Scope

### MVP - Minimum Viable Product

**Source Ingestion (FR-1):**
- PDF adapter for book ingestion
- Markdown adapter for documentation
- Ingestion status tracking

**Knowledge Extraction (FR-2):**
- 7 extraction types: Decision, Pattern, Warning, Methodology, Checklist, Persona, Workflow
- Claude-as-extractor pattern (zero API cost at query time)

**Storage (FR-3):**
- MongoDB: sources, chunks, extractions collections
- Qdrant: semantic search on chunks and extractions

**MCP Interface (FR-4):**
- `search_knowledge` - semantic search across all content
- `get_decisions`, `get_patterns`, `get_warnings` - type-specific queries
- `list_sources` - available knowledge sources

### Growth Features (Post-MVP)

- arXiv adapter for research papers (FR1.3 - deferred)
- `get_methodologies` tool (Registered tier)
- `compare_sources` tool for cross-source synthesis
- Premium authentication and tiered access
- Industry-specific patterns (fintech, healthcare, e-commerce)

### Vision (Future)

- Private MCP deployment option for enterprise
- Community marketplace for workflow packs
- Multi-region deployment
- Custom workflow development service
- White-label option for internal enterprise use

## User Journeys

### Journey 1: Builder - Book to BMAD Workflow

**Philippebeliveau transforms an 800-page AI engineering book into executable BMAD workflows.**

Philippe has the LLM Engineer's Handbook open on his desk. He wants to encode Chapter 5's RAG methodology into a BMAD workflow that will guide future users through the same decision process. Instead of manually reading and extracting, he runs the Knowledge Pipeline.

```
1. Ingest book into knowledge base
2. Query: "What methodologies does this book describe?"
3. Extract methodology steps, decisions, warnings for each step
4. Use extractions to build BMAD workflow structure
5. Query: "What persona handles this domain?"
6. Use persona extraction to define BMAD agent
7. Query: "What should this agent know about X?"
8. Use decisions/patterns/warnings to craft agent prompts
```

The breakthrough comes when he queries "What decisions exist about chunking strategies?" and receives structured extractions from multiple sources—the LLM Handbook, recent papers, and case studies—with Claude synthesizing the conflicting recommendations for his specific context.

**Capabilities Revealed:** Source ingestion, methodology extraction, persona extraction, multi-source querying, BMAD artifact generation.

### Journey 2: Solo Engineer Sarah - First RAG System

**Sarah is building her first RAG system and drowning in conflicting advice.**

Sarah has read three tutorials, two blog posts, and skimmed the LLM Handbook. Each source recommends different chunking strategies, embedding models, and retrieval approaches. She's paralyzed by trade-offs she doesn't fully understand.

She connects to the Knowledge Pipeline MCP server from Claude Code. Instead of asking "how do I build RAG?", she asks:

- "What decisions do I need to make for RAG architecture?"
- "What are the trade-offs for chunking strategies when my documents are technical manuals?"
- "What warnings should I know about before choosing an embedding model?"

The system returns structured decisions with options, considerations, and source attribution. Claude synthesizes across sources, noting where the LLM Handbook disagrees with recent papers and why. Sarah makes informed decisions in 30 minutes instead of 3 days of research.

**Capabilities Revealed:** `get_decisions`, `get_warnings`, semantic search, source attribution, multi-source synthesis.

### Journey 3: Tech Lead Marcus - Team Standardization

**Marcus needs his team of 5 engineers to follow consistent AI engineering patterns.**

His team keeps reinventing solutions. One engineer uses recursive chunking, another uses semantic chunking. Code reviews become debates about approaches nobody can objectively evaluate.

Marcus uses the Knowledge Pipeline to establish team standards:

- Query: "What patterns exist for production RAG systems?"
- Query: "What are the evaluation methodologies for retrieval quality?"
- Query: "Compare chunking approaches across sources"

He extracts the patterns and creates team guidelines backed by authoritative sources. During code reviews, he can reference specific decisions: "We use pattern X because of warning Y from the LLM Handbook."

**Capabilities Revealed:** `get_patterns`, `compare_sources`, `get_methodologies`, team knowledge sharing.

### Journey 4: API Consumer - MCP Integration

**A developer integrates Knowledge Pipeline into their existing AI development workflow.**

The developer adds the MCP server URL to their Claude Code configuration. No local setup required—just a single URL. They immediately have access to:

- `search_knowledge` for semantic search across all content
- `get_decisions` for structured decision points
- `get_patterns` for reusable code implementations
- `get_warnings` for gotchas and anti-patterns
- `list_sources` for available knowledge bases

Their AI assistant now has access to curated, structured AI engineering knowledge that goes beyond generic training data.

**Capabilities Revealed:** Hosted MCP server, zero-setup user experience, tool discoverability.

### Journey Requirements Summary

| Journey | Primary Capabilities |
|---------|---------------------|
| Builder | Ingestion, extraction (7 types), BMAD integration |
| Solo Engineer | Semantic search, decisions, warnings, synthesis |
| Tech Lead | Patterns, methodologies, source comparison |
| API Consumer | MCP tools, hosted server, authentication |

## Functional Requirements

### FR-1: Source Ingestion

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1.1 | PDF adapter for book ingestion (PyMuPDF) | MVP | Required |
| FR-1.2 | Markdown adapter for documentation | MVP | Required |
| FR-1.3 | arXiv adapter for research papers | Post-MVP | Deferred |
| FR-1.4 | Web scraper for case studies | Post-MVP | Deferred |
| FR-1.5 | Ingestion status tracking (pending, processing, complete, failed) | MVP | Required |
| FR-1.6 | Source metadata storage (title, authors, type, path) | MVP | Required |
| FR-1.7 | Chunking with position tracking (chapter, section, page) | MVP | Required |

### FR-2: Knowledge Extraction

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-2.1 | Decision extraction (choice points with options and considerations) | MVP | Required |
| FR-2.2 | Pattern extraction (reusable code/architecture implementations) | MVP | Required |
| FR-2.3 | Warning extraction (gotchas, anti-patterns, failure modes) | MVP | Required |
| FR-2.4 | Methodology extraction (step-by-step processes from books) | MVP | Required |
| FR-2.5 | Checklist extraction (verification criteria for workflow steps) | MVP | Required |
| FR-2.6 | Persona extraction (role definitions for agent creation) | MVP | Required |
| FR-2.7 | Workflow extraction (process sequences for BMAD workflow design) | MVP | Required |
| FR-2.8 | Claude-as-extractor pattern (extraction during ingestion, not query) | MVP | Required |
| FR-2.9 | Topic tagging for all extractions | MVP | Required |
| FR-2.10 | Source attribution (chunk_id, source_id traceability) | MVP | Required |

### FR-3: Storage

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-3.1 | MongoDB `sources` collection for book/paper metadata | MVP | Required |
| FR-3.2 | MongoDB `chunks` collection for raw text chunks | MVP | Required |
| FR-3.3 | MongoDB `extractions` collection for structured knowledge | MVP | Required |
| FR-3.4 | Qdrant `chunks` collection for semantic search on raw text | MVP | Required |
| FR-3.5 | Qdrant `extractions` collection for semantic search on extractions | MVP | Required |
| FR-3.6 | Compound indexes on `extractions.type` + `extractions.topics` | MVP | Required |
| FR-3.7 | Schema versioning for all documents | MVP | Required |
| FR-3.8 | Local embeddings using all-MiniLM-L6-v2 (384 dimensions) | MVP | Required |

### FR-4: MCP Interface

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-4.1 | `search_knowledge` - semantic search across all content | MVP | Public |
| FR-4.2 | `get_decisions` - query decision extractions by topic | MVP | Public |
| FR-4.3 | `get_patterns` - query code pattern extractions | MVP | Public |
| FR-4.4 | `get_warnings` - query warning extractions | MVP | Public |
| FR-4.5 | `get_methodologies` - query methodology extractions | MVP | Registered |
| FR-4.6 | `list_sources` - list available knowledge sources | MVP | Public |
| FR-4.7 | `compare_sources` - compare extractions across sources | Post-MVP | Registered |

## Non-Functional Requirements

### NFR-1: Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search latency | <500ms p95 | Qdrant + indexed MongoDB |
| MCP tool response | <1s p95 | End-to-end including synthesis |
| Concurrent users | 100+ | Stateless server design |

### NFR-2: Batch Efficiency

| Metric | Target | Measurement |
|--------|--------|-------------|
| Book ingestion | Single session | Complete 800-page book in one run |
| Extraction throughput | 100 chunks/minute | Claude-as-extractor pattern |
| Embedding generation | 1000 chunks/minute | Local sentence-transformers |

### NFR-3: Cost

| Constraint | Implementation |
|------------|----------------|
| Zero external LLM API costs at query time | Pre-extraction during ingestion |
| Zero embedding API costs | Local all-MiniLM-L6-v2 model |
| Infrastructure costs <$50/month | Railway + Atlas Free + Qdrant Free tiers |

### NFR-4: Scalability

| Metric | Target | Approach |
|--------|--------|----------|
| Total chunks | 100k+ | Qdrant clustering ready |
| Sources | 50+ books/papers | MongoDB sharding ready |
| Users | 1000+ concurrent | Stateless MCP server |

### NFR-5: Extensibility

| Extension Point | Pattern |
|-----------------|---------|
| New source types | Adapter ABC pattern |
| New extraction types | Extractor ABC pattern |
| New MCP tools | FastAPI endpoint → MCP mount |
| Schema evolution | Versioned documents with migration scripts |

### NFR-6: Reliability

| Metric | Target |
|--------|--------|
| Uptime | 99.5% |
| Data durability | MongoDB Atlas replication |
| Error recovery | Structured error responses with retry guidance |

## Constraints & Assumptions

### Technical Constraints

| Constraint | Architectural Impact |
|------------|---------------------|
| Zero LLM API costs at query time | Claude-as-extractor during ingestion, local embeddings |
| MCP protocol required | All interactions via MCP tools, fastapi-mcp framework |
| Local-first development | Docker Compose for MongoDB + Qdrant |
| Python 3.11+ | Runtime requirement for all packages |

### Assumptions

| Assumption | Risk if Invalid |
|------------|-----------------|
| Users have Claude Code or MCP-compatible client | No direct API access planned for MVP |
| Books are available in PDF format | Would need additional adapters |
| 384-dimension embeddings sufficient for semantic search | May need larger model for specialized domains |
| Single-region deployment acceptable for MVP | Latency issues for global users |

### Business Constraints

| Constraint | Impact |
|------------|--------|
| Solo developer (Philippebeliveau) | Phased delivery, MVP focus |
| Bootstrap funding | Free tier infrastructure initially |
| Dual-audience requirement | Separate tool sets for builder vs end-user |

## Dependencies

### Infrastructure Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| MongoDB | 7.x | Document storage (sources, chunks, extractions) |
| Qdrant | Latest | Vector storage and semantic search |
| Docker Compose | Latest | Local development environment |

### Python Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | >=0.115 | API framework |
| fastapi-mcp | >=0.4.0 | MCP protocol layer |
| qdrant-client | >=1.13 | Vector storage client |
| sentence-transformers | >=5.0 | Local embeddings |
| pymongo | Latest | MongoDB client |
| pymupdf | Latest | PDF parsing |
| pydantic | >=2.0 | Data validation |
| pydantic-settings | Latest | Configuration management |
| uv | Latest | Package management |

### Cloud Dependencies (Production)

| Service | Tier | Cost |
|---------|------|------|
| Railway | Starter | ~$5/mo |
| MongoDB Atlas | M0 Free → M10 | $0 → $57/mo |
| Qdrant Cloud | Free → Starter | $0 → $25/mo |

### Project Dependencies

| Dependency | Relationship |
|------------|--------------|
| BMAD Method | Module structure, workflow patterns |
| Knowledge Pipeline infrastructure | This PRD defines it |
| AI Engineering Workflows (broader vision) | Consumes Knowledge Pipeline outputs |

## Architecture Reference

**Complete architectural decisions, implementation patterns, and project structure are documented in:**

`_bmad-output/architecture.md`

Key architectural components:
- Monorepo structure: `packages/pipeline/` + `packages/mcp-server/`
- Dual-store architecture: MongoDB (documents) + Qdrant (vectors)
- Hosted MCP server model (community users connect via URL)
- 12+ implementation patterns ensuring AI agent consistency

---

## PRD Completion Summary

**Document Status:** COMPLETE ✅
**Completed:** 2025-12-30
**Author:** Philippebeliveau

### Document Chain

| Document | Location | Status |
|----------|----------|--------|
| Product Brief | `_bmad-output/AI-Engineering-Workflows-Brief.md` | Complete |
| PRD | `_bmad-output/prd.md` | Complete |
| Architecture | `_bmad-output/architecture.md` | Complete |
| Epics & Stories | `_bmad-output/epics.md` | Complete |

### Requirements Summary

| Category | Count |
|----------|-------|
| Functional Requirements (FR) | 27 |
| Non-Functional Requirements (NFR) | 6 categories |
| User Journeys | 4 |
| MCP Tools | 7 |
| Extraction Types | 7 |

### Next Steps

1. Review epics at `_bmad-output/epics.md` for implementation planning
2. Begin Epic 1: Project Foundation & Infrastructure Setup
3. Follow architecture patterns from `_bmad-output/architecture.md`
