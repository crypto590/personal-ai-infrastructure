#!/bin/bash
#
# ralph-audit.sh - Audit previous ralph iterations with Opus review
# Reviews commits that may have been auto-approved without actual review
#
# Usage: ./scripts/ralph-audit.sh [max_iterations] [--fresh]
#
# Options:
#   max_iterations  Number of iterations to audit (default: all)
#   --fresh         Start fresh, ignoring any saved checkpoint
#
# Resume: Automatically resumes from last checkpoint on crash/interrupt
#

set -e

# ============ LOAD ENV ============
if [ -f "$PWD/.env" ]; then
    export $(grep -v '^#' "$PWD/.env" | xargs)
    echo "Loaded .env"
fi

# Use Claude subscription auth
unset ANTHROPIC_API_KEY

# ============ CONFIGURATION ============
# Check for --fresh flag
FRESH_START=false
for arg in "$@"; do
    if [ "$arg" == "--fresh" ]; then
        FRESH_START=true
    fi
done

MAX_ITERATIONS=${1:-all}
# Handle if first arg is --fresh
[ "$MAX_ITERATIONS" == "--fresh" ] && MAX_ITERATIONS="all"

PROJECT_DIR="$(pwd)"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
LOG_DIR="$PROJECT_DIR/logs/audit"
TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
REPORT_FILE="$LOG_DIR/audit-report-$TIMESTAMP.md"
AUDIT_JSON="$PROJECT_DIR/audit.json"
REVIEWER_PROMPT_FILE="$PROJECT_DIR/prompts/ralph-reviewer-claude.md"
SLEEP_BETWEEN=2

# Reviewer model
REVIEWER_MODEL="${REVIEWER_MODEL:-opus}"

# Temp files
DIFF_FILE="$LOG_DIR/.diff-temp"
PROMPT_FILE="$LOG_DIR/.prompt-temp"

# Checkpoint for resume
CHECKPOINT_FILE="$LOG_DIR/.audit-checkpoint"

# ============ SETUP ============
mkdir -p "$LOG_DIR"

# Cleanup on exit (preserve checkpoint on error for resume)
cleanup() {
    local exit_code=$?
    rm -f "$DIFF_FILE" "$PROMPT_FILE" 2>/dev/null
    if [ $exit_code -eq 0 ]; then
        # Success - remove checkpoint
        rm -f "$CHECKPOINT_FILE" 2>/dev/null
        log_info "Audit completed successfully"
    else
        log_info "Cleanup complete (checkpoint preserved for resume)"
    fi
}
trap cleanup EXIT
trap 'log_warn "Interrupted"; exit 130' INT TERM

# ============ CHECKPOINT FUNCTIONS ============
save_checkpoint() {
    local index="$1"
    local pass="$2"
    local fail="$3"
    local unknown="$4"
    local report="$5"
    echo "$index|$pass|$fail|$unknown|$report" > "$CHECKPOINT_FILE"
}

