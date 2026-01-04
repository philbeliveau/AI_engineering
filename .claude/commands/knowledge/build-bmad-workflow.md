# Build BMAD Workflow from Knowledge Base

Help build a BMAD workflow by querying the knowledge base for relevant methodologies, patterns, and decisions.

**Workflow Building Process:**

1. First, understand what workflow the user wants to build: $ARGUMENTS

2. Query the knowledge base for relevant content:
   - Use `/knowledge:get-methodologies` for step-by-step processes
   - Use `/knowledge:get-patterns` for implementation patterns
   - Use `/knowledge:get-decisions` for decision points to include
   - Use `/knowledge:get-warnings` for pitfalls to avoid

3. Synthesize findings into a BMAD workflow structure:
   - Define the workflow trigger and purpose
   - Map methodology steps to workflow steps
   - Include decision points from extracted decisions
   - Add validation checkpoints from patterns
   - Include warnings as guardrails

4. Output the workflow in BMAD format using `/bmad:bmb:workflows:create-workflow`

**Note:** This command orchestrates multiple knowledge queries to inform workflow creation.
