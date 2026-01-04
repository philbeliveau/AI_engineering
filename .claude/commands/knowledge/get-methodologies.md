---
description: Query step-by-step methodologies and processes (Registered tier)
argument-hint: [methodology type or goal]
---

# Get Methodologies

Query the knowledge base for step-by-step methodologies, processes, and frameworks from AI engineering literature.

## Access Note

This is a **Registered tier** endpoint - requires API key configuration.

## Examples

- `/knowledge:get-methodologies evaluation framework for LLM apps`
- `/knowledge:get-methodologies data pipeline design process`
- `/knowledge:get-methodologies prompt engineering workflow`
- `/knowledge:get-methodologies` (lists all available methodologies)

## Task

Use the knowledge-pipeline MCP server's `get_methodologies` tool to find methodologies about: $ARGUMENTS

If no arguments provided, list all available methodologies with brief descriptions.

## Output Format

Present each methodology with:
- **Name** - Methodology identifier
- **Purpose** - What goal it achieves
- **Prerequisites** - What you need before starting
- **Steps** - Numbered step-by-step process
- **Expected outputs** - What you'll have when done
- **Source** - Book/paper and section

## Usage Tip

Use these methodologies to inform BMAD workflow creation via `/knowledge:build-bmad-workflow`.
