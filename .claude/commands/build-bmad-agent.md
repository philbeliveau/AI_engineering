# Build BMAD Agent from Knowledge Base

Help build a BMAD agent by querying the knowledge base for relevant personas, patterns, and expertise areas.

**Agent Building Process:**

1. First, understand what agent the user wants to build: $ARGUMENTS

2. Query the knowledge base for relevant content:
   - Use `/search-knowledge` for persona definitions and role descriptions
   - Use `/get-patterns` for agent interaction patterns
   - Use `/get-methodologies` for processes the agent should know
   - Use `/get-decisions` for decision frameworks the agent uses

3. Synthesize findings into a BMAD agent structure:
   - Define role and responsibilities
   - Extract expertise areas from methodologies
   - Define communication style from patterns
   - Include decision-making frameworks
   - Add domain knowledge from extractions

4. Output the agent in BMAD format using `/bmad:bmb:workflows:create-agent`

**Note:** This command orchestrates multiple knowledge queries to inform agent creation.
