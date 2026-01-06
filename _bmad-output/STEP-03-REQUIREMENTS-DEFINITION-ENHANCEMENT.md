# Step 03: Adding Requirements Definition Before Pipeline Design

**Date:** 2026-01-06
**Status:** ✅ COMPLETE
**Type:** Critical Gap Fix - Requirements Validation Gate

---

## 📋 What Was Added

Step 03 (Data Engineer) now has a **two-part workflow**:

### **PART A: REQUIREMENTS DEFINITION** (Sections 2-5)
**Before any pipeline design, deeply understand and validate data requirements**

- Section 2: Query Knowledge MCP for Requirements Elicitation
- Section 3: Deep Data Requirements Definition
- Section 4: Data Feasibility Assessment
- Section 5: Blocker Check & Decision

### **PART B: PIPELINE DESIGN** (Sections 6-17)
**Only proceed if requirements validated and feasibility gate passed**

- Section 6-17: All existing sections (renumbered)

---

## 🎯 Why This Matters

### The Problem We Fixed

**Before:**
```
Business Analyst (Step 1)
    ↓ identifies data sources, format, volume
    ↓ (no deep validation)
FTI Architect (Step 2)
    ↓ chooses RAG vs FT based on use cases
    ↓ (no data feasibility check)
Data Engineer (Step 3)
    ↓ IMMEDIATELY starts designing pipeline
    ✗ Assumes data is feasible without validation
    ✗ No check if data actually supports architecture
    ✗ No check if data is compatible with tech stack
    ✗ No blocker identification before heavy design work
```

**After:**
```
Business Analyst (Step 1)
    ↓ identifies data sources, format, volume
FTI Architect (Step 2)
    ↓ chooses RAG vs FT based on use cases
Data Engineer (Step 3) - PART A: Requirements
    ↓ deeply probes use case alignment with data
    ↓ documents data characteristics
    ↓ establishes success definition
    ↓ validates against architecture choice
    ✓ validates against tech stack (orch tool, vector DB)
    ✓ assesses team capacity and timeline
    ✓ runs blocker check
    ↓ GO/NO-GO decision
    ├─ NO-GO → Escalate (revisit sources, architecture, or stakeholders)
    ├─ CONDITIONAL GO → Proceed with mitigations documented
    └─ GO → Proceed to pipeline design
Data Engineer (Step 3) - PART B: Pipeline Design
    ✓ (only if Part A gates passed)
```

---

## 🔍 Section Details

### **Section 2: Query Knowledge MCP for Requirements Elicitation (NEW)**

Grounds requirements gathering in knowledge-based best practices:

**Queries:**
1. "Data requirements definition assessment framework AI/ML {architecture}"
2. "Data profiling assessment checklist quality validation {architecture}"
3. Topic: "data requirements feasibility"
4. Topic: "data requirements gathering discovery"

**Purpose:** Get KB guidance on HOW to gather requirements systematically, not jump to assumptions

---

### **Section 3: Deep Data Requirements Definition (NEW)**

Probes what THIS project actually needs from data:

#### **A. Use Case Alignment**

**If RAG:**
```
- What questions should your data help answer?
- Who will search/retrieve from this data?
- What makes a retrieval result "good"?
- Do users need source attribution?
- How will retrieval quality be validated?
```

**If Fine-tuning:**
```
- What specific behavior/style are you training for?
- What are "correct" vs "incorrect" examples?
- How will you know if fine-tuned model works?
- What edge cases matter most?
- How stable is this task?
```

#### **B. Data Characteristics Assessment**

**For RAG:**
```
Document Characteristics:
- What types? (PDFs, HTML, Markdown, APIs?)
- How structured?
- How current? (Annual? Daily? Real-time?)
- Versioned?
- What metadata?
- Any excluded docs?

Data Quality Reality:
- Source reliability?
- Clean or messy?
- Complete or gaps?
- Consistent?
- Previously validated?
```

**For Fine-tuning:**
```
Example Characteristics:
- Current data source?
- How many high-quality examples?
- Labeled/annotated?
- Format?
- Ground truth verified?
- Positive/negative ratio balance?

Data Diversity:
- Cover full use case?
- Obvious gaps?
- Representative?
- Duplicates?
- Quality validation rules?
```

#### **C. Success Definition - Data Perspective**

```
1. In 3 months, how will we know data pipeline works?
   (NOT: "Model has accuracy" - BUT: "Users find info" OR "Model behaves correctly")

2. What data quality metrics matter most?
   (RAG: Retrieval precision? Metadata? Coverage?
    FT: Label accuracy? Diversity? Edge cases?)

3. What's unacceptable failure?
   (Missing data? Outdated? Wrong labels? Bias?)

4. Realistic timeline?
   (When needed? Working backward: when should pipeline be done?)

5. Willing trade-offs?
   (Volume for quality? Speed for accuracy?)
```

