# Evaluation Placement in AI/ML Systems - Complete Findings

**Date:** January 6, 2026
**Source:** Knowledge Pipeline MCP Analysis + AI Engineering Workflow Study
**Documents Created:** 3 comprehensive analysis files + this summary

---

## Executive Summary

Based on comprehensive analysis of the Knowledge MCP, AI Engineering Workflow architecture, and literature patterns, evaluation placement in AI/ML systems follows a **three-layer, multi-phase approach** rather than a simple binary "before vs after" decision.

### The Three-Layer Model

```
Layer 1: INTEGRATED EVALUATION (Phases 1-3)
├─ When: Continuous during development
├─ Method: Manual spot checking
├─ Speed: <5 min per test
├─ Purpose: Guide design decisions
└─ Risk: May miss subtle issues

Layer 2: QUALITY GATE EVALUATION (Phase 4)
├─ When: Formal checkpoint before deployment
├─ Method: Structured, documented framework
├─ Speed: 3-5 days execution
├─ Purpose: Make explicit GO/NO-GO decision
└─ Risk: None - this is the gate

Layer 3: PRODUCTION MONITORING (Phase 5+)
├─ When: Continuous after deployment
├─ Method: Real-time dashboards + alerts
├─ Speed: Real-time response
├─ Purpose: Detect regressions, gather user feedback
└─ Risk: Affects real users if failure detected
```

**Key Finding:** The literature overwhelmingly recommends ALL THREE layers, not one or the other.

---

## What the Literature Says

### Core Principle
**Evaluation is NOT a single event - it's an integrated architectural pattern.**

Sources consistently recommend:
1. **Lightweight evaluation during development** (continuous, informal)
2. **Formal quality gate before deployment** (structured, explicit, auditable)
3. **Production monitoring after deployment** (continuous, real-time)

### Major Trade-offs

**Integrated (During Development)**
- ✅ Fast feedback (< 5 min)
- ✅ Guides iteration
- ✅ Low friction
- ❌ Informal and subjective
- ❌ May miss subtle issues
- ❌ Not reproducible

**Quality Gate (Before Deployment)**
- ✅ Formal and auditable
- ✅ Catches regressions
- ✅ Defensible to stakeholders
- ✅ Establishes baseline for monitoring
- ❌ Late feedback (post-design)
- ❌ More expensive (compute + human effort)

**Production Monitoring (After Deployment)**
- ✅ Real-world signals
- ✅ Catches deployment-specific issues
- ✅ User satisfaction metrics
- ❌ Affects real users first
- ❌ Recovery requires rollback

### Critical Anti-Patterns

**NEVER:**
1. ❌ Use LLM-generated test data to evaluate LLM systems (circular bias)
2. ❌ Evaluate generation quality without checking retrieval (RAG systems)
3. ❌ Use single metric for quality assessment
4. ❌ Use same model for generation AND evaluation (self-preference bias)
5. ❌ Skip formal quality gate
6. ❌ Optimize for one metric and ignore others

**ALWAYS:**
1. ✅ Include multiple evaluation methods (automated + human)
2. ✅ Separate retrieval and generation metrics (RAG)
3. ✅ Mitigate LLM-as-judge biases (position, verbosity, self-preference)
4. ✅ Use human-verified test data
5. ✅ Document all gate decisions
6. ✅ Monitor production against gate targets

---

## Key Patterns from Knowledge Base

### Pattern 1: RAG-Specific Layer Separation

For retrieval-augmented generation systems:

```
Layer A: Retrieval Evaluation
├─ Metrics: Recall@K, Precision@K, MRR, NDCG
├─ Target: Recall@5 >= 80%
├─ Question: "Are we retrieving the right documents?"
└─ Fix: Improve embeddings, ranking, or K value

Layer B: Generation Evaluation
├─ Metrics: Faithfulness, Hallucination, Relevance
├─ Target: Faithfulness >= 90%, Hallucination < 5%
├─ Question: "Is the answer grounded in retrieved context?"
└─ Fix: Adjust prompt, improve context, different model

Layer C: End-to-End Evaluation
├─ Metrics: Accuracy, Citation Accuracy
├─ Target: Accuracy >= 85%, Citations >= 90%
├─ Question: "Does the full system answer correctly?"
└─ Diagnosis: Layer A or B failure?
```

**Why Separate?** Without separation:
- Can't tell if retrieval or generation is broken
- Optimize wrong component
- Expensive, slow debugging

