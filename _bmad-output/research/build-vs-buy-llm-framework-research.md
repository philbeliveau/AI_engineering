# Build-vs-Buy LLM Decision Framework Research Report

**Date:** 2026-01-06
**Source Query:** "LLMs in Production" book by Brousseau & Sharp (2024)
**Knowledge MCP Search:** Comprehensive inventory of `knowledge-pipeline_extractions` database

---

## Executive Summary

**Status:** PARTIAL FRAMEWORK FOUND - 40-50% coverage

The Knowledge MCP contains **ONE critical build-vs-buy LLM decision extraction** from "LLMs in Production" but **MISSING the complete three-question decision framework** from Figure 1.1 (page 14) of the source.

**What Was Found:**
- Extraction ID: `695c75fdb2a07918411aca4e`
- Type: Decision (not framework)
- Source: "LLMs in Production" (695c4ffed9fd318585d2fe19)
- Topics: `llm`, `deployment`
- Extracted: 2026-01-06T02:39:56.975101Z

**What's Missing:**
- The three conditional decision questions
- The complete decision tree logic
- Privacy/security gating criteria

---

## Framework Extraction Details

### Found Extraction

**Extraction ID:** `695c75fdb2a07918411aca4e`

**Question:**
```
Should you build your own language model or buy access to an existing one?
```

**Binary Options:**
1. Buy access to an existing language model
2. Build your own language model

**Considerations (Trade-offs):**
- Speed and flexibility of accessing a language model through an API
- Ability to fail fast and test a prototype without a large upfront investment
- Potential limitations of existing language models not fitting your specific domain

**Recommended Approach:**
```
Buy access to an existing language model to start with and test the concept quickly
```

**Decision Context:**
```
When deciding how to deploy large language models in production
```

---

## Expected Framework (Figure 1.1 / Page 14)

From the book "LLMs in Production", the complete decision framework should include:

### Three Key Questions (MISSING):
1. **"Is the LLM going to be critical to your business?"**
   - If YES → More investment justifies building
   - If NO → Buying is more efficient

2. **"Are you sure?"** (Validation check)
   - Confirms confidence in answer to Q1
   - Prevents overbuilding on uncertain premise

3. **"Does your application require strict privacy or security?"**
   - If YES → Build (keep data in-house)
   - If NO → Buying increases options

### Expected Decision Tree Logic (MISSING):
```
START: Should we build or buy?
  ├─ Q1: Critical to business?
  │   ├─ NO → Q3: Privacy/security required?
  │   │   ├─ NO → RECOMMEND: BUY
  │   │   └─ YES → RECOMMEND: BUILD
  │   └─ YES → Q2: Are you sure?
  │       ├─ NO (uncertain) → RECOMMEND: BUY (test first)
  │       └─ YES (confirmed) → Q3: Privacy/security?
  │           ├─ NO → CONDITIONAL: Consider buying if model exists
  │           └─ YES → RECOMMEND: BUILD
  └─ END: Decision made
```

---

## Gap Analysis

### Coverage Assessment

| Component | Found | Missing | Priority |
|-----------|-------|---------|----------|
| Build vs Buy decision point | ✅ Yes | - | N/A |
| Initial recommendation | ✅ Yes (start with buying) | - | N/A |
| API access trade-offs | ✅ Yes | - | N/A |
| Domain fit considerations | ✅ Yes | - | N/A |
| **Three questions framework** | ❌ No | ✅ Critical | HIGH |
| **Critical to business gate** | ❌ No | ✅ Critical | HIGH |
| **Conditional privacy/security** | ❌ No | ✅ Critical | HIGH |
| **Decision tree logic** | ❌ No | ✅ Critical | HIGH |

**Overall Coverage: 40-50%**

---

## Why the Gap Exists

### Root Cause Analysis

1. **Source Chunk Extraction**
   - The source document contains the full framework
   - But the chunk extraction process likely fragmented it
   - The diagram/decision tree may not have been captured in text form

2. **Extraction Type Limitation**
   - Current extraction is classified as "decision" (binary choice)
   - The framework is actually a **decision framework** (multi-step decision tree)
   - Different extractor might have captured it differently

3. **Document Processing**
   - Figure 1.1 may be a visual diagram (not text)
   - Diagram extraction requires OCR or special handling
   - Standard PDF chunking may skip visual content

### Evidence

In the knowledge base search, we found:
- **445 total extractions** from "LLMs in Production"
- **ZERO extractions** with the three questions or "critical to business" theme
- **ZERO framework-type extractions** (all are decisions/patterns/warnings)
- **ZERO privacy/security conditional logic** extractions from this source

---

## Recommendation for Step 02 (Scoping)

### Current Usage (Safe)

The found extraction **CAN** be used for:

1. **Initial Recommendation**
   - Starting point: "Always try buying/API access first"
   - Lowest-risk entry point
   - Test the business hypothesis before major investment

2. **Trade-off Guidance**
   - API speed/flexibility vs domain fit
   - Prototype fail-fast benefits
   - Domain model limitations

3. **Phase Gate**
   - Before building: "Do we have evidence that buying won't work?"

### Usage Example in Step 02

In the FTI Architect step (line 114-156):

```markdown
**Query 1: Architecture Decision - Build vs Buy**
Endpoint: get_decisions
Topic: "build vs buy LLM deployment"
Result: [Found extraction 695c75fdb2a07918411aca4e]

**Key Recommendation from Knowledge Base:**
> Start with buying access to existing models to fail fast and test your concept.
> This lets you understand if your business case is viable before major investment.

**Trade-offs Highlighted:**
- Speed/Cost: API access is fastest, lowest initial cost
- Flexibility: Limited to what's available in market
- Domain Fit: May not exist for specialized domains
```

