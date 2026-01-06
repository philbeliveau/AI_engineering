# Knowledge Pipeline

**A cognitive framework for building AI applications — specialized agents guide you through structured workflows, backed by contextual RAG search across the AI engineering literature.**

<p align="center">
  <img src="assets/hero-image.png" alt="Knowledge Pipeline - Agents guiding chaos into clarity" width="600">
</p>

---

## Why This Exists

Building AI applications is overwhelming. You face hundreds of decisions:

- *"What chunking strategy for my domain? What size? Semantic or fixed?"*
- *"RAG or fine-tuning? Hybrid? What are the trade-offs for my scale?"*
- *"What embedding model? What vector DB? How do I evaluate quality?"*

The answers exist — scattered across books, papers, and case studies. But finding and synthesizing them while holding your specific context in mind is exhausting.

**Knowledge Pipeline is a cognitive framework that carries this load for you.**

It's not just search. It's a **workflow of specialized AI agents** that:
1. Guide you through structured steps (specification → architecture → implementation)
2. Ask the right questions at each stage
3. Search the knowledge base **contextually** — your domain, scale, and constraints shape every query
4. Synthesize across multiple sources to shrink the solution space

---

## The Power: MCP + Agentic Workflows

The magic happens when **MCP search meets structured workflows**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WITHOUT THIS FRAMEWORK                                                 │
│                                                                         │
│  Developer → Vague question → Generic search → Overwhelming results    │
│            → Still confused → Wrong decisions → Costly rework           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  WITH THIS FRAMEWORK                                                    │
│                                                                         │
│  Workflow Step: "Define your domain, scale, constraints"                │
│        ↓                                                                │
│  Context loaded: domain=legal, scale=enterprise, constraint=compliance │
│        ↓                                                                │
│  Agent searches: "legal document chunking compliance enterprise"        │
│        ↓                                                                │
│  Results: Focused, relevant, synthesized with warnings                  │
│        ↓                                                                │
│  Decision space: Shrunk from 100 options to 3 validated approaches      │
└─────────────────────────────────────────────────────────────────────────┘
```

**The workflow enforces structure. Structure shrinks the solution space. Smaller space = better decisions.**

---

## What's Encoded in the Knowledge Base

This isn't just book content. We extract **actionable structure**:

| Extraction Type | What It Captures |
|-----------------|------------------|
| **Decisions** | Architectural choices with trade-offs, options, and recommendations |
| **Patterns** | Reusable implementations with code examples and context |
| **Warnings** | Anti-patterns, pitfalls, and failure modes to avoid |
| **Methodologies** | Step-by-step processes for complex tasks |
| **Agent Personas** | Role definitions for specialized agents (Analyst, Architect, Data Engineer, AI Engineer) |
| **Workflow Steps** | Question sequences, decision trees, validation checkpoints |

The agents themselves are built from this knowledge — their questions, their expertise, their decision patterns all come from the encoded literature.

---

## Specialized Agents

Each agent brings domain expertise and asks the right questions:

| Agent | Role | Focus |
|-------|------|-------|
| **Analyst** | Business context | Domain, users, constraints, success metrics |
| **Architect** | System design | Infrastructure, scalability, integration patterns |
| **Data Engineer** | Data pipeline | Ingestion, chunking, processing, storage |
| **AI Engineer** | ML systems | Embeddings, retrieval, generation, evaluation |

Agents don't just answer — they **guide**. They know what to ask, when to warn, and how to validate.

---

## Who It's For

- **AI/ML Engineers** building LLM applications, RAG systems, or agents
- **Software Developers** adding AI capabilities to products
- **Technical Leaders** making architectural decisions
- **Solo builders** who need a thinking partner for complex AI projects

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────────────┐
│  1. KNOWLEDGE EXTRACTION (One-time)                                      │
│                                                                          │
│  Books, Papers, Case Studies                                             │
│        ↓                                                                 │
│  PDF/Markdown Parsing → Semantic Chunking → Claude API Extraction        │
│        ↓                                                                 │
│  Structured prompts extract: decisions, patterns, warnings,              │
│  methodologies, agent definitions (with validation & deduplication)      │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  2. VECTOR STORAGE                                                       │
│                                                                          │
│  MongoDB (metadata, full content) + Qdrant (768d nomic embeddings)       │
│                                                                          │
│  Semantic search with 8K context window for long-form retrieval          │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  3. MCP SERVER (Real-time queries)                                       │
│                                                                          │
│  7 tools: search, decisions, patterns, warnings, methodologies, sources  │
│  Tool descriptions guide Claude to multi-query, cross-reference, warn    │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  4. AGENTIC WORKFLOWS (Contextual guidance)                              │
│                                                                          │
│  Specialized agents → Structured steps → Contextual MCP queries          │
│                                                                          │
│  Each step loads prior context → Searches are domain-aware               │
│  Questions enforce structure → Solution space shrinks                    │
│  Warnings surface proactively → Mistakes avoided                         │
└──────────────────────────────────────────────────────────────────────────┘
```

