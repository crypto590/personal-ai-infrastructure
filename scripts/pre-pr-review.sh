#!/usr/bin/env bash
#
# pre-pr-review.sh - Multi-AI Code Review Orchestrator
# Runs Claude, Gemini, and Codex in parallel for diverse code review perspectives
#

set -euo pipefail

# macOS-compatible timeout function
run_with_timeout() {
    local timeout_secs=$1
    shift

    # Try gtimeout (coreutils), then timeout, then perl fallback
    if command -v gtimeout &>/dev/null; then
        gtimeout "$timeout_secs" "$@"
    elif command -v timeout &>/dev/null; then
        timeout "$timeout_secs" "$@"
    else
        # Perl fallback for macOS
        perl -e '
            use strict;
            use warnings;
            my $timeout = shift @ARGV;
            my $pid = fork();
            if ($pid == 0) {
                exec @ARGV;
                exit 1;
            }
            local $SIG{ALRM} = sub { kill 9, $pid; exit 124; };
            alarm $timeout;
            waitpid($pid, 0);
            my $status = $? >> 8;
            exit $status;
        ' "$timeout_secs" "$@"
    fi
}

# Configuration
BASE_BRANCH="${1:-main}"
TIMEOUT_SECONDS=300  # 5 minute timeout per reviewer
OUTPUT_DIR=$(mktemp -d)

# Get project root (where the command is run from)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
REVIEWS_DIR="$PROJECT_ROOT/docs/reviews"
TIMESTAMP=$(date +"%Y-%m-%d-%H%M%S")

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cleanup on exit
cleanup() {
    rm -rf "$OUTPUT_DIR"
}
trap cleanup EXIT

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${CYAN}$1${NC}"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check git repo
    if ! git rev-parse --is-inside-work-tree &>/dev/null; then
        log_error "Not in a git repository"
        exit 1
    fi

    # Check branch differs from base
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" = "$BASE_BRANCH" ]; then
        log_error "Currently on $BASE_BRANCH branch. Switch to a feature branch first."
        exit 1
    fi

    # Check commits exist
    COMMIT_COUNT=$(git rev-list --count "$BASE_BRANCH"..HEAD 2>/dev/null || echo "0")
    if [ "$COMMIT_COUNT" = "0" ]; then
        log_error "No commits found between $BASE_BRANCH and HEAD"
        exit 1
    fi

    # Check CLIs are installed
    local missing_cli=0
    for cli in claude gemini codex; do
        if ! command -v "$cli" &>/dev/null; then
            log_warn "$cli CLI not found - will skip this reviewer"
            missing_cli=1
        fi
    done

    log_success "Prerequisites check passed"
    log_info "Branch: $CURRENT_BRANCH"
    log_info "Base: $BASE_BRANCH"
    log_info "Commits: $COMMIT_COUNT"
}

# Get the diff for review
get_diff() {
    git diff "$BASE_BRANCH"...HEAD
}

# Get files changed summary
get_files_summary() {
    git diff "$BASE_BRANCH"...HEAD --stat | tail -1
}

# Shared review prompt
REVIEW_PROMPT='You are a senior code reviewer. Review the following git diff and provide:

1. **Critical Issues** (Must fix before merge):
   - Security vulnerabilities
   - Logic errors or bugs
   - Breaking changes

2. **Warnings** (Should address):
   - Performance concerns
   - Code quality issues
   - Missing error handling

3. **Suggestions** (Nice to have):
   - Style improvements
   - Documentation gaps
   - Refactoring opportunities

4. **Risk Assessment**:
   - Level: [Low | Medium | High]
   - Reason: [Brief explanation]

5. **Verdict**:
   - READY - Good to merge
   - NEEDS_WORK - Fix critical issues first
   - NEEDS_DISCUSSION - Architectural concerns

Be specific: cite file paths and line numbers. Be concise: focus on real issues, not nitpicks.

GIT DIFF:
'

