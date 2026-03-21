---
name: research
effort: medium
context: fork
agent: research-specialist
argument-hint: "[URL or topic]"
description: This skill should be used when analyzing external projects, frameworks, articles, or patterns for competitive intelligence. It applies when the user shares a URL, article, or description of something interesting and wants it documented as a research entry in docs/research/. Triggers on "add this to research", "check this out", sharing URLs of interesting projects, or any request to document competitive analysis for CrewOS.
metadata:
  last_reviewed: 2026-03-20
  review_cycle: 90
---

# Research -- Competitive Intelligence Workflow

## Overview

Analyze external projects, frameworks, articles, and patterns to extract actionable insights for CrewOS. Each entry documents what the project does, its architecture, and -- most importantly -- what CrewOS should steal and where we're already ahead.

## When to Use

- User shares a URL or article about an interesting project/framework
- User wants to document competitive analysis
- User says "add this to research" or similar
- User finds something that could inform CrewOS design decisions

## Workflow

### Step 1: Fetch and Analyze the Source

If a URL is provided, use WebFetch to retrieve the article content. Extract:
- What the project/tool is
- Core architecture and components
- Key features and differentiators
- Problems it solves
- Community sentiment and known limitations

If the user pastes article content directly, skip the fetch and analyze the provided text.

### Step 2: Cross-Reference with CrewOS

Before writing the entry, check what CrewOS already has:
- Read `CREWOS_REFERENCE_GUIDE.md` for existing patterns and decisions
- Check `CLAUDE.md` for current architecture and conventions
- Identify overlaps -- what have we already adopted from this or similar projects?
- Identify gaps -- what new patterns could we steal?

Key CrewOS reference points for comparison:
- Agent composition: main assistant + 6 sub-agents via Mastra (`packages/agents/`)
- Channel adapters: normalized ChannelEvent pattern (`packages/channel-adapters/`)
- Budget-aware routing: IntentClassifier + MODEL_MAP (`packages/ai-gateway/`)
- Enterprise identity: WorkOS SSO/RBAC/audit (`packages/identity/`)
- Memory: Mastra memory with thread/resource scoping
- Gateway: Fastify + WebSocket control plane (`apps/gateway/`)

### Step 3: Write the Research Entry

Load the entry template from `references/entry-template.md` in this skill directory. Create a new file at `docs/research/<project-name>.md` following the template structure.

Key principles for writing entries:
- **Be specific in takeaways** -- reference actual CrewOS packages and files, not vague suggestions
- **"Things we should steal"** should be actionable -- describe what to build, not just what's interesting
- **"What CrewOS already does better"** keeps us grounded -- prevents chasing shiny objects
- **Use `--` for dashes**, not em dashes, for consistency
- **Keep it concise** -- this is a reference library, not a blog

If the project is already a known design influence (like OpenClaw), add a prominent note at the top listing what we've already adopted and frame the entry around what's NEW that we haven't taken yet.

### Step 4: Update the Index

Add a row to the table of contents in `docs/research/README.md`:

```markdown
| [Entry Name](./filename.md) | Category | YYYY-MM-DD |
```

### Step 5: Summarize for the User

After creating the entry, provide a summary highlighting:
- Top 3 patterns worth stealing (ranked by impact)
- Where CrewOS is already ahead
- Any immediate action items or things to flag for upcoming tasks

## Project North Star

Every takeaway should be evaluated through the lens: **does this make the app feel magical to both normies and techies?** If a pattern only impresses developers but confuses normal users, note that. If it delights end users but is technically mediocre, note that too. The best patterns do both.

## Resources

### references/
- `entry-template.md` -- Standard template for new research entries. Load this when creating a new entry to ensure consistent formatting across all entries.