With separation:
- Know exactly what's failing
- Targeted fixes
- Faster resolution

### Pattern 2: LLM-as-Judge with Bias Mitigation

If using LLM to evaluate answers:

```
Bias: Position Bias (prefers first/last options)
Mitigation: Randomize option order in prompts

Bias: Verbosity Bias (prefers longer responses)
Mitigation: Length-normalize responses before judging

Bias: Self-Preference (prefers its own outputs)
Mitigation: Use DIFFERENT model for judge than system

Bias: Sycophancy (agrees with user opinions)
Mitigation: Use objective, neutral evaluation prompts

Critical: Always validate against human evaluation (>80% agreement)
```

### Pattern 3: Quality Gate Decision Options

```
GO
├─ All criteria >= target threshold
├─ No critical failures in golden set
└─ Action: Proceed to Phase 5 (Production)

CONDITIONAL GO
├─ Most criteria met
├─ Minor issues identified
├─ Mitigations documented
└─ Action: Deploy + fix conditions post-deployment

NO-GO
├─ Critical criteria failed
├─ Showstopper issues
└─ Action: Return to Phase 3 for fixes
```

**Critical Rule:** All gates are explicit, documented, and reversible (with rollback plan).

---

## MCP Implementation

### Available Query Tools

The Knowledge MCP provides four query endpoints specifically designed for evaluation guidance:

1. **search_knowledge** - Semantic search across all knowledge
   - Use for: Understanding evaluation approaches, finding examples
   - Example: `"evaluation placement phases integration RAG"`

2. **get_decisions** - Structured decision points with trade-offs
   - Use for: Making evaluation methodology choices
   - Example: `topic="evaluation"` returns decision options

3. **get_patterns** - Implementation patterns with code examples
   - Use for: Learning HOW to implement evaluation
   - Example: `topic="evaluation"` returns concrete patterns

4. **get_warnings** - Anti-patterns and pitfalls to avoid
   - Use for: Learning what NOT to do
   - Example: `topic="evaluation"` returns evaluation pitfalls

5. **get_methodologies** - Step-by-step processes
   - Use for: Following structured evaluation methodology
   - Example: `topic="evaluation"` returns evaluation phases

### Recommended Query Sequence

**For any new AI system, execute in order:**

Week 1: Understand Placement
- `search_knowledge("evaluation placement phases integration")`
- `get_decisions(topic="evaluation")`

Week 2: Learn Methods
- `get_methodologies(topic="evaluation")`
- `get_patterns(topic="evaluation")`

Week 3: Avoid Pitfalls
- `get_warnings(topic="evaluation")`
- `search_knowledge("LLM judge evaluation bias mitigation")`

Week 4: System-Specific
- `search_knowledge("[RAG|fine-tuning] evaluation metrics")`
- Domain-specific adjustments

### Current Knowledge Base

The MCP has 1,684+ extractions covering:
- **Decisions:** 356 total (~25-30 evaluation-related)
- **Warnings:** 335 total (~20-25 evaluation-related)
- **Patterns:** 314 total (~15-20 evaluation-related)
- **Methodologies:** 182 total (~10-15 evaluation-related)
- **Workflows:** 187 total (~5-10 evaluation-related)

All content is from diverse, authoritative AI engineering sources.

---

## Workflow Implementation

### AI Engineering Workflow Phase 4: Quality Gate

The workflow implements evaluation as Phase 4 (explicit gate between design and deployment):

**Step 8: LLM Evaluator** includes:

1. **Mandatory MCP Queries** (must execute)
   - `get_warnings(topic="evaluation")`
   - `search_knowledge("LLM judge evaluation bias pitfalls")`
   - `get_methodologies(topic="evaluation")`
   - `search_knowledge("model evaluation metrics benchmark")`

2. **Design Evaluation Framework**
   - Functional criteria (accuracy, relevance, completeness)
   - Non-functional criteria (latency, throughput, cost)
   - Test categories (unit, integration, E2E, regression, adversarial)
   - Test datasets (golden set, edge cases, adversarial)
   - Evaluation methods (automated + human)

3. **Execute Evaluation**
   - For RAG: Separate retrieval and generation evaluation
   - Automated metrics execution
   - LLM-as-judge (if used) with bias mitigations
   - Human evaluation of critical samples
   - Document all results

