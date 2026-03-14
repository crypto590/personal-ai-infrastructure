---
name: amendify
description: |
  Self-improvement skill for amending underperforming skills based on execution evidence.
  Use when a skill inspection reveals degraded or failing health, or when a user
  wants to improve a skill based on its observation history.

  Triggers:
  - "This skill keeps failing"
  - "Improve the code-review skill"
  - "Amendify <skill-name>"
  - After /inspect-skill shows degraded/failing health
  - When observation data shows recurring failures
---

# Amendify — Evidence-Based Skill Amendment

## Purpose

Propose targeted changes to a SKILL.md based on **actual execution evidence** — not guesses.
Every amendment must be grounded in observation data from the skill tracker database.

## Workflow

### 1. Gather Evidence

Run inspection to get the data:
```bash
uv run ~/.claude/scripts/skill-tracker/inspect.py "<skill-name>" --json
```

Read the current SKILL.md:
```bash
cat ~/.claude/skills/<category>/<skill-name>/SKILL.md
```

### 2. Analyze Failure Patterns

Map each error pattern to a root cause:

| Error Type | Likely Root Cause | Amendment Strategy |
|---|---|---|
| `tool_call` | Environment changed, wrong path, missing dependency | Fix tool references, add fallback paths, add prerequisite checks |
| `instruction` | Ambiguous steps, missing context | Rewrite unclear instructions, add examples |
| `timeout` | Task too broad, no chunking | Break into smaller steps, add early-exit conditions |
| `output_quality` | Missing format spec, weak examples | Add explicit output format, before/after examples |
| `routing` | Wrong skill selected for task | Tighten trigger conditions, add exclusions |

### 3. Propose Amendment

Generate a proposed change that includes:

1. **Change type**: One of `tighten_trigger`, `add_condition`, `reorder_steps`, `change_format`, `fix_tool_call`, `rewrite`, `other`
2. **Rationale**: Why this change is needed (cite specific observations)
3. **Diff**: What exactly changes in the SKILL.md
4. **Risk**: What could go wrong with this change

### 4. Record Amendment

```bash
uv run ~/.claude/scripts/skill-tracker/amend.py \
  --skill "<skill-name>" \
  --type "<change_type>" \
  --rationale "Explain why based on evidence" \
  --evidence '[<observation_ids>]'
```

Or record it directly in the database if the script isn't available.

### 5. Apply (With Approval)

**Default: Require human approval before applying.**

Present the proposed diff to the user and ask:
- "Apply this amendment to the SKILL.md?"
- "Apply and monitor for 5 runs before evaluating?"
- "Reject — I'll handle this manually"

If approved:
1. Back up the current SKILL.md content in the amendment record
2. Apply the change to the SKILL.md file
3. Bump the skill version in the database
4. Mark the amendment as 'applied'

### 6. Schedule Evaluation

After applying, remind the user:
> "This amendment is now active. After ~5 more executions, run `/evaluate-skill <amendment-id>` to check if it improved things."

## Anti-Patterns

- **Don't rewrite the entire skill** — make the smallest change that addresses the evidence
- **Don't amend without evidence** — "I think it could be better" is not a reason
- **Don't skip the backup** — always store original_content before applying
- **Don't auto-apply without asking** — human-in-the-loop by default

## Example Amendment

**Inspection showed:**
- 4/7 runs failed with `tool_call` error
- Pattern: "SwiftLint not found"
- All failures in project `/Users/corey/ios-app`

**Root cause:** SKILL.md assumes SwiftLint is at `/usr/local/bin/swiftlint` but the project uses `mint run swiftlint`.

**Amendment:**
```diff
- Run SwiftLint: `swiftlint lint --strict`
+ Run SwiftLint (detect installation):
+ - If `mint` is available: `mint run swiftlint lint --strict`
+ - If `swiftlint` is in PATH: `swiftlint lint --strict`
+ - Otherwise: Skip lint and note "SwiftLint not installed"
```

**Change type:** `fix_tool_call`
**Rationale:** SwiftLint invocation fails in projects using Mint package manager. Making the command detect the installation method fixes 4/7 recent failures.

## Supplementary Resources

- Workflow: [propose-amendment.md](workflows/propose-amendment.md)
- Inspection: `uv run ~/.claude/scripts/skill-tracker/inspect.py`
- Evaluation: `uv run ~/.claude/scripts/skill-tracker/evaluate.py`