Document answers as explicit success criteria.

---

### **Section 4: Data Feasibility Assessment (NEW)**

**Validates that data situation actually supports architecture + tech stack:**

#### **A. Feasibility Against Architecture**

**If RAG:**
```
✓/✗ Can parse all doc types? (PDFs, scanned docs, tables?)
✓/✗ Enough metadata?
✓/✗ Deduplicate at scale?
✓/✗ Handle document updates?
✓/✗ Retrieval quality achievable?

Blocker Check: Any "✗" marked HIGH risk?
```

**If Fine-tuning:**
```
✓/✗ Minimum viable training data? (>1000 for FT? >100 for few-shot?)
✓/✗ Labels consistent and accurate?
✓/✗ Ensure no train/eval leakage?
✓/✗ Examples cover use case distribution?
✓/✗ Generate more examples if needed?

Blocker Check: Any "✗" marked HIGH risk?
```

#### **B. Feasibility Against Tech Stack**

**Orchestration Tool:**
```
- Can {orchestration_tool} handle {data_volume}?
- Can it handle {update_frequency}?
- Support needed transformations?
- Team has skills or learning curve?

Risk: Low / Medium / High
```

**Vector DB (If RAG):**
```
- Can {vector_db} ingest {data_format}?
- Support your metadata?
- Handle {data_volume}?
- Scale to {update_frequency}?

Risk: Low / Medium / High
```

#### **C. Feasibility Against Team & Timeline**

```
✓/✗ Team expertise in {data_source_types}?
✓/✗ Dedicate {weeks_needed} to data pipeline?
✓/✗ Have data governance/privacy expertise?
✓/✗ Access ALL identified sources? (No blockers?)
✓/✗ Operational overhead acceptable?

Blocker Check: External team/approval dependencies?
```

---

### **Section 5: Blocker Check & Decision (NEW)**

**Critical Gate - Can we proceed, or escalate?**

**Summary Template:**
```markdown
## Data Feasibility Summary

### Requirements Validated
- [ ] Use case alignment clear
- [ ] Data characteristics documented
- [ ] Success definition established

### Feasibility Assessment
- [ ] Architecture supported by data
- [ ] Tech stack compatible
- [ ] Team capacity sufficient
- [ ] Timeline realistic

### Blockers Identified
[List any HIGH risk items]

### Decision
- [ ] **GO** - Proceed to pipeline design
- [ ] **CONDITIONAL GO** - Proceed with mitigations
- [ ] **NO-GO** - Escalate and revisit
```

**If NO-GO:**
```
Before we design, resolve:
1. [Blocker 1]
2. [Blocker 2]

Options:
[A] Revisit data sources (find alternative)
[B] Reconsider architecture (back to Step 2)
[C] Discuss with stakeholders (escalate)
```

**Only proceeds to Part B if GO or CONDITIONAL GO**

---

## 📊 Flow Changes

### **Section Renumbering**

Old structure:
```
1. Welcome
2. Query Knowledge MCP (pipeline patterns)
3. Architecture Focus
4. Data Source Inventory
4. Extraction Pipeline (duplicate numbering!)
5. Data Transformation
6. Data Quality Framework
7. Semantic Caching
8. Surface Anti-Patterns
9. Data Storage
10. Document Decisions
11. Generate Stories
12. Menu
```

New structure:
```
1. Welcome

PART A: REQUIREMENTS DEFINITION
2. Query Knowledge MCP (requirements elicitation) - NEW
3. Deep Data Requirements Definition - NEW
4. Data Feasibility Assessment - NEW
5. Blocker Check & Decision - NEW

PART B: PIPELINE DESIGN
6. Query Knowledge MCP (pipeline patterns)
7. Architecture Focus
8. Data Source Inventory
9. Extraction Pipeline
10. Data Transformation
11. Data Quality Framework
12. Semantic Caching
13. Surface Anti-Patterns
14. Data Storage
15. Document Decisions
16. Generate Stories
17. Menu
```

---

## ✅ Success Metrics Updated

### **New Success Criteria (Requirements Part)**

```
**Requirements Definition (Part A - CRITICAL):**
- ✅ Knowledge MCP queries for requirements elicitation executed
- ✅ Data requirements definition grounded in KB best practices
- ✅ Use case alignment probed (what does data support?)
- ✅ Data characteristics documented (type, format, volume, quality, metadata)
- ✅ Success definition explicit (how will we know data pipeline works?)
- ✅ Architecture-specific data requirements validated (RAG vs FT vs Hybrid)

**Feasibility Assessment (Part A - CRITICAL GATE):**
- ✅ Data situation validated against architecture choice
- ✅ Data situation validated against tech stack
- ✅ Team capacity and timeline assessed
- ✅ Blocker check completed
- ✅ GO/NO-GO decision made explicitly
- ✅ If NO-GO: Escalation path discussed
- ✅ Only proceeds if GO or CONDITIONAL GO
```