load_checkpoint() {
    if [ -f "$CHECKPOINT_FILE" ]; then
        cat "$CHECKPOINT_FILE"
    else
        echo ""
    fi
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_fatal() { echo -e "${RED}[FATAL]${NC} $1"; exit 1; }

# ============ VALIDATION ============
validate_setup() {
    log_info "Validating setup..."

    if [ ! -d ".git" ]; then
        log_fatal "Not a git repository."
    fi

    if ! command -v claude &> /dev/null; then
        log_fatal "Claude Code CLI not found."
    fi

    if ! command -v jq &> /dev/null; then
        log_fatal "jq not found."
    fi

    # Check/create reviewer prompt
    if [ ! -f "$REVIEWER_PROMPT_FILE" ]; then
        log_info "Creating reviewer prompt..."
        create_reviewer_prompt
    fi

    log_success "Setup validated"
}

# ============ CREATE REVIEWER PROMPT ============
create_reviewer_prompt() {
    mkdir -p "$(dirname "$REVIEWER_PROMPT_FILE")"
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

# ============ ERROR DETECTION ============
check_for_errors() {
    local output="$1"
    # Exclude REVIEW_RESULT lines - they may mention error codes in review content
    local filtered=$(echo "$output" | grep -v 'REVIEW_RESULT:')

    if echo "$filtered" | grep -qi "rate.limit\|too.many.requests\|usage.limit"; then
        return 1
    fi
    if echo "$filtered" | grep -qi "unauthorized\|authentication failed"; then
        return 1
    fi
    if echo "$filtered" | grep -qi "connection.refused\|network.error\|ECONNREFUSED"; then
        return 1
    fi
    if echo "$filtered" | grep -qi "^error:\|^ERROR:\|fatal:"; then
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

# ============ GET RALPH COMMITS ============
get_ralph_commits() {
    # Get ralph iteration commits in reverse order (oldest first)
    if [ "$MAX_ITERATIONS" == "all" ]; then
        git log --oneline --grep="ralph iteration.*approved" --reverse
    else
        git log --oneline --grep="ralph iteration.*approved" --reverse | head -n "$MAX_ITERATIONS"
    fi
}

# ============ JSON HELPERS ============
init_audit_json() {
    cat > "$AUDIT_JSON" << 'EOF'
{
  "projectName": "streakflow-audit-remediation",
  "description": "Failed audit items requiring remediation",
  "generatedAt": "TIMESTAMP_PLACEHOLDER",
  "items": []
}
EOF
    # Replace timestamp
    sed -i '' "s/TIMESTAMP_PLACEHOLDER/$(date -Iseconds)/" "$AUDIT_JSON"
}

add_failed_item_to_json() {
    local iter_num="$1"
    local commit="$2"
    local issues="$3"

    # Build acceptance criteria from issues
    local criteria_json="[]"
    if [ -n "$issues" ]; then
        criteria_json=$(echo "$issues" | jq -R -s 'split("\n") | map(select(length > 0)) | map("Fix: " + .)')
    fi

    # Create the item JSON
    local item_json=$(jq -n \
        --arg id "AUDIT-$iter_num" \
        --arg title "Remediate issues from iteration $iter_num" \
        --arg commit "$commit" \
        --argjson criteria "$criteria_json" \
        --arg notes "Commit: $commit" \
        '{
            id: $id,
            title: $title,
            acceptanceCriteria: $criteria,
            priority: 1,
            passes: false,
            dependsOn: [],
            commit: $commit,
            notes: $notes
        }')

    # Append to items array
    local tmp_file=$(mktemp)
    jq --argjson item "$item_json" '.items += [$item]' "$AUDIT_JSON" > "$tmp_file"
    mv "$tmp_file" "$AUDIT_JSON"
}

finalize_audit_json() {
    local total_failed="$1"

    # Update priorities based on order
    local tmp_file=$(mktemp)
    jq '.items |= to_entries | .items |= map(.value.priority = .key + 1 | .value) | .items |= map(.)' "$AUDIT_JSON" > "$tmp_file"
    mv "$tmp_file" "$AUDIT_JSON"

    # Add summary
    tmp_file=$(mktemp)
    jq --arg count "$total_failed" '.totalFailedItems = ($count | tonumber)' "$AUDIT_JSON" > "$tmp_file"
    mv "$tmp_file" "$AUDIT_JSON"
}

# ============ INITIALIZE REPORT ============
init_report() {
    cat > "$REPORT_FILE" << EOF
# Ralph Audit Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Reviewer:** Claude $REVIEWER_MODEL
**Max Iterations:** $MAX_ITERATIONS

---

## Summary

| Iteration | Commit | Verdict | Issues |
|-----------|--------|---------|--------|
EOF
}

append_to_report() {
    local iteration="$1"
    local commit="$2"
    local verdict="$3"
    local issue_count="$4"

    local verdict_emoji="❓"
    if [ "$verdict" == "PASS" ]; then
        verdict_emoji="✅"
    elif [ "$verdict" == "FAIL" ]; then
        verdict_emoji="❌"
    fi

    echo "| $iteration | \`$commit\` | $verdict_emoji $verdict | $issue_count |" >> "$REPORT_FILE"
}

append_details() {
    local iteration="$1"
    local commit="$2"
    local verdict="$3"
    local issues="$4"

    echo "" >> "$REPORT_FILE"
    echo "### Iteration $iteration - $verdict" >> "$REPORT_FILE"
    echo "**Commit:** \`$commit\`" >> "$REPORT_FILE"

    if [ -n "$issues" ]; then
        echo "" >> "$REPORT_FILE"
        echo "**Issues:**" >> "$REPORT_FILE"
        echo "$issues" | while read -r issue; do
            [ -n "$issue" ] && echo "- $issue" >> "$REPORT_FILE"
        done
    fi
}

finalize_report() {
    local pass_count="$1"
    local fail_count="$2"
    local unknown_count="$3"
    local total="$4"

    echo "" >> "$REPORT_FILE"
    echo "---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## Totals" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "- **Passed:** $pass_count / $total" >> "$REPORT_FILE"
    echo "- **Failed:** $fail_count / $total" >> "$REPORT_FILE"
    echo "- **Unknown:** $unknown_count / $total" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "---" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "## Details" >> "$REPORT_FILE"
}

# ============ MAIN AUDIT ============
run_audit() {
    log_info "Starting Ralph Audit"
    log_info "Reviewer: Claude $REVIEWER_MODEL"
    if [ "$MAX_ITERATIONS" == "all" ]; then
        log_info "Max iterations: ALL"
    else
        log_info "Max iterations: $MAX_ITERATIONS"
    fi
    echo ""

    # Get commits to audit
    COMMITS=$(get_ralph_commits)
    TOTAL=$(echo "$COMMITS" | grep -c "ralph iteration" || echo "0")

    if [ "$TOTAL" -eq 0 ]; then
        log_warn "No ralph iteration commits found"
        exit 0
    fi

    log_info "Found $TOTAL ralph iteration commits to audit"
    echo ""

    # Check for checkpoint (resume support)
    CHECKPOINT=$(load_checkpoint)
    START_INDEX=0
    PASS_COUNT=0
    FAIL_COUNT=0
    UNKNOWN_COUNT=0

    # Clear checkpoint if --fresh
    if [ "$FRESH_START" == "true" ] && [ -n "$CHECKPOINT" ]; then
        log_info "Fresh start requested - clearing checkpoint"
        rm -f "$CHECKPOINT_FILE" 2>/dev/null
        CHECKPOINT=""
    fi

    if [ -n "$CHECKPOINT" ]; then
        IFS='|' read -r START_INDEX PASS_COUNT FAIL_COUNT UNKNOWN_COUNT SAVED_REPORT <<< "$CHECKPOINT"
        log_info "Resuming from checkpoint: index $START_INDEX"
        log_info "Previous progress: $PASS_COUNT passed, $FAIL_COUNT failed, $UNKNOWN_COUNT unknown"
        # Use the saved report file
        REPORT_FILE="$SAVED_REPORT"
        echo ""
    else
        # Fresh start - initialize report and JSON
        init_report
        init_audit_json
        log_info "Initialized audit.json"
    fi

    AUDITED=$START_INDEX

    # Track details for later
    DETAILS_FILE="$LOG_DIR/.details-temp"
    [ "$START_INDEX" -eq 0 ] && > "$DETAILS_FILE"

    # Convert commits to array for sequential access
    COMMIT_ARRAY=()
    while IFS= read -r line; do
        COMMIT_ARRAY+=("$line")
    done <<< "$COMMITS"

    # Process each commit (diff from previous iteration to this one)
    PREV_COMMIT=""
    for i in "${!COMMIT_ARRAY[@]}"; do
        # Skip already-processed commits on resume
        if [ "$i" -lt "$START_INDEX" ]; then
            # Still need to track prev commit for diff
            PREV_COMMIT=$(echo "${COMMIT_ARRAY[$i]}" | awk '{print $1}')
            continue
        fi
        line="${COMMIT_ARRAY[$i]}"
        COMMIT_HASH=$(echo "$line" | awk '{print $1}')
        COMMIT_MSG=$(echo "$line" | cut -d' ' -f2-)

        # Extract iteration number
        ITER_NUM=$(echo "$COMMIT_MSG" | grep -o '[0-9]\+' | head -1)

        AUDITED=$((AUDITED+1))

        echo ""
        echo "╭─────────────────────────────────────────╮"
        echo "│  AUDITING: Iteration $ITER_NUM ($AUDITED/$TOTAL)        │"
        echo "│  Commit: $COMMIT_HASH                       │"
        echo "╰─────────────────────────────────────────╯"

        # Get diff between previous iteration and this one
        if [ -z "$PREV_COMMIT" ]; then
            # First iteration - diff from parent
            git diff "${COMMIT_HASH}^" "$COMMIT_HASH" > "$DIFF_FILE" 2>/dev/null || {
                git show "$COMMIT_HASH" --format="" > "$DIFF_FILE" 2>/dev/null || true
            }
        else
            # Diff from previous approved commit to this one (captures all work in iteration)
            git diff "$PREV_COMMIT" "$COMMIT_HASH" > "$DIFF_FILE" 2>/dev/null || {
                log_warn "Could not get diff for $COMMIT_HASH"
                append_to_report "$ITER_NUM" "$COMMIT_HASH" "SKIP" "0"
                UNKNOWN_COUNT=$((UNKNOWN_COUNT+1))
                PREV_COMMIT="$COMMIT_HASH"
                continue
            }
        fi

        # Skip if no meaningful changes
        if [ ! -s "$DIFF_FILE" ]; then
            log_warn "Empty diff for iteration $ITER_NUM"
            append_to_report "$ITER_NUM" "$COMMIT_HASH" "SKIP" "0"
            UNKNOWN_COUNT=$((UNKNOWN_COUNT+1))
            PREV_COMMIT="$COMMIT_HASH"
            continue
        fi

        # Check diff size - skip if just progress.txt updates
        DIFF_LINES=$(wc -l < "$DIFF_FILE" | tr -d ' ')
        if [ "$DIFF_LINES" -lt 10 ]; then
            # Check if it's just progress.txt
            if grep -q "^diff --git a/progress.txt" "$DIFF_FILE" && [ "$(grep -c "^diff --git" "$DIFF_FILE")" -eq 1 ]; then
                log_warn "Iteration $ITER_NUM only has progress.txt update, skipping"
                append_to_report "$ITER_NUM" "$COMMIT_HASH" "SKIP" "0"
                UNKNOWN_COUNT=$((UNKNOWN_COUNT+1))
                PREV_COMMIT="$COMMIT_HASH"
                continue
            fi
        fi

        log_info "Diff size: $DIFF_LINES lines"

        # Build prompt
        {
            cat "$REVIEWER_PROMPT_FILE" | sed '/{{DIFF}}/,$d'
            cat "$DIFF_FILE"
            cat "$REVIEWER_PROMPT_FILE" | sed '1,/{{DIFF}}/d'
        } > "$PROMPT_FILE"

        # Run Opus reviewer
        REVIEW_LOG="$LOG_DIR/audit-iter-$ITER_NUM.log"
        log_info "Running Opus review..."

        cat "$PROMPT_FILE" | claude -p --model "$REVIEWER_MODEL" --dangerously-skip-permissions \
            2>&1 | tee "$REVIEW_LOG" || true

        REVIEW_OUTPUT=$(cat "$REVIEW_LOG")

        # Check for errors
        if ! check_for_errors "$REVIEW_OUTPUT"; then
            log_error "Review failed with error for iteration $ITER_NUM"
            log_fatal "Stopping audit due to error. Check $REVIEW_LOG"
        fi

        # Extract verdict
        VERDICT=$(extract_verdict "$REVIEW_OUTPUT")
        ISSUES=$(extract_issues "$REVIEW_OUTPUT")
        ISSUE_COUNT=$(echo "$ISSUES" | grep -c . || echo "0")

        # Update counters and report
        if [ "$VERDICT" == "PASS" ]; then
            log_success "Iteration $ITER_NUM: PASS ✅"
            PASS_COUNT=$((PASS_COUNT+1))
            append_to_report "$ITER_NUM" "$COMMIT_HASH" "PASS" "0"
        elif [ "$VERDICT" == "FAIL" ]; then
            log_error "Iteration $ITER_NUM: FAIL ❌ ($ISSUE_COUNT issues)"
            FAIL_COUNT=$((FAIL_COUNT+1))
            append_to_report "$ITER_NUM" "$COMMIT_HASH" "FAIL" "$ISSUE_COUNT"
            # Save details
            echo "ITER:$ITER_NUM:$COMMIT_HASH:$ISSUES" >> "$DETAILS_FILE"
            # Add to audit.json for remediation
            add_failed_item_to_json "$ITER_NUM" "$COMMIT_HASH" "$ISSUES"
        else
            log_warn "Iteration $ITER_NUM: UNKNOWN ❓"
            UNKNOWN_COUNT=$((UNKNOWN_COUNT+1))
            append_to_report "$ITER_NUM" "$COMMIT_HASH" "UNKNOWN" "0"
        fi

        # Update previous commit for next iteration
        PREV_COMMIT="$COMMIT_HASH"

        # Save checkpoint after each successful iteration
        save_checkpoint "$((i + 1))" "$PASS_COUNT" "$FAIL_COUNT" "$UNKNOWN_COUNT" "$REPORT_FILE"

        log_info "Sleeping ${SLEEP_BETWEEN}s..."
        sleep $SLEEP_BETWEEN

    done

    # Finalize report
    finalize_report "$PASS_COUNT" "$FAIL_COUNT" "$UNKNOWN_COUNT" "$TOTAL"

    # Add details section for failures
    if [ -s "$DETAILS_FILE" ]; then
        while IFS=: read -r _ iter commit issues; do
            append_details "$iter" "$commit" "FAIL" "$issues"
        done < "$DETAILS_FILE"
    fi

    rm -f "$DETAILS_FILE"

    # Finalize audit.json
    finalize_audit_json "$FAIL_COUNT"

    # Print summary
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                    AUDIT COMPLETE                      ║"
    echo "╠════════════════════════════════════════════════════════╣"
    printf "║  Passed:  %-3s / %-3s                                   ║\n" "$PASS_COUNT" "$TOTAL"
    printf "║  Failed:  %-3s / %-3s                                   ║\n" "$FAIL_COUNT" "$TOTAL"
    printf "║  Unknown: %-3s / %-3s                                   ║\n" "$UNKNOWN_COUNT" "$TOTAL"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║  Report:     $REPORT_FILE"
    echo "║  Audit JSON: $AUDIT_JSON"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""

    if [ "$FAIL_COUNT" -gt 0 ]; then
        log_warn "$FAIL_COUNT iterations failed review!"
        log_info "Run './scripts/ralph-claude.sh' with PRD_FILE=audit.json to remediate"
        exit 1
    else
        log_success "All audited iterations passed!"
        # Clear audit.json if no failures
        echo '{"projectName":"streakflow-audit-remediation","items":[],"totalFailedItems":0}' > "$AUDIT_JSON"
        exit 0
    fi
}

# ============ ENTRY POINT ============
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║   🔍 RALPH AUDIT                                         ║"
    echo "║                                                           ║"
    echo "║   Retroactive review of auto-approved iterations         ║"
    echo "║   Reviewer: Claude Opus                                  ║"
    echo "║   Output:   audit.json (PRD format for remediation)      ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    validate_setup
    run_audit
}

main "$@"