# Run Claude review
run_claude_review() {
    log_info "Starting Claude review..."
    local diff_content
    diff_content=$(get_diff)

    if command -v claude &>/dev/null; then
        if run_with_timeout "$TIMEOUT_SECONDS" claude -p "${REVIEW_PROMPT}${diff_content}" \
            --output-format json \
            --allowedTools "Read,Grep,Glob,Bash(git:*)" \
            > "$OUTPUT_DIR/claude.json" 2>&1; then
            log_success "Claude review complete"
        else
            log_warn "Claude review failed or timed out"
            echo '{"error": "Review failed or timed out"}' > "$OUTPUT_DIR/claude.json"
        fi
    else
        echo '{"error": "claude CLI not installed"}' > "$OUTPUT_DIR/claude.json"
        log_warn "Claude CLI not available"
    fi
}

# Run Gemini review
run_gemini_review() {
    log_info "Starting Gemini review..."
    local diff_content
    diff_content=$(get_diff)

    if command -v gemini &>/dev/null; then
        if run_with_timeout "$TIMEOUT_SECONDS" gemini "${REVIEW_PROMPT}${diff_content}" \
            --output-format json \
            > "$OUTPUT_DIR/gemini.json" 2>&1; then
            log_success "Gemini review complete"
        else
            log_warn "Gemini review failed or timed out"
            echo '{"error": "Review failed or timed out"}' > "$OUTPUT_DIR/gemini.json"
        fi
    else
        echo '{"error": "gemini CLI not installed"}' > "$OUTPUT_DIR/gemini.json"
        log_warn "Gemini CLI not available"
    fi
}

# Run Codex review
run_codex_review() {
    log_info "Starting Codex review..."

    if command -v codex &>/dev/null; then
        # Try the dedicated review command first, fall back to exec
        if run_with_timeout "$TIMEOUT_SECONDS" codex review \
            --base "$BASE_BRANCH" \
            --json \
            > "$OUTPUT_DIR/codex.json" 2>&1; then
            log_success "Codex review complete"
        else
            # Fallback to exec if review command doesn't exist
            local diff_content
            diff_content=$(get_diff)
            if run_with_timeout "$TIMEOUT_SECONDS" codex exec "${REVIEW_PROMPT}${diff_content}" \
                --json \
                --full-auto \
                > "$OUTPUT_DIR/codex.json" 2>&1; then
                log_success "Codex review complete (via exec)"
            else
                log_warn "Codex review failed or timed out"
                echo '{"error": "Review failed or timed out"}' > "$OUTPUT_DIR/codex.json"
            fi
        fi
    else
        echo '{"error": "codex CLI not installed"}' > "$OUTPUT_DIR/codex.json"
        log_warn "Codex CLI not available"
    fi
}

# Extract review content from JSON - handles different CLI output formats
extract_review() {
    local file=$1
    local reviewer=$2

    if [ ! -f "$file" ]; then
        echo "_${reviewer} review output not found_"
        return
    fi

    # Check for error marker
    if jq -e '.error' "$file" &>/dev/null 2>&1; then
        local error_msg
        error_msg=$(jq -r '.error // "Unknown error"' "$file" 2>/dev/null)
        echo "_${reviewer} review unavailable: ${error_msg}_"
        return
    fi

    local content=""

    case "$reviewer" in
        "Claude")
            # Claude: single JSON with .result field
            content=$(jq -r '.result // empty' "$file" 2>/dev/null)
            ;;
        "Gemini")
            # Gemini: JSON with .response field, but has stderr noise at the start
            # Extract JSON block from first { to last }
            content=$(sed -n '/^{$/,/^}$/p' "$file" | jq -r '.response // empty' 2>/dev/null)
            ;;
        "Codex")
            # Codex: NDJSON format - get the LAST agent_message (the final response)
            content=$(grep 'agent_message' "$file" | tail -1 | jq -r '.item.text // empty' 2>/dev/null)
            ;;
        *)
            # Generic fallback
            content=$(jq -r '.result // .response // .content // .message // empty' "$file" 2>/dev/null)
            ;;
    esac

    if [ -n "$content" ] && [ "$content" != "null" ]; then
        echo "$content"
    else
        echo "_${reviewer} review: Could not parse output_"
    fi
}

