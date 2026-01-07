# AI Engineering Workflow - Production Deployment Checklist

**Workflow Version:** 2.0.0
**Deployment Date:** January 6, 2026
**Status:** Ready for Production Deployment
**Sign-Off Required:** Tech Lead + Infrastructure Team

---

## Section 1: Core Workflow Files (11 Items)

### Agent Definitions (11 Files)
- [ ] **business-analyst.md** - Requirements elicitation specialist (1,234 lines)
  - Personas and expertise defined
  - Communication style documented
  - Knowledge MCP integration verified
  - No broken references to external files

- [ ] **fti-architect.md** - FTI pipeline architect (1,225 lines)
  - Architecture decision patterns included
  - Trade-off analysis framework documented
  - Tech stack selection criteria specified
  - Knowledge MCP queries configured

- [ ] **data-engineer.md** - Data pipeline specialist (2,440 lines)
  - Data requirements gathering process
  - Pipeline design patterns
  - Quality assurance checks
  - Knowledge MCP for data patterns

- [ ] **embeddings-engineer.md** - Vector embeddings specialist (1,121 lines)
  - Chunking strategy guidance
  - Embedding model selection
  - Vector database configuration
  - Knowledge MCP embedding patterns

- [ ] **fine-tuning-specialist.md** - Model customization expert (1,182 lines)
  - SFT/DPO configuration
  - Dataset preparation methodology
  - Training validation criteria
  - Knowledge MCP training patterns

- [ ] **rag-specialist.md** - RAG pipeline specialist (1,157 lines)
  - Retrieval strategy design
  - Reranking configuration
  - Context window optimization
  - Knowledge MCP RAG patterns

- [ ] **prompt-engineer.md** - Prompt design specialist (1,178 lines)
  - System prompt templates
  - Few-shot example structure
  - Evaluation criteria
  - Knowledge MCP prompt patterns

- [ ] **llm-evaluator.md** - Evaluation specialist (1,195 lines)
  - Evaluation framework design
  - Metrics selection guidance
  - Benchmark integration
  - Knowledge MCP evaluation patterns

- [ ] **mlops-engineer.md** - Production ML specialist (1,209 lines)
  - Monitoring configuration
  - Drift detection setup
  - Alert thresholds
  - Knowledge MCP ops patterns

- [ ] **tech-lead.md** - Technical leadership (1,269 lines)
  - Review and validation logic
  - Conflict resolution procedures
  - Story sequencing rules
  - Handoff checklist

- [ ] **dev.md** - Development reference (1,414 lines)
  - Implementation patterns
  - Code generation guidance
  - Testing requirements
  - Documentation standards

---

## Section 2: Agent Configuration Files (11 Items)

### XML Agent Configurations in `agents/config/`
- [ ] **business-analyst-agent.xml** - Configuration verified
- [ ] **fti-architect-agent.xml** - Configuration verified
- [ ] **data-engineer-agent.xml** - Configuration verified
- [ ] **embeddings-engineer-agent.xml** - Configuration verified
- [ ] **fine-tuning-specialist-agent.xml** - Configuration verified
- [ ] **rag-specialist-agent.xml** - Configuration verified
- [ ] **prompt-engineer-agent.xml** - Configuration verified
- [ ] **llm-evaluator-agent.xml** - Configuration verified
- [ ] **mlops-engineer-agent.xml** - Configuration verified
- [ ] **tech-lead-agent.xml** - Configuration verified
- [ ] **dev-agent.xml** - Configuration verified

**Verification Tasks for Each:**
- [ ] XML syntax valid (no parsing errors)
- [ ] Agent references correct markdown file
- [ ] Tool definitions match workflow needs
- [ ] No hardcoded paths (uses variables)
- [ ] Knowledge MCP endpoints correct

---

## Section 3: Workflow Steps (11 Items)

### Phase 0: Scoping (Steps 1-2B)
- [ ] **step-01-business-analyst.md** - Initial requirements gathering
  - User input collection framework
  - Stakeholder analysis template
  - Use case documentation
  - Metrics definition
  - Knowledge MCP business queries

