# Tech Stack Integration into AI Engineering Workflow

**Date:** 2026-01-06
**Status:** Complete
**Integration Point:** Phase 0 (Scoping) - Step 2: FTI Architect

---

## 🎯 What Was Updated

### 1. Step 02: FTI Architect (`step-02-fti-architect.md`)

**Added complete tech stack selection workflow:**

#### New Sections:
- **Section 5.5:** Knowledge MCP queries for tool selection
  - 5 mandatory queries grounded in LLM Handbook extractions
  - Covers: orchestration, tracking, monitoring, deployment patterns

- **Section 6:** Tech stack constraints gathering
  - Cloud provider assessment
  - Team size and expertise
  - Budget and operational overhead

- **Section 7:** Tech stack options presentation
  - Option A: Cost-optimized (open-source stack)
  - Option B: Balanced (managed services)
  - Option C: Enterprise (unified platform)
  - Decision matrix with trade-offs

- **Section 8:** Tech stack decision framework
  - Structured recommendation based on constraints
  - Rationale documentation

- **Section 9:** Documentation updates
  - Creates `tech-stack-decision.md` with full justification
  - Updates `sidecar.yaml` with tech_stack section
  - Adds TECH-001 entry to `decision-log.md`
  - Updates `project-spec.md` with technology choices

#### Success Criteria Updated:
- ✅ Must query Knowledge MCP for tool selection (all 5 queries)
- ✅ Must gather team constraints before recommendations
- ✅ Must create tech-stack-decision.md with rationale for each tool
- ✅ Must update sidecar with tech_stack values
- ✅ Must document both ARCH-001 AND TECH-001 decisions

---

### 2. FTI Architect Agent (`agents/fti-architect.md`)

**Enhanced agent persona to own tech stack selection:**

- Added explicit expertise in tool ecosystem and technology selection
- Updated outputs to include `tech-stack-decision.md` as artifact
- Enhanced handoff to list specific tool decisions (orchestration, vector DB, tracking, serving)
- Strengthened identity to reflect pragmatic tool selection approach

---

## 📋 Tech Stack Decision Framework

### Dynamic Query-Based Approach

**NOT hardcoded stacks. Instead:**

Each tool layer is selected independently through contextualized Knowledge MCP queries:

| Layer | Query Context | Knowledge Base Returns |
|-------|---------------|----------------------|
| **Orchestration** | [Architecture] + [Team Size] + [Cloud] | Tools suited to that specific context |
| **Vector DB** | [Deployment Type] + [Performance Needs] | Options with trade-offs (managed vs self-hosted, cost, latency) |
| **Experiment Tracking** | [ML Focus: LLM vs General] + [Budget] | Recommended tools with pros/cons |
| **Serving** | [Cloud] + [Scale] + [Latency SLA] | Deployment options with operational implications |
| **Monitoring** | [LLM vs General] + [Complexity Tolerance] | Monitoring solutions with integration guidance |

### Example Query Process (User-Driven)

**User context:**
- Small startup (3 engineers)
- AWS cloud
- Building RAG system
- $5K annual budget
- Needs LLM-specific monitoring (Opik interest)

**Queries executed (by agent, with user input):**
```
1. "RAG orchestration tools 3 engineers AWS startup budget"
   → KB returns: Airflow, ZenML patterns, trade-offs

2. "vector database managed cloud AWS qdrant latency"
   → KB returns: Qdrant cloud, managed options, costs

3. "LLM experiment tracking evaluation monitoring startup budget"
   → KB returns: Opik recommendations, integration with Qdrant

4. "lightweight inference serving AWS FastAPI docker"
   → KB returns: Deployment patterns, cost estimates

5. "LLM monitoring observability opik startup"
   → KB returns: Opik patterns, integration with orchestration
```

**Synthesized stack (from KB, not hardcoded):**
- Orchestration: Airflow (lightweight, free, startup-friendly per KB)
- Vector DB: Qdrant Cloud (managed option, cost-effective per KB)
- Experiment Tracking: Opik (LLM-native, startup tier per KB)
- Serving: FastAPI + AWS (lightweight, self-managed per KB)
- Monitoring: Opik + custom (integrated monitoring per KB patterns)

**Cost & Effort (from KB patterns):**
- Annual: ~$3-5K (Qdrant + Opik + compute per KB estimates)
- Setup: ~6-8 weeks (based on KB workflow templates)
- Overhead: Medium (self-managed infrastructure per KB patterns)

---

## 🔗 Knowledge Base Integration

### Dynamic Query Patterns (Contextualized with User Constraints)

**No hardcoded queries. Instead, agent constructs queries from user context:**

