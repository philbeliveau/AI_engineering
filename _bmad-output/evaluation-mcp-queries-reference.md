# Knowledge MCP Query Reference for Evaluation Timing

## Overview

This document provides a practical reference for using the Knowledge MCP to research evaluation placement, methods, and anti-patterns. It shows which queries to run and what to expect from each.

**Live MCP Server:** https://knowledge-mcp-production.up.railway.app/mcp

---

## Query Set 1: Understanding Evaluation Placement

### Query 1.1: Search for Evaluation Placement Guidance

**Tool:** `search_knowledge`

```bash
Query: "evaluation placement phases integration timing when"
Limit: 10-15
Purpose: Understand when evaluation should happen
```

**Expected Results:**
- Chunk results from methodology books
- Extraction results (decisions, patterns, warnings)
- Mix of discussion on integrated vs gate-based evaluation
- References to quality checkpoints

**What to Look For:**
- Does evaluation happen during or after development?
- Are there multiple evaluation phases?
- When is the "go/no-go" decision made?
- Examples of evaluation timelines

**Example Result Structure:**
```json
{
  "results": [
    {
      "id": "qdrant_point_id",
      "score": 0.85,
      "type": "chunk|extraction",
      "content": "...",
      "source": {
        "title": "Building LLM Applications",
        "authors": ["Author Name"],
        "position": {
          "chapter": 5,
          "section": "Evaluation Strategy",
          "page": 143
        }
      }
    }
  ],
  "metadata": {
    "query": "evaluation placement phases integration timing when",
    "sources_cited": ["Building LLM Applications", "Designing ML Systems", ...],
    "result_count": 12,
    "latency_ms": 245
  }
}
```

---

### Query 1.2: Get Evaluation Decisions

**Tool:** `get_decisions`

```bash
Topic: "evaluation"
Limit: 20
Purpose: Understand trade-offs in evaluation approaches
```

**Expected Results:**
- Decision objects with questions like:
  - "When should evaluation happen: during or after development?"
  - "Should evaluation be continuous or at a gate?"
  - "How many evaluation methods should we use?"
  - "Should we use LLM-as-judge for evaluation?"

**Structure of Each Decision Result:**
```json
{
  "id": "decision_123",
  "question": "When should quality evaluation occur relative to system deployment?",
  "options": [
    "Integrated throughout development",
    "Formal gate before deployment",
    "Post-deployment monitoring only",
    "Multiple phases: integrated + gate + monitoring"
  ],
  "considerations": [
    "Early evaluation provides faster feedback but may not catch everything",
    "Late evaluation risks discovering showstopper issues after system complete",
    "Production monitoring is essential but shouldn't be only evaluation",
    "Multiple phases allow risk mitigation at each stage"
  ],
  "recommended_approach": "Multiple phases: lightweight integrated testing during development, formal quality gate before deployment, production monitoring after",
  "topics": ["evaluation", "quality-gates", "llm-ops"],
  "source_title": "Designing ML Systems",
  "source_id": "source_456"
}
```

**What to Extract:**
- Pattern of multiple evaluation phases
- Trade-offs between speed and rigor
- Risk mitigation at each stage

---

## Query Set 2: Evaluation Methods & Methodologies

### Query 2.1: Get Evaluation Methodologies

**Tool:** `get_methodologies`

```bash
Topic: "evaluation"
Limit: 5-10
Purpose: Learn step-by-step evaluation processes
```

**Expected Results:**
- Methodology objects with:
  - Name: e.g., "RAG System Evaluation Methodology"
  - Steps: Ordered sequence (7-12 steps typically)
  - Prerequisites: What you need before starting
  - Outputs: What you'll have when done