- [ ] **step-02a-fti-architect.md** - Build vs Buy analysis
  - Architecture decision framework
  - RAG vs Fine-tuning trade-offs
  - Knowledge MCP architecture patterns
  - Output: architecture-decision.md generated

- [ ] **step-02b-tech-stack.md** - Technology selection
  - Model selection criteria
  - Framework comparison
  - Infrastructure requirements
  - Knowledge MCP tech stack patterns
  - Input: Reads architecture-decision.md
  - Output: tech-stack-decision.md generated

### Phase 1: Feature Engineering (Steps 3-4)
- [ ] **step-03a-data-requirements.md** - Data feasibility assessment
  - Data availability analysis
  - Quality assessment framework
  - Privacy/compliance checklist
  - Knowledge MCP data patterns
  - Inputs: architecture-decision.md, tech-stack-decision.md
  - Output: data-requirements.md generated

- [ ] **step-03b-data-pipeline.md** - Data pipeline design
  - Ingestion workflow design
  - Processing pipeline architecture
  - Quality validation rules
  - Knowledge MCP pipeline patterns
  - Input: data-requirements.md
  - Output: data-pipeline-spec.md generated

- [ ] **step-04-embeddings-engineer.md** - Embeddings configuration
  - Chunking strategy selection
  - Embedding model evaluation
  - Vector database setup
  - Knowledge MCP embedding patterns

### Phase 2: Training (Step 5 - Conditional)
- [ ] **step-05-fine-tuning-specialist.md** - Training configuration
  - SFT/DPO setup guide
  - Dataset preparation (conditional)
  - Validation criteria
  - Knowledge MCP training patterns
  - CONDITIONAL: Skipped if architecture == "rag-only"

### Phase 3: Inference (Steps 6-7)
- [ ] **step-06-rag-specialist.md** - RAG pipeline design
  - Retrieval system architecture
  - Reranking configuration
  - Context optimization
  - Knowledge MCP RAG patterns

- [ ] **step-07-prompt-engineer.md** - Prompt engineering
  - System prompt design
  - Few-shot example selection
  - Prompt testing framework
  - Knowledge MCP prompt patterns

### Phase 4: Evaluation (Step 8)
- [ ] **step-08-llm-evaluator.md** - Evaluation framework
  - Metric selection methodology
  - Benchmark setup
  - Quality gate criteria
  - Knowledge MCP evaluation patterns

### Phase 5: Operations (Step 9)
- [ ] **step-09-mlops-engineer.md** - Monitoring and alerting
  - Monitoring dashboard setup
  - Drift detection configuration
  - Alert thresholds
  - Knowledge MCP ops patterns

### Phase 6: Integration (Steps 10-11)
- [ ] **step-10-tech-lead.md** - Integration review
  - Consistency validation
  - Conflict detection
  - Story sequencing
  - GO/REVISE decision
  - Feedback loop logic

- [ ] **step-11-story-elaborator.md** - BMM handoff
  - Story transformation logic
  - Task elaboration framework
  - Developer notes generation
  - BMM format compliance

---

## Section 4: Configuration Files (5 Items)

- [ ] **config.yaml** - Master workflow configuration
  - Path variables all use {variables} syntax
  - Knowledge MCP endpoints verified (Production URL)
  - Phase structure correct (7 phases)
  - Step sequence matches actual files
  - Story prefixes defined for all steps
  - Agent roster complete (11 agents)
  - Sidecar template structure valid
  - BMM integration endpoints correct

- [ ] **templates/sidecar.template.yaml** - Project state tracking template
  - All required fields present (project_name, currentStep, etc.)
  - Phase tracking keys match phase_folders in config.yaml
  - Stories object structure defined

- [ ] **templates/project-context.template.md** - Context for agents
  - Placeholder variables for substitution
  - Knowledge MCP integration points noted
  - Format compatible with all agents

- [ ] **templates/bmm-story.template.md** - BMM story format
  - All required sections present
  - Task structure correct
  - Acceptance criteria format defined
  - Dev notes template included

- [ ] **templates/project-spec.template.md** - Project specification
  - Requirements structure
  - Architecture placeholder
  - Metrics framework

---

## Section 5: Config Templates (5 Items)

