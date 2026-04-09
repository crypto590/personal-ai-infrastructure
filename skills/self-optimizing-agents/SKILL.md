---
name: self-optimizing-agents
description: "Meta-agent / task-agent patterns for building agents that improve over time. Covers failure-trace analysis, verification loops, hill-climbing protocols, overfitting guardrails, and the fixed-boundary architecture from AutoAgent. Worked examples target Mastra but the patterns generalize to any agent framework."
---

# Self-Optimizing Agent Patterns

How to build agents that improve themselves through meta-agent supervision, trace analysis, and verification loops. Based on the AutoAgent architecture (https://github.com/kevinrgu/autoagent) — the first open-source library for autonomously improving agents.

## Core idea: meta-agent / task-agent split

Two agents, same model:

- **Task agent** — domain specialist that executes work
- **Meta-agent** — optimizer that reads task-agent traces and edits its config

Use the same model for both (**model empathy** — Claude optimizing Claude outperforms cross-model optimization).

The power comes from the **constraints**, not the code. See `references/patterns.md` for the full architecture and seven concrete patterns.

## Patterns

| # | Pattern | Purpose |
|---|---------|---------|
| 1 | **Fixed Boundary** | Split agent file into mutable config (meta edits) vs immutable adapter |
| 2 | **Hill-Climbing Protocol** | Propose → build → test → keep-or-discard loop |
| 3 | **ATIF Trajectory Capture** | Record full reasoning chains, not just pass/fail |
| 4 | **Verification Sub-Agent** | Generate → verify → retry (never just generate) |
| 5 | **Results Ledger** | Append-only record of what's been tried and what stuck |
| 6 | **Overfitting Prevention** | Self-reflection constraints on the meta-agent |
| 7 | **Tool Design Over Prompt Tuning** | Prefer better tools to better prompts |

## When to use

Build a self-optimizing agent when:

- The task is **evaluable** (you can score outputs automatically)
- The task recurs with **varying inputs** (one-off tasks don't need optimization)
- You have **traces worth reading** (black-box scoring isn't enough)
- Failure modes are **diverse** enough that no fixed prompt wins

Don't use when:

- The task is deterministic — just write code
- You can't score outputs — there's nothing to hill-climb against
- You only run it once — meta-optimization cost dwarfs the payoff

## Key principles

- **Spot check before expensive execution** — cheap feasibility pass first
- **Progressive disclosure** — stage context incrementally, don't dump it
- **Dynamic agent assembly** — build specialist agents at runtime
- **Never just generate** — always verify, then retry

## Full patterns reference

See [`references/patterns.md`](references/patterns.md) for:

- The complete AutoAgent architecture walkthrough
- TypeScript/Mastra worked examples for each of the 7 patterns
- A composed end-to-end self-optimizing pipeline
- Key principles extracted from the reference implementation
