# AI Engineering Workflow & Agent Design

> Summary of the RAG-powered BMAD workflow architecture for AI Engineering guidance.

**Created:** 2026-01-04
**Status:** Design Complete, Ready for Implementation

---

## Overview

This document captures the design decisions for building BMAD workflows that leverage the Knowledge Pipeline MCP server. The architecture enables Claude Code to intelligently search, retrieve, and synthesize knowledge from multiple AI engineering sources (books, papers, case studies).

**Core Philosophy:** The MCP tools provide navigation; Claude provides synthesis.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: MCP Tool Descriptions                   │
│         (Implicit prompts that guide Claude's tool usage)           │
│                                                                     │
│   search_knowledge | get_decisions | get_patterns | get_warnings   │
│   get_methodologies | list_sources | compare_sources               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 LAYER 2: Agent Capabilities Section                  │
│        (Persistent knowledge retrieval protocol in agent.md)        │
│                                                                     │
│   <capabilities>                                                    │
│     <knowledge-retrieval-protocol>                                  │
│       - Context-aware search rules                                  │
│       - Multi-source requirements                                   │
│       - Proactive warnings mandate                                  │
│     </knowledge-retrieval-protocol>                                 │
│   </capabilities>                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   LAYER 3: Workflow Step Instructions               │
│          (Step-specific guidance that references loaded spec)       │
│                                                                     │
│   Step 1: Create Specification → outputs spec.md                    │
│   Step 2: Data Processing → loads spec.md, contextual search        │
│   Step 3: Architecture → loads spec.md, decision synthesis          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: MCP Tool Descriptions (Implemented)

The tool descriptions in `packages/mcp-server/src/tools/*.py` have been enhanced with:

### Description Pattern

Each tool includes:
1. **WHEN TO USE** - Trigger conditions for this tool
2. **WHEN NOT TO USE** - Redirect to the correct tool
3. **MULTI-QUERY/PATTERN STRATEGY** - How to get comprehensive results
4. **SYNTHESIS GUIDANCE** - How to combine and present results
5. **COMBINE WITH** - Related tools to chain

### Tool Chaining Logic

```
User Intent                    Primary Tool        Follow-up Tools
─────────────────────────────────────────────────────────────────────
"What is X?"                   search_knowledge    -
"Should I use X or Y?"         get_decisions       get_warnings, compare_sources
"How do I implement X?"        get_patterns        get_warnings (ALWAYS)
"What can go wrong with X?"    get_warnings        -
"What's the process for X?"    get_methodologies   get_patterns, get_warnings
"What sources cover X?"        list_sources        compare_sources
```

### Spec-Awareness in Descriptions

All tool descriptions include reminders:
- "If spec/context is loaded, ALWAYS include domain terms in query"
- "Include domain from loaded spec if available"
- "Weight perspectives by relevance to domain/constraints"

---

## Layer 2: Agent Capabilities Section (To Build)

### Agent File Location

```
_bmad/bmm/agents/ai-engineer.md
```

### Proposed Agent Structure

```xml
<agent id="ai-engineer.agent.yaml" name="Ada" title="AI Engineering Specialist" icon="🤖">

  <persona>
    <role>AI Engineering Specialist + RAG Architect</role>
    <identity>
      Senior AI engineer with deep expertise in LLM applications, RAG systems,
      and production ML. Specializes in translating business problems into
      robust AI solutions.
    </identity>
    <communication_style>
      Technical but accessible. Shows work and cites sources.
      Always explains trade-offs.
    </communication_style>
    <principles>
      - Every recommendation grounded in retrieved knowledge, not assumptions
      - Surface warnings proactively before implementation
      - Synthesize across multiple sources for balanced perspective
    </principles>
  </persona>

  <capabilities critical="ALWAYS_ACTIVE">
    <knowledge-retrieval-protocol>
      <description>
        This agent has access to an AI Engineering knowledge base via MCP tools.
        The following protocol governs ALL knowledge retrieval operations.
      </description>

      <tools available="true">
        <tool name="search_knowledge">Semantic search across all sources</tool>
        <tool name="get_decisions">Architectural decision points</tool>
        <tool name="get_patterns">Implementation patterns with code</tool>
        <tool name="get_warnings">Pitfalls and anti-patterns</tool>
        <tool name="get_methodologies">Step-by-step processes</tool>
        <tool name="list_sources">Available knowledge sources</tool>
        <tool name="compare_sources">Cross-source comparison</tool>
      </tools>

      <context-aware-search rule="MANDATORY">
        When a specification or context document is loaded:
        1. EXTRACT key attributes: domain, scale, constraints, use_case
        2. ALL searches MUST incorporate these attributes
        3. Query formulation pattern:
           - "{domain} + {concept}" for domain-specific results
           - Include scale terms if enterprise: "scalable", "production"
           - Include constraint terms: "low-latency", "high-accuracy"

        GOOD: "legal document chunking for compliance"
        BAD:  "chunking" (ignores loaded context)
      </context-aware-search>

      <multi-source-requirement rule="MANDATORY">
        For any substantive recommendation:
        1. Make at least 2-3 search_knowledge() calls with varied queries
        2. Results must span at least 2 different sources
        3. If single-source dominates, reformulate query for diversity
      </multi-source-requirement>

      <proactive-warnings rule="MANDATORY">
        BEFORE recommending any implementation:
        1. Call get_warnings() for the relevant topic
        2. Surface top 2-3 warnings in your recommendation
        3. Frame as "To avoid X, ensure you Y"
      </proactive-warnings>

      <synthesis-protocol>
        When combining results from multiple tools:
        1. Note agreements across sources (strong signal)
        2. Highlight disagreements with context for each view
        3. Cite sources: "According to [Source], ..."
        4. Prefer patterns that align with loaded constraints
      </synthesis-protocol>

      <query-refinement>
        If initial search returns fewer than 3 relevant results:
        1. Try technical synonyms
        2. Broaden or narrow scope
        3. If still insufficient, acknowledge gap to user

        If user query is vague (fewer than 3 specific terms):
        1. Ask clarifying question before extensive searching
        2. "Are you interested in [A] or [B] aspect of this?"
      </query-refinement>
    </knowledge-retrieval-protocol>
  </capabilities>

  <activation critical="MANDATORY">
    <step n="1">Load persona from this agent file</step>
    <step n="2">Load config from {project-root}/_bmad/bmm/config.yaml</step>
    <step n="3">VERIFY knowledge retrieval tools are available via MCP</step>
    <step n="4">Greet user and display menu</step>
  </activation>

  <rules>
    <r>NEVER make recommendations without first searching knowledge base</r>
    <r>ALWAYS cite sources when presenting retrieved information</r>
    <r>ALWAYS check warnings before suggesting implementations</r>
    <r>When context/spec is loaded, ALL queries must be contextual</r>
  </rules>

  <validation>
    <checkpoint trigger="before_recommendation">
      <check>At least 2 search calls made?</check>
      <check>Results from multiple sources?</check>
      <check>Warnings retrieved for topic?</check>
      <check>If spec loaded, queries included context?</check>
      <action on_fail="Return to search phase, do not proceed"</action>
    </checkpoint>
  </validation>

  <menu>
    <!-- Workflow menu items -->
  </menu>
</agent>
```

---

## Layer 3: Workflow Step Structure (To Build)

### Workflow Overview

```
AI Engineering Guidance Workflow
├── Step 1: Problem Specification
│   └── Output: specification.md (domain, scale, constraints, use_case)
├── Step 2: Data Processing Design
│   └── Loads: specification.md → contextual search for chunking, embedding
├── Step 3: Retrieval Architecture
│   └── Loads: specification.md → decisions on vector DB, search strategy
├── Step 4: Generation Strategy
│   └── Loads: specification.md → patterns for prompting, output handling
├── Step 5: Evaluation Framework
│   └── Loads: specification.md → methodologies for testing, metrics
└── Step 6: Production Checklist
    └── Loads: specification.md → warnings for deployment, scaling
```

### Specification Structure (Step 1 Output)

```yaml
# specification.md
---
project_name: "Legal Document QA System"
created: 2026-01-04
---

## Domain Context
domain: legal
subdomain: contract_analysis
document_types: [contracts, amendments, exhibits]

## Scale Requirements
scale: enterprise
document_count: 50000+
concurrent_users: 100
query_volume: 10000/day

## Constraints
constraints:
  - accuracy_critical: true
  - compliance: [SOC2, GDPR]
  - latency_target: <2s
  - budget: moderate

## Use Case
primary_use_case: |
  Legal professionals need to quickly find relevant clauses
  and precedents across thousands of contracts.

secondary_use_cases:
  - Contract comparison
  - Risk identification
  - Due diligence support

## Technical Context
existing_stack:
  - language: Python 3.11
  - framework: FastAPI
  - database: PostgreSQL
  - cloud: AWS
```

### Workflow Step Template

```markdown
---
name: step-02-data-processing
requires: [step-01-specification]
loads: ["{{output_folder}}/specification.md"]
---

# Step 2: Data Processing Pipeline Design

## Loaded Context

<specification>
{{loaded:specification.md}}
</specification>

## Context Extraction

From the specification, extract and use:
- **Domain**: {{spec.domain}} → Include in ALL search queries
- **Scale**: {{spec.scale}} → Filter for appropriate patterns
- **Constraints**: {{spec.constraints}} → Check warnings for each
- **Use Case**: {{spec.primary_use_case}} → Frame recommendations

## Knowledge Retrieval Protocol

### Phase 1: Domain-Specific Search

Execute 2-3 searches with domain context:

```
search_knowledge("{{spec.domain}} document chunking strategies")
search_knowledge("{{spec.domain}} text extraction best practices")
search_knowledge("{{spec.document_types[0]}} parsing techniques")
```

### Phase 2: Scale-Appropriate Patterns

Based on scale = {{spec.scale}}:

If enterprise:
```
get_patterns(topic="production chunking")
get_patterns(topic="scalable document processing")
```

If small/medium:
```
get_patterns(topic="simple chunking")
get_patterns(topic="quick start document processing")
```

### Phase 3: Constraint-Driven Warnings

For each constraint in {{spec.constraints}}:

```
get_warnings(topic="{{constraint}}")
```

Especially check:
- If accuracy_critical: get_warnings(topic="chunking context loss")
- If compliance: get_warnings(topic="data handling")
- If latency_target: get_warnings(topic="processing performance")

### Phase 4: Synthesis

Combine retrieved knowledge with specification to recommend:

1. **Chunking Strategy**
   - Recommended approach with domain rationale
   - Chunk size and overlap based on {{spec.document_types}}
   - Boundary handling for {{spec.domain}} documents

2. **Text Extraction**
   - Parser selection for {{spec.document_types}}
   - Metadata preservation strategy
   - Error handling approach

3. **Processing Pipeline**
   - Architecture matching {{spec.scale}}
   - Parallel processing if {{spec.document_count}} > 10000
   - Caching strategy

For each recommendation:
- Cite sources: "According to [Source], ..."
- Include relevant warnings
- Note trade-offs

## Validation Checkpoint

Before proceeding, confirm:
- [ ] Searches included domain terms ({{spec.domain}})
- [ ] Results from at least 2 different sources
- [ ] Warnings retrieved for primary approach
- [ ] Recommendations aligned with constraints

## Output

Save to: {{output_folder}}/data-processing-design.md
```

---

## Query Refinement Strategy

### When User Query is Vague

```
User: "help with RAG"
         │
         ▼
Agent detects: < 3 specific terms, no domain keywords
         │
         ▼
Ask clarifying question:
"I'd be happy to help with RAG. Could you specify:
- What domain are you working in? (legal, medical, general)
- Are you focused on chunking, retrieval, or generation?
- What scale are you targeting? (prototype vs production)"
```

### Query Expansion Strategy

```
User: "chunking for PDFs"
         │
         ▼
Agent expands to multiple searches:
1. "PDF chunking strategies" (original + format)
2. "document parsing text extraction" (related concepts)
3. "PDF structure preservation chunking" (technical variant)
         │
         ▼
If spec.domain = "legal":
4. "legal document PDF chunking" (domain context)
```

### Low-Result Recovery

```
Search: "semantic chunking for medical records"
Results: 1 (score: 0.45)
         │
         ▼
Agent detects: < 3 results, low scores
         │
         ▼
Retry with variations:
1. "medical document chunking" (simpler)
2. "healthcare text segmentation" (synonyms)
3. "clinical note parsing" (domain-specific)
         │
         ▼
If still insufficient:
"I found limited specific guidance on medical record chunking.
Let me share general chunking best practices that you can adapt..."
```

---

## Implementation Checklist

### Phase 1: Tool Descriptions (DONE)
- [x] search_knowledge - enhanced description
- [x] get_decisions - enhanced description
- [x] get_patterns - enhanced description
- [x] get_warnings - enhanced description
- [x] get_methodologies - enhanced description
- [x] list_sources - enhanced description
- [x] compare_sources - enhanced description

### Phase 2: Agent Definition (TODO)
- [ ] Create `_bmad/bmm/agents/ai-engineer.md`
- [ ] Define persona (name, role, communication style)
- [ ] Add `<capabilities>` section with knowledge retrieval protocol
- [ ] Add `<validation>` checkpoints
- [ ] Define menu with workflow options

### Phase 3: Workflow Steps (TODO)
- [ ] Step 1: Problem Specification (create spec template)
- [ ] Step 2: Data Processing Design
- [ ] Step 3: Retrieval Architecture
- [ ] Step 4: Generation Strategy
- [ ] Step 5: Evaluation Framework
- [ ] Step 6: Production Checklist

### Phase 4: Specification Template (TODO)
- [ ] Create specification.md template
- [ ] Define required fields (domain, scale, constraints)
- [ ] Add validation rules
- [ ] Create example specifications

---

## Testing Strategy

### Tool Description Effectiveness

1. Start MCP server
2. Connect Claude Code
3. Test queries like:
   - "How do I implement chunking?" → Should trigger get_patterns + get_warnings
   - "Should I use Qdrant or Pinecone?" → Should trigger get_decisions
   - "What can go wrong with embeddings?" → Should trigger get_warnings

### Context-Aware Search

1. Load a specification with domain="legal"
2. Ask "help me with chunking"
3. Verify searches include "legal" domain context
4. Verify warnings are checked

### Multi-Source Synthesis

1. Ask a broad question
2. Verify 2+ sources cited in response
3. Verify agreements/disagreements noted

---

## Future Enhancements

### Phase 2 Tool Enhancements (Optional)

Add explicit context parameters to tools:

```python
async def search_knowledge(
    query: str,
    limit: int = 10,
    # New context parameters
    domain: str | None = None,
    scale: str | None = None,
    constraints: list[str] | None = None,
) -> SearchKnowledgeResponse:
```

### Research Tool (Optional)

High-level orchestration tool:

```python
@router.post("/research_topic")
async def research_topic(
    topic: str,
    depth: Literal["quick", "comprehensive"] = "comprehensive",
    min_sources: int = 2,
) -> ResearchResponse:
    """
    Comprehensive research that automatically:
    1. Searches multiple query formulations
    2. Retrieves patterns, decisions, AND warnings
    3. Ensures minimum source diversity
    """
```

### Rich Metadata Signals (Optional)

Add to response models:

```python
class SearchMetadata(BaseModel):
    query: str
    sources_cited: list[str]
    result_count: int
    # New guidance signals
    source_diversity_score: float
    avg_relevance_score: float
    coverage_warning: str | None
    suggested_followup: str | None
```