### Configuration Template Files in `templates/config-templates/`
- [ ] **embedding-config.template.yaml** - Embeddings configuration template
- [ ] **training-config.template.yaml** - Training configuration template
- [ ] **chunking-config.template.yaml** - Chunking strategy template
- [ ] **deployment-config.template.yaml** - Deployment configuration template
- [ ] **alerts-config.template.yaml** - Alert configuration template

**Verification:**
- [ ] All templates use YAML syntax
- [ ] Placeholder variables clearly marked
- [ ] Default values reasonable
- [ ] Comments explain configuration options

---

## Section 6: Checklists and Guides (4 Items)

- [ ] **checklists/step-01-completion-checklist.md** - Requirements gathering checklist
  - All items numbered
  - Clear completion criteria
  - Sign-off points defined

- [ ] **checklists/tech-lead-consistency-checklist.md** - Integration validation
  - All consistency checks listed
  - Conflict detection criteria
  - Feedback loop instructions

- [ ] **checklists/quality-gate-checklist.md** - Final validation
  - Go/No-go criteria
  - Sign-off requirements
  - Rollback trigger conditions

- [ ] **checklists/CHECKLIST-DESIGN-NOTES.md** - Checklist development notes
  - Design rationale documented
  - Future improvement notes

---

## Section 7: Documentation Files (2 Items)

- [ ] **workflow.md** - Main workflow documentation (18,973 lines)
  - Complete step-by-step guide
  - Architecture explanation
  - Agent roster with icons
  - Processing rules documented
  - Knowledge MCP integration explained

- [ ] **workflow-plan-ai-engineering-workflow.md** - Planning document (14,215 lines)
  - Implementation plan
  - Design decisions
  - Phase breakdown

---

## Section 8: Knowledge MCP Integration Verification (7 Items)

- [ ] **Knowledge MCP Production URL verified**
  - URL: https://knowledge-mcp-production.up.railway.app
  - Endpoint: /mcp
  - Status: Production ready
  - Fallback: None (primary endpoint)

- [ ] **Search Knowledge tool** - Semantic search across all knowledge
  - Used in: All agent steps
  - Response format: Consistent
  - Error handling: Documented

- [ ] **Get Decisions tool** - Architectural decisions with trade-offs
  - Used in: Steps 2A, 2B, 3A
  - Response includes: Decision, trade-offs, constraints
  - Error handling: Fallback documented

- [ ] **Get Patterns tool** - Reusable implementation patterns
  - Used in: Steps 3, 4, 5, 6, 7, 8, 9
  - Response includes: Pattern, example, prerequisites
  - Error handling: Fallback documented

- [ ] **Get Warnings tool** - Anti-patterns and pitfalls
  - Used in: All decision points
  - Response includes: Warning, cause, mitigation
  - Error handling: Fallback documented

- [ ] **Get Methodologies tool** - Step-by-step processes
  - Used in: Steps 3, 4, 5, 6, 7, 8, 9
  - Response includes: Steps, timing, dependencies
  - Error handling: Fallback documented

- [ ] **List Sources tool** - Available knowledge sources
  - Used in: Reference sections
  - Response includes: Source metadata, coverage areas
  - Documented in: workflow.md

---

## Section 9: File Integrity Checks (15 Items)

- [ ] **No broken markdown links** - All internal references valid
  - Agents referenced in config exist
  - Steps referenced in config exist
  - Templates referenced in steps exist
  - Checklists referenced in steps exist

- [ ] **No hardcoded file paths** - All paths use {variables}
  - {workflow_path} for workflow root
  - {output_folder} for project outputs
  - {project_name} for project-specific paths
  - {nextStepFile} for step transitions

- [ ] **No hardcoded values in workflow** - All values come from MCP or user input
  - Model recommendations: From Knowledge MCP
  - Tech stack options: From Knowledge MCP
  - Evaluation metrics: From Knowledge MCP
  - Best practices: From Knowledge MCP

