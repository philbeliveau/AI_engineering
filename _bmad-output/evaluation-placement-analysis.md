# Evaluation Placement in AI Engineering Systems

## Executive Summary

Based on analysis of the Knowledge Pipeline MCP, AI Engineering Workflow, and literature patterns, evaluation placement follows a **multi-phase, integrated approach** rather than a single "before vs after" decision. The architecture distinguishes between:

1. **Continuous evaluation** (integrated during development)
2. **Quality gate evaluation** (explicit checkpoint before deployment)
3. **Production monitoring** (post-deployment feedback loops)

This document synthesizes findings from the knowledge base through the MCP server architecture and recommended patterns.

---

## 1. WHAT THE LITERATURE SAYS ABOUT EVALUATION TIMING

### Core Principle: Evaluation is NOT a Single Event

The AI Engineering Workflow structures evaluation as **Phase 4** - a distinct but integrated phase that:
- Executes AFTER feature, training (optional), and inference pipelines are designed
- Creates gate between design and deployment
- Serves as quality checkpoint for operational readiness

### Available MCP Query Endpoints

The Knowledge MCP provides four tools for evaluation queries:

```
- search_knowledge: Semantic search (e.g., "evaluation placement phases integration")
- get_decisions: Architectural decisions about evaluation choices
- get_patterns: Implementation patterns for evaluation methodologies
- get_warnings: Anti-patterns and pitfalls in evaluation design
- get_methodologies: Step-by-step evaluation processes
```

### What Sources Recommend

From the workflow's mandatory query patterns in Step 8 (LLM Evaluator):

**Query 1: Evaluation Warnings**
```
Endpoint: get_warnings
Topic: "evaluation"
Surfaces: Anti-patterns, LLM-as-judge biases, circular evaluation risks
```

**Query 2: LLM Judge Patterns**
```
Endpoint: search_knowledge
Query: "LLM judge evaluation bias pitfalls"
Surfaces: Position bias, verbosity bias, self-preference bias mitigation
```

**Query 3: Evaluation Methodologies**
```
Endpoint: get_methodologies
Topic: "evaluation"
Surfaces: Step-by-step evaluation processes, prerequisites, outputs
```

**Key Anti-Patterns to Avoid:**
> Using LLM-generated test data to evaluate LLM systems (creates circular bias)

---

## 2. TRADE-OFFS: INTEGRATED EVALUATION VS GATE-BASED EVALUATION

### A. Integrated Evaluation (During Development)

**Where It Happens:**
- During Phase 3 (Inference Pipeline design)
- Developer runs quick manual tests
- Prototype evaluation against golden examples
- Informal A/B testing during iteration

**Advantages:**
- Fast feedback loop - developers know if changes help/hurt
- Low friction - no formal process needed
- Catches obvious failures early
- Informs design decisions in real-time

**Disadvantages:**
- Subjective and informal
- Not reproducible
- Doesn't catch subtle degradations
- Test data often biased toward current approach

**Example:** Prompt engineer tweaks system message, quickly tests against 10 examples to see if accuracy improves

---

### B. Quality Gate Evaluation (Phase 4)

**Where It Happens:**
- Explicitly after all pipelines designed
- Before deployment authorization
- Rigorous, documented, reproducible
- Uses pre-defined test datasets and metrics

**Advantages:**
- Formal, auditable quality assessment
- Catches subtle regressions
- Establishes performance baseline
- Creates deployment gate/checkpoint
- Defensible to stakeholders
- Enables rollback decisions

**Disadvantages:**
- Late feedback (post-design)
- Can reveal major issues too late
- Requires significant test data preparation
- More expensive (compute + human effort)

**Example:** Quality gate checklist requires Accuracy >= 85%, Latency P99 <= 500ms, and no hallucinations on golden set before deployment approval

---

### C. Production Monitoring (Phase 5+)

**Where It Happens:**
- After deployment to real users
- Continuous metric tracking
- Alert on regressions
- User feedback loops