4. **Make Quality Gate Decision**
   - Compare metrics against pre-defined thresholds
   - Choose: GO / CONDITIONAL GO / NO-GO
   - Document decision in decision-log.md
   - Update sidecar with evaluation results

5. **Generate Implementation Stories**
   - Stories for golden dataset creation
   - Stories for automated evaluation implementation
   - Stories for human evaluation
   - Stories for quality gate automation

---

## Recommended Evaluation Timeline

### For a Typical RAG System (6-month project)

```
Month 1-2: Phase 0-1 (Scoping & Feature Pipeline)
├─ Define quality targets
├─ Spot-check data quality with examples
└─ Integrated evaluation: Manual tests on 10-20 examples

Month 2-3: Phase 2 (Training, if fine-tuning)
├─ Monitor loss curves
├─ Integrated evaluation: Convergence checks
└─ Hold-out test set tracking

Month 3-4: Phase 3 (Inference Pipeline - RAG + Prompts)
├─ Design retrieval and generation
├─ Integrated evaluation: Quick manual tests
└─ Iterate on prompt engineering

Month 4-5: Phase 4 (Quality Gate - FORMAL EVALUATION)
├─ Week 1: Design evaluation framework
│  ├─ Query Knowledge MCP
│  ├─ Define criteria and metrics
│  ├─ Design test datasets
│  └─ Plan evaluation methods
├─ Week 2: Execute evaluation
│  ├─ Retrieval layer tests (~4 hours)
│  ├─ Generation layer tests (~8 hours)
│  ├─ End-to-end tests (~4 hours)
│  └─ Safety and adversarial tests (~2 hours)
└─ Week 3: Make gate decision
   ├─ Analyze results
   ├─ Document decision
   ├─ Get stakeholder approval
   └─ Generate implementation stories

Month 5-6: Phase 5 (Operations - Deployment & Monitoring)
├─ Deploy to production
├─ Set up monitoring dashboards
├─ Configure alerts
└─ Monitor against gate targets (ongoing)

Month 6+: Phase 6+ (Continuous Improvement)
└─ User feedback, metric tracking, iteration
```

---

## Success Criteria

### Evaluation Design Complete When:

✅ Quality targets defined (from Phase 0)
✅ Test dataset identified or planned
✅ Evaluation methodology chosen (from KnowledgeMCP guidance)
✅ Metrics selected and thresholds set
✅ Evaluation methods decided (automated/human/LLM-as-judge)
✅ Anti-patterns understood and mitigations planned
✅ RAG-specific layers separated (if applicable)
✅ LLM-as-judge biases addressed (if applicable)
✅ Quality gate criteria documented
✅ Decision log started

### Quality Gate Decision Valid When:

✅ All evaluation methods completed
✅ Results documented with evidence
✅ Metrics compared against pre-defined thresholds
✅ Explicit decision recorded (GO/CONDITIONAL/NO-GO)
✅ If NO-GO, blockers clearly identified and plan to fix
✅ If CONDITIONAL, conditions listed with deadlines
✅ Decision log updated
✅ Stakeholder approval obtained
✅ Implementation stories generated
✅ Sidecar updated with phase status

---

## Key Insights from Knowledge MCP

### What Sources Agree On

1. **Multi-phase evaluation is essential** - All sources recommend integrated + gate + production
2. **Formal gate before deployment** - Documented, explicit decision point prevents surprises
3. **Multiple evaluation methods** - Never rely on single metric; balance automated + human
4. **Separate retrieval and generation** - For RAG systems; debug independently
5. **Test data from humans** - LLM-generated data creates circular bias
6. **Mitigate LLM-as-judge biases** - Use different models, randomize, validate
7. **Document everything** - Audit trail needed for stakeholder confidence
8. **Production monitoring critical** - Gate targets establish monitoring baseline

### Where Sources Differ

1. **Specific metric thresholds** - No universal targets; must be domain/context-specific
2. **Which evaluation methods** - Depends on budget, timeline, precision requirements
3. **Test dataset size** - Ranges from 50 (quick) to 500+ (comprehensive)
4. **Human evaluation extent** - Ranges from 5-10% sample to 50%+ coverage
5. **LLM-as-judge viability** - Some sources caution against it; others recommend with mitigations

**Resolution:** Use sources as guidance, adapt to your constraints, always mitigate risks.

---

## Documents Created