- [ ] **All step transitions documented** - Each step knows next step
  - Step 1 → Step 2A
  - Step 2A → Step 2B
  - Step 2B → Step 3A (conditional on scoping)
  - Step 3A → Step 3B
  - Step 3B → Step 4
  - Step 4 → Step 5 (conditional on architecture)
  - Step 5 → Step 6 (skip if rag-only)
  - Step 6 → Step 7
  - Step 7 → Step 8
  - Step 8 → Step 9
  - Step 9 → Step 10
  - Step 10 → Step 11 (if approved)

- [ ] **All conditional logic clear** - Conditions well-documented
  - Phase 2 (Training): Skip if architecture == "rag-only"
  - Step 5: Only if fine-tuning selected
  - Step 10: May redirect to previous phases for revision

- [ ] **All agent handoffs documented** - Clear context passing
  - Each step includes "Handoff Context" section
  - Previous step outputs listed
  - Next step expectations clear

- [ ] **All user confirmation checkpoints present**
  - Step 1: Requirements approval needed
  - Step 2: Architecture decision confirmation
  - Step 3: Data assessment sign-off
  - Step 8: Quality gate GO/NO-GO
  - Step 10: Tech Lead final approval

- [ ] **Story generation configured** - All steps can generate stories
  - Story ID prefixes defined in config
  - Template format specified
  - Acceptance criteria structure defined
  - Task elaboration rules documented

- [ ] **No version mismatches** - Consistency across files
  - workflow.md version: 1.0.0 (upgrading to 2.0.0)
  - config.yaml version: 1.0.0 (upgrading to 2.0.0)
  - All agents aligned
  - All steps aligned

- [ ] **XML configurations valid** - No malformed XML
  - All 11 agent XML files parse correctly
  - No missing closing tags
  - All attributes properly quoted
  - File encoding correct (UTF-8)

- [ ] **YAML configurations valid** - Proper YAML syntax
  - config.yaml: Parses without errors
  - All template YAML files: Valid syntax
  - Indentation consistent (2 spaces)
  - No tab characters used

- [ ] **Markdown syntax valid** - All markdown files parse
  - Proper heading hierarchy
  - Code blocks closed
  - Links properly formatted
  - Tables properly aligned

- [ ] **All external resources verified** - URLs and endpoints checked
  - Knowledge MCP production URL: Live and responding
  - BMAD agent references: Correct format (/bmad:bmm:agents:dev)
  - GitHub references: Valid and accessible (if any)

- [ ] **No encoding issues** - Files use UTF-8 encoding
  - No special characters breaking parsing
  - No BOM markers in files
  - Special characters properly escaped

---

## Section 10: Performance and Scale Verification (6 Items)

- [ ] **Workflow latency acceptable**
  - Average step execution: < 5 minutes
  - Agent context loading: < 1 minute
  - Knowledge MCP queries: < 2 seconds
  - Story generation: < 3 minutes

- [ ] **Concurrent execution safe**
  - No race conditions in file writes
  - sidecar.yaml locking mechanism verified
  - Step isolation confirmed
  - No shared state corruption

- [ ] **Large project support**
  - Can handle 50+ user stories
  - Can handle 20+ decisions
  - Can handle 100+ Knowledge MCP queries
  - Output folder structure scalable

- [ ] **Memory footprint acceptable**
  - Agent context: < 10MB per step
  - Step file size: All < 50KB
  - Config files: < 1MB total
  - No memory leaks in agent loops

- [ ] **Storage requirements documented**
  - Estimated project output: 5-15MB
  - Workflow package: 2MB (all files)
  - Template storage: 500KB
  - Scaling to 100 projects: 1.5GB

- [ ] **Network dependency minimal**
  - Only Knowledge MCP requires network
  - Can proceed without network (degraded mode)
  - Fallback answers documented
  - Offline mode instructions available

---

## Section 11: Security and Compliance (8 Items)

- [ ] **No hardcoded credentials** - All secrets use variables
  - MongoDB connection: From environment
  - API keys: From environment
  - Service tokens: From environment
  - No test credentials left in code

- [ ] **Access control proper** - File permissions correct
  - Agent files: Readable by all roles
  - Step files: Readable by all roles
  - Config files: Readable, not writable
  - Output folders: Project-specific permissions

- [ ] **Data privacy respected** - No PII in templates
  - No example email addresses
  - No example phone numbers
  - No example social security numbers
  - Privacy checklist included in Step 3A

