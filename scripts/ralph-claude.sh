#!/bin/bash
#
# ralph-claude.sh - Single-vendor autonomous coding loop
# Driver: Claude Sonnet (fast implementation)
# Reviewer: Claude Opus (thorough review)
#
# Usage: ./scripts/ralph-claude.sh [max_iterations]
#
# v2.0 - Improved reliability:
#   - Added timeout handling for Claude CLI
#   - Better logging with timestamps
#   - Avoided pipe buffering issues
#   - Progress heartbeat for long operations
#

set -e

# ============ LOAD ENV ============
if [ -f "$PWD/.env" ]; then
    set -a
    source "$PWD/.env"
    set +a
    echo "Loaded .env"
fi

# Use Claude subscription auth instead of API key
unset ANTHROPIC_API_KEY

# ============ CONFIGURATION ============
MAX_ITERATIONS=${1:-20}
PROJECT_DIR="$(pwd)"
PRD_FILE="${PRD_FILE:-$PROJECT_DIR/prd.json}"
PROGRESS_FILE="$PROJECT_DIR/progress.txt"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
LOG_DIR="$PROJECT_DIR/logs"
DRIVER_PROMPT_FILE="$PROJECT_DIR/prompts/ralph-driver.md"
REVIEWER_PROMPT_FILE="$PROJECT_DIR/prompts/ralph-reviewer-claude.md"
PROGRESS_TEMPLATE="$PROJECT_DIR/prompts/progress-template.md"
SLEEP_BETWEEN=3

# Model configuration
DRIVER_MODEL="${DRIVER_MODEL:-sonnet}"
REVIEWER_MODEL="${REVIEWER_MODEL:-opus}"

# Timeout configuration (in seconds)
DRIVER_TIMEOUT="${DRIVER_TIMEOUT:-600}"    # 10 minutes for driver
REVIEWER_TIMEOUT="${REVIEWER_TIMEOUT:-300}" # 5 minutes for reviewer

# Temp files
DIFF_FILE="$LOG_DIR/.diff-temp"
PROMPT_FILE="$LOG_DIR/.prompt-temp"
RESPONSE_FILE="$LOG_DIR/.response-temp"

# Heartbeat/debug log (separate from iteration logs)
HEARTBEAT_LOG="$LOG_DIR/heartbeat.log"

# ============ SETUP ============
mkdir -p "$LOG_DIR"

# Cleanup on exit
cleanup() {
    # Kill any background heartbeat process
    if [ -n "$HEARTBEAT_PID" ] && kill -0 "$HEARTBEAT_PID" 2>/dev/null; then
        kill "$HEARTBEAT_PID" 2>/dev/null || true
    fi
    rm -f "$DIFF_FILE" "$PROMPT_FILE" "$RESPONSE_FILE" 2>/dev/null
    log_info "Cleanup complete"
}
trap cleanup EXIT
trap 'log_warn "Interrupted"; exit 130' INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Timestamped logging
timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log_info() { echo -e "${BLUE}[INFO $(timestamp)]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS $(timestamp)]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN $(timestamp)]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR $(timestamp)]${NC} $1"; }
log_fatal() { echo -e "${RED}[FATAL $(timestamp)]${NC} $1"; exit 1; }

# Debug logging to heartbeat file
log_debug() {
    echo "[$(timestamp)] $1" >> "$HEARTBEAT_LOG"
}

# ============ VALIDATION ============
validate_setup() {
    log_info "Validating setup..."

    # Check required files
    if [ ! -f "$PRD_FILE" ]; then
        log_fatal "prd.json not found. Create it first."
    fi

    if [ ! -f "$CLAUDE_MD" ]; then
        log_fatal "CLAUDE.md not found. Create it first."
    fi

    if [ ! -f "$PROGRESS_FILE" ]; then
        log_warn "progress.txt not found. Creating from template..."
        if [ -f "$PROGRESS_TEMPLATE" ]; then
            sed "s/{{DATE}}/$(date '+%Y-%m-%d %H:%M')/" "$PROGRESS_TEMPLATE" > "$PROGRESS_FILE"
        else
            echo "# Progress Log - $(date '+%Y-%m-%d %H:%M')" > "$PROGRESS_FILE"
        fi
    fi

    if [ ! -f "$DRIVER_PROMPT_FILE" ]; then
        log_fatal "prompts/ralph-driver.md not found. Create it first."
    fi

    # Create reviewer prompt if it doesn't exist
    if [ ! -f "$REVIEWER_PROMPT_FILE" ]; then
        log_info "Creating Claude-specific reviewer prompt..."
        create_reviewer_prompt
    fi

    # Check git
    if [ ! -d ".git" ]; then
        log_fatal "Not a git repository. Run 'git init' first."
    fi

    # Check Claude CLI
    if ! command -v claude &> /dev/null; then
        log_fatal "Claude Code CLI not found. Install it first."
    fi

    if ! command -v jq &> /dev/null; then
        log_fatal "jq not found. Install it first."
    fi

    log_success "Setup validated"
}