**Design Philosophy:**
- Extractions are for *navigation*, Claude is for *synthesis*
- Workflows provide *structure*, agents provide *expertise*
- Context flows forward, each step builds on the last

---

## Intelligent Tool Behavior

The MCP tools aren't passive endpoints — their descriptions **embed behavioral guidance** that shapes how Claude uses them:

### Multi-Query & Synthesis

```
Tool description instructs:
"For comprehensive answers, call this tool 2-3 times with varied queries:
 1. User's original phrasing
 2. Technical synonyms (e.g., 'RAG' → 'retrieval augmented generation')
 3. Related concepts (e.g., 'chunking' → 'document splitting')"

Result: Claude automatically expands searches, cross-references, synthesizes.
```

### Query Refinement

```
Tool description instructs:
"If results < 3 relevant, try synonyms or related concepts.
 If user query is vague (< 3 specific terms), ask clarifying question first."

Result: Claude rephrases, expands, or asks before giving incomplete answers.
```

### Proactive Warnings

```
Tool description instructs:
"ALWAYS call get_warnings() before recommending any implementation.
 Surface top 2-3 warnings. Frame as 'To avoid X, ensure you Y'."

Result: Claude debates trade-offs, surfaces pitfalls, never gives blind recommendations.
```

### Source Diversity

```
Tool description instructs:
"Results must span at least 2 different sources.
 If single source dominates, reformulate query for diversity."

Result: Claude synthesizes across books/papers, notes agreements and disagreements.
```

### Tool Chaining

```
Tool descriptions cross-reference:
"After search, call get_decisions() if results mention trade-offs.
 Call get_warnings() if implementing. Call get_patterns() for code."

Result: Claude chains tools intelligently based on user intent.
```

This creates an **implicit orchestration layer** — Claude behaves like a research analyst, not a search box.

---

## AI Engineering Workflow (FTI Pattern)

The workflow follows the **Feature/Training/Inference (FTI)** pipeline pattern from the LLM Engineer's Handbook:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    FEATURE      │     │    TRAINING     │     │   INFERENCE     │
│    PIPELINE     │────▶│    PIPELINE     │────▶│    PIPELINE     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Phase Structure

| Phase | Description | Key Decisions |
|-------|-------------|---------------|
| **0. Scoping** | Use case classification, RAG vs Fine-tuning | Architecture direction |
| **1. Feature Pipeline** | Data collection, processing, vectorization | Data & embedding choices |
| **2. Training Pipeline** | SFT, DPO, model optimization (if fine-tuning) | Training strategy |
| **3. Inference Pipeline** | RAG setup, deployment, serving | Deployment pattern |
| **4. Evaluation** | Testing, benchmarking, quality assurance | Evaluation metrics |
| **5. Operations** | Drift detection, prompt monitoring, scaling | Monitoring strategy |

