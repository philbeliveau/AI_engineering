# AI Engineering Workflow - User Quick Start Guide

**Version:** 1.0.0
**Last Updated:** January 6, 2026
**Time to First Project:** 5-10 minutes

---

## Welcome!

You're about to use the **AI Engineering Workflow** - a comprehensive, 13-step process to design AI/LLM systems from business concept to production-ready implementation stories.

**What you'll get:**
- Complete architectural decisions documented
- Technical design for all system components
- Implementation roadmap with stories
- Production-ready operational strategy
- 3-6 month implementation timeline

**Estimated total time:** 3-4 hours spread over multiple sessions (or continuous if preferred)

---

## 5-Minute Setup

### Step 1: Access the Workflow

The workflow is built into BMAD (the system you're using). No installation needed.

### Step 2: Verify Knowledge MCP Connection

The workflow queries the Knowledge MCP for best practices. Verify your Claude Code config includes:

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

**No Knowledge MCP?** Don't worry - the workflow will still work, but without real-time best-practice grounding. Contact support to set it up.

### Step 3: Choose Your Project Type

Before starting, decide which applies to your project:

**RAG-Only:**
- You have documents to search/retrieve from
- You don't need to fine-tune a custom model
- You want to build fast with existing LLMs
- **Estimated time:** 2-2.5 hours

**Fine-Tuning:**
- You have training data to customize a model
- You don't need document retrieval
- You're building a specialized model
- **Estimated time:** 2.5-3 hours

**Hybrid (RAG + Fine-Tuning):**
- You have both documents and training data
- You want maximum customization
- You're building a sophisticated system
- **Estimated time:** 3-3.5 hours

---

## Running Your First Project (5-Minute Walkthrough)

### The Process

You're about to run 13 steps. Here's what happens at each level:

```
1. You describe your AI project (Business Analyst phase)
   ↓
2. System asks you architecture questions (FTI Architect phase)
   ↓
3. Specialized experts design each system component
   ↓
4. Tech Lead validates everything is consistent
   ↓
5. Stories are generated for your implementation team
```

### Running Step 1: Business Requirements

**Duration:** 15-20 minutes

1. Start Step 1 with the AI Engineering Workflow
2. Describe your AI project in natural language
   - What problem does it solve?
   - Who are the stakeholders?
   - What does success look like?
3. The Business Analyst will ask follow-up questions
4. Approve the generated `requirements.md`
5. Move to Step 2

**What you'll produce:**
- `requirements.md` - Your project's foundation document

---

### Running Step 2A: Architecture Decision (Part 1)

**Duration:** 20-25 minutes

**Critical Step:** This decision shapes your entire project

1. The FTI Architect reviews your requirements
2. System queries Knowledge MCP for best practices (you'll see this happening)
3. You're presented with 3 architecture options:
   - **RAG-Only** - Document retrieval without model customization
   - **Fine-Tuning** - Model customization without retrieval
   - **Hybrid** - Both retrieval and model customization
4. Select one (or ask for clarification)
5. System records your decision

**What you'll produce:**
- `architecture-decision.md` - Your architectural approach

**Note:** Your choice here determines which subsequent steps run:
- RAG-Only path: Skips Step 5 (Fine-Tuning), focuses on retrieval
- Fine-Tuning path: Skips advanced RAG, focuses on model training
- Hybrid path: Runs all steps

---

### Running Step 2B: Tech Stack Selection (Part 2)

**Duration:** 25-30 minutes

**Critical Checkpoint:** Architecture Confirmation

1. FTI Architect queries Knowledge MCP for tech recommendations
2. You choose specific technologies:
   - Vector Database (Pinecone? Qdrant? Weaviate?)
   - Embedding Model (OpenAI? Hugging Face?)
   - LLM Framework (LangChain? LlamaIndex?)
   - Fine-Tuning Framework (if applicable)
3. System presents trade-offs for each choice
4. **CRITICAL:** You must confirm the overall architecture is correct before proceeding

**What you'll produce:**
- `tech-stack.md` - Your technology selections with rationale

---

### Running Steps 3-4: Data & Embeddings Design

**Duration:** 40-50 minutes total

**Step 3A: Data Requirements** (15-20 min)
- Assess data availability
- Define quality requirements
- Plan data sourcing strategy

**Step 3B: Data Pipeline Design** (20-25 min)
- Design ingestion workflow
- Define quality checks
- Plan monitoring

**Step 4: Embeddings Strategy** (20-25 min)
- Choose chunking strategy (how to split documents)
- Select embedding model
- Configure vector database

**What you'll produce:**
- `data-requirements.md` - Data strategy
- `data-pipeline.md` - Ingestion workflow
- `embeddings-strategy.md` - Vector setup

---

### Running Step 5 (Conditional): Fine-Tuning Design

**Duration:** 25-30 minutes (only if you selected Fine-Tuning or Hybrid)

**Skipped if:** You selected RAG-Only

**Topics covered:**
- Fine-tuning approach (SFT? DPO? LoRA?)
- Training data preparation
- Cost estimation
- Training timeline

**What you'll produce:**
- `fine-tuning-config.md` - Training configuration (if applicable)

---

### Running Steps 6-7: RAG & Prompting Design

**Duration:** 45-50 minutes total

**Step 6: RAG Pipeline** (25-30 min, or skip if Fine-Tuning only)
- Retrieval strategy
- Reranking approach
- Context assembly

**Step 7: Prompt Design** (20-25 min)
- System prompt templates
- Few-shot examples
- Response formatting

**What you'll produce:**
- `rag-design.md` - Retrieval strategy (if applicable)
- `prompt-design.md` - Prompt templates

---

### Running Steps 8-9: Evaluation & Operations

**Duration:** 40-50 minutes total

**Step 8: Evaluation Framework** (20-25 min)
- Success metrics
- Benchmark dataset
- Testing approach

**Step 9: MLOps & Monitoring** (20-25 min)
- Production monitoring
- Drift detection
- Alert strategy
- Incident response

**What you'll produce:**
- `evaluation-framework.md` - Testing strategy
- `operations-plan.md` - Production checklist

---

### Running Step 10: Tech Lead Review

**Duration:** 30-40 minutes

**This is important:** Everything gets validated

1. Tech Lead reviews all previous outputs
2. Checks for consistency across steps
3. Identifies any conflicts or issues
4. Decision: GO or REVISE

**If GO:**
→ Proceed to story generation

**If REVISE:**
→ Go back to specific steps to fix issues
→ Return to Tech Lead review

**What you'll produce:**
- `validation-report.md` - Review findings

---

### Running Steps 11-13: Story Generation

**Duration:** 60-90 minutes total

**Step 11: Story Elaboration** (30-40 min)
- Convert designs to implementation stories
- Add acceptance criteria
- Add developer notes

**Step 12: Story Sequencing** (15-20 min)
- Organize by phase
- Identify dependencies
- Create sprint plan

**Step 13: Handoff** (15-20 min)
- Generate implementation guide
- Package all deliverables
- Create reference materials

**Final Deliverables:**
- `stories/` directory - Elaborated user stories (11+)
- `implementation-guide.md` - How to get started
- `roadmap.md` - 3-6 month implementation plan
- All design documents
- Project archive

---

## Common Scenarios

### Scenario 1: Build a RAG Chatbot (5-Minute Example)

**Your Project:** Build a customer support chatbot that answers questions from your company's documentation

**Timeline:**
```
Step 1 (15 min):   "I need a customer support chatbot using our docs"
                   → System extracts requirements

Step 2A (20 min):  "RAG-only is best - we don't need fine-tuning"
                   → Build vs Buy: Buy Claude API
                   → Architecture: RAG-only

Step 2B (25 min):  "Qdrant for vectors, sentence-transformers for embeddings, LangChain"
                   → Confirm architecture: ChatbotRAG system

Steps 3-4 (45 min): Data assessment, embeddings strategy
                    → Design vector store

Steps 6-7 (45 min): RAG pipeline, prompt templates
                    → Design retrieval + response generation

Steps 8-9 (45 min): Evaluation metrics, monitoring
                    → Define success criteria

Step 10 (30 min):   Tech Lead validates
                    → GO

Steps 11-13 (75 min): Generate stories
                      → 11 stories elaborated, roadmap created

Total: ~3.5 hours → Fully designed chatbot system
```

---

### Scenario 2: Fine-Tune a Specialized Model (5-Minute Example)

**Your Project:** Fine-tune Mistral for medical document analysis

**Timeline:**
```
Step 1 (15 min):   "Fine-tune Mistral for medical documents"
                   → System extracts requirements

Step 2A (20 min):  "Fine-tuning only - no document retrieval"
                   → Build vs Buy: Build/fine-tune Mistral
                   → Architecture: Fine-tuning

Step 2B (25 min):  "vLLM for serving, transformers for training"
                   → Confirm architecture

Steps 3-4 (45 min): Data assessment, embeddings (for tokenization)
                    → Plan training data collection

Step 5 (30 min):    Fine-tuning config
                    → DPO approach, 10k example dataset, 2-week timeline

Step 6 (skip):      RAG not needed

Steps 7-9 (60 min): Prompting, evaluation, MLOps
                    → Evaluation on medical benchmarks, production monitoring

Step 10 (30 min):   Tech Lead validates
                    → GO

Steps 11-13 (75 min): Generate stories
                      → 10 stories, 6-week roadmap

Total: ~3.5 hours → Fully designed fine-tuning project
```

---

### Scenario 3: Hybrid RAG + Fine-Tuning (5-Minute Example)

**Your Project:** Build a research assistant with retrieval + custom model

**Timeline:**
```
Step 1 (15 min):   "Research assistant with retrieval and custom fine-tuning"
                   → System extracts requirements

Step 2A (20 min):  "Hybrid approach - both retrieval and fine-tuning"
                   → Architecture: RAG + Fine-tuning

Step 2B (25 min):  "Qdrant + OpenAI embeddings + LangChain + TRL for fine-tuning"
                   → Confirm architecture

Steps 3-4 (45 min): Data strategy (retrieval + training)
                    → Plan both retrieval corpus and fine-tuning dataset

Step 5 (30 min):    Fine-tuning config
                    → SFT on research papers, 5k examples

Steps 6-9 (90 min): RAG pipeline, prompting, evaluation, MLOps
                    → Design complete integrated system

Step 10 (40 min):   Tech Lead validates (complex system)
                    → GO (or minor revisions)

Steps 11-13 (90 min): Generate stories
                      → 13 stories, complex dependencies, 8-week roadmap

Total: ~4.5 hours → Fully designed research assistant system
```

---

## Troubleshooting

### I'm stuck on a step - what do I do?

**During step execution:**
1. Re-read the step instructions (they're detailed)
2. Look for examples in the step file
3. Check if your project type (RAG/FT/Hybrid) skips this step
4. Ask for clarification (don't skip)

**After step completion:**
1. Tech Lead will catch issues in Step 10
2. Work gets sent back for revision if needed
3. It's normal to revise once

---

### Knowledge MCP queries are failing

**Why this happens:**
- Network issue
- Knowledge MCP endpoint is down
- Your connection doesn't allow SSE (Server-Sent Events)

**What to do:**
1. Check your network connection
2. Verify the Knowledge MCP URL is accessible
3. Reach out to support - you can continue without it
4. The workflow still works, just without real-time best-practice grounding

---

### I'm not sure which architecture to pick (Step 2A)

**Questions to ask yourself:**

**Do you have documents/knowledge to search?**
- YES → Consider RAG
- NO → Consider Fine-tuning

**Do you need model customization?**
- YES → Consider Fine-tuning or Hybrid
- NO → Consider RAG-only

**Do you have training data?**
- YES → Consider Fine-tuning or Hybrid
- NO → Consider RAG-only

**Do you need both?**
- YES → Hybrid
- NO → Pick the primary need

**Still unsure?** Hybrid is always safe (runs everything), takes ~30 min longer.

---

### Step 5 was skipped - is that correct?

**Yes, if:**
- You selected RAG-only in Step 2A
- Fine-tuning isn't part of your architecture

**The workflow is designed to skip unnecessary steps:**
- RAG-only projects skip Step 5
- Fine-tuning-only projects have minimal Step 6
- This saves 30-40 minutes

**Check your sidecar.yaml** to confirm the path.

---

### Tech Lead sent me back for revisions - what now?

**This is normal and good:**
1. Read the validation report
2. Understand which steps need rework
3. Go back to those specific steps
4. Make requested changes
5. Return to Step 10 (Tech Lead re-validates)

**Typical revision reasons:**
- Inconsistent architecture decisions
- Tech stack incompatibilities
- Data strategy misalignment
- Missing contingencies

**Not a failure** - it's the system catching issues before implementation.

---

### How do I use the final stories for my team?

**The stories are implementation-ready:**
1. Open `stories/` directory
2. Each file is a user story
3. Follow the acceptance criteria
4. Check "Developer Notes" for context
5. Start with "Foundational" stories first

**The implementation guide** (`implementation-guide.md`) walks you through the first story.

---

## What's Next After This Workflow?

### You Now Have:

1. **Complete design documentation** (11+ files)
2. **Implementation stories** (11+ elaborated stories)
3. **3-6 month roadmap** (with dependencies)
4. **Deployment checklist** (for production)
5. **Monitoring strategy** (for operations)

### Next Steps:

1. **Assemble your team** based on story assignments
2. **Set up your development environment** (implementation guide explains)
3. **Start with foundational stories** (infrastructure setup)
4. **Execute in order** (roadmap shows dependency chains)
5. **Reference the design docs** (always available)
6. **Follow the operations plan** (when deploying)

### Expected Timeline:

- **RAG-only:** 8-12 weeks
- **Fine-tuning:** 10-14 weeks
- **Hybrid:** 12-16 weeks

---

## FAQ

### Can I pause and come back?

**Absolutely.** All progress is saved in `sidecar.yaml`. You can:
- Stop at any point
- Come back days/weeks later
- Continue from where you left off
- The workflow remembers your decisions

### Can I change my mind about architecture?

**Before Step 3:** Yes, go back to Step 2A
**After Step 3:** Tech Lead will flag inconsistencies in Step 10

Changing late is more work, but possible - the system will route you back for redesign.

### Do I need technical expertise?

**No.** The workflow guides you through everything. It assumes:
- You understand your problem domain
- You can make architectural trade-off decisions
- You have access to stakeholder input

Technical details are handled by the specialized agents.

### Can I customize the workflow?

**The core 13 steps are fixed** - they've been designed for completeness and consistency.

However:
- You can add extra details in outputs
- You can ask for deeper dives in any step
- You can have your team review/adjust stories post-generation

The workflow is the foundation - you build on top of it.

### What if my project is unusual?

**The workflow handles:**
- Chatbots (RAG)
- Code analysis systems (Fine-tuning)
- Search engines (RAG)
- Content generation (Fine-tuning)
- Customer support (RAG or Hybrid)
- Medical analysis (Fine-tuning or Hybrid)
- Any AI/LLM system really

If you have a weird use case, the steps still apply - just answer based on your specifics.

---

## Support & Resources

### Documentation

- **Architecture Overview:** Complete system design reference
- **Remediation Summary:** Everything that went into making this production-ready
- **Knowledge Grounding Guide:** How the workflow uses best practices
- **Developer Guide:** For extending/maintaining the workflow
- **This guide:** User-focused quick start

### Knowledge MCP

Access 1,600+ best practices via the Knowledge MCP:
- `search_knowledge` - Semantic search
- `get_decisions` - Architectural decisions
- `get_patterns` - Implementation patterns
- `get_warnings` - Pitfalls to avoid
- `get_methodologies` - Step-by-step processes

### Getting Help

1. **Workflow stuck?** Re-read the current step (it's detailed)
2. **Tech question?** The Knowledge MCP likely has an answer
3. **Validation issue?** Read the validation report for specific feedback
4. **Design help?** Ask Claude to elaborate on options

---

## You're Ready to Start!

Now run the workflow:

1. **Pick your project type** (RAG-only, Fine-tuning, or Hybrid)
2. **Start Step 1** with the Business Analyst
3. **Follow each step** in order
4. **Let the system guide you** - each step is detailed
5. **Answer questions honestly** - quality input → quality output
6. **Approve outputs** at each step
7. **Let Tech Lead validate** in Step 10
8. **Collect your stories** in Steps 11-13

**Estimated time:** 3-4 hours for a complete AI/LLM system design

**Result:** Production-ready architectural design, implementation stories, and 3-6 month roadmap

**Go build something great!**