# ============ CREATE REVIEWER PROMPT ============
create_reviewer_prompt() {
    cat > "$REVIEWER_PROMPT_FILE" << 'PROMPT_EOF'
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
PROMPT_EOF
    log_success "Created $REVIEWER_PROMPT_FILE"
}

# ============ PRD HELPERS ============
check_all_complete() {
    jq -e '.items | all(.passes == true)' "$PRD_FILE" > /dev/null 2>&1
}

get_next_item() {
    jq -r '.items | map(select(.passes == false)) | sort_by(.priority) | .[0].id // empty' "$PRD_FILE"
}

# ============ ERROR DETECTION ============
check_for_errors() {
    local output="$1"
    local log_file="$2"
    # Exclude REVIEW_RESULT lines - they may mention error codes in review content
    local filtered=$(echo "$output" | grep -v 'REVIEW_RESULT:')

    # Check for rate limit errors (removed bare 429 - appears in code discussions)
    if echo "$filtered" | grep -qi "rate.limit.exceeded\|rate.limited\|too.many.requests\|usage.limit.reached"; then
        log_error "Rate limit detected in $log_file"
        return 1
    fi

    # Check for authentication errors (removed bare status codes)
    if echo "$filtered" | grep -qi "invalid.api.key\|authentication failed"; then
        log_error "Authentication error detected in $log_file"
        return 1
    fi

    # Check for network errors
    if echo "$filtered" | grep -qi "connection.refused\|network.error\|ECONNREFUSED"; then
        log_error "Network error detected in $log_file"
        return 1
    fi

    # Check for Claude CLI errors
    if echo "$filtered" | grep -qi "^error:\|^ERROR:\|fatal:"; then
        log_error "CLI error detected in $log_file"
        return 1
    fi

    return 0
}

# ============ STRIP ANSI CODES ============
# Removes ANSI escape sequences from text (fixes parsing when output contains color codes)
strip_ansi() {
    sed 's/\x1b\[[0-9;]*m//g'
}

# ============ EXTRACT VERDICT ============
# Note: Uses sed instead of regex to handle nested braces in JSON content
extract_verdict() {
    local output="$1"
    # Strip ANSI codes first, then extract JSON after REVIEW_RESULT:
    local json=$(echo "$output" | strip_ansi | grep 'REVIEW_RESULT:' | head -1 | sed 's/.*REVIEW_RESULT://')
    if [ -z "$json" ]; then
        echo "UNKNOWN"
        return
    fi
    local verdict=$(echo "$json" | jq -r '.verdict // "UNKNOWN"' 2>/dev/null)
    echo "${verdict:-UNKNOWN}"
}

extract_issues() {
    local output="$1"
    local json=$(echo "$output" | strip_ansi | grep 'REVIEW_RESULT:' | head -1 | sed 's/.*REVIEW_RESULT://')
    echo "$json" | jq -r '.issues[]? // empty' 2>/dev/null
}

extract_patterns() {
    local output="$1"
    local json=$(echo "$output" | strip_ansi | grep 'REVIEW_RESULT:' | head -1 | sed 's/.*REVIEW_RESULT://')
    echo "$json" | jq -r '.new_patterns[]? // empty' 2>/dev/null
}

extract_gotchas() {
    local output="$1"
    local json=$(echo "$output" | strip_ansi | grep 'REVIEW_RESULT:' | head -1 | sed 's/.*REVIEW_RESULT://')
    echo "$json" | jq -r '.new_gotchas[]? // empty' 2>/dev/null
}