**Advantages:**
- Real-world performance signal
- Catches deployment-specific issues
- Enables continuous improvement
- User satisfaction metrics

**Disadvantages:**
- Affects real users first
- Recovery requires rollback/hotfix
- Delays problem detection

**Example:** Production dashboard shows accuracy dropping 2% over past week → triggers incident response

---

## 3. ARCHITECTURE PATTERN: THE THREE-LAYER APPROACH

The AI Engineering Workflow implements a three-layer evaluation architecture:

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: INTEGRATED (Continuous, during development)    │
├─────────────────────────────────────────────────────────┤
│ • Manual testing during iteration                        │
│ • Quick feedback (<5 min per test)                       │
│ • Informal metrics (spot checks)                         │
│ • Guides design decisions                               │
│ • Rule: Keep test sets small and representative         │
└─────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 2: QUALITY GATE (Phase 4, explicit checkpoint)    │
├─────────────────────────────────────────────────────────┤
│ • Formal evaluation against golden dataset               │
│ • Structured metrics with thresholds                    │
│ • Multiple evaluation methods                           │
│ • GO/NO-GO decision point                              │
│ • Document all results for audit trail                  │
│ • Rule: All criteria must be explicit and measurable    │
└─────────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ Layer 3: PRODUCTION (Phase 5+, continuous monitoring)   │
├─────────────────────────────────────────────────────────┤
│ • Real-time metric dashboards                           │
│ • Alert thresholds matched to quality gate targets      │
│ • User feedback collection                              │
│ • Regression detection                                  │
│ • Rule: Monitor production against baseline              │
└─────────────────────────────────────────────────────────┘
```

---

## 4. KEY PATTERNS FROM KNOWLEDGE BASE

### Pattern 1: Multi-Method Evaluation Strategy

From the workflow's evaluation step design (Step 8):

**Automated Methods:**
| Method | Use Case | Limitations |
|--------|----------|-------------|
| Exact Match | Factual QA | Too strict for generation |
| ROUGE/BLEU | Summarization | Doesn't capture meaning |
| Embedding Similarity | Semantic matching | Misses nuance |
| LLM-as-Judge | General quality | Bias risk (see warnings) |
| Custom Rubrics | Domain-specific | Requires design effort |

**Human Evaluation Methods:**
| Method | Use Case | Effort |
|--------|----------|--------|
| A/B Testing | Compare versions | Medium |
| Likert Scoring | Subjective quality | Low |
| Pairwise Comparison | Ranking responses | Medium |
| Expert Review | Domain accuracy | High |

**Key Insight:**
> No single metric captures quality. Use 2-3 complementary methods.

---

### Pattern 2: RAG-Specific Evaluation Layers

For retrieval-augmented generation systems, evaluation splits:

**Layer A: Retrieval Quality (before generation)**
- Metric: Recall@K (relevant docs in top K)
- Target: >80%
- Measures: Retrieval pipeline quality in isolation

**Layer B: Generation Quality (with context)**
- Metric: Faithfulness (answer grounded in context)
- Metric: Hallucination rate (answer diverges from sources)
- Target: >90% faithful, <5% hallucination
- Measures: Generation behavior WITH retrieved context

**Layer C: End-to-End Quality**
- Metric: Accuracy (correct answer provided)
- Metric: Citation accuracy (sources correct)
- Target: >85% accuracy, >90% citation accuracy
- Measures: Full system performance on golden Q&A pairs

**Why Three Layers?**
- Layer A failure → fix retrieval strategy
- Layer B failure → fix prompt/model
- Layer C failure → fix combination or gather more data

---

### Pattern 3: LLM-as-Judge Configuration with Bias Mitigation

**Warning:** LLM-as-judge introduces biases (position, verbosity, self-preference)

**Recommended Mitigations:**
```yaml
llm_judge:
  enabled: true
  model: "[different model from system model]"  # Avoid self-preference bias
  rubric_file: "evaluation-rubric.md"
  mitigations:
    - randomize_position                         # Avoid position bias
    - length_normalization                       # Avoid verbosity bias
  calibration:
    human_agreement_target: ">80%"              # Validate against humans