### 1. evaluation-placement-analysis.md (20 KB)
**Comprehensive analysis of when evaluation happens and why**

Contents:
- What literature says about evaluation timing
- Trade-offs between integrated and gate-based evaluation
- Architecture pattern (three-layer approach)
- Key patterns from knowledge base
- Anti-patterns to avoid
- Recommended workflow sequence
- Current MCP implementation details
- Critical success factors and references

### 2. evaluation-timing-architecture.md (24 KB)
**Visual architecture and timelines for evaluation placement**

Contents:
- Timeline showing when evaluation happens
- Evaluation methods by phase
- RAG system layer separation diagram
- Quality gate decision matrix
- Knowledge MCP integration points
- Common failure modes and prevention
- Decision flowchart for evaluation approach
- Three-layer summary recap

### 3. evaluation-mcp-queries-reference.md (19 KB)
**Practical guide for querying the Knowledge MCP**

Contents:
- Overview of MCP tools
- Specific query examples and expected results
- Query sets for understanding placement
- Query sets for evaluation methods
- Query sets for warnings and anti-patterns
- Query sets for specific decisions
- Results interpretation guide
- Recommended query sequence
- Cheat sheet with query templates
- Integration with AI Engineering Workflow
- Success criteria for MCP integration

---

## How to Use These Documents

### For Quick Reference
Start with **EVALUATION-FINDINGS-SUMMARY.md** (this document)
- 5-minute overview
- Key findings highlighted
- Document roadmap

### For Detailed Understanding
Read **evaluation-placement-analysis.md**
- Comprehensive analysis
- All patterns and anti-patterns
- MCP tool descriptions
- Success factors

### For Architecture Understanding
Study **evaluation-timing-architecture.md**
- Visual timelines and diagrams
- Phase-specific approaches
- Decision flowcharts
- Common pitfalls

### For Implementation
Use **evaluation-mcp-queries-reference.md**
- Specific query templates
- Expected results format
- Query sequences
- Integration guidance

---

## Next Steps

### To Implement This in Your Project

1. **Week 1: Research Phase (Using MCP)**
   ```bash
   # Execute these queries
   search_knowledge("evaluation placement phases integration")
   get_decisions(topic="evaluation")
   get_warnings(topic="evaluation")
   ```

2. **Week 2: Design Phase**
   - Define evaluation criteria
   - Design test datasets
   - Select evaluation methods
   - Plan metrics and thresholds

3. **Week 3: Implementation Phase**
   - Create test infrastructure
   - Implement evaluation pipeline
   - Run initial evaluation

4. **Week 4: Gate Decision Phase**
   - Analyze results
   - Make GO/NO-GO decision
   - Document in decision-log.md
   - Generate implementation stories

5. **Ongoing: Monitoring Phase**
   - Deploy to production
   - Monitor against gate targets
   - Collect user feedback
   - Iterate based on production signals

---

## References

**AI Engineering Workflow Step 8:** `/bmad-output/bmb-creations/workflows/ai-engineering-workflow/steps/4-evaluation/step-08-llm-evaluator.md`

**Quality Gate Checklist:** `/bmad-output/bmb-creations/workflows/ai-engineering-workflow/checklists/quality-gate-checklist.md`

**Knowledge MCP Server:** `https://knowledge-mcp-production.up.railway.app/mcp`

**Knowledge Base Statistics:**
- Total extractions: 1,684+
- Evaluation-specific: ~75-100 (decisions, warnings, patterns, methodologies, workflows)
- All from authoritative AI engineering sources

---

## Conclusion

The research is clear: **evaluation is not a binary "before or after" decision - it's a three-layer architectural pattern that includes integrated testing during development, a formal quality gate before deployment, and continuous monitoring in production.**

The AI Engineering Workflow operationalizes this as Phase 4 (Quality Gate), positioned explicitly between inference design and operations deployment. This timing is optimal because:

1. **Pipelines are complete** - No need for major rearchitecture
2. **Issues are still fixable** - Can return to Phase 3 for fixes
3. **Decision is explicit** - Documented gate for stakeholders
4. **Baseline is established** - Enables production monitoring

The Knowledge MCP supports this architecture by surfacing patterns, decisions, and warnings as practitioners navigate evaluation design through Phase 4 of the workflow.

---

**Analysis Complete**
*Documents ready for integration into project workflow*
*Ready for Phase 4 execution: Evaluation & Quality Gate*
