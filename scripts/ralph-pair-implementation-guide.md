# Ralph Pair Programming Loop: Implementation Guide

A dual-model autonomous coding loop using Claude Code (Opus 4.5) as driver and OpenAI Codex (GPT) as reviewer. Fresh context each iteration, learnings persist via files and git.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Structure](#2-project-structure)
3. [Initial Setup](#3-initial-setup)
4. [Core Files](#4-core-files)
5. [The Ralph Pair Script](#5-the-ralph-pair-script)
6. [Testing Your Setup](#6-testing-your-setup)
7. [Running the Loop](#7-running-the-loop)
8. [Monitoring & Debugging](#8-monitoring--debugging)
9. [Best Practices](#9-best-practices)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

### Required Tools

```bash
# Claude Code CLI
npm install -g @anthropic-ai/claude-code
# Or via Homebrew
brew install claude-code

# OpenAI Codex CLI
npm install -g @openai/codex
# Or via Homebrew
brew install --cask codex

# jq for JSON parsing
brew install jq  # macOS
sudo apt install jq  # Ubuntu/Debian

# yq for YAML parsing (optional, for advanced config)
brew install yq
```

### Authentication

```bash
# Authenticate Claude Code
claude
# Follow browser prompts to sign in

# Authenticate Codex
codex
# Select "Sign in with ChatGPT" or use API key
```

### Verify Installation

```bash
# Check Claude Code
claude --version
claude --help

# Check Codex
codex --version
codex --help

# Check jq
jq --version
```

---

## 2. Project Structure

Create this directory structure in your project:

```
your-project/
├── CLAUDE.md              # Auto-read by Claude Code (conventions + learnings)
├── AGENTS.md              # Auto-read by Codex (synced from CLAUDE.md)
├── prd.json               # Task tracking (passes: true/false)
├── progress.txt           # Iteration history + learnings
├── specs/                 # Project specifications
│   ├── conventions.md     # Code style rules
│   ├── architecture.md    # System design
│   └── api-contract.md    # API specs (if applicable)
├── logs/                  # Execution logs (gitignored)
│   ├── driver-1.log
│   ├── review-1.log
│   └── ...
├── scripts/
│   └── ralph-pair.sh      # Main orchestration script
└── src/                   # Your source code
```

### Initialize Structure

```bash
# Run from your project root
mkdir -p specs logs scripts

# Add logs to gitignore
echo "logs/" >> .gitignore
echo "*.log" >> .gitignore
```

---

## 3. Initial Setup

### Step 3.1: Initialize Git (if not already)

```bash
git init
git add .
git commit -m "Initial commit before Ralph loop"
```

### Step 3.2: Create specs directory with your conventions

```bash
mkdir -p specs
```

Create `specs/conventions.md`:

```markdown
# Code Conventions

## General Rules
- Use descriptive variable names
- Functions should do one thing
- Maximum function length: 30 lines
- All public APIs must be documented

## Error Handling
- Never swallow errors silently
- Use typed errors where possible
- Log errors with context

## Testing
- All new code requires tests
- Minimum 80% coverage for new files
- Integration tests for API endpoints
```

Create `specs/architecture.md` (customize for your project):

```markdown
# Architecture

## Project Type
[iOS App / Web App / API / etc.]

## Key Patterns
- [List your architectural patterns]
- [e.g., MVVM, Clean Architecture, etc.]

## Directory Structure
- `src/` - Main source code
- `tests/` - Test files
- [Add your specific structure]
```

---

## 4. Core Files

### 4.1: CLAUDE.md

This file is **auto-loaded** by Claude Code at session start.

Create `CLAUDE.md` in project root:

```markdown
# Project: [Your Project Name]

## Tech Stack
- [Language/Framework]
- [Key dependencies]
- [Runtime version]

## Build & Test

```bash
# Build
[your build command]

# Test
[your test command]

# Lint
[your lint command]
```

## Conventions
- [Key convention 1]
- [Key convention 2]
- [Key convention 3]

## File Structure
- `src/` - Source code
- `tests/` - Test files
- `specs/` - Requirements and conventions

## Learned Patterns
<!-- Ralph auto-appends learnings here -->

## Known Gotchas
<!-- Issues discovered during development -->
```

### 4.2: AGENTS.md

This is auto-loaded by Codex. The script keeps it synced with CLAUDE.md.

```bash
# Initially just copy CLAUDE.md
cp CLAUDE.md AGENTS.md
```

### 4.3: prd.json

Task tracking with completion status.

Create `prd.json`:

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
    },
    {
      "id": "US-002",
      "title": "Second task description",
      "acceptanceCriteria": [
        "Criterion 1",
        "Criterion 2"
      ],
      "priority": 2,
      "passes": false,
      "dependsOn": ["US-001"],
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

### 4.4: progress.txt

Iteration history and accumulated learnings.

Create `progress.txt`:

```markdown
# Progress Log

## Codebase Patterns
(Learnings will accumulate here as Ralph runs)

## Completed Work
(none yet)

---
Started: [DATE]
```

---

## 5. The Ralph Pair Script

Create `scripts/ralph-pair.sh`:

```bash
#!/bin/bash
#
# ralph-pair.sh - Dual-model autonomous coding loop
# Driver: Claude Code (Opus 4.5)
# Reviewer: OpenAI Codex (GPT)
#
# Usage: ./scripts/ralph-pair.sh [max_iterations]
#

set -e

# ============ CONFIGURATION ============
MAX_ITERATIONS=${1:-20}
PROJECT_DIR="$(pwd)"
PRD_FILE="$PROJECT_DIR/prd.json"
PROGRESS_FILE="$PROJECT_DIR/progress.txt"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
AGENTS_MD="$PROJECT_DIR/AGENTS.md"
LOG_DIR="$PROJECT_DIR/logs"
SLEEP_BETWEEN=3

# Model configuration
CLAUDE_MODEL="claude-opus-4-5-20250514"
CODEX_MODEL="gpt-5-codex"

# ============ SETUP ============
mkdir -p "$LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ VALIDATION ============
validate_setup() {
    log_info "Validating setup..."
    
    # Check required files
    if [ ! -f "$PRD_FILE" ]; then
        log_error "prd.json not found. Create it first."
        exit 1
    fi
    
    if [ ! -f "$CLAUDE_MD" ]; then
        log_error "CLAUDE.md not found. Create it first."
        exit 1
    fi
    
    if [ ! -f "$PROGRESS_FILE" ]; then
        log_warn "progress.txt not found. Creating..."
        echo "# Progress Log

## Codebase Patterns

## Completed Work

---
Started: $(date '+%Y-%m-%d %H:%M')" > "$PROGRESS_FILE"
    fi
    
    # Check git
    if [ ! -d ".git" ]; then
        log_error "Not a git repository. Run 'git init' first."
        exit 1
    fi
    
    # Check tools
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code CLI not found. Install it first."
        exit 1
    fi
    
    if ! command -v codex &> /dev/null; then
        log_error "Codex CLI not found. Install it first."
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_error "jq not found. Install it first."
        exit 1
    fi
    
    log_success "Setup validated"
}

# ============ PRD HELPERS ============
check_all_complete() {
    jq -e '.items | all(.passes == true)' "$PRD_FILE" > /dev/null 2>&1
}

get_next_item() {
    jq -r '.items | map(select(.passes == false)) | sort_by(.priority) | .[0].id // empty' "$PRD_FILE"
}

# ============ SYNC AGENTS.md ============
sync_agents_md() {
    cp "$CLAUDE_MD" "$AGENTS_MD"
    log_info "Synced CLAUDE.md → AGENTS.md"
}

# ============ MAIN LOOP ============
run_loop() {
    local ITERATION=1
    
    log_info "Starting Ralph Pair Loop"
    log_info "Max iterations: $MAX_ITERATIONS"
    log_info "Driver: Claude Code ($CLAUDE_MODEL)"
    log_info "Reviewer: Codex ($CODEX_MODEL)"
    echo ""
    
    while [ $ITERATION -le $MAX_ITERATIONS ]; do
        echo ""
        echo "╔════════════════════════════════════════════════════════╗"
        echo "║  ITERATION $ITERATION of $MAX_ITERATIONS - $(date '+%H:%M:%S')                      ║"
        echo "╚════════════════════════════════════════════════════════╝"
        
        # Check if all PRD items complete
        if check_all_complete; then
            log_success "All PRD items complete!"
            echo ""
            echo "🎉 Ralph Pair Loop finished successfully!"
            exit 0
        fi
        
        NEXT_ITEM=$(get_next_item)
        log_info "Next item: $NEXT_ITEM"
        
        # ============ DRIVER PHASE ============
        echo ""
        log_info "╭─────────────────────────────────────╮"
        log_info "│  DRIVER: Claude Code (Opus 4.5)    │"
        log_info "╰─────────────────────────────────────╯"
        
        DRIVER_PROMPT="## Your Task This Iteration

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

Output <promise>DONE</promise> when the item is complete and committed."

        # Run Claude Code - FRESH PROCESS
        claude --model "$CLAUDE_MODEL" \
               --dangerously-skip-permissions \
               --print "$DRIVER_PROMPT" \
               2>&1 | tee "$LOG_DIR/driver-$ITERATION.log"
        
        # Claude process is now DEAD - context cleared
        
        # Commit driver work
        git add -A
        git commit -m "ralph iteration $ITERATION - driver work" --allow-empty || true
        
        log_success "Driver phase complete"
        
        # ============ REVIEWER PHASE ============
        echo ""
        log_info "╭─────────────────────────────────────╮"
        log_info "│  REVIEWER: Codex (GPT)             │"
        log_info "╰─────────────────────────────────────╯"
        
        # Sync CLAUDE.md to AGENTS.md for Codex
        sync_agents_md
        
        # Get diff for review
        DIFF=$(git diff HEAD~1 2>/dev/null || echo "No changes detected")
        
        REVIEW_PROMPT="You are reviewing code changes against project conventions.

## Git Diff to Review
\`\`\`
$DIFF
\`\`\`

## Your Task
Review against conventions in AGENTS.md. Check for:
- Convention violations
- Missing error handling
- Missing tests
- Architectural drift
- Security issues

Respond with ONLY this JSON (no markdown, no backticks, no explanation):
{\"verdict\": \"PASS\", \"issues\": [], \"new_patterns\": [], \"new_gotchas\": []}

Or if there are issues:
{\"verdict\": \"FAIL\", \"issues\": [\"issue 1\", \"issue 2\"], \"new_patterns\": [], \"new_gotchas\": []}"

        # Run Codex - FRESH PROCESS
        codex exec \
            --model "$CODEX_MODEL" \
            --dangerously-bypass-approvals-and-sandbox \
            "$REVIEW_PROMPT" \
            2>&1 | tee "$LOG_DIR/review-$ITERATION.log"
        
        # Codex process is now DEAD - context cleared
        
        # Parse review output
        REVIEW_OUTPUT=$(cat "$LOG_DIR/review-$ITERATION.log")
        
        # Extract verdict (handle various JSON formats)
        VERDICT=$(echo "$REVIEW_OUTPUT" | grep -oP '"verdict"\s*:\s*"\K[^"]+' | head -1 || echo "UNKNOWN")
        
        echo ""
        if [ "$VERDICT" == "PASS" ]; then
            log_success "Review PASSED ✓"
            
            # Tag approved iteration
            git tag "approved-iter-$ITERATION" || true
            
            # Extract and append learnings
            NEW_PATTERNS=$(echo "$REVIEW_OUTPUT" | jq -r '.new_patterns[]? // empty' 2>/dev/null || true)
            NEW_GOTCHAS=$(echo "$REVIEW_OUTPUT" | jq -r '.new_gotchas[]? // empty' 2>/dev/null || true)
            
            if [ -n "$NEW_PATTERNS" ]; then
                echo "- $NEW_PATTERNS" >> "$CLAUDE_MD"
                log_info "Added new pattern to CLAUDE.md"
            fi
            
            if [ -n "$NEW_GOTCHAS" ]; then
                echo "- $NEW_GOTCHAS" >> "$CLAUDE_MD"
                log_info "Added new gotcha to CLAUDE.md"
            fi
            
            # Append success to progress
            echo "" >> "$PROGRESS_FILE"
            echo "### Iteration $ITERATION - PASSED ✓" >> "$PROGRESS_FILE"
            echo "$(date '+%Y-%m-%d %H:%M')" >> "$PROGRESS_FILE"
            
            git add -A
            git commit -m "ralph iteration $ITERATION - approved" --allow-empty || true
            
        elif [ "$VERDICT" == "FAIL" ]; then
            log_error "Review FAILED ✗"
            
            # Extract issues
            ISSUES=$(echo "$REVIEW_OUTPUT" | jq -r '.issues[]? // empty' 2>/dev/null || echo "$REVIEW_OUTPUT")
            
            # Log to progress.txt
            echo "" >> "$PROGRESS_FILE"
            echo "### Iteration $ITERATION - FAILED ✗" >> "$PROGRESS_FILE"
            echo "$(date '+%Y-%m-%d %H:%M')" >> "$PROGRESS_FILE"
            echo "Issues:" >> "$PROGRESS_FILE"
            echo "$ISSUES" >> "$PROGRESS_FILE"
            
            # Revert code but keep progress/learnings
            log_info "Reverting code changes, keeping feedback..."
            git stash push -- "$PROGRESS_FILE" "$CLAUDE_MD" 2>/dev/null || true
            git reset --hard HEAD~1
            git stash pop 2>/dev/null || true
            
            git add -A
            git commit -m "ralph iteration $ITERATION - feedback logged" --allow-empty || true
            
        else
            log_warn "Could not parse verdict: $VERDICT"
            log_warn "Review output saved to logs/review-$ITERATION.log"
            
            # Continue anyway, assume pass
            git add -A
            git commit -m "ralph iteration $ITERATION - review unclear" --allow-empty || true
        fi
        
        ITERATION=$((ITERATION+1))
        
        echo ""
        log_info "Sleeping ${SLEEP_BETWEEN}s before next iteration..."
        sleep $SLEEP_BETWEEN
    done
    
    log_warn "Max iterations ($MAX_ITERATIONS) reached"
    log_warn "Not all PRD items completed. Review progress.txt and prd.json"
    exit 1
}

# ============ ENTRY POINT ============
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║   🔄 RALPH PAIR PROGRAMMING LOOP                         ║"
    echo "║                                                           ║"
    echo "║   Driver:   Claude Code (Opus 4.5)                       ║"
    echo "║   Reviewer: OpenAI Codex (GPT)                           ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    
    validate_setup
    run_loop
}

main "$@"
```

Make executable:

```bash
chmod +x scripts/ralph-pair.sh
```

---

## 6. Testing Your Setup

### Step 6.1: Dry Run Validation

```bash
# Test that script validates correctly
./scripts/ralph-pair.sh 1
```

This should:
- Validate all files exist
- Check CLI tools are installed
- Run exactly 1 iteration
- Show driver and reviewer phases

### Step 6.2: Create a Simple Test Task

Update `prd.json` with a trivial task:

```json
{
  "projectName": "test-project",
  "branchName": "test/ralph-setup",
  "items": [
    {
      "id": "TEST-001",
      "title": "Create a README.md file",
      "acceptanceCriteria": [
        "README.md exists in project root",
        "Contains project name",
        "Contains basic description"
      ],
      "priority": 1,
      "passes": false,
      "dependsOn": [],
      "notes": "Simple test task"
    }
  ]
}
```

### Step 6.3: Run Single Iteration Test

```bash
# Run with just 1 iteration
./scripts/ralph-pair.sh 1
```

**Expected behavior:**
1. Driver creates README.md
2. Driver updates prd.json (passes: true)
3. Driver commits changes
4. Reviewer checks the diff
5. Reviewer outputs verdict
6. Script handles verdict appropriately

### Step 6.4: Verify Outputs

```bash
# Check prd.json was updated
cat prd.json | jq '.items[0].passes'

# Check progress.txt has entry
cat progress.txt

# Check git history
git log --oneline -5

# Check logs were created
ls -la logs/
```

---

## 7. Running the Loop

### Basic Run

```bash
# Run with default 20 iterations
./scripts/ralph-pair.sh

# Run with custom iteration limit
./scripts/ralph-pair.sh 50
```

### Background/Overnight Run

```bash
# Run in background with output to file
nohup ./scripts/ralph-pair.sh 50 > ralph-output.log 2>&1 &

# Get the process ID
echo $!

# Check if still running
ps aux | grep ralph-pair
```

### With Terminal Multiplexer (Recommended)

```bash
# Using tmux
tmux new-session -d -s ralph './scripts/ralph-pair.sh 50'

# Attach to watch
tmux attach -t ralph

# Detach: Ctrl+B, then D
```

### With Notification on Completion

Create `scripts/ralph-notify.sh`:

```bash
#!/bin/bash

# Run Ralph and notify when done
./scripts/ralph-pair.sh "$@"
EXIT_CODE=$?

# macOS notification
if command -v osascript &> /dev/null; then
    if [ $EXIT_CODE -eq 0 ]; then
        osascript -e 'display notification "All PRD items complete!" with title "Ralph Pair Loop" sound name "Glass"'
    else
        osascript -e 'display notification "Loop ended with issues" with title "Ralph Pair Loop" sound name "Basso"'
    fi
fi

# Or use terminal-notifier (brew install terminal-notifier)
# terminal-notifier -title "Ralph" -message "Loop complete"

exit $EXIT_CODE
```

---

## 8. Monitoring & Debugging

### Real-time Log Monitoring

```bash
# In a separate terminal, watch driver logs
tail -f logs/driver-*.log

# Watch review logs
tail -f logs/review-*.log

# Watch both
tail -f logs/*.log
```

### Progress Monitoring

```bash
# Watch progress.txt updates
watch -n 5 cat progress.txt

# Check PRD status
watch -n 5 'cat prd.json | jq ".items[] | {id, title, passes}"'
```

### Git History Review

```bash
# See all Ralph commits
git log --oneline --grep="ralph"

# See approved iterations
git tag -l "approved-*"

# Diff between iterations
git diff approved-iter-3 approved-iter-5
```

### Debug Failed Iterations

```bash
# Find failed iterations in progress
grep -A 5 "FAILED" progress.txt

# Check specific review log
cat logs/review-5.log

# See what was reverted
git reflog | head -20
```

---

## 9. Best Practices

### PRD Design

| Do | Don't |
|-----|-------|
| Keep tasks small (1 context window) | "Build entire feature" |
| Specific acceptance criteria | Vague requirements |
| Clear priority ordering | All same priority |
| Use dependsOn for sequencing | Assume implicit order |

**Good task:**
```json
{
  "id": "US-001",
  "title": "Add email validation to signup form",
  "acceptanceCriteria": [
    "Email field validates format",
    "Shows error message for invalid email",
    "Passes unit test"
  ],
  "priority": 1,
  "passes": false
}
```

**Bad task:**
```json
{
  "id": "US-001",
  "title": "Build user authentication",
  "acceptanceCriteria": ["Users can log in"],
  "priority": 1,
  "passes": false
}
```

### CLAUDE.md Maintenance

- Keep under 300 lines
- Use `@path/to/file` to reference detailed docs
- Update after each major discovery
- Remove outdated patterns regularly

### When to Intervene

| Scenario | Action |
|----------|--------|
| Same error 3+ iterations | Stop, fix manually, restart |
| Cost running high | Reduce max_iterations |
| Wrong approach | Update specs, restart |
| Review always fails | Check reviewer prompt |

### Cost Management

```bash
# Estimate: ~$5-10 per 10 iterations (varies by task size)

# Conservative settings for testing
./scripts/ralph-pair.sh 5

# Production run
./scripts/ralph-pair.sh 30
```

---

## 10. Troubleshooting

### Common Issues

**"Claude Code not authenticated"**
```bash
claude
# Follow auth flow in browser
```

**"Codex not authenticated"**
```bash
codex
# Select sign-in method
```

**"jq: command not found"**
```bash
brew install jq  # macOS
sudo apt install jq  # Ubuntu
```

**"Permission denied"**
```bash
chmod +x scripts/ralph-pair.sh
```

**"CLAUDE.md not found"**
- Ensure you're in the project root
- Create the file following Section 4.1

**Review always returns UNKNOWN**
- Check `logs/review-*.log` for actual output
- Codex may need different prompt format
- Try simplifying the review prompt

**Loop runs forever**
- Always set `--max-iterations`
- Check prd.json updates are being committed
- Verify tests actually run and pass

### Reset and Restart

```bash
# Reset to last approved state
git reset --hard $(git tag -l "approved-*" | tail -1)

# Clear all logs
rm -rf logs/*

# Reset prd.json items
cat prd.json | jq '.items[].passes = false' > tmp.json && mv tmp.json prd.json

# Restart
./scripts/ralph-pair.sh
```

### Manual Override

```bash
# Mark item complete manually
cat prd.json | jq '.items[0].passes = true' > tmp.json && mv tmp.json prd.json
git add prd.json && git commit -m "manual: mark item complete"
```

---

## Quick Start Checklist

```
□ Prerequisites installed (claude, codex, jq)
□ Both CLIs authenticated
□ Git repository initialized
□ CLAUDE.md created with project conventions
□ prd.json created with small, clear tasks
□ progress.txt initialized
□ specs/ directory with conventions
□ ralph-pair.sh is executable
□ Ran single iteration test successfully
□ Logs directory created and gitignored
```

---

## Next Steps

1. **Start small**: Run with 5 iterations on a trivial task
2. **Review outputs**: Check logs, progress.txt, CLAUDE.md changes
3. **Tune prompts**: Adjust driver/reviewer prompts based on results
4. **Scale up**: Increase iterations for larger features
5. **Go overnight**: Use tmux + notifications for AFK runs

---

*Last updated: January 2026*
