# Knowledge Pipeline

**A cognitive framework for building AI applications — specialized agents guide you through structured workflows, backed by contextual knowledge search across the AI engineering literature.**

<p align="center">
  <img src="assets/hero-image.png" alt="Knowledge Pipeline - Agents guiding chaos into clarity" width="600">
</p>

---

## Why This Exists

Building AI applications is overwhelming. You face hundreds of decisions about architecture, data pipelines, embeddings, fine-tuning, RAG, evaluation, and operations.

The answers exist — scattered across books, papers, and case studies. But finding and synthesizing them while holding your specific context in mind is exhausting.

**Knowledge Pipeline is a cognitive framework that carries this load for you.**

It combines two key ideas:
1. **Knowledge Extraction** — Structured extractions from AI engineering literature (decisions, patterns, warnings, methodologies)
2. **Agentic Workflows** — Specialized agents that guide you through building production LLM systems with contextual, knowledge-grounded decisions at each step

---

## What's Encoded in the Knowledge Base

We extract **actionable structure** from the literature:

| Extraction Type | What It Captures |
|-----------------|------------------|
| **Decisions** | Architectural choices with trade-offs and recommendations |
| **Patterns** | Reusable implementations with context and constraints |
| **Warnings** | Anti-patterns, pitfalls, and failure modes to avoid |
| **Methodologies** | Step-by-step processes for complex tasks |

### Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    AI ENGINEERING WORKFLOW                               │
│                    (11 Specialized Agents)                               │
└──────────────────────────────────────────────────────────────────────────┘

PHASE 0: SCOPING
  Step 1: Business Analyst   📋  → Stakeholders, use cases, success metrics
  Step 2: FTI Architect      🏗️  → RAG vs Fine-tuning decision

PHASE 1: FEATURE PIPELINE
  Step 3: Data Engineer      🔧  → Data sources, ingestion, cleaning
  Step 4: Embeddings Engineer 🧬 → Chunking strategy, embedding model

PHASE 2: TRAINING (Conditional)
  Step 5: Fine-Tuning Specialist 🎯 → SFT/DPO config, dataset prep

PHASE 3: INFERENCE
  Step 6: RAG Specialist     🔍  → RAG pipeline, retrieval, reranking
  Step 7: Prompt Engineer    📝  → System prompts, few-shot examples

PHASE 4: EVALUATION
  Step 8: LLM Evaluator      📊  → Evaluation framework, quality gate

PHASE 5: OPERATIONS
  Step 9: MLOps Engineer     🔄  → Monitoring, drift detection, alerting

PHASE 6: INTEGRATION & HANDOFF
  Step 10: Tech Lead         👨‍💼 → Story review, sequencing, GO/REVISE decision
  Step 11: Story Elaborator  📚  → BMM format transformation, dev handoff
```

### The 11 Specialized Agents

Each agent brings domain expertise, asks clarifying questions, and generates implementation stories:

| Step | Agent | Focus |
|------|-------|-------|
| **1** | **Business Analyst** 📋 | Project initialization, stakeholder identification, use cases, success metrics |
| **2** | **FTI Architect** 🏗️ | Architecture decision (RAG-only, fine-tuning, or hybrid), design trade-offs |
| **3** | **Data Engineer** 🔧 | Data sources, ingestion pipeline, data quality, cleaning workflows |
| **4** | **Embeddings Engineer** 🧬 | Chunking strategy selection, embedding model choice, vector DB setup |
| **5** | **Fine-Tuning Specialist** 🎯 | SFT/DPO configuration, dataset preparation, training workflow (conditional) |
| **6** | **RAG Specialist** 🔍 | RAG pipeline design, retrieval strategy, reranking, context optimization |
| **7** | **Prompt Engineer** 📝 | System prompt design, few-shot examples, response templates |
| **8** | **LLM Evaluator** 📊 | Evaluation framework design, metrics selection, quality gates |
| **9** | **MLOps Engineer** 🔄 | Deployment architecture, monitoring setup, drift detection, alerting |
| **10** | **Tech Lead** 👨‍💼 | Story review, dependency sequencing, implementation validation, GO/REVISE decision |
| **11** | **Story Elaborator** 📚 | Story format transformation, task breakdown, dev handoff |

### How to Run the Workflow

The workflow is designed to be executed step-by-step with your AI engineering project:

1. **Start at Step 1** — Business Analyst
   - Initialize your project with stakeholder and use case discovery
   - Generate project specification and success metrics
   - Create `sidecar.yaml` for state tracking

2. **Progress Through Steps** — Follow the numbered sequence
   - Each step reads completely before execution
   - Each agent queries Knowledge MCP contextually
   - Each phase generates implementation stories

3. **Conditional Routing at Step 2** — FTI Architect decides
   - **RAG-only path** — Skips Step 5 (Training), goes directly to Step 6
   - **Fine-tuning path** — Includes Step 5, then continues to inference
   - **Hybrid path** — Uses both fine-tuning and RAG together

4. **Quality Gate at Step 8** — LLM Evaluator validates
   - Define metrics and benchmarks before inference
   - Ensure quality standards before deployment

5. **Tech Lead Review at Step 10** — Integration validation
   - Review all stories from previous steps
   - Validate sequencing and dependencies
   - Make GO/REVISE decision

6. **Handoff to Development** — Step 11 Story Elaborator
   - Transform stories to BMM format
   - Break down into implementation tasks
   - Hand off to development team via dev agent

---

## Getting Started

### Option 1: Use via Claude Desktop (No Installation)

Add to your `claude_desktop_config.json`:

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

**File locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Then restart Claude. Claude can now query the knowledge pipeline using these tools:
- `search_knowledge` — Semantic search across all knowledge
- `get_decisions` — Architectural decisions with trade-offs
- `get_patterns` — Reusable implementation patterns
- `get_warnings` — Anti-patterns and pitfalls to avoid
- `list_sources` — List all knowledge sources

**Example:** Ask Claude "What decisions should I consider for RAG vs fine-tuning?"

### Option 2: Clone & Use Slash Commands

```bash
git clone https://github.com/YOUR_USERNAME/AI_engineering.git
cd AI_engineering

# Use these slash commands in Claude Code:
/search-knowledge prompt injection
/get-decisions RAG vs fine-tuning
/get-patterns semantic caching
/get-warnings fine-tuning pitfalls
```

## License

MIT
