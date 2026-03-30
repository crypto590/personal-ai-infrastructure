---
name: plan
effort: high
model: claude-opus-4-6
context: fork
description: "Full planning pipeline: product → design → engineering. Spawns 3 sub-agents, each adds criteria to a shared feature registry. Output is the complete contract for implementation."
metadata:
  last_reviewed: 2026-03-28
  review_cycle: 90
  based_on: "Anthropic Engineering — Harness Design (Planner role, Pattern C)"
---

# Plan — Full Feature Planning Pipeline

Orchestrates the complete planning process for a feature. Spawns three sub-agents with fresh context, each contributing criteria in their domain to a shared feature registry.

Source: [Anthropic Engineering — Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

> "The planner expands 1-4 sentence prompts into comprehensive product specs. Deliberately high-level — granular technical details cause cascading errors downstream."

---

## Input

A short feature description (1-4 sentences). Examples:

- `Build a Mercury.com-style homepage for TransitPay.`
- `Add Stripe webhook handling for subscription lifecycle events.`
- `Build a real-time analytics dashboard for gateway transactions.`

Do NOT require the user to provide design specs, acceptance criteria, or technical details. The point of this skill is to generate all of that.

---

## Output

A complete feature registry at `docs/feature-registry/<feature-slug>.json` with criteria from all three planning domains, plus a summary report.

---

## Process

### Step 0: Setup

1. Slugify the feature description (lowercase, hyphens, max 50 chars)
2. Create `docs/feature-registry/` directory if it doesn't exist
3. Initialize the registry file:

```json
{
  "feature": "<slug>",
  "created": "<YYYY-MM-DD>",
  "story": "<original user request>",
  "plan": null,
  "criteria": [],
  "summary": { "total": 0, "passing": 0, "failing": 0 }
}
```

4. Read the project's CLAUDE.md to understand the tech stack and conventions

---

### Step 1: Product Planning

Spawn an Agent (subagent_type: `plan-architect`) with this task:

```
You are the PRODUCT PLANNER for this feature.

Feature: <user's description>
Project context: <summary of CLAUDE.md / tech stack>

Your job:
1. Research what the user is asking for — if they reference a website or product, fetch it
2. Define the product scope: what's in, what's out
3. Identify user stories and edge cases
4. Challenge the scope — what's the minimum viable version?

Output 3-6 criteria as JSON array. Only these categories:
- "functional" — core behaviors the feature must have
- "edge-case" — boundary conditions, error states, empty states

Format each criterion as:
{"id": "P1", "description": "...", "category": "functional|edge-case", "passes": false, "evidence": null}

Prefix IDs with P (product). Be specific and testable. Do NOT include design or engineering criteria.
```

Read the agent's output. Parse the criteria array and append to the registry.

---

### Step 2: Design Planning

Spawn an Agent (subagent_type: `plan-architect`) with this task:

```
You are the DESIGN PLANNER for this feature.

Feature: <user's description>
Project context: <tech stack, existing design patterns>
Product criteria already defined: <list P criteria from registry>

Your job:
1. If the user referenced a design inspiration (website, style), research it
2. Define the visual design direction — typography, color, layout, spacing
3. Define interaction patterns — hover states, transitions, responsive behavior
4. Check for AI slop patterns to avoid (generic gradients, stock layouts, default typography)
5. Check for accessibility requirements

Output 3-6 criteria as JSON array. Only these categories:
- "design" — visual quality, originality, craft
- "accessibility" — WCAG compliance, screen readers, contrast, touch targets

Format each criterion as:
{"id": "D1", "description": "...", "category": "design|accessibility", "passes": false, "evidence": null}

Prefix IDs with D (design). Criteria must be verifiable by looking at the running UI — not by reading code.
```

Read the agent's output. Parse the criteria array and append to the registry.

---

### Step 3: Engineering Planning

Spawn an Agent (subagent_type: `plan-architect`) with this task:

```
You are the ENGINEERING PLANNER for this feature.

Feature: <user's description>
Project context: <tech stack, conventions, architecture>
Product criteria: <list P criteria>
Design criteria: <list D criteria>

Your job:
1. Define the architecture — components, data flow, file structure
2. Identify code quality requirements — patterns to follow, abstractions needed
3. Map test coverage needs — what paths need tests
4. Estimate performance requirements — bundle size, latency, queries

Output 3-6 criteria as JSON array. Only these categories:
- "architecture" — component boundaries, data flow, patterns
- "performance" — bundle size, latency, query efficiency
- "test-coverage" — critical paths that need tests

Format each criterion as:
{"id": "E1", "description": "...", "category": "architecture|performance|test-coverage", "passes": false, "evidence": null}

Prefix IDs with E (engineering). Each criterion must be independently verifiable.
```

Read the agent's output. Parse the criteria array and append to the registry.

---

### Step 4: Assemble and Score

1. Read the complete registry with all P, D, and E criteria
2. Write the high-level plan (2-3 sentences synthesizing all three domains)
3. Update the summary counts
4. Write the final registry to `docs/feature-registry/<slug>.json`

Then produce the planning report:

```
## Plan: <feature name>

### Story
<original user request>

### Plan
<2-3 sentence high-level approach>

### Criteria (<N> total)

#### Product (P)
- P1: [description]
- P2: [description]
...

#### Design (D)
- D1: [description]
- D2: [description]
...

#### Engineering (E)
- E1: [description]
- E2: [description]
...

### Implementation Order
<suggested order to implement criteria, respecting dependencies>

### Registry
Written to: docs/feature-registry/<slug>.json
```

---

## Rules

1. **Keep the plan HIGH-LEVEL** — the generator decides implementation details. Over-specifying causes cascading errors.
2. **10-18 total criteria** across all three domains. More than that = scope too large, split the feature.
3. **Each criterion must be independently testable** by an evaluator agent that reads code + interacts with the running app.
4. **No implementation details in criteria** — describe WHAT to verify, not HOW to build it.
5. **Sub-agents get fresh context** — pass them the information they need, don't assume they can read your state.
6. **If the user referenced an external site/product**, the product and design agents should research it. Don't ask the user for details the agents can discover.

---

## Integration

### With harness.sh (bash)
```bash
# Plan first in TUI, then hand off to harness for build+eval
/plan "Build a Mercury-style homepage"
# Then:
~/.claude/scripts/harness.sh --registry docs/feature-registry/homepage.json
```

### With TUI flow (no harness)
```
/plan "Build a Mercury-style homepage"
# Then build it
# Then /review to evaluate
# Then /qa report for health check
```

### With plan sub-skills
If you only need one domain:
- `/plan-product` — product scope only
- `/plan-design` — design audit only
- `/plan-eng` — engineering review only

`/plan` runs all three and merges the output.

---

## References

- `context/knowledge/patterns/feature-registry.md` — registry schema and rules
- `context/knowledge/patterns/evaluator-loop.md` — scoring pattern used by sub-plans
- `context/knowledge/patterns/quality-contract.md` — project-specific weight overrides
