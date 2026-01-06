# Build vs Buy Framework Integration

**Date:** 2026-01-06
**Source:** "LLMs in Production" by Brousseau & Sharp (2024), Figure 1.1, Page 14
**Integration Point:** Phase 0 (Scoping) - Step 2: FTI Architect - **Section 2 (NEW)**

---

## 📚 What Was Integrated

**The Three-Question Build vs Buy Decision Framework from LLMs in Production:**

```
Q1: Is the LLM going to be critical to your business?
    ↓ YES → Continue to Q2
    ↓ NO  → Lean toward BUYING

Q2: Are you sure? (Validate your confidence)
    ↓ YES → Continue to Q3
    ↓ NO  → Reconsider Q1

Q3: Does your application require strict privacy or security?
    ↓ YES → BUILDING (You need custom/fine-tuned LLM)
    ↓ NO  → Trade-off analysis needed
```

**Decision Outcomes:**
- **BUYING:** Use API access (OpenAI, Claude, etc.) → Fail fast, test concept quickly
- **BUILDING:** Build/fine-tune custom LLM → Critical business need + privacy/security requirements

---

## 🏗️ How It's Positioned in the Workflow

**NEW DECISION HIERARCHY (updated Step 02):**

```
Phase 0: Scoping
  ├─ Section 2: BUILD vs BUY (NEW)
  │  └─ Three-question framework decides: Buy API or Build custom?
  │
  ├─ If BUYING:
  │  └─ Section 5: API Provider Selection
  │     └─ Choose provider (OpenAI, Claude, other)
  │     └─ Skip architecture & fine-tuning decisions
  │
  ├─ If BUILDING:
  │  ├─ Section 4: Gather Use Case Requirements
  │  ├─ Section 6: Make Architecture Decision (RAG vs FT)
  │  │
  │  └─ Section 7-13: Tech Stack Selection
  │
  └─ All paths: Section 14-15 Document decisions & proceed to Phase 1
```

---

## 🔄 Workflow Changes

### Before (Missing)
- No explicit "build vs buy" decision
- Assumed projects would always build/customize
- Jumped directly to RAG vs Fine-tuning choice

### After (Comprehensive)
- **Section 2:** Build vs Buy (THREE-QUESTION GATE)
- **Section 5:** API Provider Selection (if buying)
- **Section 6:** Architecture Decision (if building)
- **Section 7-13:** Tech Stack (all projects)
- **Conditional paths:** Different flows for build vs buy

---

## 📋 Decision Documentation

### Sidecar.yaml Updated

```yaml
build_vs_buy: "[build | buy]"                    # NEW PRIMARY DECISION
api_provider: "[OpenAI | Claude | other | N/A]"  # Only if buying
architecture: "[rag-only | fine-tuning | hybrid | N/A]"  # Only if building

decisions:
  - id: "build-001"  # NEW
    choice: "[build | buy]"
    knowledge_ref: "LLMs in Production, Figure 1.1"
  - id: "arch-001"   # CONDITIONAL
    choice: "[rag-only | fine-tuning | hybrid]"
    conditional: "only_if_building"
```

### Decision Log Entry (BUILD-001)

```markdown
## BUILD-001: Build vs Buy LLM Decision

Three-Question Framework (from LLMs in Production):
- Q1: Critical to business? [YES/NO]
- Q2: Are you sure? [YES/NO]
- Q3: Privacy/security? [YES/NO]

Final Decision: [Build | Buy]
Rationale: [From framework answers]
Knowledge Reference: Figure 1.1, Page 14
```

---

## 🎯 Key Insights from the Framework

**Start with BUYING (Default):**
> "Start by buying/using API access to test your concept quickly. Fail fast without large upfront investment."

**Build ONLY when:**
✅ LLM is critical to business AND
✅ Privacy or security requirements mandate custom approach

**Avoid over-engineering:**
❌ Don't build custom LLM unless business criticality + privacy/security force it
❌ Many projects should start with API access (Claude, OpenAI) and iterate

---

## 🔗 Knowledge Base Reference

**Extraction ID:** `695c75fdb2a07918411aca4e`
**Source:** "LLMs in Production" (2024)
**Type:** Decision
**Topics:** LLM, deployment
**Key Concept:** Build-vs-buy trade-off analysis with business criticality gate

---

## 📊 Impact on Project Paths

### Path A: BUYING (API Access)
```
Scoping
  ├─ Q1-Q3 Framework → "Buy"
  ├─ API Provider Selection (Section 5)
  │  └─ Choose: OpenAI? Claude? Other?
  ├─ Tech Stack Selection (Sections 7-13)
  │  └─ Orchestration: API calls + wrapper services
  │  └─ No training tools needed
  │  └─ Focus on prompt engineering, retrieval, caching
  └─ Phase 1 (Direct to using API)
     └─ No fine-tuning specialist needed
     └─ Focus on feature/prompt engineering
```

### Path B: BUILDING (Custom/Fine-tuned LLM)
```
Scoping
  ├─ Q1-Q3 Framework → "Build"
  ├─ Architecture Decision (Section 6)
  │  └─ RAG vs Fine-tuning vs Hybrid
  ├─ Tech Stack Selection (Sections 7-13)
  │  └─ Includes training, monitoring, orchestration
  └─ Phase 1-5
     └─ Full workflow with fine-tuning specialist
     └─ Dedicated training and inference phases
```

---

## ✅ Success Criteria for This Decision

**User completes Build vs Buy when:**
- [ ] Presented the three-question framework
- [ ] Answers Q1 clearly (business criticality)
- [ ] Validates answer in Q2 (confidence check)
- [ ] Addresses Q3 (privacy/security needs)
- [ ] Makes explicit BUILD or BUY choice
- [ ] BUILD-001 decision logged with three-question details
- [ ] Proceeds to appropriate path (Provider Selection or Architecture)

---

## 🎓 Why This Matters

**Before:** Workflow assumed everyone would build/customize → Generic approach
**After:** Workflow respects the build-vs-buy trade-off → Context-aware paths

**Key Achievement:** The FTI Architect now owns the **foundational decision** before architecture, guided by literature best practices from "LLMs in Production."

This prevents common mistake: **Over-engineering by building custom LLMs when buying API access would be faster and cheaper.**

---

## 🔮 Future Enhancement

As the knowledge base grows, this framework could be:
- **Extended:** Add cost/effort estimates from KB
- **Refined:** Add decision criteria for edge cases
- **Automated:** Query KB for "when to build vs buy" patterns
- **Integrated:** Connect to provider API costs and latency data

---

## 📁 Files Modified

1. **`step-02-fti-architect.md`**
   - Added Section 2: Build vs Buy framework
   - Added Section 5: API Provider Selection (if buying)
   - Renumbered all sections for new flow
   - Updated sidecar structure with build_vs_buy
   - Updated decision-log with BUILD-001 entry
   - Updated success/failure metrics

2. **`agents/fti-architect.md`**
   - Enhanced outputs to include build/buy decision
   - Updated handoff to note conditional paths

---

**Key Quote from LLMs in Production:**
> "Start by buying/using API access to test the concept quickly and fail fast without a large upfront investment."

This is now **the default recommendation** in Phase 0, unless the three-question framework forces a BUILD decision.

---

*Integrated: 2026-01-06 | Figure 1.1, Page 14 | "LLMs in Production" (Brousseau & Sharp, 2024)*
