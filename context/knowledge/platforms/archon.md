# Archon Workflow Engine — Reference

> Last updated: 2026-04-10
> Source: https://github.com/coleam00/Archon

---

## 1. What Is Archon

Open-source workflow engine for deterministic AI coding. Defines development processes as YAML DAGs where each node is either an AI prompt or a bash command. The AI fills in the intelligence; the structure is deterministic and repeatable.

**Key properties:**
- Deterministic execution — same sequence every time
- Git worktree isolation — parallel runs without conflicts
- Fire-and-forget — start a workflow, return to a completed PR
- Composable — mix bash gates with AI reasoning
- Portable — same workflow works across CLI, web UI, Slack, Telegram, GitHub

---

## 2. Architecture

```
Platform Layer       Web UI | CLI | Slack | Telegram | Discord | GitHub Webhooks
                          |
Orchestration        Message routing + context management
                          |
Execution            Command handlers | Workflow executor (DAGs) | AI clients
                          |
Data Layer           SQLite or PostgreSQL
                     Tables: codebases, conversations, sessions,
                             workflow_runs, isolation_envs, messages, events
```

**Tech stack:** TypeScript, Bun runtime, Claude Code / Codex AI backends.

---

## 3. YAML Workflow Schema

### File Location
```
.archon/
├── workflows/
│   ├── defaults/               # Bundled (17 workflows)
│   └── custom-workflow.yaml    # User overrides (same name = override)
├── commands/
│   └── custom.md               # Reusable AI commands
└── config.yaml                 # Credentials, model, platform config
```

### Top-Level Structure
```yaml
# workflow-name.yaml
nodes:
  - id: string              # Unique node identifier
    depends_on: [string]     # Array of prerequisite node IDs (optional)
    prompt: string           # AI instruction (mutually exclusive with bash)
    bash: string             # Shell command (mutually exclusive with prompt)
    loop:                    # Optional loop configuration
      until: string          # Completion condition
      fresh_context: bool    # Clean AI context per iteration
      interactive: bool      # Pause for human input
```

### Node Types

| Type | Field | Behavior |
|---|---|---|
| AI | `prompt` | Sends prompt to AI with full codebase + tool access |
| Bash | `bash` | Runs shell command, fails workflow on non-zero exit |
| Loop | `loop` | Repeats node until condition met |
| Interactive | `loop.interactive` | Pauses for human input |

### Loop Conditions

| Condition | Meaning |
|---|---|
| `ALL_TASKS_COMPLETE` | AI decides all planned work is done |
| `APPROVED` | Human approves (requires `interactive: true`) |
| `TESTS_PASS` | All tests pass |

### Execution Rules
- Nodes without `depends_on` execute first
- Independent nodes run in parallel
- A node starts only after all `depends_on` nodes complete
- Failed bash nodes stop the workflow
- Loop nodes with `fresh_context: true` get clean AI context per iteration

---

## 4. Built-in Workflows

| Name | Nodes | Description |
|---|---|---|
| `archon-fix-github-issue` | 7 | Classify → investigate → plan → implement (loop) → test → review → PR |
| `archon-idea-to-pr` | 6 | Plan → implement (loop) → parallel review → approval → PR |
| `archon-comprehensive-pr-review` | 5 | Multi-agent review with self-fixing loop |
| `archon-architect` | 4 | Codebase health analysis → architectural improvements |
| `archon-refactor-safely` | 5 | Type-checked refactoring with behavior verification |

17 total default workflows covering issue fixing, feature development, PR review, refactoring, documentation, and more.

---

## 5. CLI Reference

```bash
# Installation
curl -fsSL https://archon.diy/install | bash
brew install coleam00/archon/archon

# Commands
archon workflow list              # List available workflows
archon workflow run <name>        # Run a specific workflow
archon serve                      # Start web UI (http://localhost:3000)

# Natural language (via Claude Code)
cd /path/to/project
claude
# "Use archon to fix issue #42"
# "Run the idea-to-pr workflow for adding dark mode"
```

---

## 6. Configuration

### config.yaml
```yaml
model: claude-opus-4-6

database:
  type: sqlite                    # sqlite | postgresql
  path: .archon/data.db

platforms:
  github:
    enabled: true
    webhook_secret: $GITHUB_WEBHOOK_SECRET
  slack:
    enabled: false
    token: $SLACK_BOT_TOKEN
  telegram:
    enabled: false
    token: $TELEGRAM_BOT_TOKEN
```

### Environment Variables
| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API access |
| `GITHUB_WEBHOOK_SECRET` | GitHub webhook verification |
| `SLACK_BOT_TOKEN` | Slack adapter |
| `TELEGRAM_BOT_TOKEN` | Telegram adapter |

---

## 7. Git Worktree Isolation

Each workflow run creates an isolated git worktree:

```
project/
├── .git/                         # Shared git state
├── src/                          # Main working tree
└── .git/worktrees/
    ├── archon-run-abc123/        # Workflow run 1
    └── archon-run-def456/        # Workflow run 2 (parallel)
```

**Benefits:**
- Multiple workflows run simultaneously without conflicts
- Each run has its own file state
- Changes are committed independently
- Worktrees are cleaned up after workflow completion

---

## 8. Database Schema

7 tables for state management:

| Table | Purpose |
|---|---|
| `codebases` | Registered repositories |
| `conversations` | Chat threads across platforms |
| `sessions` | Active AI sessions |
| `workflow_runs` | Execution state and history |
| `isolation_envs` | Git worktree tracking |
| `messages` | Message history |
| `workflow_events` | Step-by-step execution log |