# ============ HEARTBEAT FUNCTION ============
# Writes periodic heartbeat to log file so we can tell if process is still alive
start_heartbeat() {
    local label="$1"
    local interval="${2:-30}"  # Default 30 seconds
    local hb_log="$HEARTBEAT_LOG"  # Capture in local var for subshell

    (
        while true; do
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] HEARTBEAT: $label still running..." >> "$hb_log"
            sleep $interval
        done
    ) &
    HEARTBEAT_PID=$!
    log_debug "Started heartbeat (PID $HEARTBEAT_PID) for: $label"
}

stop_heartbeat() {
    if [ -n "$HEARTBEAT_PID" ] && kill -0 "$HEARTBEAT_PID" 2>/dev/null; then
        kill "$HEARTBEAT_PID" 2>/dev/null || true
        wait "$HEARTBEAT_PID" 2>/dev/null || true
        log_debug "Stopped heartbeat (PID $HEARTBEAT_PID)"
    fi
    HEARTBEAT_PID=""
}

# ============ ROBUST CLAUDE RUNNER ============
# Runs Claude CLI with timeout and proper output handling
# Avoids pipe buffering issues by writing directly to file
#
# Arguments:
#   $1 - prompt file path
#   $2 - output log file path
#   $3 - model name
#   $4 - timeout in seconds
#   $5 - label for logging
#
# Returns: 0 on success, 1 on failure
run_claude() {
    local prompt_file="$1"
    local log_file="$2"
    local model="$3"
    local timeout_secs="$4"
    local label="$5"

    log_debug "=== Starting $label ==="
    log_debug "Prompt file: $prompt_file"
    log_debug "Log file: $log_file"
    log_debug "Model: $model"
    log_debug "Timeout: ${timeout_secs}s"

    # Verify prompt file exists and has content
    if [ ! -f "$prompt_file" ]; then
        log_error "Prompt file not found: $prompt_file"
        log_debug "ERROR: Prompt file not found"
        return 1
    fi

    local prompt_size=$(wc -c < "$prompt_file")
    log_debug "Prompt size: $prompt_size bytes"

    if [ "$prompt_size" -eq 0 ]; then
        log_error "Prompt file is empty: $prompt_file"
        log_debug "ERROR: Empty prompt file"
        return 1
    fi

    # Clear previous log
    > "$log_file"

    # Start heartbeat
    start_heartbeat "$label"

    log_debug "Spawning Claude CLI process..."

    # Run Claude with timeout
    # Using timeout command with direct file redirection (no pipes)
    # The < redirection is more reliable than cat | for stdin
    local exit_code=0

    if command -v timeout &> /dev/null; then
        # GNU timeout available (Linux)
        timeout "$timeout_secs" claude -p \
            --model "$model" \
            --dangerously-skip-permissions \
            < "$prompt_file" \
            > "$log_file" 2>&1 || exit_code=$?
    elif command -v gtimeout &> /dev/null; then
        # GNU timeout via Homebrew (macOS)
        gtimeout "$timeout_secs" claude -p \
            --model "$model" \
            --dangerously-skip-permissions \
            < "$prompt_file" \
            > "$log_file" 2>&1 || exit_code=$?
    else
        # Fallback: use background job with manual timeout
        log_debug "Using manual timeout (no timeout/gtimeout found)"

        claude -p \
            --model "$model" \
            --dangerously-skip-permissions \
            < "$prompt_file" \
            > "$log_file" 2>&1 &
        local claude_pid=$!

        log_debug "Claude PID: $claude_pid"

        # Wait for completion or timeout
        local elapsed=0
        local last_size=0
        local stall_count=0
        local max_stall=180  # 3 minutes of no output = likely hung

        while kill -0 "$claude_pid" 2>/dev/null; do
            if [ $elapsed -ge $timeout_secs ]; then
                log_error "Timeout after ${timeout_secs}s - killing Claude process"
                log_debug "TIMEOUT: Killing PID $claude_pid after ${elapsed}s"
                kill -TERM "$claude_pid" 2>/dev/null || true
                sleep 2
                kill -KILL "$claude_pid" 2>/dev/null || true
                exit_code=124  # Same as timeout command
                break
            fi

            sleep 1
            elapsed=$((elapsed + 1))

            # Check if output file is growing (detect stalls)
            if [ -f "$log_file" ]; then
                local current_size=$(wc -c < "$log_file" 2>/dev/null || echo "0")
                if [ "$current_size" -eq "$last_size" ]; then
                    stall_count=$((stall_count + 1))
                    if [ $stall_count -ge $max_stall ]; then
                        log_error "No output for ${max_stall}s - process may be hung"
                        log_debug "STALL DETECTED: No output growth for ${stall_count}s"
                        log_debug "Output size stuck at: $current_size bytes"
                        # Don't kill yet - Claude might be thinking
                        # But log prominently for diagnosis
                    fi
                else
                    stall_count=0
                    last_size=$current_size
                fi
            fi

            # Log progress every 60 seconds
            if [ $((elapsed % 60)) -eq 0 ]; then
                local cur_size=$(wc -c < "$log_file" 2>/dev/null || echo "0")
                log_debug "Still waiting... ${elapsed}s elapsed, output: ${cur_size} bytes"
            fi
        done

        if [ $exit_code -eq 0 ]; then
            wait "$claude_pid" 2>/dev/null || exit_code=$?
        fi
    fi

    # Stop heartbeat
    stop_heartbeat

    log_debug "Claude process finished with exit code: $exit_code"

    # Check output
    if [ -f "$log_file" ]; then
        local output_size=$(wc -c < "$log_file")
        log_debug "Output size: $output_size bytes"
    else
        log_debug "WARNING: No output file created"
    fi

    # Handle exit codes
    if [ $exit_code -eq 124 ]; then
        log_error "$label timed out after ${timeout_secs}s"
        log_debug "TIMEOUT: $label"
        return 1
    elif [ $exit_code -ne 0 ]; then
        log_error "$label failed with exit code $exit_code"
        log_debug "FAILED: Exit code $exit_code"
        return 1
    fi

    log_debug "=== Completed $label successfully ==="
    return 0
}