- [ ] **Compliance documented** - GDPR/regulatory requirements
  - Data handling documented in Step 3A
  - Compliance checklist in data-engineer.md
  - Privacy-by-design principles followed
  - Data retention policy referenced

- [ ] **Knowledge MCP security verified**
  - HTTPS endpoint used (not HTTP)
  - No credentials in workflow config
  - API authentication delegated to environment
  - Rate limiting documented

- [ ] **Agent prompts safe** - No prompt injection vectors
  - User input escaped properly
  - No direct substitution of user input
  - Output validation enforced
  - Fallback answers for malicious input

- [ ] **Workflow state protected** - sidecar.yaml secure
  - No sensitive data stored
  - File permissions restrictive
  - Backup mechanism documented
  - Corruption detection implemented

- [ ] **Audit trail available** - All decisions logged
  - Decision log template included
  - Timestamps recorded
  - User attribution possible
  - Immutable audit log recommended

---

## Section 12: Testing and Quality Assurance (8 Items)

- [ ] **Unit test coverage** - Each component testable
  - Agent personas: Can be tested in isolation
  - Step logic: Can be validated independently
  - Template generation: Can be verified
  - Configuration parsing: Can be tested

- [ ] **Integration test readiness** - End-to-end scenarios
  - Happy path: Step 1→11 execution
  - Branch path: RAG-only architecture
  - Branch path: Fine-tuning required
  - Error path: User revision loops

- [ ] **Test data prepared** - Sample project data
  - Sample requirements.md provided (or template)
  - Sample architecture-decision.md provided
  - Sample data-requirements.md provided
  - Sample story output provided

- [ ] **Quality metrics defined** - Success criteria clear
  - Story completeness: 95%+ acceptance criteria
  - Decision documentation: All decisions recorded
  - Knowledge MCP coverage: 90%+ of decisions from MCP
  - Step duration: Average < 5 min/step

- [ ] **Acceptance testing planned** - Real-world scenarios
  - Test Scenario 1: Simple RAG chatbot
  - Test Scenario 2: Fine-tuned domain assistant
  - Test Scenario 3: Hybrid RAG + fine-tuning
  - Test Scenario 4: User revisions workflow

- [ ] **Load testing performed** - Concurrent users
  - Single user: 11 steps, ~45 minutes
  - Multiple users: No interference
  - Knowledge MCP: Rate limiting acceptable
  - Storage: No scalability issues

- [ ] **Regression testing prepared** - Changes won't break
  - Baseline performance captured
  - Before/after metrics plan
  - Known issues documented
  - Future compatibility guaranteed

- [ ] **User acceptance testing scheduled** - Real users test
  - UAT date: [From deployment plan]
  - Test users: AI engineering team
  - Success criteria: All steps executable
  - Sign-off: Product manager + tech lead

---

## Section 13: Documentation Completeness (5 Items)

- [ ] **User documentation complete**
  - Getting started guide (OPERATIONS_GUIDE.md)
  - Step-by-step instructions (workflow.md)
  - Troubleshooting guide (in OPERATIONS_GUIDE.md)
  - FAQ section (in OPERATIONS_GUIDE.md)

- [ ] **Operator documentation complete**
  - Deployment procedure (DEPLOYMENT_PLAN.md)
  - Rollback instructions (ROLLBACK_PROCEDURE.md)
  - Monitoring dashboard setup (in OPERATIONS_GUIDE.md)
  - Incident response procedures (in OPERATIONS_GUIDE.md)

- [ ] **Developer documentation complete**
  - Architecture overview (workflow.md)
  - Code structure explanation (in workflow.md)
  - Extension points documented (in workflow.md)
  - Contributing guidelines (in VERSION_NOTES.md)

- [ ] **API documentation complete**
  - Knowledge MCP endpoints documented
  - Agent activation documented
  - Story output format documented
  - Error handling documented

- [ ] **Change log complete**
  - Version 2.0.0 changes documented (VERSION_NOTES.md)
  - Breaking changes identified
  - Migration path provided
  - Deprecations noted

---

## Section 14: Deployment Readiness (6 Items)