1. **For Orchestration (contextualized):**
   - Endpoint: `search_knowledge`
   - Pattern: `"[RAG|fine-tuning|hybrid] orchestration tools [team_size] [cloud] [budget]"`
   - Examples:
     - "RAG orchestration tools 3 engineers AWS startup"
     - "fine-tuning orchestration tools enterprise kubernetes on-prem"
   - KB returns: Tools suited to that exact context with trade-offs

2. **For Vector DB (contextualized):**
   - Endpoint: `search_knowledge`
   - Pattern: `"vector database [managed|self-hosted] [cloud] [latency_requirement]"`
   - Examples:
     - "vector database managed cloud AWS latency requirements"
     - "self-hosted vector database on-prem performance"

3. **For Experiment Tracking (contextualized):**
   - Endpoint: `search_knowledge`
   - Pattern: `"[LLM|general] experiment tracking [team_size] [budget]"`
   - Examples:
     - "LLM experiment tracking startup budget open source"
     - "MLOps experiment tracking enterprise collaboration"

4. **For Serving (contextualized):**
   - Endpoint: `search_knowledge`
   - Pattern: `"inference serving [cloud] [scale] [latency_sla]"`
   - Examples:
     - "inference serving AWS production latency SLA"
     - "lightweight inference serving docker single machine"

5. **For Monitoring (contextualized):**
   - Endpoint: `search_knowledge`
   - Pattern: `"[LLM|general] monitoring observability [requirements]"`
   - Examples:
     - "LLM monitoring observability opik evaluation"
     - "lightweight monitoring prometheus grafana cost"

6. **General Framework (if needed):**
   - Endpoint: `get_decisions`
   - Topic: "tool selection infrastructure deployment"
   - Purpose: Understand decision criteria for ambiguous choices

### Key Principle

**Queries are constructed FROM user context, not executed against fixed query strings.**

The agent gathers constraints, then crafts specific queries that will return recommendations matching that user's situation, not generic recommendations.

---

## 🔄 Workflow Flow-Through

### Tech Stack as Foundation

The tech stack decision becomes **THE FOUNDATION** for all downstream phases:

```
Step 1: Business Analyst
   ↓
Step 2: FTI Architect
   ├─ Decides: Architecture (RAG vs FT)
   └─ Decides: Tech Stack (3 options)
   ↓
Step 3: Data Engineer (Phase 1)
   └─ Uses orchestration tool + vector DB from tech-stack-decision.md
   ↓
Step 4: Training Specialist (Phase 2, if FT)
   └─ Uses orchestration + tracking tools from tech-stack-decision.md
   ↓
Step 5: Inference Architect (Phase 3)
   └─ Uses serving tool + monitoring (Opik) from tech-stack-decision.md
   ↓
Step 6: Evaluator (Phase 4)
   └─ Uses tracking tool + cost constraints from tech-stack-decision.md
   ↓
Step 9: MLOps Engineer (Phase 5)
   └─ Uses monitoring + orchestration tools from tech-stack-decision.md
```

### Critical Constraint

**Any downstream phase suggesting different tools = BLOCKER until reconciled with Phase 0 tech stack decision.**

Tool consistency across phases is CRITICAL. If a phase recommends a different tool, it must be explicitly documented with rationale in that phase's decision log, referencing the Phase 0 tech stack choice.

---

## 📁 New/Updated Artifacts

### Created in Each Project

When a user completes Step 2, they now have:

1. **`architecture-decision.md`** - Architectural choice (existing)
2. **`tech-stack-decision.md`** - NEW: Tool selection with full rationale
3. **`sidecar.yaml`** - Updated with `tech_stack` section
4. **`decision-log.md`** - Updated with ARCH-001 and TECH-001 entries
5. **`project-spec.md`** - Updated with technology choices

### Tech Stack Decision Template

```yaml
# Tech Stack Decision

## Chosen Stack
orchestration: "[ZenML | Airflow | ...]"
vector_db: "[Qdrant | Pinecone | ...]"
monitoring: "[Opik | Comet | ...]"
serving: "[SageMaker | FastAPI | ...]"
tracking: "[MLflow | Comet | ...]"

## Rationale Per Tool
# (with cost, setup time, team expertise required)

## Total Cost Estimate
annual_cost: "[calculated]"
setup_effort_weeks: "[weeks]"
operational_overhead: "[high/medium/low]"

## Handoff to Each Phase
# Shows which tool each phase uses
```

---

## 🎓 Knowledge Base Coverage

From the knowledge base analysis:

