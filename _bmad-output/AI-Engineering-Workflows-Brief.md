# AI Engineering Workflows System - Product Brief

**Version:** 0.1 (Draft)
**Date:** December 30, 2025
**Author:** Philippe Beliveau
**Status:** Concept/Planning Phase

---

## Executive Summary

A comprehensive AI engineering knowledge system that transforms dense methodology books (like the 800-page LLM Engineer's Handbook) into interactive, executable workflows. Instead of reading and generalizing, practitioners are guided through structured decision trees that reduce cognitive load and narrow the solution space based on their specific context, constraints, and data.

**Core Insight:** AI doesn't answer - it structures thought and reduces the space where the solution exists.

---

## The Problem

### Current State
- AI engineering methodologies are trapped in 800+ page books
- Practitioners must read, understand, AND generalize to their specific problem
- Cognitive overwhelm leads to poor decisions or paralysis
- Knowledge is scattered: books, papers, Medium articles, case studies, GitHub repos
- Each new project requires re-learning and re-applying the same frameworks

### Pain Points
1. **Information Overload:** Too much unstructured knowledge
2. **Generalization Gap:** Knowing the methodology ≠ Applying it correctly
3. **Decision Sequencing:** Don't know which decisions to make first
4. **Context Loss:** Each decision depends on previous decisions, but this context is lost
5. **Rapid Evolution:** AI landscape changes monthly; books are outdated quickly

---

## The Vision

### What We're Building
A **living, executable knowledge system** for AI engineering that:
- Encodes methodologies as interactive workflows (not static text)
- Guides practitioners through decision trees with context awareness
- Generates structured artifacts at each step (specs, architectures, configs)
- Integrates multiple knowledge sources (books, papers, case studies, GitHub)
- Updates continuously as the AI landscape evolves

### Philosophical Foundation
Inspired by the **spec-forecasting** framework: Every AI engineering decision is a function of:
```
decision = f(
    previous_decisions,
    project_context,
    constraints,
    dataset_characteristics,
    business_requirements
)
```

The system structures this function and reduces the solution space systematically.

---

## Target Audience

### Primary Users
1. **ML Engineers** transitioning to LLM/AI engineering
2. **Software Engineers** building AI-powered products
3. **Data Scientists** deploying models to production
4. **Technical Leads** architecting AI systems

### Secondary Users
1. **Startups** needing rapid AI implementation guidance
2. **Enterprise Teams** standardizing AI engineering practices
3. **Consultants** delivering AI projects to clients
4. **Educators** teaching modern AI engineering

### User Personas

**Persona 1: Solo Engineer Sarah**
- Building RAG system for first time
- Read tutorials, confused by trade-offs
- Needs: Step-by-step guidance with decision rationale

**Persona 2: Tech Lead Marcus**
- Managing team building AI features
- Needs: Standardized workflows, architectural patterns
- Values: Consistency, best practices, proven patterns

**Persona 3: Startup Founder Alex**
- Non-technical, hiring first AI engineer
- Needs: Understanding what questions to ask
- Values: De-risking technical decisions

---

## The Solution

### Core Components

#### 1. BMAD Module: AI Engineering (aie)
A complete BMAD module with specialized agents and workflows.

**Agents:**
- `ai-architect.md` - System design and architecture decisions
- `llm-specialist.md` - Model selection, fine-tuning, prompting
- `data-engineer.md` - Data pipelines, processing, quality
- `mlops-expert.md` - Deployment, monitoring, optimization

#### 2. Dual Entry Points

**Discovery Path** (Problem → Solution)
```
problem-framing.md
    ↓
solution-assessment.md
    ↓
[Routes to appropriate implementation workflow]
```

**Implementation Path** (Direct to specific pattern)
```
User knows they need RAG
    ↓
rag-architecture.md
    ↓
chunking-strategy.md
    ↓
evaluation-framework.md
```

#### 3. Multi-Source Knowledge Architecture

**Embedded Knowledge** (In workflows)
- LLM Engineer's Handbook methodology
- "LLMs in Production" best practices
- Decision trees and frameworks
- Core patterns and principles

**MCP Servers** (External, queryable)
- **Scholar MCP:** Research papers (semantic search)
- **GitHub MCP:** Production code examples
- **Case Study MCP:** Enterprise implementations, Medium articles
- **Premium MCP:** Proprietary patterns, expert interviews

#### 4. Artifact-Based Context Passing
Like BMAD's PRD → Architecture → Stories flow:

```
problem-spec.yaml
    ↓
solution-approach.yaml
    ↓
rag-architecture.yaml
    ↓
chunking-spec.yaml
    ↓
evaluation-plan.yaml
```

Each workflow reads previous artifacts to inform decisions.

---

## Monetization Strategy

### Three-Tiered Model

#### Tier 1: Community (Free/Open Source)
**What's Included:**
- Core workflows (discovery + 3 implementation paths)
- Embedded LLM Handbook methodology
- Public MCP access (Scholar, basic GitHub)
- GitHub community support

**Value:** Build audience, prove concept, community growth

#### Tier 2: Pro ($19/month)
**What's Included:**
- **Authenticated MCP Server:**
  - 50+ enterprise case studies
  - Industry-specific patterns (fintech, healthcare, e-commerce)
  - Expert interviews encoded as workflows
- **Premium workflows** (encrypted in repo):
  - Advanced RAG optimization
  - Production deployment playbooks
  - Multi-agent system patterns
- **Monthly content drops:**
  - 2 new workflows
  - 5 new case studies
  - Updated patterns for new models
- **Community Discord access**
- **Early access** (1 month before free tier)

**Target:** Individual practitioners, small teams

#### Tier 3: Enterprise ($99-499/month)
**What's Included:**
- Everything in Pro
- **Private MCP server** option (on-premise or VPC)
- **Custom workflow development** (2 per year)
- **Team training sessions** (monthly)
- **Priority support** (24hr response)
- **White-label option** (rebrand for internal use)

**Target:** Companies with 5+ AI engineers

### Revenue Protection

**Layer 1: Server-Side MCP** (Primary)
- Premium content on authenticated servers
- Token-based access control
- Usage monitoring and abuse detection

**Layer 2: Encrypted Premium Workflows** (Secondary)
- High-value workflows encrypted in repo
- Decrypt with valid subscription token
- Cache locally for 30 days after auth

**Layer 3: Continuous Value** (Retention)
- Monthly new content (workflows, case studies)
- Rapid updates as AI landscape evolves
- Community and network effects
- Pirated content becomes stale quickly

---

## Technical Architecture

### Repository Structure
```
ai-engineering-workflows/
├── _bmad/
│   └── aie/  (AI Engineering module)
│       ├── agents/
│       │   ├── ai-architect.md
│       │   ├── llm-specialist.md
│       │   ├── data-engineer.md
│       │   └── mlops-expert.md
│       ├── workflows/
│       │   ├── discovery/
│       │   │   ├── problem-framing.md
│       │   │   └── solution-assessment.md
│       │   ├── rag-systems/
│       │   │   ├── rag-architecture.md
│       │   │   ├── chunking-strategy.md
│       │   │   ├── retrieval-optimization.md
│       │   │   └── evaluation-framework.md
│       │   ├── fine-tuning/
│       │   │   ├── data-preparation.md
│       │   │   ├── training-strategy.md
│       │   │   └── evaluation-metrics.md
│       │   ├── production/
│       │   │   ├── deployment-architecture.md
│       │   │   ├── monitoring-observability.md
│       │   │   └── cost-optimization.md
│       │   └── premium/ (encrypted)
│       │       ├── advanced-rag.md.enc
│       │       ├── multi-agent-systems.md.enc
│       │       └── enterprise-patterns.md.enc
│       └── knowledge/
│           ├── methodologies/
│           │   ├── llm-handbook-framework.md
│           │   └── production-patterns.md
│           └── decision-trees/
│               ├── model-selection.yaml
│               └── architecture-choices.yaml
├── mcp-servers/
│   ├── scholar-mcp/  (research papers)
│   ├── github-mcp/   (code examples)
│   └── premium-mcp/  (enterprise content - closed source)
├── outputs/  (generated artifacts)
│   ├── problem-spec.yaml
│   ├── solution-approach.yaml
│   └── ...
└── docs/
    ├── getting-started.md
    └── workflow-guide.md
```

### MCP Server Stack
```
Backend:
├── FastAPI (API server)
├── PostgreSQL (users, subscriptions)
├── Redis (tokens, rate limiting)
├── Stripe (payments)
└── S3 (content storage)

Infrastructure:
├── Railway/Render ($50-100/mo)
├── Cloudflare (CDN, protection)
└── Sentry (monitoring)
```

---

## Differentiation

### vs. Reading Books
- **Books:** Static, require generalization
- **Us:** Interactive, context-aware, executable

### vs. ChatGPT/Claude
- **LLMs:** Reactive, no decision sequencing, context loss
- **Us:** Proactive workflows, structured artifacts, persistent context

### vs. LangChain/LlamaIndex Docs
- **Frameworks:** Tool documentation
- **Us:** Methodology and decision frameworks that use those tools

### vs. Online Courses
- **Courses:** Watch and learn
- **Us:** Work on YOUR project with guided methodology

### vs. Consultants
- **Consultants:** $200-500/hr, one-time engagement
- **Us:** $19/mo, continuous access, self-serve

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-2) - FREE
**Goal:** Prove value, build community