# Extract verdict from review content
extract_verdict() {
    local content="$1"
    local reviewer="$2"

    if echo "$content" | grep -qi "READY.*merge\|Good to merge\|READY -"; then
        echo "READY"
    elif echo "$content" | grep -qi "NEEDS_WORK\|NEEDS WORK\|Fix critical"; then
        echo "NEEDS_WORK"
    elif echo "$content" | grep -qi "NEEDS_DISCUSSION"; then
        echo "NEEDS_DISCUSSION"
    elif echo "$content" | grep -qi "Could not parse\|unavailable\|failed"; then
        echo "UNAVAILABLE"
    else
        echo "UNKNOWN"
    fi
}

# Extract risk level from review content
extract_risk() {
    local content="$1"

    if echo "$content" | grep -qiE "Level.*High|Risk.*High|\*\*High\*\*"; then
        echo "High"
    elif echo "$content" | grep -qiE "Level.*Medium|Risk.*Medium|\*\*Medium\*\*|Low-Medium"; then
        echo "Medium"
    elif echo "$content" | grep -qiE "Level.*Low|Risk.*Low|\*\*Low\*\*"; then
        echo "Low"
    else
        echo "-"
    fi
}

# Generate executive summary from all reviews
generate_summary() {
    local claude_review="$1"
    local gemini_review="$2"
    local codex_review="$3"

    local claude_verdict=$(extract_verdict "$claude_review" "Claude")
    local gemini_verdict=$(extract_verdict "$gemini_review" "Gemini")
    local codex_verdict=$(extract_verdict "$codex_review" "Codex")

    local claude_risk=$(extract_risk "$claude_review")
    local gemini_risk=$(extract_risk "$gemini_review")
    local codex_risk=$(extract_risk "$codex_review")

    # Count verdicts
    local ready_count=0
    local needs_work_count=0
    [[ "$claude_verdict" == "READY" ]] && ((ready_count++))
    [[ "$gemini_verdict" == "READY" ]] && ((ready_count++))
    [[ "$codex_verdict" == "READY" ]] && ((ready_count++))
    [[ "$claude_verdict" == "NEEDS_WORK" ]] && ((needs_work_count++))
    [[ "$gemini_verdict" == "NEEDS_WORK" ]] && ((needs_work_count++))
    [[ "$codex_verdict" == "NEEDS_WORK" ]] && ((needs_work_count++))

    # Determine overall recommendation
    local overall_verdict
    if [[ $needs_work_count -ge 2 ]]; then
        overall_verdict="NEEDS_WORK"
    elif [[ $ready_count -ge 2 ]]; then
        overall_verdict="READY"
    else
        overall_verdict="MIXED"
    fi

    cat <<SUMMARY
## Executive Summary

| Reviewer | Verdict | Risk |
|----------|---------|------|
| Claude | $claude_verdict | $claude_risk |
| Gemini | $gemini_verdict | $gemini_risk |
| Codex | $codex_verdict | $codex_risk |

**Overall**: $overall_verdict ($ready_count/3 approve, $needs_work_count/3 need work)

### Common Concerns
SUMMARY

    # Check for common issues mentioned by multiple reviewers
    local common_issues=""
    local mention_count=0

    # Check pagination (count how many reviewers mention it)
    mention_count=0
    echo "$claude_review" | grep -qiE "pagination|loadMore|infinite.scroll|onAppear" && ((mention_count++))
    echo "$gemini_review" | grep -qiE "pagination|loadMore|infinite.scroll|onAppear" && ((mention_count++))
    echo "$codex_review" | grep -qiE "pagination|loadMore|infinite.scroll|onAppear" && ((mention_count++))
    [[ $mention_count -ge 2 ]] && common_issues+="- **Pagination**: Multiple reviewers flagged pagination/infinite scroll changes\n"

    # Check date formatting
    mention_count=0
    echo "$claude_review" | grep -qiE "ISO8601|DateFormatter|date.pars|fractionalSeconds" && ((mention_count++))
    echo "$gemini_review" | grep -qiE "ISO8601|DateFormatter|date.pars|fractionalSeconds" && ((mention_count++))
    echo "$codex_review" | grep -qiE "ISO8601|DateFormatter|date.pars|fractionalSeconds" && ((mention_count++))
    [[ $mention_count -ge 2 ]] && common_issues+="- **Date Parsing**: Multiple reviewers flagged ISO8601/date formatting concerns\n"

    # Check gitignore
    mention_count=0
    echo "$claude_review" | grep -qiE "gitignore|cy-docs" && ((mention_count++))
    echo "$gemini_review" | grep -qiE "gitignore|cy-docs" && ((mention_count++))
    echo "$codex_review" | grep -qiE "gitignore|cy-docs" && ((mention_count++))
    [[ $mention_count -ge 2 ]] && common_issues+="- **Gitignore**: Multiple reviewers noted .gitignore changes\n"

    # Check error handling
    mention_count=0
    echo "$claude_review" | grep -qiE "error.handling|success.flag|missing.+handling" && ((mention_count++))
    echo "$gemini_review" | grep -qiE "error.handling|success.flag|missing.+handling" && ((mention_count++))
    echo "$codex_review" | grep -qiE "error.handling|success.flag|missing.+handling" && ((mention_count++))
    [[ $mention_count -ge 2 ]] && common_issues+="- **Error Handling**: Multiple reviewers flagged missing error handling\n"

    if [[ -n "$common_issues" ]]; then
        echo -e "$common_issues"
    else
        echo "_No consensus issues identified - reviewers flagged different concerns._"
    fi

    echo ""
}

