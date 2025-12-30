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
