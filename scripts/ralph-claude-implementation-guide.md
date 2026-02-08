# Ralph Claude Loop: Implementation Guide

A single-vendor autonomous coding loop using Claude Sonnet as driver and Claude Opus as reviewer. Fresh context each iteration, learnings persist via files and git.

**For use in EXISTING projects** - this guide focuses on what files you need to ADD.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Files to Add](#2-files-to-add)
3. [Prompt Files](#3-prompt-files)
4. [Configuration](#4-configuration)
5. [Running the Loop](#5-running-the-loop)
6. [Monitoring & Debugging](#6-monitoring--debugging)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Prerequisites

### Required Tools

```bash
# Claude Code CLI
npm install -g @anthropic-ai/claude-code
# Or via Homebrew
brew install claude-code

# jq for JSON parsing
brew install jq  # macOS
sudo apt install jq  # Ubuntu/Debian
```

### Authentication

```bash
# Authenticate Claude Code
claude
# Follow browser prompts to sign in
```

### Verify Installation

```bash
claude --version
jq --version
```

---

## 2. Files to Add

Add these files to your existing project:

```
your-project/
├── CLAUDE.md              # (may already exist - update if needed)
├── prd.json               # Task tracking (NEW)
├── progress.txt           # Iteration history (auto-created)
├── prompts/               # Prompt files (NEW)
│   ├── ralph-driver.md
│   ├── ralph-reviewer-claude.md
│   └── progress-template.md
├── logs/                  # Execution logs (auto-created, gitignore)
└── .env                   # Optional: configuration overrides
```

### Update .gitignore

Add to your existing `.gitignore`:

```
logs/
*.log
progress.txt.tmp
CLAUDE.md.tmp
```

### Create prd.json

Task tracking with completion status:

```json
{
  "projectName": "your-project-name",
  "branchName": "feature/your-feature",
  "items": [
    {
      "id": "US-001",
      "title": "First task description",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2",
        "Criterion 3"
      ],
      "priority": 1,
      "passes": false,
      "dependsOn": [],
      "notes": ""
    }
  ]
}
```

**PRD Guidelines:**
- Keep tasks small (completable in one context window)
- Priority 1 = highest priority
- Use `dependsOn` for task ordering
- `passes: false` until verified complete

### Update CLAUDE.md

If you already have a `CLAUDE.md`, ensure it includes:
- Build/test commands
- Code conventions
- A section for "Learned Patterns" (Ralph appends here)

---

## 3. Prompt Files

Create a `prompts/` directory with these files:

### prompts/ralph-driver.md

```markdown
## Your Task This Iteration

1. Read progress.txt to understand what's been done
2. Read prd.json to find incomplete items (passes: false)
3. Pick the highest priority incomplete item
4. Implement it following CLAUDE.md conventions
5. Run tests to verify
6. If tests pass:
   - Update prd.json: set passes: true for completed item
   - Append to progress.txt: what you did and patterns learned
   - If you discovered a NEW PATTERN or GOTCHA, add it to CLAUDE.md
7. Commit all changes with descriptive message

Focus on ONE item per iteration. Do not attempt multiple items.
```

### prompts/ralph-reviewer-claude.md

```markdown
You are reviewing code changes against project conventions.

## Git Diff to Review
```
{{DIFF}}
```

## Your Task
Review against conventions in CLAUDE.md. Check for:
- Convention violations
- Missing error handling
- Missing tests
- Architectural drift
- Security issues

IMPORTANT: Your response MUST start with "REVIEW_RESULT:" followed by valid JSON on the same line.

If the code passes review:
REVIEW_RESULT:{"verdict":"PASS","issues":[],"new_patterns":[],"new_gotchas":[]}

If there are issues:
REVIEW_RESULT:{"verdict":"FAIL","issues":["issue 1","issue 2"],"new_patterns":[],"new_gotchas":[]}

Do not include any other text, markdown, or explanation. Just the REVIEW_RESULT line.
```

### prompts/progress-template.md (Optional)

```markdown
# Progress Log

## Codebase Patterns
(Learnings will accumulate here as Ralph runs)

## Completed Work
(none yet)

---
Started: {{DATE}}
```

---

## 4. Configuration

### Environment Variables

Create a `.env` file (optional) to override defaults:

```bash
# Custom PRD file location
PRD_FILE=./docs/audit.json

# Model overrides (defaults: sonnet/opus)
DRIVER_MODEL=sonnet
REVIEWER_MODEL=opus
```

### Command Line Options

```bash
# Default: 20 iterations
./ralph-claude.sh

# Custom iteration limit
./ralph-claude.sh 50
```

### Script Location

Copy `ralph-claude.sh` to your project:

```bash
mkdir -p scripts
cp /path/to/ralph-claude.sh scripts/
chmod +x scripts/ralph-claude.sh
```

Or run from a central location:

```bash
~/.claude/scripts/ralph-claude.sh 20
```

---

## 5. Running the Loop

### Basic Run

```bash
# Run with default 20 iterations
./scripts/ralph-claude.sh

# Run with custom iteration limit
./scripts/ralph-claude.sh 50
```

### With Custom PRD File

```bash
PRD_FILE=./audit.json ./scripts/ralph-claude.sh 30
```

### Background/Overnight Run

```bash
# Run in background
nohup ./scripts/ralph-claude.sh 50 > ralph-output.log 2>&1 &

# Using tmux (recommended)
tmux new-session -d -s ralph './scripts/ralph-claude.sh 50'
tmux attach -t ralph  # To watch
# Detach: Ctrl+B, then D
```

### Stopping the Loop

The loop automatically stops when:
1. All PRD items have `passes: true`
2. Max iterations reached
3. No PRD progress for 3 consecutive iterations
4. Unparseable reviewer response

To manually stop: `Ctrl+C` (cleanup runs automatically)

---

## 6. Monitoring & Debugging

### Real-time Log Monitoring

```bash
# Watch driver logs
tail -f logs/driver-*.log

# Watch review logs
tail -f logs/review-*.log
```

### Progress Monitoring

```bash
# Check PRD status
cat prd.json | jq ".items[] | {id, title, passes}"

# View progress history
cat progress.txt
```

### Git History

```bash
# See Ralph commits
git log --oneline --grep="ralph"

# See approved iterations
git tag -l "approved-*"
```

---

## 7. Troubleshooting

### Common Issues

**"Claude Code not authenticated"**
```bash
claude
# Follow auth flow in browser
```

**"prd.json not found"**
- Ensure you're in the project root
- Or set `PRD_FILE=/path/to/prd.json`

**"prompts/ralph-driver.md not found"**
- Create the `prompts/` directory and files per Section 3

**Review always returns UNKNOWN**
- Check `logs/review-*.log` for actual output
- Ensure reviewer outputs `REVIEW_RESULT:` prefix
- The script auto-creates the reviewer prompt if missing

**"No PRD progress for 3 consecutive iterations"**
- Driver may be stuck on a task
- Check `progress.txt` for failure patterns
- Simplify the current PRD item
- Manually mark items complete if needed

**Rate limit errors**
- Script has built-in retry with exponential backoff
- If persistent, wait and retry later

### Manual Overrides

```bash
# Mark item complete manually
cat prd.json | jq '.items[0].passes = true' > tmp.json && mv tmp.json prd.json
git add prd.json && git commit -m "manual: mark item complete"

# Reset PRD items
cat prd.json | jq '.items[].passes = false' > tmp.json && mv tmp.json prd.json
```

### Reset and Restart

```bash
# Reset to last approved state
git reset --hard $(git tag -l "approved-*" | tail -1)

# Clear logs
rm -rf logs/*

# Restart
./scripts/ralph-claude.sh
```

---

## Quick Start Checklist

```
[ ] Claude CLI installed and authenticated
[ ] jq installed
[ ] Git repository initialized
[ ] CLAUDE.md exists with project conventions
[ ] prd.json created with small, clear tasks
[ ] prompts/ralph-driver.md created
[ ] logs/ added to .gitignore
[ ] ralph-claude.sh is executable
```

---

## Key Differences from ralph-pair.sh

| Feature | ralph-pair.sh | ralph-claude.sh |
|---------|---------------|-----------------|
| Vendors | Claude + OpenAI Codex | Claude only |
| Driver | Opus 4.5 | Sonnet |
| Reviewer | GPT (Codex) | Opus |
| AGENTS.md sync | Required | Not needed |
| Prompt files | Inline | External files |
| Revert method | Git stash | Temp files |
| Retry logic | None | Exponential backoff |
| No-progress detection | None | 3 iteration limit |
| .env support | No | Yes |

---

*Last updated: February 2026*
