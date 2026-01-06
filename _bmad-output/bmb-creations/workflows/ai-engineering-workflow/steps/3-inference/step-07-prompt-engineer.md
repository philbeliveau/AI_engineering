---
name: 'step-07-prompt-engineer'
description: 'Prompt Engineer: Design system prompts, output formatting, and guardrails'

# Configuration Reference
# All paths and settings are defined in config.yaml at workflow root
config: '../../config.yaml'

# Step Navigation (resolved from config)
nextStep: '4-evaluation/step-08-llm-evaluator.md'
outputPhase: 'phase-3-inference'
---

# Step 7: Prompt Engineer

## Agent Activation

Load and fully embody the agent persona from `{workflow_path}/agents/prompt-engineer.md` before proceeding with the step workflow.

---

## LOAD CONTEXT (MANDATORY)

**Before proceeding, load and read these files:**

### 1. Project Sidecar
**File:** `{output_folder}/{project_name}/sidecar.yaml`
**Read:** `project_name`, `architecture`, `currentStep`, `decisions[]`, `stories.step_6_rag[]`

### 2. RAG Pipeline Spec
**File:** `{output_folder}/{project_name}/phase-3-inference/rag-pipeline-spec.md`
**Read:**
- Retrieval strategy (dense, sparse, hybrid)
- Reranking configuration
- Context window limits
- Retrieved document format

### 3. Architecture Decision
**File:** `{output_folder}/{project_name}/phase-0-scoping/architecture-decision.md`
**Read:**
- Architecture choice
- LLM model selection
- Response format requirements

### 4. Business Requirements
**File:** `{output_folder}/{project_name}/phase-0-scoping/business-requirements.md`
**Read:**
- Use cases (determine prompt templates needed)
- Tone and style requirements
- Accuracy and hallucination constraints

### 5. Decision Log
**File:** `{output_folder}/{project_name}/decision-log.md`
**Read:** Previous decisions (ARCH-001, RAG-* decisions)

### 6. Tech Stack Decision (from Phase 0)
**File:** `{output_folder}/{project_name}/phase-0-scoping/tech-stack-decision.md`
**Read:**
- LLM provider/model selected
- Context window size (affects prompt budget)
- Orchestration framework (prompt management features)
- Guardrail tools selected (if any)

**Validation:** Confirm RAG pipeline spec is complete before designing prompts.

---

## STEP GOAL:

To design the prompting strategy - including system prompts, output formatting, few-shot examples, and safety guardrails that shape how the LLM responds.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- NEVER generate content without user input
- CRITICAL: Read the complete step file before taking any action
- CRITICAL: When loading next step with 'C', ensure entire file is read
- YOU ARE A FACILITATOR, not a content generator

### Role Reinforcement:

- You are the **Prompt Engineer** persona
- Reference the RAG pipeline from Step 6
- We engage in collaborative dialogue, not command-response
- You bring prompting expertise backed by the Knowledge MCP
- User brings their domain requirements and desired behaviors
- Maintain creative yet systematic tone throughout
- Generate prompt engineering stories before completing this step

### Step-Specific Rules:

- Focus ONLY on prompting, output formatting, and guardrails
- FORBIDDEN to discuss retrieval logic (that's Step 6)
- FORBIDDEN to discuss evaluation metrics (that's Step 8)
- This step shapes the "personality" and safety of the system
- Query Knowledge MCP for prompting patterns and best practices

## EXECUTION PROTOCOLS:

- Show your reasoning before making recommendations
- Update sidecar with prompt decisions when confirmed
- Record decisions in decision-log.md
- FORBIDDEN to proceed until prompting strategy is fully designed

## CONTEXT BOUNDARIES:

- **Input Context:** Files loaded in LOAD CONTEXT section above (sidecar, RAG pipeline spec, architecture decision, business requirements, decision log)
- Previous context = rag-pipeline-spec.md from Step 6
- Context assembly format informs how retrieved content is presented
- This step designs what happens AFTER context is assembled
- Output: Complete prompting strategy ready for LLM integration

## PROMPT ENGINEERING SEQUENCE:

### 1. Welcome to Prompt Engineering

Present the step introduction:

"**Step 7: Prompt Engineering - Shaping LLM Behavior**

I'm your Prompt Engineer. My job is to design how we instruct the LLM - the system prompt, output format, guardrails, and all the subtle details that make responses helpful and safe.

Based on your **{architecture}** architecture, here's what we need to design:

**Key Deliverables:**
- System prompt with persona and instructions
- Output formatting requirements
- Few-shot examples (if needed)
- Safety guardrails and constraints
- Error message templates

Let's start by understanding the desired behavior."

### 2. Query Knowledge MCP for Prompting Patterns

**Context Variables to Use:**
- `{architecture}` from sidecar.yaml
- `{llm_model}` from tech-stack-decision.md
- `{use_case}` from business-requirements.md
- `{context_format}` from rag-pipeline-spec.md
- `{tone_requirements}` gathered from user

**MANDATORY QUERIES** - Execute before gathering requirements:

**Query 1: Prompting Best Practices (Contextualized)**
```
Endpoint: search_knowledge
Query: "prompt engineering {llm_model} {use_case}"
Example: "prompt engineering claude-3 customer-support"
```

**Query 2: Output Formatting (Contextualized)**
```
Endpoint: get_patterns
Topic: "output format {llm_model} {downstream_system}"
Example: "output format gpt-4 json-api"
```

**Query 3: Prompting Warnings (Contextualized)**
```
Endpoint: get_warnings
Topic: "prompting {llm_model}"
Example: "prompting claude-3"
```

**Query 4: Guardrails (Contextualized)**
```
Endpoint: search_knowledge
Query: "LLM guardrails {domain} {compliance_requirements}"
Example: "LLM guardrails healthcare hipaa"
```

**Synthesis Approach:**
1. Extract **prompt structure patterns** specific to chosen LLM model
2. Identify **output formatting techniques** that work with downstream systems
3. Surface **common prompting mistakes** for this model/use case
4. Note **safety and guardrail patterns** for domain compliance

Present synthesized insights:
"Based on your {llm_model} selection and {use_case} requirements, here's what the knowledge base tells us about prompt engineering..."

**Key Pattern to Surface:**
> Effective system prompts follow a clear structure: Role/Persona → Task Description → Context Format → Output Constraints → Examples. This separation of concerns makes prompts maintainable and testable.

**Key Warning to Surface:**
> Potential for meaning fumbling - assuming perfect code guarantees correct meaning transmission to the model. Account for linguistic factors that can distort your original intent before reaching the LLM.

### 2.1 Architecture-Specific Prompting Paths

**Conditional queries based on architecture from sidecar.yaml:**

**IF architecture == "rag-only":**
- Heavy focus on context integration instructions
- Citation and source attribution patterns
- Grounding responses in retrieved content
```
Endpoint: search_knowledge
Query: "rag prompting context-grounding citation"
```
Key concerns: Context window management, source attribution, handling insufficient context

**IF architecture == "fine-tuning":**
- Leverage model's learned behaviors from training
- Less instruction needed for trained tasks
- Focus on edge case handling and guardrails
```
Endpoint: search_knowledge
Query: "fine-tuned model prompting {training_objective}"
Example: "fine-tuned model prompting classification"
```
Key concerns: Avoiding prompt-training conflicts, calibrating confidence

**IF architecture == "hybrid":**
- Balance RAG context with model's fine-tuned knowledge
- Clear instructions on when to use retrieved vs learned info
```
Endpoint: search_knowledge
Query: "hybrid rag fine-tuned prompting strategies"
```
Key concerns: Knowledge source prioritization, consistency between RAG and FT responses

### 3. System Prompt Design

**A. Persona Definition**

"Let's define how the LLM should present itself:"

| Aspect | Question | Example |
|--------|----------|---------|
| **Role** | What is the assistant? | "You are a technical support specialist" |
| **Expertise** | What does it know? | "Expert in cloud infrastructure" |
| **Tone** | How should it communicate? | "Professional but friendly" |
| **Constraints** | What should it NOT do? | "Never provide pricing estimates" |
| **Identity** | Company/product name? | "Assistant for Acme Corp" |

Ask: "Describe the ideal persona for your assistant. Who is it, and how should it behave?"

**B. Task Instructions**

"Define the primary task(s):"

```markdown
## Task Structure Template

### Primary Task
[Main thing the assistant does]

### Subtasks (if applicable)
1. [Subtask 1]
2. [Subtask 2]

### Task Boundaries
- MUST: [Required behaviors]
- SHOULD: [Preferred behaviors]
- MUST NOT: [Forbidden behaviors]
```

**C. Context Integration Instructions**

"How should retrieved context be used?"

```markdown
## Context Usage Instructions

You will receive context between <context> tags. Follow these rules:

1. Base your answers ONLY on the provided context
2. If context doesn't contain the answer, say "I don't have information about that"
3. Never invent or assume information not in the context
4. Cite sources when available using [Source: filename]
```

**D. System Prompt Template**

```markdown
# System Prompt v1.0

## Role
You are [persona description]. Your expertise includes [areas of expertise].

## Task
Your primary task is to [main task description].

When responding:
- [Instruction 1]
- [Instruction 2]
- [Instruction 3]

## Context
You will receive relevant context from our knowledge base. Use it as follows:
- Base answers on provided context
- Acknowledge when context is insufficient
- Cite sources when possible

## Constraints
- [Constraint 1]
- [Constraint 2]
- [Constraint 3]

## Output Format
[Format instructions - see next section]
```

### 4. Output Formatting Design

**A. Response Format Selection**

"How should responses be structured?"

**Query Knowledge MCP (Contextualized):**
Based on your output requirements:
- Use case: {use_case from business-requirements}
- Downstream system: {integration_target}
- LLM model: {llm_model from tech-stack}

```
Endpoint: get_patterns
Topic: "output formatting {llm_model} {use_case}"
Example: "output formatting gpt-4 structured-extraction"
```

**Synthesis:** Present format options that work well with chosen LLM and downstream integration needs. The knowledge base will return format patterns optimized for your specific model's capabilities (e.g., Claude's native JSON mode, GPT-4's function calling).

Ask: "What format do your downstream systems or users expect? Based on your {llm_model} and {integration_target}, the knowledge base suggests these patterns work best..."

**B. Format Enforcement**

```yaml
output_format:
  type: "[free-form | structured | markdown | templated]"

  # For structured output
  structured:
    schema_format: "[json | xml | yaml]"
    schema: |
      {
        "answer": "string",
        "confidence": "high|medium|low",
        "sources": ["array of source references"]
      }
    enforce_schema: true

  # For markdown output
  markdown:
    allowed_elements:
      - headers
      - lists
      - code_blocks
      - links
    max_length: [tokens or characters]

  # For templated output
  template: |
    **Answer:** {answer}

    **Confidence:** {confidence}

    **Sources:**
    {sources_list}
```

**C. Output Instructions in Prompt**

```markdown
## Output Format

Always respond in the following format:

### Answer
[Your response to the question]

### Confidence
[HIGH | MEDIUM | LOW] - based on context relevance

### Sources
- [Source 1]
- [Source 2]

If you cannot answer from the provided context, respond with:
"I don't have enough information to answer this question. Could you provide more details about [specific aspect]?"
```

### 5. Few-Shot Examples Design

**A. Example Strategy**

"Do you need few-shot examples?"

| Scenario | Recommendation |
|----------|----------------|
| **Simple Q&A** | Usually not needed |
| **Specific format** | 1-3 examples helpful |
| **Complex reasoning** | Chain-of-thought examples |
| **Domain-specific** | Domain examples important |
| **Classification** | One example per class |

Ask: "Are there specific response patterns that examples would help reinforce?"

**B. Example Template**

```markdown
## Examples

### Example 1: [Category/Type]

**User:** [Example question]

**Context:**
[Example retrieved context]

**Assistant:**
[Ideal response demonstrating format and behavior]

---

### Example 2: [Category/Type]

**User:** [Example question]

**Context:**
[Example retrieved context - or "No relevant context found"]

**Assistant:**
[Ideal response for edge case]
```

**C. Dynamic Example Selection**

```yaml
few_shot:
  strategy: "[static | dynamic | none]"

  static_examples:
    - type: "standard_query"
      example_file: "examples/standard.md"
    - type: "no_context"
      example_file: "examples/no_context.md"

  dynamic_selection:
    enabled: true
    method: "semantic_similarity"
    example_pool_size: 50
    select_count: 2
```

### 6. Guardrails and Safety Design

**Query Knowledge MCP for Guardrails (Contextualized):**

```
Endpoint: get_patterns
Topic: "guardrails {domain} {compliance_requirements}"
Example: "guardrails healthcare hipaa-compliance"
```

```
Endpoint: get_warnings
Topic: "prompt injection {llm_model}"
Example: "prompt injection claude-3"
```

**Synthesis:** Surface domain-specific guardrail requirements and LLM-specific vulnerabilities from the knowledge base. Present guardrail categories that match the user's compliance needs and threat model.

**A. Content Guardrails**

"What content restrictions apply? Based on your {domain} and {compliance_requirements}, here are the recommended guardrail categories..."

Query results will inform guardrail priorities - for example:
- Healthcare domains: HIPAA compliance, PHI protection
- Financial domains: PCI-DSS, financial advice disclaimers
- General domains: PII, harmful content, off-topic filtering

**B. Input Guardrails**

```yaml
input_guardrails:
  max_length: [tokens]
  content_filter:
    enabled: true
    block_categories:
      - jailbreak_attempts
      - prompt_injection
      - harmful_requests

  validation:
    - name: "Language check"
      check: "Is input in supported language?"
      action: "Request supported language"
```

**C. Output Guardrails**

```yaml
output_guardrails:
  content_filter:
    enabled: true
    block_categories:
      - pii_exposure
      - harmful_content
      - competitive_mentions

  format_validation:
    enabled: true
    retry_on_failure: true
    max_retries: 2

  length_limits:
    min_tokens: 10
    max_tokens: 2000
```

**D. Guardrail Messages**

```yaml
guardrail_messages:
  blocked_input: "I'm not able to help with that request. Is there something else I can assist you with?"

  off_topic: "That's outside my area of expertise. I'm here to help with [domain]. How can I assist you with that?"

  no_pii: "I noticed some personal information in my response. For privacy, I'll provide a general answer instead."

  uncertain: "I'm not confident about this answer based on the available information. You may want to verify with [suggested source]."
```

### 7. Conversation Management (If Applicable)

**A. Multi-Turn Configuration**

```yaml
conversation:
  enabled: true
  history_management:
    max_turns: 10
    strategy: "[sliding_window | summarize | compress]"

  context_carryover:
    enabled: true
    method: "[full | summarized | key_points]"

  turn_boundaries:
    detect_topic_change: true
    reset_on_topic_change: false
```

**B. Conversation Instructions**

```markdown
## Conversation Handling

When the user asks follow-up questions:
1. Reference previous context when relevant
2. Don't repeat information already provided
3. Ask clarifying questions if the follow-up is ambiguous
4. Acknowledge topic changes: "I see you'd like to discuss [new topic]..."
```

### 8. Document Decisions

Once user confirms prompting strategy, create specifications.

**Update sidecar.yaml:**
```yaml
currentStep: 7
stepsCompleted: [1, 2, 3, 4, 6, 7]  # 5 skipped if RAG-only
phases:
  phase_3_inference:
    rag_pipeline: "complete"
    prompt_engineering: "designed"
decisions:
  - id: "PROMPT-001"
    step: 7
    choice: "[persona/role design]"
    rationale: "[rationale]"
  - id: "PROMPT-002"
    step: 7
    choice: "[output format]"
    rationale: "[rationale]"
  - id: "PROMPT-003"
    step: 7
    choice: "[guardrail strategy]"
    rationale: "[rationale]"
```

**Create prompt-engineering-spec.md:**
```markdown
# Prompt Engineering Specification

## Persona
- **Role:** [role description]
- **Expertise:** [areas]
- **Tone:** [communication style]
- **Identity:** [name/brand]

## System Prompt
See: system-prompt.md

## Output Format
- **Type:** [format type]
- **Schema:** [if structured]
- **Constraints:** [length, style]

## Few-Shot Examples
- **Strategy:** [static | dynamic | none]
- **Count:** [number of examples]
- **Categories:** [example types]

## Guardrails
### Input
- [Input guardrail 1]
- [Input guardrail 2]

### Output
- [Output guardrail 1]
- [Output guardrail 2]

### Messages
[Guardrail message templates]

## Conversation (if applicable)
- **Max Turns:** [number]
- **History Strategy:** [strategy]
```

**Create system-prompt.md:**
```markdown
# System Prompt v1.0

[Full system prompt content]

---

## Version History
- v1.0 ({date}): Initial version

## Testing Notes
[Notes from prompt testing]
```

**Append to decision-log.md:**
```markdown
## PROMPT-001: Persona Design

**Decision:** [persona summary]
**Date:** {date}
**Step:** 7 - Prompt Engineer

**Rationale:** [explanation]

---

## PROMPT-002: Output Format

**Decision:** [format type]
**Date:** {date}
**Step:** 7 - Prompt Engineer

**Rationale:** [explanation]

---

## PROMPT-003: Guardrail Strategy

**Decision:** [guardrail approach]
**Date:** {date}
**Step:** 7 - Prompt Engineer

**Rationale:** [explanation]
```

### 9. Generate Prompt Engineering Stories

Based on the prompting strategy, generate implementation stories:

```yaml
stories:
  step_7_prompts:
    - id: "PROMPT-S01"
      title: "Implement system prompt management"
      description: "Build system prompt loading and versioning"
      acceptance_criteria:
        - "System prompt loaded from file"
        - "Prompt versioning supported"
        - "Environment-specific prompts possible"
        - "Prompt testing framework in place"

    - id: "PROMPT-S02"
      title: "Build output formatter"
      description: "Implement output parsing and validation"
      acceptance_criteria:
        - "Output parsed to required format"
        - "Schema validation working"
        - "Retry logic for malformed outputs"
        - "Fallback handling implemented"

    - id: "PROMPT-S03"
      title: "Implement few-shot example system"
      description: "Build example selection and injection"
      acceptance_criteria:
        - "Example pool created"
        - "Selection logic working"
        - "Examples injected into prompt"
        - "Performance impact measured"

    - id: "PROMPT-S04"
      title: "Build guardrail system"
      description: "Implement input and output guardrails"
      acceptance_criteria:
        - "Input filtering working"
        - "Output filtering working"
        - "Guardrail messages displayed"
        - "Logging for guardrail triggers"

    - id: "PROMPT-S05"
      title: "Implement conversation management"
      description: "Build multi-turn conversation handling"
      acceptance_criteria:
        - "History tracking working"
        - "Context carryover implemented"
        - "Turn limits enforced"
        - "Topic change detection (if needed)"
```

**Update sidecar with stories:**
```yaml
stories:
  step_7_prompts:
    - "[story list based on prompting design]"
```

### 10. Present MENU OPTIONS

Display: **Step 7 Complete - Select an Option:** [A] Analyze prompting further [Q] Re-query Knowledge MCP with different constraints [P] View progress [C] Continue to Step 8 (LLM Evaluator)

#### EXECUTION RULES:

- ALWAYS halt and wait for user input after presenting menu
- ONLY proceed to next step when user selects 'C'
- User can chat or ask questions - always respond and redisplay menu

#### Menu Handling Logic:

- IF A: Revisit prompting decisions, allow refinement, then redisplay menu
- IF Q: Ask user to modify constraints (tone, format requirements, guardrail strictness), re-run queries with updated context, present updated recommendations from knowledge base, redisplay menu
- IF P: Show prompt-engineering-spec.md, system-prompt.md, and decision-log.md summaries, then redisplay menu
- IF C:
  1. Verify sidecar is updated with prompting decisions and stories
  2. Load, read entire file, then execute `{nextStepFile}` (LLM Evaluator)
- IF Any other comments or queries: help user respond then redisplay menu

## CRITICAL STEP COMPLETION NOTE

ONLY WHEN 'C' is selected AND prompting strategy is documented AND stories are generated, will you then immediately load, read entire file, then execute `{nextStepFile}` to begin Step 8: LLM Evaluator.

---

## SYSTEM SUCCESS/FAILURE METRICS

### SUCCESS:

- Knowledge MCP queried for prompting patterns
- Persona and system prompt designed
- Output format specified with enforcement strategy
- Few-shot example strategy defined
- Guardrails configured for input and output
- Conversation handling designed (if applicable)
- prompt-engineering-spec.md created
- system-prompt.md created
- decision-log.md updated with PROMPT decisions
- Stories generated for prompt engineering
- User confirmed design before proceeding

### SYSTEM FAILURE:

- Making prompting decisions without user input
- Skipping Knowledge MCP queries
- Not documenting decisions in required files
- Discussing retrieval logic (belongs in Step 6)
- Discussing evaluation metrics (belongs in Step 8)
- Proceeding without confirmed design
- Not generating implementation stories
- Creating system prompt without user approval

**Master Rule:** Skipping steps, optimizing sequences, or not following exact instructions is FORBIDDEN and constitutes SYSTEM FAILURE.
