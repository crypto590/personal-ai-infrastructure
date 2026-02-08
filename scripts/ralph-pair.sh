#!/bin/bash
#
# ralph-pair.sh - Dual-model autonomous coding loop
# Driver: Claude Code (Opus 4.5)
# Reviewer: OpenAI Codex (GPT)
#
# Usage: ./scripts/ralph-pair.sh [max_iterations]
#

set -e

# ============ LOAD ENV ============
if [ -f "$PWD/.env" ]; then
    export $(grep -v '^#' "$PWD/.env" | xargs)
    echo "Loaded .env"
fi

# Use Claude subscription auth instead of API key
unset ANTHROPIC_API_KEY

# ============ CONFIGURATION ============
MAX_ITERATIONS=${1:-20}
PROJECT_DIR="$(pwd)"
PRD_FILE="$PROJECT_DIR/prd.json"
PROGRESS_FILE="$PROJECT_DIR/progress.txt"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
AGENTS_MD="$PROJECT_DIR/AGENTS.md"
LOG_DIR="$PROJECT_DIR/logs"
DRIVER_PROMPT_FILE="$PROJECT_DIR/prompts/ralph-driver.md"
REVIEWER_PROMPT_FILE="$PROJECT_DIR/prompts/ralph-reviewer.md"
PROGRESS_TEMPLATE="$PROJECT_DIR/prompts/progress-template.md"
SLEEP_BETWEEN=3

# Model configuration (override via env vars)
CLAUDE_MODEL="${CLAUDE_MODEL:-opus}"
CODEX_MODEL="${CODEX_MODEL:-gpt-5.2-codex}"

# Temp files
DIFF_FILE="$LOG_DIR/.diff-temp"
PROMPT_FILE="$LOG_DIR/.prompt-temp"

# ============ SETUP ============
mkdir -p "$LOG_DIR"

# Cleanup on exit
cleanup() {
    rm -f "$DIFF_FILE" "$PROMPT_FILE" 2>/dev/null
    log_info "Cleanup complete"
}
trap cleanup EXIT
trap 'log_warn "Interrupted"; exit 130' INT TERM

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
        log_warn "progress.txt not found. Creating from template..."
        sed "s/{{DATE}}/$(date '+%Y-%m-%d %H:%M')/" "$PROGRESS_TEMPLATE" > "$PROGRESS_FILE"
    fi

    if [ ! -f "$DRIVER_PROMPT_FILE" ]; then
        log_error "prompts/ralph-driver.md not found. Create it first."
        exit 1
    fi

    if [ ! -f "$REVIEWER_PROMPT_FILE" ]; then
        log_error "prompts/ralph-reviewer.md not found. Create it first."
        exit 1
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
    log_info "Driver: Claude ($CLAUDE_MODEL)"
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

        # Run Claude Code - pipe prompt via stdin (|| true to prevent set -e exit)
        cat "$DRIVER_PROMPT_FILE" | claude -p --model "$CLAUDE_MODEL" --dangerously-skip-permissions \
               2>&1 | tee "$LOG_DIR/driver-$ITERATION.log" || true

        # Claude process is now DEAD - context cleared

        log_success "Driver phase complete"

        # ============ REVIEWER PHASE ============
        echo ""
        log_info "╭─────────────────────────────────────╮"
        log_info "│  REVIEWER: Codex (GPT)             │"
        log_info "╰─────────────────────────────────────╯"

        # Sync CLAUDE.md to AGENTS.md for Codex
        sync_agents_md

        # Save diff to temp file
        git diff HEAD~1 > "$DIFF_FILE" 2>/dev/null || echo "No changes detected" > "$DIFF_FILE"

        # Build prompt with diff inserted (avoids sed escaping issues)
        {
            cat "$REVIEWER_PROMPT_FILE" | sed '/{{DIFF}}/,$d'
            cat "$DIFF_FILE"
            cat "$REVIEWER_PROMPT_FILE" | sed '1,/{{DIFF}}/d'
        } > "$PROMPT_FILE"

        # Run Codex - FRESH PROCESS (|| true to prevent set -e exit)
        cat "$PROMPT_FILE" | codex exec \
            --model "$CODEX_MODEL" \
            --dangerously-bypass-approvals-and-sandbox \
            2>&1 | tee "$LOG_DIR/review-$ITERATION.log" || true

        # Codex process is now DEAD - context cleared

        # Parse review output
        REVIEW_OUTPUT=$(cat "$LOG_DIR/review-$ITERATION.log")

        # Extract verdict (portable - works on macOS and Linux)
        VERDICT=$(echo "$REVIEW_OUTPUT" | sed -n 's/.*"verdict"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
        VERDICT="${VERDICT:-UNKNOWN}"

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

            # Discard failed code changes, keep progress/learnings
            log_info "Discarding failed changes, keeping feedback..."
            git stash push -- "$PROGRESS_FILE" "$CLAUDE_MD" 2>/dev/null || true
            git checkout -- . 2>/dev/null || true
            git clean -fd 2>/dev/null || true
            git stash pop 2>/dev/null || true

        else
            log_warn "Could not parse verdict: $VERDICT"
            log_warn "Review output saved to logs/review-$ITERATION.log"
            # Continue anyway without committing
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