```

**Key Pattern:**
> Never use the same model that generates answers to judge its own quality.

---

### Pattern 4: Test Dataset Design

**Critical Warning (from knowledge base):**
> Avoid using LLM-generated test data to evaluate LLM systems - this creates circular bias.

**Recommended Test Dataset Types:**

| Dataset Type | Size | Purpose | Source |
|--------------|------|---------|--------|
| **Golden Set** | 50-100 | High-quality baseline | Manual curation |
| **Edge Cases** | 20-50 | Boundary conditions | Domain expert |
| **Adversarial** | 10-30 | Attack resistance | Red teaming |
| **Domain Coverage** | 100+ | All use case categories | Sampled from real queries (human-verified) |

**Total Test Budget:** ~200-300 examples for thorough evaluation

---

## 5. QUALITY GATE STRUCTURE (THE DECISION POINT)

The workflow defines three evaluation outcomes at the quality gate:

### Option 1: GO
**Criteria Met:**
- All functional criteria >= threshold
- All non-functional criteria met
- No critical failures in golden set
- Safety validation passed

**Action:** Proceed to Phase 5 (Operations/Deployment)

### Option 2: CONDITIONAL GO
**Criteria Met:**
- Most criteria met
- Minor issues identified
- Mitigations in place
- Acceptable risk documented

**Action:** Proceed with monitoring + post-deployment fixes

### Option 3: NO-GO
**Criteria Not Met:**
- Critical criteria failed
- Showstopper issues
- Mitigations not feasible

**Action:** Return to relevant phase for fixes, reschedule evaluation

---

## 6. ANTI-PATTERNS: WHAT THE LITERATURE WARNS AGAINST

### Anti-Pattern 1: Evaluation Too Late
**Problem:**
- Evaluate only after full system built
- Discover major issues requiring re-architecture
- Stakeholder disappointment

**Solution:**
- Integrate evaluation throughout development
- Quality gate just documents what's already tested

### Anti-Pattern 2: Using Single Metric
**Problem:**
- Optimize for one metric, break others
- Miss important quality dimensions
- False confidence in readiness

**Solution:**
- Use balanced scorecard approach
- Require multiple correlated metrics

### Anti-Pattern 3: Circular Evaluation Bias
**Problem:**
- Use LLM to generate test data
- Use same LLM to evaluate test data
- System optimizes for its own outputs

**Solution:**
- Test data from domain experts or production examples
- Evaluation judge different from system model
- Regular human review of edge cases

### Anti-Pattern 4: Ignoring Retrieval-Generation Split
**Problem:**
- Test "accuracy" without checking if retrieval works
- Blame generation quality for retrieval failures
- Fix wrong component

**Solution:**
- Separate retrieval metrics (Recall@K, NDCG)
- Separate generation metrics (faithfulness, hallucination)
- Debug each layer independently

### Anti-Pattern 5: Static Test Data
**Problem:**
- Create golden set once
- Never update as system evolves
- Regression detection fails

**Solution:**
- Versioned test datasets
- Regular additions as new edge cases discovered
- Track test data changes in decision log

---

## 7. RECOMMENDED WORKFLOW SEQUENCE

Based on the AI Engineering Workflow structure:

```
Phase 0: Scoping
  ↓
  Define success metrics
  Define quality targets
  Document stakeholder requirements

Phase 1: Feature Pipeline (Data & Chunking)
  ↓
  Integrated evaluation: spot-check data quality

Phase 2: Training Pipeline (optional, for fine-tuning)
  ↓
  Integrated evaluation: model convergence, loss trends

Phase 3: Inference Pipeline (RAG + Prompts)
  ↓
  Integrated evaluation: quick manual testing

