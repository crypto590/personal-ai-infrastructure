---
name: reference_anthropic_harness_design
description: Anthropic's harness design principles for long-running agentic apps — all named patterns, anti-patterns, agent roles, evaluation criteria, and evolution model
type: reference
---

Source: https://www.anthropic.com/engineering/harness-design-long-running-apps (March 24, 2026)

## Definition

A **harness** is the entire execution environment wrapping an LLM: prompts, tool connections, inter-agent structures, feedback loops, validation logic, state management, and context strategies. The harness determines the outcome.

## The Two Core Problems

### Context Anxiety
As context fills (~70-80%), models: produce shorter outputs, summarize instead of execute, declare subtasks complete prematurely, wrap up despite incomplete work.
- Compaction alone is insufficient (Sonnet 4.5 case study)
- Fix: **Context Reset** — clear window, fresh agent reads structured progress file
- Alternative fixes: chunking (30-40% window units), compaction

### Poor Self-Evaluation
Generators "confidently praise" mediocre outputs. Self-evaluation produces: self-serving rationalization, superficial testing, systematic approval bias, missed subjective failures.
- Fix: separate Evaluator agent (never self-eval the generator)
- Uncalibrated evaluators identify issues then "talk themselves into deciding they weren't a big deal" — must be tuned

## Three Harness Patterns

**Pattern A: Simple Validation Loop** — single agent + hard automated checks (linters, tests). Best for <30 min tasks with objectively checkable outcomes.

**Pattern B: Generator-Evaluator Pair** — two agents with rubric + interaction tools. Best for moderately subjective tasks, 1-4 hours.

**Pattern C: Full Harness (Planner-Generator-Evaluator)** — three agents + progress files + context resets + sprint contracts. Best for multi-hour/day production tasks.

## Three-Agent Roles

**Planner**: Expands 1-4 sentence prompts into product specs. Intentionally HIGH-LEVEL — granular specs cause cascading errors. Identifies AI feature opportunities. Outputs JSON task list with dependencies + completion criteria.

**Generator**: Works in sprints (one feature at a time). Has git access. Tightly scoped system prompt. Outputs sentinel `TASK_COMPLETE:` to signal handoff. Self-evaluates lightly before handoff (not primary QA).

**Evaluator**: Uses Playwright MCP on LIVE running apps — clicks UI, tests APIs, checks DB state. Grades against explicit rubric. Must be calibrated for skepticism. Harsher on later iterations (round 3+).

## Sprint Contracts
Before each sprint: generator and evaluator negotiate a contract specifying exact implementation details AND specific testable behaviors that verify completion. Bridges user stories to verifiable implementation.

## Progress/State Files
JSON/YAML/Markdown files = agent's externalised memory. Carry: completion status, current work, remaining tasks, blockers, decisions made. Enable context resets and resumption.

## Evaluation Criteria

**Frontend design (4 dimensions):**
1. Design Quality — coherent aesthetic unity (colors, typography, layout, imagery)
2. Originality — custom decisions; avoids "AI slop" (named anti-pattern: "purple gradients over white cards")
3. Craft — typography hierarchy, spacing consistency, color harmony, contrast ratios
4. Functionality — usability independent of aesthetics

**Full-stack default rubric:**
- Correctness 35%
- Completeness 25%
- Quality 20%
- Originality 20%

## Evaluator Tuning (3 Lessons)
1. Make subjective qualities gradable — numeric scales or yes/no, not "is this beautiful?"
2. Weight criteria based on observed model weaknesses — reweight dynamically
3. Let evaluator interact with output — Playwright, test runner, linters; not just code review

## GAN-Inspired Structure
Generator-Evaluator loop explicitly inspired by GANs. Separation is structural: "Separating generator and evaluator roles proved far more tractable than making generators self-critical."

## Evolution Across Model Generations
- Sonnet 4.5: 2-agent (Initializer + Coder), mandatory context resets, strong context anxiety
- Opus 4.5: 3-agent full harness, per-sprint evaluation, $200/6hr game maker
- Opus 4.6: Sprint structure REMOVED (improved long-context), single end-of-build eval, $125/4hr browser DAW

**Core principle:** "Every harness component encodes an assumption about what the model cannot do on its own. When models improve, those assumptions must be re-tested."

**Simplification method:** Remove one component at a time, measure regression. If no regression = unnecessary scaffolding. If regression = load-bearing, restore it.

## Cost Data
Solo agent: 20 min / $9 / broken features. Full harness: 6 hrs / $200 / functional + polished. 20x cost, qualitatively superior output.

## Anti-Patterns
1. Naive long-running single agent
2. Context compaction alone (insufficient for context-anxious models)
3. Generator self-evaluation
4. Uncalibrated/untested evaluator (rubber-stamps outputs)
5. Overly granular planning (cascading errors)
6. Static harness across model versions
7. Code-only evaluation (misses runtime integration failures)
8. Vague evaluation criteria
9. "AI slop" patterns: purple gradients, generic layouts, default typography

## Industry Convergence
- Manus: rewrote harness 5x in 6 months
- LangChain: redesigned Deep Research 4x
- Vercel: removed 80% of agent tools, results improved

## Key Quote
"The space of interesting harness combinations doesn't shrink as models improve — it moves, and the work for AI engineers is finding the next novel combination."