**Structure of Each Methodology:**
```json
{
  "id": "methodology_789",
  "name": "RAG System Evaluation Framework",
  "steps": [
    {
      "number": 1,
      "title": "Define Evaluation Criteria",
      "description": "Establish functional and non-functional requirements",
      "inputs": ["Quality targets from scoping"],
      "outputs": ["Evaluation criteria document"],
      "duration": "1-2 days"
    },
    {
      "number": 2,
      "title": "Design Test Datasets",
      "description": "Create golden set, edge cases, adversarial examples",
      "inputs": ["Domain knowledge", "User scenarios"],
      "outputs": ["200+ test examples (human-verified)"],
      "duration": "3-5 days"
    },
    {
      "number": 3,
      "title": "Evaluate Retrieval Layer",
      "description": "Measure Recall@K, Precision@K, MRR, NDCG",
      "inputs": ["Test dataset", "Retrieval system"],
      "outputs": ["Retrieval metrics"],
      "duration": "4 hours"
    },
    {
      "number": 4,
      "title": "Evaluate Generation Layer",
      "description": "Measure faithfulness, hallucination, relevance",
      "inputs": ["Test Q&A pairs", "Retrieved context"],
      "outputs": ["Generation metrics"],
      "duration": "8 hours"
    },
    {
      "number": 5,
      "title": "Make Gate Decision",
      "description": "Compare metrics against thresholds, decide GO/NO-GO",
      "inputs": ["All evaluation results"],
      "outputs": ["Quality gate decision document"],
      "duration": "1 day"
    }
  ],
  "prerequisites": [
    "Phases 1-3 complete (feature, training, inference pipelines designed)",
    "Quality targets defined",
    "Test data identified or procurement planned"
  ],
  "outputs": [
    "evaluation-spec.md with all criteria",
    "Test dataset (200+ examples)",
    "Evaluation results with all metrics",
    "Quality gate decision (GO/NO-GO/CONDITIONAL)"
  ],
  "topics": ["evaluation", "quality-gates", "rag"],
  "source_title": "LLM Engineer's Handbook"
}
```

**What to Extract:**
- Step-by-step process
- Duration expectations
- Specific metrics to measure
- Decision-making criteria

---

### Query 2.2: Get Evaluation Patterns

**Tool:** `get_patterns`

```bash
Topic: "evaluation"
Limit: 10-20
Purpose: Learn implementation patterns for evaluation
```

**Expected Results:**
- Pattern objects with:
  - Name: "LLM-as-Judge Evaluation Pattern"
  - Problem: What situation this solves
  - Solution: How to implement it
  - Code examples: Working implementations
  - Trade-offs: What you gain/lose

**Structure of Each Pattern:**
```json
{
  "id": "pattern_012",
  "name": "Multi-Layer RAG Evaluation",
  "problem": "How do you know if failures are from retrieval or generation?",
  "solution": "Separate evaluation into retrieval metrics, generation metrics, and end-to-end metrics. Debug each layer independently.",
  "code_example": {
    "language": "python",
    "implementation": "def evaluate_rag_system():\n    # Retrieval layer\n    retrieval_metrics = evaluate_retrieval(...)\n    # Generation layer\n    generation_metrics = evaluate_generation(...)\n    # End-to-end\n    e2e_metrics = evaluate_end_to_end(...)\n    return combine_results(...)"
  },
  "context": "Useful for RAG systems with separate retrieval and generation components",
  "trade_offs": "Requires 3x the evaluation infrastructure but enables targeted debugging",
  "topics": ["evaluation", "rag", "metrics", "debugging"],
  "source_title": "Building LLM Applications"
}
```

**What to Extract:**
- Concrete implementation approach
- Code you can adapt
- Trade-offs to consider

---

## Query Set 3: Warnings and Anti-Patterns

### Query 3.1: Get Evaluation Warnings

**Tool:** `get_warnings`

```bash
Topic: "evaluation"
Limit: 15-20
Purpose: Learn evaluation pitfalls to avoid
```

**Expected Results:**
- Warning objects with:
  - Title: e.g., "LLM-as-Judge Position Bias"
  - Description: What the problem is
  - Symptoms: How to recognize it
  - Consequences: What goes wrong if ignored
  - Prevention: How to avoid it

**Structure of Each Warning:**
```json
{
  "id": "warning_345",
  "title": "Circular Evaluation Bias in LLM Systems",
  "description": "Using LLM-generated data for training and evaluation creates circular bias - the model optimizes for its own outputs rather than real-world quality.",
  "symptoms": [
    "Test accuracy very high but production accuracy much lower",
    "LLM consistently prefers its own outputs over alternatives",
    "Metrics improve but users report no quality improvement"
  ],
  "consequences": [
    "False confidence in system readiness",
    "Production failures after gate approval",
    "Wasted time optimizing the wrong thing"
  ],
  "prevention": [
    "Source test data from humans, not LLM",
    "If using LLM for generation, use different model for evaluation",
    "Include human evaluation spot checks for validation",
    "Compare against external benchmarks"
  ],
  "topics": ["evaluation", "bias", "llm-as-judge", "testing"],
  "source_title": "Designing ML Systems"
}
```

**What to Extract:**
- Specific pitfalls relevant to your approach
- Symptoms to watch for
- Concrete prevention strategies

---

### Query 3.2: Specific Bias Warnings for LLM-as-Judge

**Tool:** `search_knowledge`

```bash
Query: "LLM judge evaluation bias position verbosity self-preference"
Limit: 10-15
Purpose: Understand and mitigate LLM-as-judge biases
```

