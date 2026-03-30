# Harness: 3-Agent Feature Builder

Pattern C from [Anthropic Engineering — Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps).

Three `claude -p` processes with full context resets between them. Feature registry JSON is the shared state file.

---

## Quick Start

```bash
# From your project root:
~/.claude/scripts/harness.sh "Add email verification to signup flow"
```

## How It Works

```
USER STORY
    │
    ▼
┌─────────┐     .feature-registry/
│ PLANNER  │────▶  <feature>.json     ◀─── shared state
│ (Opus)   │     (4-8 criteria)       │
└─────────┘                           │
    │ context reset                   │
    ▼                                 │
┌───────────┐   reads next failing    │
│ GENERATOR │◀──criterion─────────────┤
│ (Opus)    │                         │
│           │───▶ git commit          │
└───────────┘                         │
    │ context reset                   │
    ▼                                 │
┌───────────┐   tests all criteria    │
│ EVALUATOR │─── flips passes ────────┤
│ (Opus)    │    records evidence     │
│           │                         │
└───────────┘                         │
    │                                 │
    ├── all pass? ──▶ DONE           │
    │                                 │
    └── failures? ──▶ feedback file ──┘
         loop back to GENERATOR
```

Each box is a separate `claude -p` process. Context is fully cleared between phases. The only continuity is:
- `.feature-registry/<feature>.json` — criteria + pass/fail + evidence
- `logs/harness/.feedback` — evaluator's notes to generator on failures
- Git history — committed code

---

## When to Use What

| Task Complexity | Duration | Approach |
|---|---|---|
| Bug fix, config change | < 30 min | TUI directly — no harness needed |
| Single feature, clear scope | 30 min - 2 hr | TUI with `/plan-eng` → code → `/review` |
| Multi-criteria feature | 1-4 hr | **harness.sh** (this script) |
| Multi-feature project | 4+ hr | harness.sh per feature, or ralph-claude.sh with prd.json |

### TUI Alternative (Pattern B)

For medium tasks, the TUI's Agent tool provides context isolation without a bash script:

```
1. /plan-eng        → generates .feature-registry/<name>.json
2. You code         → or ask Claude to implement
3. /review          → evaluator loop with scoring rubric
4. /qa report       → health check
```

The TUI approach has access to MCP tools (chrome-devtools for live testing) that `claude -p` does not.

---

## Options

```bash
# Basic: provide a feature story
harness.sh "Add Stripe webhook handling for subscription events"

# Resume after interrupt/crash
harness.sh --resume

# Use a feature registry you already created (e.g., from /plan-eng)
harness.sh --registry .feature-registry/stripe-webhooks.json

# Give evaluator live browser testing via chrome-devtools MCP
harness.sh --mcp-config ~/.claude/.mcp.json "Add dashboard stats page"

# Or pass MCP config inline
harness.sh --mcp-config '{"mcpServers":{"chrome-devtools":{"command":"npx","args":["-y","@anthropic/chrome-devtools-mcp"]}}}' "Add login form"

# Override models
GENERATOR_MODEL=sonnet harness.sh "Quick feature"

# Limit iterations
MAX_ITERATIONS=5 harness.sh "Small feature"
```

## MCP Integration (Live Testing)

The article's strongest recommendation: "evaluators must experience the running app, not just read code."

Pass `--mcp-config` to give the evaluator chrome-devtools MCP access:

```bash
# Use your existing MCP config
harness.sh --mcp-config ~/.claude/.mcp.json "Add user profile page"

# Or via env var
MCP_CONFIG=~/.claude/.mcp.json harness.sh "Add user profile page"
```

When MCP is enabled, the evaluator:
- Navigates to pages and takes screenshots
- Clicks buttons and fills forms
- Checks console for errors
- Monitors network requests
- Uses live interaction as evidence instead of static code reading

Only the **evaluator** gets MCP tools. The planner and generator work with code only.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MAX_ITERATIONS` | 15 | Max build-eval cycles |
| `PLANNER_MODEL` | opus | Model for planning |
| `GENERATOR_MODEL` | opus | Model for generating |
| `EVALUATOR_MODEL` | opus | Model for evaluating |
| `MCP_CONFIG` | (none) | MCP server config file/string for evaluator |
| `PLAN_TIMEOUT` | 300 | Planner timeout (seconds) |
| `GENERATE_TIMEOUT` | 600 | Generator timeout (seconds) |
| `EVAL_TIMEOUT` | 300 | Evaluator timeout (seconds) |

---

## Project Setup

The harness works with any project that has:

1. **A git repo** (for commits + diffs)
2. **A CLAUDE.md** (for conventions — Claude reads this automatically)

The harness creates:
- `.feature-registry/` — feature registry JSON files
- `logs/harness/` — per-phase logs

Add to `.gitignore`:
```
logs/
```

Optionally track registries in git (recommended — they're your acceptance criteria):
```bash
git add .feature-registry/
```

---

## Monitoring

```bash
# Watch heartbeat
tail -f logs/harness/heartbeat.log

# Watch current phase
tail -f logs/harness/generator-*.log
tail -f logs/harness/evaluator-*.log

# Check registry state
jq '.criteria[] | "\(.id) [\(if .passes then "PASS" else "FAIL" end)] \(.description)"' \
    .feature-registry/<name>.json

# Check progress
jq '.summary' .feature-registry/<name>.json
```

---

## Differences from ralph-claude.sh

| | ralph-claude.sh | harness.sh |
|---|---|---|
| Pattern | B (Generator + Evaluator) | C (Planner + Generator + Evaluator) |
| State file | prd.json (task list) | feature-registry JSON (criteria + evidence) |
| Scope | Multi-task PRD | Single feature |
| Planning | Manual (you write the PRD) | Automated (planner agent writes criteria) |
| Evidence | None — verdict only | Required per criterion |
| Granularity | Task-level pass/fail | Criterion-level pass/fail with evidence |
| Feedback loop | Revert on fail | Targeted feedback on failing criteria |

---

## Iterative Simplification

Per the article: "Every harness component encodes an assumption about what the model cannot do on its own."

Test by removing one component:
1. Skip planner — write registry manually → Does quality change?
2. Skip evaluator — trust generator self-eval → Does quality change?
3. Remove feedback loop — one-shot generate + eval → Does quality change?

No regression = remove the component. Re-test after model upgrades.
