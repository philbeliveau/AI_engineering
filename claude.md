# AI Engineering Workflows - Claude Development Notes

## Project Overview

Building an executable AI engineering knowledge system that transforms methodology books into interactive, context-aware workflows.

**Core Philosophy:** AI doesn't answer - it structures thought and reduces the space where the solution exists.

## Current Status

**Phase:** Concept/Planning
**Brief:** `_bmad-output/AI-Engineering-Workflows-Brief.md`
**Started:** December 30, 2025

## What We're Building

A BMAD module (`aie`) that:
- Guides practitioners through AI engineering decisions
- Generates structured artifacts (specs, architectures, configs)
- Integrates multiple knowledge sources (books, papers, case studies)
- Updates continuously as AI landscape evolves

### Dual Entry Points
1. **Discovery:** Problem → Solution (framing → assessment → implementation)
2. **Implementation:** Direct to specific patterns (RAG, fine-tuning, deployment)

## Monetization Model

**Free Tier:** Core workflows, embedded methodology, public MCP access
**Pro ($19/mo):** Enterprise case studies, advanced workflows, monthly updates
**Enterprise ($99+/mo):** Private MCP, custom workflows, team training

### Protection Strategy
1. Server-side MCP with authentication (primary)
2. Encrypted premium workflows (secondary)
3. Continuous monthly value (retention)

## Technical Stack

**Repository:**
- BMAD module structure (`_bmad/aie/`)
- Agents: ai-architect, llm-specialist, data-engineer, mlops-expert
- Workflows: discovery, rag-systems, fine-tuning, production

**MCP Servers:**
- Scholar MCP (research papers)
- GitHub MCP (code examples)
- Premium MCP (enterprise content, authenticated)

## Source Knowledge

### Books Being Encoded
- LLM Engineer's Handbook (Paul Iusztin, Maxime Labonne) - 800 pages
- LLMs in Production (Christopher Brousseau, Matthew Sharp)

### Additional Sources
- Research papers (via Scholar MCP)
- Medium articles and blog posts
- Enterprise case studies
- GitHub repositories

## Connection to Spec-Forecasting

This project applies the spec-forecasting philosophy to AI engineering:
```
decision = f(
    previous_decisions,
    project_context,
    constraints,
    dataset_characteristics,
    business_requirements
)
```

Like spec-forecasting reduces time series decision space, this system reduces AI engineering decision space.

## Next Steps

1. Validate demand with AI engineers
2. Build first workflows (problem-framing, rag-architecture)
3. Set up MCP server infrastructure
4. Launch public repo (free tier)
5. Build Pro tier with enterprise content

## Working with Claude/BMAD

Using BMAD Builder agent to:
- Create the `aie` module structure
- Design workflows with proper artifact passing
- Integrate knowledge sources effectively
- Follow BMAD best practices

## Open Questions

1. Product name? (AI Engineering Workflows vs Spec-Forecasting for AI)
2. Positioning? (Methodology, platform, or knowledge commons)
3. First 5 workflows to build?
4. Community platform? (Discord vs Slack)
5. Content sourcing strategy?

---

**For full details, see:** `_bmad-output/AI-Engineering-Workflows-Brief.md`