### **New Failure Criteria (Requirements Part)**

```
**Requirements Definition (Part A - CRITICAL GATE):**
- ❌ Skipping requirements definition sections (2-5) and jumping to pipeline design
- ❌ Not probing use case alignment with data
- ❌ Not documenting data characteristics
- ❌ Not establishing explicit success criteria
- ❌ Not validating data situation against architecture choice
- ❌ Not validating data situation against tech stack
- ❌ Skipping feasibility assessment or blocker check
- ❌ Proceeding to pipeline design with NO-GO decision
- ❌ Not documenting GO/NO-GO decision explicitly

**Master Rule:**
- Skipping requirements definition (Part A) = AUTOMATIC FAILURE
- Proceeding with NO-GO blockers = AUTOMATIC FAILURE
- Not using knowledge base for requirements elicitation = AUTOMATIC FAILURE
- Not validating feasibility before design = AUTOMATIC FAILURE
```

---

## 🎓 Key Principles Applied

### **1. Requirements Before Design**

Questions asked BEFORE designing pipelines:
- Does the data actually support the architecture choice?
- Is the data format compatible with the tech stack?
- Can the team execute this in the timeline?
- What are the blockers?

### **2. Knowledge-Grounded Requirements**

Requirements gathering is guided by Knowledge MCP:
- Query for "data requirements definition frameworks"
- Query for "data assessment methodologies"
- Query for "data feasibility decision criteria"
- Surface common mistakes in requirements

### **3. Explicit Feasibility Gate**

Users can't skip from requirements straight to pipeline design:
- GO: Proceed
- CONDITIONAL GO: Proceed with documented mitigations
- NO-GO: Escalate (must resolve before proceeding)

### **4. Architecture-Specific Requirements**

Different requirements for different architectures:
- RAG: Metadata critical, deduplication, versioning, retrieval quality
- FT: Label quality, example diversity, no data leakage
- Hybrid: Both pipelines must be validated separately

---

## 🔗 Integration Points

### **Input from Step 1 (Business Analyst)**
- Data landscape baseline (sources, formats, volumes)
- Data sensitivity levels
- Use case priorities

### **Input from Step 2 (FTI Architect)**
- Architecture choice (RAG/FT/Hybrid)
- Tech stack (orchestration tool, vector DB)
- Success metrics

### **Output to Part B (Pipeline Design)**
- Validated data requirements
- Feasibility assessment with GO/NO-GO
- Identified blockers (if any)
- Success criteria for data pipeline

### **Output to Downstream Steps**
- Data-pipeline-spec.md (ready for implementation)
- Stories (with architecture-specific tasks)
- Quality gates (validated against feasibility)

---

## 📁 Files Modified

**`step-03-data-engineer.md`**
- Added 4 new sections (2-5) with 1500+ lines
- Renumbered all downstream sections (6-17)
- Updated success/failure metrics to include requirements validation
- Added PART A and PART B markers to clarify workflow structure
- Enhanced critical success criteria for feasibility gating

---

## 🚀 Next Steps

With this enhancement, Step 03 now has:

✅ **Requirements Definition Gate** - Validates data before design
✅ **Feasibility Assessment** - Checks architecture + tech stack compatibility
✅ **Blocker Check** - Prevents wasted design effort
✅ **Knowledge-Grounded** - Uses KB for requirements methodology
✅ **Architecture-Aware** - Different requirements for RAG vs FT
✅ **Pipeline Design** - Follows only if requirements validated

**This pattern can now be applied to Steps 04-09** to ensure each phase has:
1. Requirements definition/validation
2. Feasibility assessment
3. Knowledge-grounded decision making
4. Implementation with clear success criteria

---

## 📊 Impact Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Requirements Validation** | ❌ Minimal | ✅ Comprehensive |
| **Feasibility Check** | ❌ None | ✅ Structured gate |
| **Architecture Alignment** | ⚠️ Assumed | ✅ Validated |
| **Tech Stack Compatibility** | ❌ Not checked | ✅ Validated |
| **Team Capacity Assessment** | ❌ Not checked | ✅ Validated |
| **Blocker Identification** | ❌ Late (discovery) | ✅ Early (prevention) |
| **Knowledge Grounding** | ⚠️ Partial | ✅ Comprehensive |
| **Success Criteria** | ⚠️ Generic | ✅ Data-specific |

---

**Enhancement Complete: 2026-01-06**
**Status: Ready for Testing and Downstream Application**