**Expected Results:**
- References to:
  - Position bias (prefers first/last options)
  - Verbosity bias (prefers longer responses)
  - Self-preference bias (prefers its own outputs)
  - Sycophancy bias (agrees with user opinions)
  - Mitigation strategies for each

**What to Look For:**
- Specific bias examples
- How to detect each bias in results
- Mitigation techniques (randomization, normalization, etc.)

---

### Query 3.3: Evaluation Pitfalls Specific to RAG

**Tool:** `search_knowledge`

```bash
Query: "RAG evaluation pitfalls retrieval generation hallucination"
Limit: 10-15
Purpose: Learn RAG-specific evaluation mistakes
```

**Expected Results:**
- References to:
  - Forgetting to evaluate retrieval separately
  - Confusing retrieval and generation failures
  - Hallucination detection challenges
  - Citation accuracy importance

**What to Look For:**
- Layer-specific metrics and how to set thresholds
- Common confusion points between retrieval and generation
- How to distinguish "bad retrieval" from "bad generation"

---

## Query Set 4: Specific Decision Support

### Query 4.1: Should We Use LLM-as-Judge?

**Tool:** `get_decisions`

```bash
Topic: "evaluation"
Filter: Search results for "judge" or "llm-as-judge"
Purpose: Get decision framework for using LLM-as-judge
```

**Expected Decision Format:**
```
Question: "Should we use LLM-as-judge or human evaluation?"

Options:
1. Automated metrics only (ROUGE, BLEU, embedding similarity)
   - Pros: Fast, no human effort
   - Cons: May not capture nuance

2. LLM-as-judge with bias mitigation
   - Pros: Scales to large datasets, captures nuance
   - Cons: Requires careful implementation, bias risks

3. Human evaluation only
   - Pros: Ground truth, catches subtle issues
   - Cons: Expensive, slow, subjective

4. Hybrid (LLM-as-judge + human sample validation)
   - Pros: Scales + validates quality
   - Cons: Most effort, but best results

Considerations:
- Budget constraints?
- Timeline?
- Precision requirements?
- Whether evaluation is blocking deployment?
```

---

### Query 4.2: What Metrics Should We Use?

**Tool:** `get_patterns`

```bash
Topic: "evaluation"
Filter: Search results for "metrics" or "evaluation metrics"
Purpose: Find recommended metrics by system type
```

**Expected Pattern Results:**
```
For RAG Systems:

Retrieval Metrics:
├─ Recall@K (recommended: >= 80%)
├─ Precision@K (recommended: >= 60%)
├─ MRR: Mean Reciprocal Rank (recommended: >= 0.5)
└─ NDCG: Normalized DCG (recommended: >= 0.7)

Generation Metrics:
├─ Faithfulness (recommended: >= 90%)
├─ Hallucination rate (recommended: < 5%)
├─ Relevance (recommended: >= 85%)
└─ Citation accuracy (recommended: >= 90%)

End-to-End Metrics:
├─ Accuracy (recommended: >= 85%)
└─ User satisfaction (when available)
```

---

## Query Set 5: Creating Your Evaluation Plan

### Recommended Query Sequence

For a new AI system, execute queries in this order:

**Week 1: Understanding the Landscape**
1. `search_knowledge("evaluation placement phases integration")`
   - Understand when evaluation happens
   - See examples from multiple sources

2. `get_decisions(topic="evaluation")`
   - Understand trade-offs
   - See recommended approaches

**Week 2: Learning Evaluation Methods**
3. `get_methodologies(topic="evaluation")`
   - Get step-by-step process
   - See what outputs you need

4. `get_patterns(topic="evaluation")`
   - Learn implementation patterns
   - See code examples

**Week 3: Avoiding Pitfalls**
5. `get_warnings(topic="evaluation")`
   - Understand evaluation pitfalls
   - Learn prevention strategies

6. `search_knowledge("LLM judge evaluation bias mitigation")`
   - If using LLM-as-judge, learn biases
   - Get mitigation strategies

**Week 4: Making Specific Decisions**
7. `search_knowledge("[YOUR_SYSTEM_TYPE] evaluation metrics")`
   - Replace [YOUR_SYSTEM_TYPE] with "RAG" or "fine-tuning"
   - Get system-specific metrics

8. `get_methodologies(topic="[your domain]")`
   - If applicable, get domain-specific evaluation guidance

---

## Query Results Interpretation Guide

### High-Quality Results (Score > 0.7)
- Directly relevant to your query
- Use as foundation for your plan
- Extract specific recommendations

### Medium-Quality Results (Score 0.5-0.7)
- Tangentially relevant
- May provide context
- Use to fill gaps in understanding