**Deliverables:**
- `aie` BMAD module structure
- 2 agents (ai-architect, llm-specialist)
- 5 core workflows (discovery + RAG + evaluation)
- Embedded LLM Handbook methodology
- Scholar MCP integration
- Public GitHub repo

**Success Metrics:**
- 100 GitHub stars
- 20 active users
- 5 community contributions

### Phase 2: Premium Launch (Month 3)
**Goal:** First paying customers

**Deliverables:**
- MCP server with authentication
- 10 enterprise case studies
- 3 premium workflows (encrypted)
- Stripe integration
- Pro tier launch ($19/mo early bird)

**Success Metrics:**
- 50 paying subscribers
- <5% churn

### Phase 3: Content Engine (Months 4-6)
**Goal:** Establish continuous value

**Deliverables:**
- Monthly content schedule (2 workflows, 5 case studies)
- 5 more implementation workflows
- Industry-specific patterns (3 industries)
- Community Discord

**Success Metrics:**
- 200 subscribers
- >85% retention
- 2 enterprise pilots

### Phase 4: Scale (Months 7-12)
**Goal:** Enterprise tier, marketplace

**Deliverables:**
- Enterprise tier ($99-499/mo)
- Private MCP deployment option
- Custom workflow service
- Community marketplace (workflow packs)

