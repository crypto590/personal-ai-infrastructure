---
name: archon
effort: medium
description: "Archon deterministic workflow engine: YAML-based DAG workflows for AI coding with git worktree isolation, fire-and-forget execution, and multi-platform adapters."
metadata:
  last_reviewed: 2026-04-10
  review_cycle: 90
---

# Archon — Deterministic AI Coding Workflows

Workflow engine that makes AI-assisted coding deterministic and repeatable. Define structured development processes as YAML DAGs — the AI fills in the intelligence at each step, but the structure is owned by you.

**Source:** https://github.com/coleam00/Archon

---

## Quick Routing Table

| Need to... | Read this |
|---|---|
| Install Archon and configure it | `workflows/setup.md` |
| Author custom YAML workflows | `workflows/workflow-authoring.md` |
| Bridge PAI skills into Archon workflows | `workflows/pai-bridges.md` |
| Full YAML schema and node reference | `context/knowledge/platforms/archon.md` |

---

## Why Archon + PAI

PAI skills define **what** to do (review criteria, planning methodology, shipping pipeline). Archon defines **how** to execute it — deterministically, in isolation, with human gates at the right moments.

| PAI Has | Archon Adds |
|---|---|
| Skills (instructions for AI) | Executable workflow DAGs |
| Commands (manual step lists) | Deterministic, automated pipelines |
| Sub-agents (one-shot delegation) | Loop nodes with retry + approval gates |
| Sequential execution | Git worktree isolation for parallel runs |
| CLI interaction only | Slack, Telegram, Discord, GitHub webhook adapters |

Together: PAI skills become the intelligence inside Archon's deterministic structure.

---

## Core Concepts

### 1. Deterministic Execution
Workflows follow the same sequence every time. No model drift, no skipped steps.

### 2. Git Worktree Isolation
Each workflow run operates in its own git worktree — parallel execution without conflicts. Multiple workflows can run simultaneously on the same repo.

### 3. Fire-and-Forget
Start a workflow, walk away. Come back to a completed PR with review comments.

### 4. Composable Nodes
YAML nodes combine deterministic operations (bash scripts, tests, git) with AI-powered steps (planning, code generation, review).

### 5. Portability
Workflows committed to `.archon/workflows/` work identically across CLI, web UI, Slack, Telegram, and GitHub.

---

## Built-in Workflows

| Workflow | What it does |
|---|---|
| `archon-fix-github-issue` | Classify → investigate → implement → validate → PR |
| `archon-idea-to-pr` | Plan → implement (loop) → parallel review → PR |
| `archon-comprehensive-pr-review` | Multi-agent review with self-fixing loop |
| `archon-architect` | Codebase health analysis + architectural improvements |
| `archon-refactor-safely` | Type-checked refactoring with behavior verification |

17 default workflows total. Override any by placing a same-named file in your `.archon/workflows/`.

---

## CLI Quick Reference

```bash
# Install
curl -fsSL https://archon.diy/install | bash
# Or: brew install coleam00/archon/archon

# From your project directory
cd /path/to/project
claude                          # Natural language — Archon routes to workflows
archon workflow list            # List available workflows
archon serve                    # Start web UI dashboard
```

---

## Directory Structure

```
.archon/
├── workflows/
│   ├── defaults/               # Bundled workflows (17 built-in)
│   └── my-custom-workflow.yaml # User-defined overrides
├── commands/
│   └── custom.md               # Reusable AI commands
└── config.yaml                 # Credentials, model selection, platform config
```

---

## Decision Guide

- **Want deterministic dev pipelines?** → Use Archon workflows
- **Need parallel isolated execution?** → Archon's worktree isolation
- **Want Slack/Telegram/Discord triggers?** → Configure platform adapters
- **Building a custom workflow?** → `workflows/workflow-authoring.md`
- **Connecting PAI skills to Archon?** → `workflows/pai-bridges.md`

---

## Dependencies

**Related skills:**
- `ship/` — Archon can execute the ship pipeline as a deterministic workflow
- `review/` — Archon's review workflows complement PAI's 2-pass review
- `plan/` — Archon's idea-to-pr workflow parallels PAI's planning pipeline

**Required context:**
- `context/knowledge/platforms/archon.md` — Full YAML schema reference