### Low-Quality Results (Score < 0.5)
- Consider re-querying with different terms
- Or using different search strategy

### Synthesis Workflow

```
┌─────────────────────────────────────────────┐
│ Run Query Set                               │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Collect Results (20-40 total)              │
│ Sort by score                              │
│ Filter to high-confidence results          │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Identify Patterns                          │
│ - Common recommendations                   │
│ - Consistent warnings                      │
│ - Trade-offs mentioned repeatedly          │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Synthesize Insights                        │
│ - What do sources agree on?                │
│ - Where do they disagree?                  │
│ - What's specific to your domain?          │
└──────────────┬──────────────────────────────┘
               ↓
┌─────────────────────────────────────────────┐
│ Apply to Your Project                      │
│ - Adapt patterns to your constraints       │
│ - Address specific warnings                │
│ - Follow recommended methodology           │
└─────────────────────────────────────────────┘
```

---

## Cheat Sheet: Query Templates

Copy and adapt these for your specific project:

### Query Template 1: Understanding Your System Type
```
search_knowledge("[RAG|fine-tuning|prompt-engineering] evaluation methodology")
```

### Query Template 2: Finding Metrics for Your Domain
```
search_knowledge("[YOUR_DOMAIN] evaluation metrics quality assessment")
```

### Query Template 3: Learning About Specific Method
```
search_knowledge("[METHOD_NAME] evaluation implementation pattern code")
```

### Query Template 4: Understanding Risks
```
get_warnings(topic="[YOUR_SYSTEM_TYPE]")
```

### Query Template 5: Decision Support
```
get_decisions(topic="[evaluation|quality-gates|testing]")
```

### Query Template 6: Step-by-Step Process
```
get_methodologies(topic="[evaluation|quality-gates]")
```

---

## What NOT to Query the MCP For

The Knowledge MCP is great for patterns, but NOT for:

**Don't Query For:**
- Specific metric values for your project (domain-specific)
  - Example: ❌ "What accuracy target should I use?"
  - Instead: ✓ Use recommendations as starting point, adjust for your requirements

- Actual evaluation execution guidance
  - Example: ❌ "Run my evaluation for me"
  - Instead: ✓ Implement patterns from MCP results yourself

- Test dataset content
  - Example: ❌ "Generate test examples for my domain"
  - Instead: ✓ Use MCP guidance on dataset design, create examples yourself

- Final go/no-go decisions
  - Example: ❌ "Should we deploy this system?"
  - Instead: ✓ Use MCP + your specific requirements for decision-making

---

## Integration with AI Engineering Workflow

The AI Engineering Workflow (Step 8: LLM Evaluator) implements this MCP query strategy:

1. **Welcome to Evaluation**
   - Explain evaluation phase

2. **Query Knowledge MCP** (mandatory)
   - `get_warnings(topic="evaluation")`
   - `search_knowledge("LLM judge evaluation bias pitfalls")`
   - `get_methodologies(topic="evaluation")`
   - `search_knowledge("model evaluation metrics benchmark")`

3. **Synthesize Insights**
   - Extract anti-patterns
   - Identify recommended practices
   - Surface critical warnings

4. **Design Evaluation Framework**
   - Use MCP insights
   - Adapt to your specific project
   - Document decisions

5. **Execute Evaluation**
   - Follow methodology from MCP
   - Implement patterns from MCP results
   - Track against thresholds

6. **Make Quality Gate Decision**
   - Document all decision points
   - Reference MCP sources as rationale
   - Update project sidecar with decisions

---

## Success Criteria for MCP Integration

You've successfully used the Knowledge MCP for evaluation planning if:

✅ You understand evaluation happens in multiple phases
✅ You know specific anti-patterns to avoid
✅ You have concrete metrics to measure
✅ You understand LLM-as-judge biases (if using)
✅ You have a methodology to follow
✅ You know layer-specific evaluation (if RAG)
✅ You can explain your evaluation plan to stakeholders
✅ You have backup from literature for your decisions

---

## References

**Live Knowledge MCP Server:**
```
https://knowledge-mcp-production.up.railway.app/mcp
```

**Claude Configuration (if available):**
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

**Available Extraction Types in Knowledge Base:**
- Decisions (356 total, ~25-30 evaluation-related)
- Warnings (335 total, ~20-25 evaluation-related)
- Patterns (314 total, ~15-20 evaluation-related)
- Methodologies (182 total, ~10-15 evaluation-related)
- Workflows (187 total, ~5-10 evaluation-related)

**Search as a Fallback:**
If specific topic queries don't return results, use broader search with relevant keywords.