Phase 4: EVALUATION (Quality Gate)
  ↓
  └─ Query Knowledge MCP for best practices
  ├─ Design evaluation framework
  │   ├─ Functional criteria (accuracy, relevance, etc.)
  │   ├─ Non-functional criteria (latency, cost, etc.)
  │   ├─ Test categories (unit, integration, E2E)
  │   ├─ Test datasets (golden, edge cases, adversarial)
  │   └─ Evaluation methods (automated + human)
  │
  ├─ Execute evaluation
  │   ├─ Retrieval metrics (if RAG)
  │   ├─ Generation metrics
  │   ├─ End-to-end metrics
  │   └─ Document all results
  │
  └─ Quality Gate Decision
      ├─ GO → proceed to Phase 5
      ├─ CONDITIONAL GO → proceed with conditions
      └─ NO-GO → return to Phase 3 for fixes

Phase 5: Operations (Deployment & Monitoring)
  ↓
  Set up production metrics
  Configure alerts
  Establish monitoring baseline

Phase 6+: Production Feedback Loops
  ↓
  Monitor against quality gate targets
  Detect regressions
  Update test datasets from production insights
```

---

## 8. CURRENT IMPLEMENTATION IN KNOWLEDGE PIPELINE MCP

### MCP Tool Design Pattern

The MCP server implements four query tools for evaluation guidance:

**1. search_knowledge() - Semantic Search**
```python
# Query structure for evaluation topic
query = "evaluation placement phases integration"
results = search_knowledge(query=query, limit=10)
# Returns: Ranked results from all sources mentioning evaluation timing
```

**2. get_decisions() - Decision Points**
```python
# Query evaluation-related decisions
results = get_decisions(topic="evaluation", limit=20)
# Returns: Decision objects with:
#   - question: "When should evaluation happen?"
#   - options: [integrated, gate-based, post-deployment]
#   - considerations: trade-offs for each option
#   - recommended_approach: based on literature consensus
```

**3. get_warnings() - Anti-Patterns**
```python
# Query evaluation pitfalls
results = get_warnings(topic="evaluation", limit=20)
# Returns: Warning objects with:
#   - title: Anti-pattern name
#   - description: What goes wrong
#   - symptoms: How to recognize it
#   - prevention: How to avoid it
```

**4. get_patterns() - Implementation Patterns**
```python
# Query evaluation implementation approaches
results = get_patterns(topic="evaluation", limit=20)
# Returns: Pattern objects with:
#   - name: Pattern name
#   - problem: What situation it solves
#   - solution: How to implement
#   - code_example: Working implementation
```

### Knowledge Base Content

Current extraction statistics show 1,684+ extractions covering:

| Type | Count | Evaluation-Relevant |
|------|-------|-------------------|
| Decisions | 356 | ~25-30 (evaluation placement, methodology choice) |
| Warnings | 335 | ~20-25 (evaluation pitfalls, bias risks) |
| Patterns | 314 | ~15-20 (evaluation framework design, metrics) |
| Methodologies | 182 | ~10-15 (step-by-step evaluation processes) |
| Workflows | 187 | ~5-10 (evaluation integration in ML systems) |

---

## 9. SYNTHESIS: RECOMMENDED EVALUATION PLACEMENT

### For RAG Systems (Most Common)

**Phase 4 Quality Gate Includes:**

```markdown
## Evaluation Layers (In Sequence)

1. **Retrieval Layer Evaluation**
   - Metric: Recall@5 >= 80%
   - Dataset: 100+ diverse queries with golden passages
   - Method: Automated vector similarity matching
   - Timing: 30 minutes execution

2. **Generation Layer Evaluation**
   - Metrics: Faithfulness >= 90%, Hallucination < 5%
   - Dataset: 50 Q&A pairs with expected answers
   - Method: LLM-as-judge + manual spot check
   - Timing: 1-2 hours execution