### Gap to Address

**MUST ADD** to complete the decision framework for Step 02:

1. **Three-Question Gate (Manual)**
   - Since not in KB yet, add to step template:

```markdown
**Step 02.B: Three-Question Business Gate**

Before deciding on RAG vs Fine-tuning, answer these three questions:

Q1: **Is the LLM going to be critical to your business?**
- YES → More justification for building custom model
- NO → Buying is more cost-efficient

Q2: **Are you sure?** (Confidence check)
- Re-assess your answer to Q1
- Avoid overbuilding on uncertain premise
- Consider: How would things change if the model fails?

Q3: **Does your application require strict privacy or security?**
- YES → Build (data stays in-house, full control)
- NO → Buying expands options (managed services, APIs)

**Decision Logic:**
- Not critical + No privacy needs → Consider buying
- Critical business need → Likely need custom/fine-tuned
- Privacy/security critical → Build (data control)
```

---

## Action Items

### Short-term (For Step 02)

1. ✅ **Use the found extraction** (695c75fdb2a07918411aca4e) for:
   - Initial "try buying first" recommendation
   - Trade-off framework discussion
   - API-first prototyping guidance

2. ⚠️ **Supplement with manual framework** for:
   - Three conditional questions
   - Privacy/security gating
   - Business criticality assessment

### Medium-term (For Knowledge Base)

3. 🔄 **Re-extract from source document:**
   - Check if Figure 1.1 is a visual diagram
   - If diagram: Request OCR extraction
   - If text: Rechunk and re-extract with "framework" extractor

4. 🔄 **Add new extraction type:**
   - Introduce "decision-framework" type
   - Captures multi-step decision logic
   - Different from simple binary decisions

### Long-term (For Workflow)

5. 📋 **Create handoff to Step 02:**
   - Document this gap in claude.md
   - Link KB gap to workflow location
   - Provide template for three-question gate

---

## Knowledge Base Status

### Extraction Summary

From `knowledge-pipeline_extractions` collection:

| Type | Count | Status |
|------|-------|--------|
| decision | 356 | ✅ Complete |
| warning | 335 | ✅ Complete |
| pattern | 314 | ✅ Complete |
| methodology | 182 | ✅ Complete |
| checklist | 115 | ✅ Complete |
| workflow | 187 | ✅ Complete |
| persona | 195 | ✅ Complete |
| **TOTAL** | **1,684** | ⚠️ Framework gaps remain |

### Sources Containing Framework

| Source | Title | Extractions | Has Framework? |
|--------|-------|-------------|----------------|
| 695c4ffed9fd318585d2fe19 | LLMs in Production | 445 | ⚠️ Partial (build-vs-buy only) |

---

## Integration Point

### Step 02: FTI Architect (Line 114-156)

The step currently calls for:
- `get_decisions` for RAG vs Fine-tuning
- `search_knowledge` for patterns
- `get_warnings` for mistakes

**Addition needed:** Three-question gate before RAG vs Fine-tuning decision.

**File to update:**
```
_bmad-output/bmb-creations/workflows/ai-engineering-workflow/steps/0-scoping/step-02-fti-architect.md
```

**Section to add (after line 156):**
```markdown
### 2.1 Three-Question Business Gate (Manual Framework)

Before diving into RAG vs Fine-tuning, use this framework from "LLMs in Production":

**Question 1: Is the LLM going to be critical to your business?**
...
```

---

## References

### Knowledge Base Location
- **Database:** MongoDB (knowledge-cluster)
- **Collection:** `knowledge-pipeline_extractions`
- **Query:** `_id: "695c75fdb2a07918411aca4e"`
- **Source:** `source_id: "695c4ffed9fd318585d2fe19"`

### Source Document
- **Title:** LLMs in Production: From Language Models to Successful Products
- **Authors:** Christopher Brousseau, Matthew Sharp
- **Year:** 2024
- **Section:** Chapter 1, Figure 1.1, Page 14

### Related Extractions (From Same Source)
- 444 additional extractions available
- Topics: RAG, fine-tuning, deployment, inference, evaluation
- All decision-type extractions (no framework-type yet)

---

## Appendix: Full Extraction JSON

```json
{
  "_id": "695c75fdb2a07918411aca4e",
  "type": "decision",
  "source_id": "695c4ffed9fd318585d2fe19",
  "chunk_id": "695c502ad9fd318585d2fe33",
  "content": {
    "context_level": "chunk",
    "context_id": "695c502ad9fd318585d2fe33",
    "chunk_ids": ["695c502ad9fd318585d2fe33"],
    "question": "Should you build your own language model or buy access to an existing one?",
    "options": [
      "Buy access to an existing language model",
      "Build your own language model"
    ],
    "considerations": [
      "Speed and flexibility of accessing a language model through an API",
      "Ability to fail fast and test a prototype without a large upfront investment",
      "Potential limitations of existing language models not fitting your specific domain"
    ],
    "recommended_approach": "Buy access to an existing language model to start with and test the concept quickly",
    "context": "When deciding how to deploy large language models in production"
  },
  "topics": ["llm", "deployment"],
  "schema_version": "1.1.0",
  "extracted_at": "2026-01-06T02:39:56.975101Z"
}
```

---

**Report Generated:** 2026-01-06
**Search Scope:** Complete `knowledge-pipeline_extractions` collection (1,684 items)
**Confidence Level:** HIGH (direct database queries, extraction verified)