### Why FTI Pattern

- **Solves training-serving skew** — same feature logic in training and inference
- **Clear separation of concerns** — each pipeline has one job
- **Independent scaling** — scale inference without touching training
- **Team ownership** — different teams can own different pipelines

### Knowledge Integration

Each phase queries the knowledge base contextually:

| Phase | Knowledge Queries |
|-------|------------------|
| Scoping | `get_decisions` for RAG vs fine-tuning trade-offs |
| Feature | `get_patterns` for chunking, embedding strategies |
| Training | `get_methodologies` for SFT, DPO processes |
| Inference | `get_patterns` for RAG, caching, deployment |
| Evaluation | `get_warnings` for evaluation pitfalls |
| Operations | `get_warnings` for drift detection, monitoring gaps |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Runtime** | Python 3.11, uv package manager |
| **API** | FastAPI + fastapi-mcp |
| **Vector DB** | Qdrant Cloud (768d embeddings) |
| **Document DB** | MongoDB Atlas |
| **Embeddings** | nomic-embed-text-v1.5 (local, 8K context, no API costs) |
| **Extraction** | Claude API with structured prompts (one-time ingestion) |
| **Deployment** | Railway (server), Docker |

---

## Quick Start — Connect to the MCP Server

Add the Knowledge Pipeline to your Claude configuration to get AI engineering knowledge directly in your conversations.

### Claude Desktop / Claude Code

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "knowledge-pipeline": {
      "type": "sse",
      "url": "https://knowledge-mcp-production.up.railway.app/mcp"
    }
  }
}
```

Then restart Claude Desktop/Claude Code.

---

## Slash Commands (Clone & Use)

If you clone this repo, you get instant access to these slash commands in Claude Code:

| Command | Description |
|---------|-------------|
| `/search-knowledge <query>` | Semantic search across all knowledge |
| `/get-decisions <topic>` | Architectural decisions with trade-offs |
| `/get-patterns <topic>` | Reusable implementation patterns |
| `/get-warnings <topic>` | Anti-patterns and pitfalls to avoid |
| `/list-sources` | List all knowledge sources |
| `/ai-knowledge <question>` | General AI engineering assistant |

### Usage

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/AI_engineering.git
cd AI_engineering

# Use slash commands in Claude Code
/get-decisions RAG vs fine-tuning
/get-patterns semantic caching
/search-knowledge prompt injection
```

---

## Available MCP Tools

Once connected, Claude can use these tools to answer your AI engineering questions:

| Tool | Description |
|------|-------------|
| `search_knowledge` | Semantic search across all AI engineering knowledge |
| `get_decisions` | Architectural decisions with trade-offs and recommendations |
| `get_patterns` | Reusable implementation patterns with code examples |
| `get_warnings` | Anti-patterns and pitfalls to avoid |
| `list_sources` | List all knowledge sources (books, papers, case studies) |

### Example Questions

After connecting, try asking Claude:

- "What are best practices for LLM API retry logic?"
- "Show me patterns for semantic caching"
- "What decisions should I consider for RAG vs fine-tuning?"
- "What are common pitfalls when building AI agents?"

## Project Structure

```
packages/
├── pipeline/      # Batch ingestion & extraction (PDF → Knowledge)
└── mcp-server/    # Real-time MCP query server (Knowledge → Claude)
```

## Development

See individual package READMEs for development setup:

- [MCP Server Development](packages/mcp-server/README.md)
- Pipeline Development (coming soon)

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check (MongoDB + Qdrant status) |
| `GET /docs` | Interactive API documentation |
| `/mcp` | MCP protocol endpoint for Claude clients |

## Status

**Production:** https://knowledge-mcp-production.up.railway.app

| Service | Status |
|---------|--------|
| MCP Server | Deployed on Railway |
| MongoDB | Atlas M0 (Free) |
| Qdrant | Cloud (Free) |

## License

MIT