3. **End-to-End Evaluation**
   - Metrics: Accuracy >= 85%, Citation Accuracy >= 90%
   - Dataset: 50 golden Q&A pairs (human verified)
   - Method: A/B comparison, human review of edge cases
   - Timing: 2-4 hours execution

4. **Safety Evaluation**
   - Metrics: No hallucinations on adversarial tests
   - Dataset: 20-30 adversarial examples
   - Method: Manual red-team + automated checks
   - Timing: 1-2 hours execution

## Quality Gate Checklist
- [ ] Retrieval layer metrics met
- [ ] Generation layer metrics met
- [ ] End-to-end metrics met
- [ ] Safety tests passed
- [ ] No critical failures in golden set
- [ ] Latency P99 < 500ms
- [ ] Cost per query < $0.01
- [ ] Decision log updated
- [ ] All decisions documented

## Gate Decision
- [ ] GO (all criteria met)
- [ ] CONDITIONAL (minor issues, mitigations documented)
- [ ] NO-GO (critical failures, return to Phase 3)
```

---

### For Fine-Tuned Systems

**Phase 2 Training Adds:**
- Validation loss tracking during training
- Hold-out test set (never seen during training)
- Integrated testing: monitor convergence

**Phase 4 Quality Gate Includes:**
- All RAG layers PLUS
- Model-specific metrics (perplexity, task-specific benchmarks)
- Comparison to baseline (pre-fine-tune)
- Fairness/bias evaluation

---

## 10. CRITICAL SUCCESS FACTORS

### DO:
1. ✅ Integrate light evaluation throughout development
2. ✅ Create formal quality gate before deployment
3. ✅ Use multiple evaluation methods (automated + human)
4. ✅ Separate retrieval and generation evaluation
5. ✅ Mitigate LLM-as-judge biases
6. ✅ Use human-curated test data
7. ✅ Document all gate decisions
8. ✅ Monitor production against gate targets

### DON'T:
1. ❌ Evaluate only after system complete
2. ❌ Use single metric for quality assessment
3. ❌ Use LLM-generated test data
4. ❌ Evaluate generation without checking retrieval
5. ❌ Use same model for evaluation and generation
6. ❌ Skip formal quality gate
7. ❌ Deploy without documented decision
8. ❌ Stop monitoring after deployment

---

## 11. REFERENCES TO KNOWLEDGE MCP

### To Implement This Architecture:

**Query 1: Understand evaluation timing best practices**
```
Endpoint: search_knowledge
Query: "evaluation placement phases integration RAG system"
Expected: Examples of when evaluation should occur
```

**Query 2: Make evaluation methodology decision**
```
Endpoint: get_decisions
Topic: "evaluation"
Expected: Options and trade-offs for evaluation approach
```

**Query 3: Learn evaluation implementation patterns**
```
Endpoint: get_patterns
Topic: "evaluation"
Expected: How to design evaluation framework, metrics, test data
```

**Query 4: Avoid evaluation pitfalls**
```
Endpoint: get_warnings
Topic: "evaluation"
Expected: Anti-patterns, biases, common mistakes
```

**Query 5: Learn step-by-step evaluation methodology**
```
Endpoint: get_methodologies
Topic: "evaluation"
Expected: Evaluation phases, prerequisites, outputs
```

---

## Conclusion

The literature pattern is clear: **evaluation is not "before vs after" - it's a multi-phase architecture**:

1. **Continuous integration** during development (fast feedback)
2. **Formal quality gate** before deployment (defensible checkpoint)
3. **Production monitoring** after deployment (real-world validation)

The AI Engineering Workflow implements this as **Phase 4 Quality Gate**, positioned explicitly between inference design and operations. This timing is optimal because:
- Pipelines are complete (no rearchitecture needed)
- Issues are still fixable (not discovered in production)
- Decision is documented (audit trail for stakeholders)
- Production baseline established (enables monitoring)

The Knowledge MCP tools support this architecture by surfacing patterns, decisions, and warnings as agents navigate evaluation design.