**Tools Covered:**
- ✅ ZenML (54 extractions) - Orchestration, reproducibility
- ✅ SageMaker (54 extractions) - Training, inference, deployment
- ✅ Opik (5 extractions) - LLM monitoring, evaluation
- ✅ Comet (10 extractions) - Experiment management
- ✅ Weights & Biases (16 extractions) - Experiment tracking
- ✅ Airflow (6 extractions) - DAG orchestration

**Extraction Types for Step 02:**
- 60 Workflows - Step-by-step processes
- 62 Checklists - Production readiness
- 19 Patterns - Architecture patterns
- 18 Decisions - Tool selection frameworks
- 26 Methodologies - Process guidance
- 57 Warnings - Anti-patterns and pitfalls

**All from LLM Handbook (1,137 extractions, 67% of knowledge base)**

---

## ✅ Verification Checklist

Before Step 2 is complete, verify:

- [ ] Knowledge MCP queries executed (all 5)
- [ ] Team constraints documented (cloud, budget, expertise, overhead)
- [ ] Tech stack option presented (A, B, or C)
- [ ] Tool rationale documented for each layer
- [ ] `tech-stack-decision.md` created
- [ ] `sidecar.yaml` updated with `tech_stack` section
- [ ] `decision-log.md` updated with TECH-001 entry
- [ ] User confirmed tech stack before proceeding
- [ ] Handoff to Data Engineer includes tech-stack-decision.md reference

---

## 🔄 Integration with Phase 0 Handoff

### From Business Analyst (Step 1) → FTI Architect (Step 2)
- Use cases and priorities
- Success metrics and constraints
- Data sensitivity and sources

### From FTI Architect (Step 2) → Data Engineer (Step 3)
- **Architecture decision** (RAG vs FT)
- **Tech stack decision** (Option A/B/C with tool selections)
- **Orchestration tool** to use in Phase 1
- **Vector DB** for semantic storage
- **Cost constraints** and effort estimates
- **Team expertise requirements**

---

## 📝 Next Steps

1. **Test Step 2 workflow** with sample user contexts:
   - Startup (3 engineers, AWS, $5K budget)
   - Scale-up (10 engineers, multi-cloud, $20K budget)
   - Enterprise (50 engineers, on-prem + AWS, $50K+ budget)

2. **Verify dynamic query approach:**
   - Agent constructs queries from user constraints (not hardcoded)
   - KB returns context-specific recommendations
   - Synthesis shows trade-offs relevant to user context
   - User can see query process and modify constraints to re-query

3. **Validate query results:**
   - Does "RAG orchestration tools 3 engineers AWS startup" return appropriate recommendations?
   - Does re-querying with different constraints change results appropriately?
   - Are cost/effort estimates from KB patterns realistic?

4. **Document Phase 1-5 usage** of tech-stack-decision.md:
   - Data Engineer: Uses orchestration + vector DB
   - Training Specialist: Uses orchestration + tracking
   - Inference Architect: Uses serving + monitoring
   - Etc.

5. **Create phase-specific templates** that reference tech-stack-decision.md values
6. **Test handoff consistency** - ensure each downstream phase uses correct tools from Phase 0 decision

---

## 🎯 Why This Matters

**Before (Gap):** Tech stack was assumed, not decided. Phases made independent tool choices. Tools were generic or hardcoded.

**After (Solution - KNOWLEDGE-GROUNDED):**
- Tech stack is explicit decision at Phase 0
- ALL downstream phases reference and use it
- **Recommendations come from Knowledge MCP queries, not hardcoded options**
- **Each user gets tool stacks tailored to their constraints, not generic templates**
- **Knowledge base grows and recommendations evolve automatically**

**Principles Enforced:**
✅ **No hardcoding** - Use knowledge base queries, not static options
✅ **Runtime queries** - Contextualized with user constraints
✅ **Synthesis visible** - User sees KB patterns and trade-offs
✅ **Future-proof** - As KB grows with new sources, recommendations improve

**Benefits:**
- **Consistency:** All phases use same tools decided in Phase 0
- **Context-Aware:** Recommendations fit user's actual constraints
- **Knowledge-Grounded:** Tools chosen from 1,137+ LLM Handbook extractions
- **Transparent:** User understands why each tool was chosen (via KB patterns)
- **Evolving:** Knowledge base growth automatically improves future recommendations
- **No Generic Templates:** Each project gets custom stack, not "Option A/B/C"

---

**Key Achievement:** The FTI Architect now owns tech stack selection as a **knowledge-grounded decision**, not a configuration template.

*Updated: 2026-01-06 | BMad Builder | FTI Architect Enhancement (Dynamic Query-Based)*