# Aggregate results into markdown report
aggregate_results() {
    log_info "Aggregating results..."

    local current_branch
    current_branch=$(git branch --show-current)
    local commit_count
    commit_count=$(git rev-list --count "$BASE_BRANCH"..HEAD)
    local files_summary
    files_summary=$(get_files_summary)
    local review_date
    review_date=$(date +"%Y-%m-%d %H:%M:%S")

    # Create reviews directory if it doesn't exist
    mkdir -p "$REVIEWS_DIR"

    local output_file="$REVIEWS_DIR/pre-pr-review-${TIMESTAMP}.md"

    # Extract reviews first for summary generation
    local claude_review=$(extract_review "$OUTPUT_DIR/claude.json" "Claude")
    local gemini_review=$(extract_review "$OUTPUT_DIR/gemini.json" "Gemini")
    local codex_review=$(extract_review "$OUTPUT_DIR/codex.json" "Codex")

    cat > "$output_file" <<EOF
# Pre-PR Review: ${current_branch}

**Date**: ${review_date}
**Branch**: ${current_branch} -> ${BASE_BRANCH}
**Commits**: ${commit_count}
**Changes**: ${files_summary}

---

$(generate_summary "$claude_review" "$gemini_review" "$codex_review")

---

## Claude's Review

${claude_review}

---

## Gemini's Review

${gemini_review}

---

## Codex's Review

${codex_review}

---

## Review Metadata

- **Generated by**: pre-pr-review.sh
- **Timestamp**: ${TIMESTAMP}
- **Base branch**: ${BASE_BRANCH}
- **Project**: ${PROJECT_ROOT}
EOF

    echo "$output_file"
}

# Main execution
main() {
    log_header "=========================================="
    log_header "  Pre-PR Multi-AI Review"
    log_header "=========================================="
    echo

    check_prerequisites
    echo

    log_info "Starting parallel reviews (timeout: ${TIMEOUT_SECONDS}s each)..."
    echo

    # Run all reviews in parallel
    run_claude_review &
    local claude_pid=$!

    run_gemini_review &
    local gemini_pid=$!

    run_codex_review &
    local codex_pid=$!

    # Wait for all to complete
    wait $claude_pid 2>/dev/null || true
    wait $gemini_pid 2>/dev/null || true
    wait $codex_pid 2>/dev/null || true

    echo
    log_info "All reviews complete. Generating report..."
    echo

    # Generate and output the report
    local output_file
    output_file=$(aggregate_results)

    log_success "Review saved to: $output_file"
    echo

    # Output the file path for the command to use
    echo "REVIEW_FILE=$output_file"
}

# Run main function
main "$@"