- [ ] **All files in correct location**
  - Workflow: /ai-engineering-workflow/
  - Agents: /ai-engineering-workflow/agents/
  - Steps: /ai-engineering-workflow/steps/
  - Config: /ai-engineering-workflow/config.yaml
  - Checklists: /ai-engineering-workflow/checklists/
  - Templates: /ai-engineering-workflow/templates/

- [ ] **All dependencies resolved**
  - BMAD framework available
  - Knowledge MCP accessible
  - Claude Code compatible
  - No missing external tools

- [ ] **Environment configuration ready**
  - Knowledge MCP endpoint in claude_desktop_config.json
  - BMAD paths correct
  - Project folders writable
  - Backups scheduled

- [ ] **Rollback plan verified**
  - Previous version archived
  - Rollback procedure documented
  - Smoke test procedure defined
  - Go-back decision criteria clear

- [ ] **Monitoring instrumentation complete**
  - Step execution logging
  - Knowledge MCP query logging
  - Error tracking
  - Performance metrics collection

- [ ] **Incident response plan ready**
  - On-call contact defined
  - Escalation procedure documented
  - Known issues documented
  - Workarounds provided

---

## Section 15: Sign-Off and Approval (5 Items)

- [ ] **Technical Lead review complete**
  - Workflow architecture reviewed
  - Agent personas validated
  - Knowledge MCP integration verified
  - Story output format approved

- [ ] **Product Manager approval obtained**
  - User journey satisfactory
  - Requirements completeness confirmed
  - Acceptance criteria clear
  - Success metrics defined

- [ ] **Infrastructure team sign-off**
  - Knowledge MCP production status verified
  - Database connections tested
  - Scaling plan reviewed
  - Backup and recovery tested

- [ ] **Security review completed**
  - No hardcoded credentials
  - Access control proper
  - Data handling compliant
  - Audit trail implemented

- [ ] **QA team certification**
  - All test cases passed
  - No critical bugs
  - Performance acceptable
  - Ready for production

---

## Final Verification

### Metrics Summary
| Metric | Value | Status |
|--------|-------|--------|
| Total Files | 55 | ✓ Complete |
| Total Lines of Code | 16,429 | ✓ Complete |
| Agent Files | 11 | ✓ Complete |
| Agent Configurations | 11 | ✓ Complete |
| Step Files | 11 | ✓ Complete |
| Config Files | 9 | ✓ Complete |
| Checklist Files | 4 | ✓ Complete |
| Knowledge MCP Integration Points | 50+ | ✓ Complete |
| User Confirmation Points | 5+ | ✓ Complete |
| Documentation Pages | 60+ | ✓ Complete |

### Final Checklist
- [ ] All 50+ items above checked and verified
- [ ] All files tested for syntax errors
- [ ] All configurations validated
- [ ] All references verified
- [ ] Knowledge MCP integration confirmed
- [ ] Security review passed
- [ ] Performance testing passed
- [ ] User acceptance testing scheduled
- [ ] Deployment plan confirmed
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Incident response plan reviewed
- [ ] Documentation complete
- [ ] Team trained and ready

---

## Deployment Authorization

**Deployment Status:** READY FOR PRODUCTION

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tech Lead | [Name] | [Date] | [ ] |
| Product Manager | [Name] | [Date] | [ ] |
| Infrastructure Lead | [Name] | [Date] | [ ] |
| Security Officer | [Name] | [Date] | [ ] |
| QA Lead | [Name] | [Date] | [ ] |

---

## Post-Deployment Verification (After Deployment)

- [ ] All workflow files deployed successfully
- [ ] Knowledge MCP endpoint responding
- [ ] Sample project created and tested
- [ ] All 11 steps executable
- [ ] Story generation working
- [ ] No critical errors in logs
- [ ] Performance metrics normal
- [ ] User feedback positive
- [ ] Rollback plan tested
- [ ] Monitoring dashboards active

**Deployment Complete Date:** [To be filled after deployment]

**Deployment Completed By:** [Name]

**Post-Deployment Sign-Off:** [ ] Yes [ ] No

---

**Document Version:** 2.0.0
**Last Updated:** January 6, 2026
**Next Review Date:** [Q1 2026 or upon major changes]