# ============ RETRY WRAPPER ============
run_with_retry() {
    local max_retries=3
    local retry_delay=10
    local attempt=1

    # Arguments for run_claude
    local prompt_file="$1"
    local log_file="$2"
    local model="$3"
    local timeout_secs="$4"
    local label="$5"

    while [ $attempt -le $max_retries ]; do
        log_debug "Attempt $attempt of $max_retries for $label"

        if run_claude "$prompt_file" "$log_file" "$model" "$timeout_secs" "$label"; then
            return 0
        fi

        if [ $attempt -lt $max_retries ]; then
            log_warn "Attempt $attempt failed. Retrying in ${retry_delay}s..."
            log_debug "Retry delay: ${retry_delay}s"
            sleep $retry_delay
            retry_delay=$((retry_delay * 2))  # Exponential backoff
        fi
        attempt=$((attempt + 1))
    done

    log_error "All $max_retries attempts failed for $label"
    log_debug "FAILED: All retries exhausted for $label"
    return 1
}

# ============ MAIN LOOP ============
run_loop() {
    local ITERATION=1
    local NO_PROGRESS_COUNT=0
    local LAST_PRD_HASH=""

    log_info "Starting Ralph Claude Loop"
    log_info "PRD file: $PRD_FILE"
    log_info "Max iterations: $MAX_ITERATIONS"
    log_info "Driver: Claude $DRIVER_MODEL"
    log_info "Reviewer: Claude $REVIEWER_MODEL"
    echo ""

    while [ $ITERATION -le $MAX_ITERATIONS ]; do
        echo ""
        PROGRESS_PCT=$((ITERATION * 100 / MAX_ITERATIONS))
        echo "╔════════════════════════════════════════════════════════╗"
        echo "║  ITERATION $ITERATION of $MAX_ITERATIONS - $(date '+%H:%M:%S')                      ║"
        echo "╚════════════════════════════════════════════════════════╝"
        log_info "Progress: $PROGRESS_PCT% ($ITERATION/$MAX_ITERATIONS)"

        # Check for no-progress condition (prevent infinite loops)
        CURRENT_PRD_HASH=$(md5 -q "$PRD_FILE" 2>/dev/null || md5sum "$PRD_FILE" 2>/dev/null | cut -d' ' -f1)
        if [ "$CURRENT_PRD_HASH" == "$LAST_PRD_HASH" ]; then
            NO_PROGRESS_COUNT=$((NO_PROGRESS_COUNT + 1))
            if [ $NO_PROGRESS_COUNT -ge 3 ]; then
                log_error "No PRD progress for 3 consecutive iterations. Stopping to prevent infinite loop."
                log_warn "Review prd.json and progress.txt for issues."
                exit 1
            fi
            log_warn "No PRD change detected ($NO_PROGRESS_COUNT/3 warnings)"
        else
            NO_PROGRESS_COUNT=0
            LAST_PRD_HASH="$CURRENT_PRD_HASH"
        fi

        # Check if all PRD items complete
        if check_all_complete; then
            log_success "All PRD items complete!"
            echo ""
            echo "🎉 Ralph Claude Loop finished successfully!"
            exit 0
        fi

        NEXT_ITEM=$(get_next_item)
        log_info "Next item: $NEXT_ITEM"

        # ============ DRIVER PHASE ============
        echo ""
        log_info "╭─────────────────────────────────────╮"
        log_info "│  DRIVER: Claude $DRIVER_MODEL              │"
        log_info "╰─────────────────────────────────────╯"

        # Run Claude Sonnet as driver (with retry logic)
        DRIVER_LOG="$LOG_DIR/driver-$ITERATION.log"

        log_debug "Starting driver phase for iteration $ITERATION"
        log_info "Driver timeout: ${DRIVER_TIMEOUT}s"

        if ! run_with_retry "$DRIVER_PROMPT_FILE" "$DRIVER_LOG" "$DRIVER_MODEL" "$DRIVER_TIMEOUT" "Driver (iteration $ITERATION)"; then
            log_fatal "Driver phase failed after retries. Check $DRIVER_LOG and $HEARTBEAT_LOG"
        fi

        # Verify driver produced output
        if [ ! -s "$DRIVER_LOG" ]; then
            log_fatal "Driver phase produced no output. Check Claude CLI."
        fi

        # Check for errors in driver output
        DRIVER_OUTPUT=$(cat "$DRIVER_LOG")
        if ! check_for_errors "$DRIVER_OUTPUT" "$DRIVER_LOG"; then
            log_fatal "Driver phase failed with error. Check $DRIVER_LOG"
        fi

        log_success "Driver phase complete"
        log_debug "Driver phase completed successfully"

        # ============ REVIEWER PHASE ============
        echo ""
        log_info "╭─────────────────────────────────────╮"
        log_info "│  REVIEWER: Claude $REVIEWER_MODEL            │"
        log_info "╰─────────────────────────────────────╯"

        # Save diff to temp file (diff current commit vs previous commit)
        git diff HEAD~1 HEAD > "$DIFF_FILE" 2>/dev/null || echo "No changes detected" > "$DIFF_FILE"

        # Check if there are actual changes to review
        if [ ! -s "$DIFF_FILE" ] || grep -q "No changes detected" "$DIFF_FILE"; then
            log_warn "No changes to review. Continuing..."
            ITERATION=$((ITERATION+1))
            continue
        fi

        # Build prompt with diff inserted
        log_debug "Building reviewer prompt with diff"
        {
            sed '/{{DIFF}}/,$d' "$REVIEWER_PROMPT_FILE"
            cat "$DIFF_FILE"
            sed '1,/{{DIFF}}/d' "$REVIEWER_PROMPT_FILE"
        } > "$PROMPT_FILE"

        local prompt_lines=$(wc -l < "$PROMPT_FILE")
        log_debug "Reviewer prompt: $prompt_lines lines"

        # Run Claude Opus as reviewer (with retry logic)
        REVIEW_LOG="$LOG_DIR/review-$ITERATION.log"

        log_debug "Starting reviewer phase for iteration $ITERATION"
        log_info "Reviewer timeout: ${REVIEWER_TIMEOUT}s"

        if ! run_with_retry "$PROMPT_FILE" "$REVIEW_LOG" "$REVIEWER_MODEL" "$REVIEWER_TIMEOUT" "Reviewer (iteration $ITERATION)"; then
            log_fatal "Reviewer phase failed after retries. Check $REVIEW_LOG and $HEARTBEAT_LOG"
        fi

        # Check for errors in reviewer output
        REVIEW_OUTPUT=$(cat "$REVIEW_LOG")
        if ! check_for_errors "$REVIEW_OUTPUT" "$REVIEW_LOG"; then
            log_fatal "Reviewer phase failed with error. Check $REVIEW_LOG"
        fi

        # Extract verdict using the REVIEW_RESULT: prefix
        VERDICT=$(extract_verdict "$REVIEW_OUTPUT")

        echo ""
        if [ "$VERDICT" == "PASS" ]; then
            log_success "Review PASSED ✓"

            # Tag approved iteration
            git tag "approved-iter-$ITERATION" 2>/dev/null || true

            # Extract and append learnings
            NEW_PATTERNS=$(extract_patterns "$REVIEW_OUTPUT")
            NEW_GOTCHAS=$(extract_gotchas "$REVIEW_OUTPUT")

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
            ISSUES=$(extract_issues "$REVIEW_OUTPUT")

            # Log to progress.txt
            echo "" >> "$PROGRESS_FILE"
            echo "### Iteration $ITERATION - FAILED ✗" >> "$PROGRESS_FILE"
            echo "$(date '+%Y-%m-%d %H:%M')" >> "$PROGRESS_FILE"
            echo "Issues:" >> "$PROGRESS_FILE"
            echo "$ISSUES" >> "$PROGRESS_FILE"

            # Discard failed code changes, keep progress/learnings
            log_info "Discarding failed changes, keeping feedback..."

            # Save learnings to temp files first
            cp "$PROGRESS_FILE" "$PROGRESS_FILE.tmp" 2>/dev/null || true
            cp "$CLAUDE_MD" "$CLAUDE_MD.tmp" 2>/dev/null || true

            # Reset to clean state
            git checkout -- . 2>/dev/null || true
            git clean -fd 2>/dev/null || true

            # Restore learnings from temp files
            mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE" 2>/dev/null || true
            mv "$CLAUDE_MD.tmp" "$CLAUDE_MD" 2>/dev/null || true

        else
            log_error "Could not parse verdict: $VERDICT"
            log_error "Review output saved to $REVIEW_LOG"
            log_fatal "Stopping loop due to unparseable review response"
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
    echo "║   RALPH CLAUDE LOOP v2.0                                  ║"
    echo "║                                                           ║"
    echo "║   Driver:   Claude Sonnet (fast implementation)          ║"
    echo "║   Reviewer: Claude Opus (thorough review)                ║"
    echo "║                                                           ║"
    if [[ "$PRD_FILE" == *"audit.json"* ]]; then
    echo "║   Mode:     AUDIT REMEDIATION                            ║"
    fi
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # Initialize heartbeat log
    mkdir -p "$LOG_DIR"
    echo "=== Ralph Claude Loop Started: $(timestamp) ===" > "$HEARTBEAT_LOG"
    echo "Project: $PROJECT_DIR" >> "$HEARTBEAT_LOG"
    echo "PRD: $PRD_FILE" >> "$HEARTBEAT_LOG"
    echo "Driver model: $DRIVER_MODEL (timeout: ${DRIVER_TIMEOUT}s)" >> "$HEARTBEAT_LOG"
    echo "Reviewer model: $REVIEWER_MODEL (timeout: ${REVIEWER_TIMEOUT}s)" >> "$HEARTBEAT_LOG"
    echo "" >> "$HEARTBEAT_LOG"

    # Check for timeout command
    if command -v timeout &> /dev/null; then
        log_info "Using GNU timeout command"
        log_debug "Timeout: GNU timeout"
    elif command -v gtimeout &> /dev/null; then
        log_info "Using Homebrew gtimeout command"
        log_debug "Timeout: gtimeout (Homebrew)"
    else
        log_warn "No timeout command found - using manual timeout (less reliable)"
        log_warn "Install coreutils for better reliability: brew install coreutils"
        log_debug "Timeout: manual (fallback)"
    fi

    echo ""
    log_info "Heartbeat log: $HEARTBEAT_LOG"
    log_info "Tail the heartbeat log to monitor: tail -f $HEARTBEAT_LOG"
    echo ""

    validate_setup
    run_loop
}

main "$@"