**Success Metrics:**
- 300 Pro subscribers
- 10 Enterprise customers
- $8-10K MRR

---

## Success Metrics

### User Metrics
- **Activation:** User completes first workflow (70% target)
- **Engagement:** Workflows run per month (8+ = engaged)
- **Retention:** Monthly active users (80% target)

### Business Metrics
- **Conversion:** Free → Pro (10% target)
- **Churn:** Monthly churn (<5% target)
- **LTV:** Customer lifetime value (>$300 target)

### Content Metrics
- **Quality:** User rating of workflows (4.5+ / 5)
- **Coverage:** New patterns added monthly (2+ workflows)
- **Freshness:** Content update frequency (bi-weekly)

---

## Risks & Mitigations

### Risk 1: Content Piracy
**Mitigation:**
- Server-side MCP for premium content
- Continuous value model (monthly updates)
- Community network effects
- Encrypted workflows with token auth

### Risk 2: AI Landscape Changes Too Fast
**Mitigation:**
- This is actually our ADVANTAGE
- Subscribers stay for updated patterns
- Free tier becomes marketing for latest paid content

### Risk 3: Low Conversion (Free → Paid)
**Mitigation:**
- Generous free tier (prove value first)
- Clear differentiation (advanced vs basic)
- Time-limited trials (1 month Pro free)

### Risk 4: High Content Creation Burden
**Mitigation:**
- Community contributions (curated)
- Semi-automated case study extraction
- Reusable workflow templates
- Focus on quality over quantity

### Risk 5: Complex Onboarding
**Mitigation:**
- Quickstart guide (5 min to first workflow)
- Video walkthroughs
- Example projects
- Community support

---

## Next Actions

### Immediate (This Week)
1. **Validate demand:** Share concept with 10 AI engineers, gather feedback
2. **Map first workflow:** Fully design `problem-framing.md` workflow
3. **Research MCP:** Deep dive on MCP server best practices
4. **Create landing page:** Simple value proposition + email signup

### Short-term (Month 1)
1. Build `aie` module structure
2. Create first 3 workflows (discovery + RAG architecture)
3. Embed LLM Handbook methodology
4. Launch public repo
5. Write "Getting Started" guide

### Medium-term (Months 2-3)
1. Build MCP server infrastructure
2. Create first 10 case studies
3. Premium workflows (3 encrypted)
4. Stripe integration
5. Launch Pro tier

---

## Questions to Resolve

1. **Branding:** What's the product name?
   - "AI Engineering Workflows"
   - "Spec-Forecasting for AI"
   - "LLM Engineering Framework"
   - Other?

2. **Positioning:** Are we:
   - A methodology (like BMAD)
   - A platform (like GitHub)
   - A knowledge commons (like Wikipedia)

3. **Initial workflows:** Which 5 workflows deliver most value?
   - Problem framing ✓
   - RAG architecture ✓
   - Evaluation framework ✓
   - ???
   - ???

4. **Community strategy:**
   - Discord or Slack?
   - Open GitHub issues or private forum?
   - How to encourage contributions?

5. **Content sourcing:**
   - Encode books ourselves or hire domain experts?
   - Accept community-contributed case studies?
   - Partner with companies for real use cases?

---

## Appendix: Inspiration & Prior Art

### Spec-Forecasting Framework
- Vanilla framework for time series forecasting
- Reduces cognitive load through structured decision trees
- Each prediction is a function of previous context
- Published: https://www.npmjs.com/package/@new-code/spec-forecasting

### Source Books
1. **LLM Engineer's Handbook** (Paul Iusztin, Maxime Labonne)
   - 800 pages of LLM engineering methodology
   - Covers: training, fine-tuning, RAG, deployment, monitoring

2. **LLMs in Production** (Christopher Brousseau, Matthew Sharp)
   - Production-focused patterns
   - Real-world case studies

### Similar Approaches
- **BMAD Method:** Workflow-based software development
- **Design Patterns:** Encoding best practices as reusable patterns
- **Decision Trees:** Medical diagnosis, troubleshooting guides

---

**End of Brief**
