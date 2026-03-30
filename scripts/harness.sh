#!/bin/bash
#
# harness.sh - 3-Agent Feature Harness (Pattern C)
#
# Planner (Opus)  → Feature registry + high-level plan
# Generator (Opus) → Implements one criterion at a time
# Evaluator (Opus) → Tests criteria, flips passes, records evidence
#
# Based on: https://www.anthropic.com/engineering/harness-design-long-running-apps
# Evolved from: ralph-claude.sh (Pattern B → Pattern C)
#
# Usage:
#   ./scripts/harness.sh "Add email verification to signup flow"
#   ./scripts/harness.sh --resume                  # Resume from checkpoint
#   ./scripts/harness.sh --registry path/to/reg.json  # Use existing registry
#   MAX_ITERATIONS=10 ./scripts/harness.sh "..."
#
# Phases:
#   1. PLAN  — Opus reads user story → writes .feature-registry/<name>.json
#   2. BUILD — Opus reads registry → implements next failing criterion → commits
#   3. EVAL  — Opus reads registry + diff → tests criteria → flips passes
#   If evaluator finds failures → loop back to BUILD with feedback
#

set -euo pipefail

# ============ LOAD ENV ============
if [ -f "$PWD/.env" ]; then
    set -a; source "$PWD/.env"; set +a
fi

# Use Claude subscription auth
unset ANTHROPIC_API_KEY

# ============ CONFIGURATION ============
PROJECT_DIR="$(pwd)"
REGISTRY_DIR="$PROJECT_DIR/docs/feature-registry"
LOG_DIR="$PROJECT_DIR/logs/harness"
FEEDBACK_FILE="$LOG_DIR/.feedback"
CHECKPOINT_FILE="$LOG_DIR/.checkpoint"
HEARTBEAT_LOG="$LOG_DIR/heartbeat.log"

# Models — all Opus by default per article's Stage 3 finding
PLANNER_MODEL="${PLANNER_MODEL:-opus}"
GENERATOR_MODEL="${GENERATOR_MODEL:-opus}"
EVALUATOR_MODEL="${EVALUATOR_MODEL:-opus}"

# MCP config — pass to evaluator for live testing (chrome-devtools, etc.)
# Override via env or --mcp-config flag
MCP_CONFIG="${MCP_CONFIG:-}"

# Limits
MAX_ITERATIONS="${MAX_ITERATIONS:-15}"
MAX_EVAL_RETRIES=3          # Max times evaluator can send generator back
PLAN_TIMEOUT="${PLAN_TIMEOUT:-300}"       # 5 min
GENERATE_TIMEOUT="${GENERATE_TIMEOUT:-600}" # 10 min
EVAL_TIMEOUT="${EVAL_TIMEOUT:-300}"       # 5 min

# ============ SETUP ============
mkdir -p "$REGISTRY_DIR" "$LOG_DIR"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }
log_info()    { echo -e "${BLUE}[$(timestamp)]${NC} $1"; }
log_success() { echo -e "${GREEN}[$(timestamp)]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[$(timestamp)]${NC} $1"; }
log_error()   { echo -e "${RED}[$(timestamp)]${NC} $1"; }
log_phase()   { echo -e "${CYAN}[$(timestamp)]${NC} $1"; }
log_debug()   { echo "[$(timestamp)] $1" >> "$HEARTBEAT_LOG"; }

# ============ CLEANUP ============
HEARTBEAT_PID=""
cleanup() {
    [ -n "$HEARTBEAT_PID" ] && kill "$HEARTBEAT_PID" 2>/dev/null || true
    log_info "Cleanup complete"
}
trap cleanup EXIT
trap 'log_warn "Interrupted"; exit 130' INT TERM

# ============ TIMEOUT HELPER ============
run_timeout() {
    local secs=$1; shift
    if command -v gtimeout &>/dev/null; then
        gtimeout "$secs" "$@"
    elif command -v timeout &>/dev/null; then
        timeout "$secs" "$@"
    else
        # Manual fallback
        "$@" &
        local pid=$!
        ( sleep "$secs"; kill -TERM "$pid" 2>/dev/null ) &
        local watcher=$!
        wait "$pid" 2>/dev/null
        local code=$?
        kill "$watcher" 2>/dev/null || true
        return $code
    fi
}

# ============ CLAUDE RUNNER ============
# Runs claude -p with timeout, writes output to file
# Args: $1=prompt_file $2=log_file $3=model $4=timeout $5=label $6=allowed_tools $7=mcp_config
run_claude() {
    local prompt_file="$1" log_file="$2" model="$3" timeout_secs="$4" label="$5"
    local allowed_tools="${6:-}" mcp_config="${7:-}"

    log_debug "=== $label ==="
    log_debug "Model: $model | Timeout: ${timeout_secs}s | Prompt: $(wc -c < "$prompt_file") bytes"
    [ -n "$allowed_tools" ] && log_debug "Allowed tools: $allowed_tools"
    [ -n "$mcp_config" ] && log_debug "MCP config: $mcp_config"

    > "$log_file"

    # Build command args array
    local cmd_args=(claude -p --model "$model" --dangerously-skip-permissions)

    if [ -n "$allowed_tools" ]; then
        cmd_args+=(--allowedTools "$allowed_tools")
    fi

    if [ -n "$mcp_config" ]; then
        cmd_args+=(--mcp-config "$mcp_config")
    fi

    local exit_code=0
    run_timeout "$timeout_secs" "${cmd_args[@]}" \
        < "$prompt_file" \
        > "$log_file" 2>&1 || exit_code=$?

    local output_size=$(wc -c < "$log_file" 2>/dev/null || echo 0)
    log_debug "$label finished: exit=$exit_code size=${output_size}b"

    if [ $exit_code -eq 124 ]; then
        log_error "$label timed out after ${timeout_secs}s"
        return 1
    elif [ $exit_code -ne 0 ]; then
        log_error "$label failed (exit $exit_code)"
        return 1
    fi
    return 0
}

# ============ REGISTRY HELPERS ============
registry_path() {
    echo "$REGISTRY_DIR/$FEATURE_SLUG.json"
}

count_passing() {
    jq '[.criteria[] | select(.passes == true)] | length' "$(registry_path)"
}

count_total() {
    jq '.criteria | length' "$(registry_path)"
}

all_passing() {
    jq -e '[.criteria[] | .passes] | all' "$(registry_path)" >/dev/null 2>&1
}

next_failing_id() {
    jq -r '[.criteria[] | select(.passes == false)][0].id // empty' "$(registry_path)"
}

next_failing_desc() {
    jq -r '[.criteria[] | select(.passes == false)][0].description // empty' "$(registry_path)"
}

update_summary() {
    local reg="$(registry_path)"
    local total=$(jq '.criteria | length' "$reg")
    local passing=$(jq '[.criteria[] | select(.passes == true)] | length' "$reg")
    local failing=$((total - passing))
    local tmp=$(mktemp)
    jq --argjson t "$total" --argjson p "$passing" --argjson f "$failing" \
        '.summary = {total: $t, passing: $p, failing: $f}' "$reg" > "$tmp"
    mv "$tmp" "$reg"
}

# ============ CHECKPOINT ============
save_checkpoint() {
    local phase="$1" iteration="$2" eval_retries="$3"
    echo "$phase|$iteration|$eval_retries|$FEATURE_SLUG" > "$CHECKPOINT_FILE"
    log_debug "Checkpoint: phase=$phase iter=$iteration retries=$eval_retries"
}

load_checkpoint() {
    [ -f "$CHECKPOINT_FILE" ] && cat "$CHECKPOINT_FILE" || echo ""
}

# ============ VALIDATION ============
validate_setup() {
    log_info "Validating setup..."

    [ -d ".git" ] || { log_error "Not a git repo"; exit 1; }
    command -v claude &>/dev/null || { log_error "Claude CLI not found"; exit 1; }
    command -v jq &>/dev/null || { log_error "jq not found"; exit 1; }

    log_success "Setup validated"
}

# ============ SLUGIFY ============
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//' | cut -c1-50
}

# ============ PHASE 1: PLAN ============
run_planner() {
    local story="$1"

    echo ""
    log_phase "╭──────────────────────────────────────────╮"
    log_phase "│  PHASE 1: PLANNER (Opus)                 │"
    log_phase "╰──────────────────────────────────────────╯"
    log_info "Story: $story"

    local prompt_file="$LOG_DIR/.planner-prompt"
    local log_file="$LOG_DIR/planner.log"
    local reg="$(registry_path)"

    cat > "$prompt_file" <<PROMPT_EOF
You are the PLANNER agent in a 3-agent harness (Planner → Generator → Evaluator).

Your job: Read the user story and produce a feature registry JSON file with concrete, testable acceptance criteria.

## User Story
$story

## Project Context
Read the project's CLAUDE.md for conventions, architecture, and tech stack.
Explore the codebase to understand existing patterns.

## Output Requirements

You MUST write a JSON file to this exact path:
$reg

Use this exact schema:
{
  "feature": "$FEATURE_SLUG",
  "created": "$(date '+%Y-%m-%d')",
  "story": "<the user story>",
  "plan": "<2-3 sentence high-level approach — no implementation details>",
  "criteria": [
    {
      "id": "C1",
      "description": "<specific testable behavior>",
      "category": "functional|edge-case|security|performance|accessibility",
      "passes": false,
      "evidence": null
    }
  ],
  "summary": {
    "total": <N>,
    "passing": 0,
    "failing": <N>
  }
}

## Rules
- 4-8 criteria per feature (not more)
- Each criterion must be independently testable
- Include at least 1 edge-case and 1 security criterion where applicable
- Keep the plan HIGH-LEVEL — the generator decides implementation details
- Categories: functional, edge-case, security, performance, accessibility
- The description should state WHAT to verify, not HOW to build it

Write the file and confirm with: PLAN_COMPLETE
PROMPT_EOF

    # Planner: read-only exploration + write registry
    local planner_tools="Read,Grep,Glob,Bash(git:*),Write"

    if ! run_claude "$prompt_file" "$log_file" "$PLANNER_MODEL" "$PLAN_TIMEOUT" "Planner" "$planner_tools"; then
        log_error "Planner failed. Check $log_file"
        exit 1
    fi

    # Verify registry was created
    if [ ! -f "$reg" ]; then
        log_error "Planner did not create registry at $reg"
        log_error "Check $log_file for output"
        exit 1
    fi

    # Validate JSON
    if ! jq empty "$reg" 2>/dev/null; then
        log_error "Registry is not valid JSON"
        exit 1
    fi

    local total=$(count_total)
    log_success "Plan complete: $total criteria defined"
    log_info "Registry: $reg"

    # Show criteria
    echo ""
    jq -r '.criteria[] | "  \(.id): [\(.category)] \(.description)"' "$reg"
    echo ""
}

# ============ PHASE 2: GENERATE ============
run_generator() {
    local criterion_id="$1"
    local criterion_desc="$2"
    local iteration="$3"

    echo ""
    log_phase "╭──────────────────────────────────────────╮"
    log_phase "│  PHASE 2: GENERATOR (Opus)               │"
    log_phase "╰──────────────────────────────────────────╯"
    log_info "Criterion: $criterion_id — $criterion_desc"

    local prompt_file="$LOG_DIR/.generator-prompt"
    local log_file="$LOG_DIR/generator-${criterion_id}-iter${iteration}.log"
    local reg="$(registry_path)"

    # Include feedback from previous evaluator run if it exists
    local feedback_section=""
    if [ -f "$FEEDBACK_FILE" ] && [ -s "$FEEDBACK_FILE" ]; then
        feedback_section="## Evaluator Feedback from Previous Attempt
$(cat "$FEEDBACK_FILE")

Fix the issues above before proceeding."
        > "$FEEDBACK_FILE"  # Clear after reading
    fi

    cat > "$prompt_file" <<PROMPT_EOF
You are the GENERATOR agent in a 3-agent harness (Planner → Generator → Evaluator).

Your job: Implement ONE criterion from the feature registry.

## Feature Registry
$(cat "$reg")

## Your Target
Implement criterion: $criterion_id
Description: $criterion_desc

$feedback_section

## Rules
1. Read CLAUDE.md for project conventions
2. Read existing code to understand patterns BEFORE writing
3. Implement ONLY what is needed for this criterion
4. Follow existing patterns — do not invent new abstractions
5. Write tests for the criterion if the project has tests
6. Make ONE atomic commit when done with message: "feat: $criterion_id — $criterion_desc"
7. Do NOT modify the feature registry JSON — the evaluator does that
8. Do NOT work on other criteria — focus on $criterion_id only

When implementation is committed, output: GENERATE_COMPLETE
PROMPT_EOF

    # Generator: full code editing + bash for builds/tests
    local generator_tools="Read,Write,Edit,Bash,Grep,Glob"

    if ! run_claude "$prompt_file" "$log_file" "$GENERATOR_MODEL" "$GENERATE_TIMEOUT" "Generator ($criterion_id)" "$generator_tools"; then
        log_error "Generator failed for $criterion_id. Check $log_file"
        return 1
    fi

    log_success "Generator complete for $criterion_id"
    return 0
}

# ============ PHASE 3: EVALUATE ============
# Returns: 0 = all criteria verified, 1 = failures remain, 2 = error
run_evaluator() {
    local iteration="$1"

    echo ""
    log_phase "╭──────────────────────────────────────────╮"
    log_phase "│  PHASE 3: EVALUATOR (Opus)               │"
    log_phase "╰──────────────────────────────────────────╯"

    local prompt_file="$LOG_DIR/.evaluator-prompt"
    local log_file="$LOG_DIR/evaluator-iter${iteration}.log"
    local reg="$(registry_path)"

    # Get diff of recent work
    local diff_content
    diff_content=$(git diff HEAD~1 HEAD 2>/dev/null || echo "No diff available")

    # Build MCP instructions if chrome-devtools is available
    local mcp_section=""
    if [ -n "$MCP_CONFIG" ]; then
        mcp_section="
## Live Testing (chrome-devtools MCP)
You have access to chrome-devtools MCP tools for live UI testing. USE THEM.
- Navigate to pages with mcp__chrome-devtools__navigate_page
- Take screenshots with mcp__chrome-devtools__take_screenshot
- Click elements with mcp__chrome-devtools__click
- Fill forms with mcp__chrome-devtools__fill
- Check console errors with mcp__chrome-devtools__list_console_messages
- Check network requests with mcp__chrome-devtools__list_network_requests

For UI/functional criteria: interact with the running app, don't just read code.
Static code reading is NOT evidence for UI behavior — screenshot or interaction is."
    fi

    cat > "$prompt_file" <<PROMPT_EOF
You are the EVALUATOR agent in a 3-agent harness (Planner → Generator → Evaluator).

Your job: Test each criterion in the feature registry against the actual code and update the registry.

## Feature Registry
$(cat "$reg")

## Recent Changes (git diff)
\`\`\`
$diff_content
\`\`\`
$mcp_section

## Your Process
For each criterion where passes is false:
1. Read the relevant source code
2. Run tests if they exist (check CLAUDE.md for test commands)
3. Verify the criterion is actually met — be skeptical, not generous
4. If it passes: update the registry JSON — set passes to true, add evidence
5. If it fails: leave passes as false, add evidence explaining what's wrong

## Rules
1. You MUST write your updates to: $reg
2. Only modify the "passes", "evidence", and "summary" fields — never change criteria descriptions or IDs
3. Evidence must be SPECIFIC: test name that passed, file:line that proves it, command output
4. Be skeptical — "the code looks like it handles this" is NOT evidence. Run it or trace it.
5. Update the summary counts after all evaluations
6. If a criterion genuinely cannot be tested statically, note that in evidence

## Output Format
After updating the registry, output a summary:

EVAL_RESULT:{"passing": N, "failing": N, "total": N, "failures": ["C2: reason", "C5: reason"]}

If ALL criteria pass, also output: ALL_CRITERIA_PASS
PROMPT_EOF

    # Evaluator: read + bash for running tests + write registry + MCP for live testing
    local evaluator_tools="Read,Bash,Grep,Glob,Write"
    # Append MCP tool patterns if MCP config is provided
    if [ -n "$MCP_CONFIG" ]; then
        evaluator_tools="$evaluator_tools,mcp__chrome-devtools__*"
    fi

    if ! run_claude "$prompt_file" "$log_file" "$EVALUATOR_MODEL" "$EVAL_TIMEOUT" "Evaluator (iter $iteration)" "$evaluator_tools" "$MCP_CONFIG"; then
        log_error "Evaluator failed. Check $log_file"
        return 2
    fi

    # Re-read registry to check state
    update_summary
    local passing=$(count_passing)
    local total=$(count_total)

    log_info "Evaluator result: $passing/$total criteria passing"

    if all_passing; then
        log_success "All criteria pass!"
        return 0
    fi

    # Extract failure reasons for feedback to generator
    local eval_output
    eval_output=$(cat "$log_file")
    local failures
    failures=$(echo "$eval_output" | grep 'EVAL_RESULT:' | head -1 | sed 's/.*EVAL_RESULT://' | jq -r '.failures[]? // empty' 2>/dev/null || true)

    if [ -n "$failures" ]; then
        echo "$failures" > "$FEEDBACK_FILE"
        log_warn "Failures written to feedback file for generator"
    else
        # Fallback: extract from registry
        jq -r '.criteria[] | select(.passes == false) | "\(.id): \(.evidence // "no evidence")"' "$reg" > "$FEEDBACK_FILE"
    fi

    return 1
}

# ============ MAIN LOOP ============
run_harness() {
    local story="$1"
    local skip_plan="${2:-false}"

    local iteration=1
    local eval_retries=0

    # Check for resume
    local checkpoint
    checkpoint=$(load_checkpoint)
    if [ -n "$checkpoint" ]; then
        IFS='|' read -r saved_phase saved_iter saved_retries saved_slug <<< "$checkpoint"
        FEATURE_SLUG="$saved_slug"
        iteration=$saved_iter
        eval_retries=$saved_retries
        skip_plan=true
        log_info "Resuming: phase=$saved_phase iter=$iteration retries=$eval_retries slug=$FEATURE_SLUG"
    fi

    # Phase 1: Plan (unless resuming or using existing registry)
    if [ "$skip_plan" != "true" ]; then
        run_planner "$story"
        git add "$REGISTRY_DIR/" 2>/dev/null || true
        git commit -m "plan: feature registry for $FEATURE_SLUG" --allow-empty 2>/dev/null || true
        save_checkpoint "build" "$iteration" "$eval_retries"
    fi

    # Verify registry exists
    if [ ! -f "$(registry_path)" ]; then
        log_error "No registry at $(registry_path)"
        exit 1
    fi

    # Phase 2+3: Build-Evaluate loop
    while [ $iteration -le $MAX_ITERATIONS ]; do
        echo ""
        echo "╔════════════════════════════════════════════════════════════╗"
        printf "║  ITERATION %-3s of %-3s — %s                    ║\n" "$iteration" "$MAX_ITERATIONS" "$(date '+%H:%M:%S')"
        echo "║  Feature: $FEATURE_SLUG"
        printf "║  Progress: %s/%s criteria passing\n" "$(count_passing)" "$(count_total)"
        echo "╚════════════════════════════════════════════════════════════╝"

        # Check completion
        if all_passing; then
            echo ""
            log_success "ALL CRITERIA PASS — Feature complete!"
            echo ""
            jq -r '.criteria[] | "  \(.id): [\(.passes | if . then "PASS" else "FAIL" end)] \(.description)"' "$(registry_path)"
            echo ""

            # Final commit
            git add -A 2>/dev/null || true
            git commit -m "feat: $FEATURE_SLUG complete — all $(count_total) criteria pass" --allow-empty 2>/dev/null || true

            # Clean checkpoint
            rm -f "$CHECKPOINT_FILE" "$FEEDBACK_FILE"
            return 0
        fi

        # Get next failing criterion
        local cid
        cid=$(next_failing_id)
        local cdesc
        cdesc=$(next_failing_desc)

        if [ -z "$cid" ]; then
            log_error "No failing criteria found but all_passing returned false"
            exit 1
        fi

        # Phase 2: Generate
        save_checkpoint "generate" "$iteration" "$eval_retries"
        if ! run_generator "$cid" "$cdesc" "$iteration"; then
            log_error "Generator failed — stopping"
            exit 1
        fi

        # Commit generator work (generator should have committed, but ensure)
        git add -A 2>/dev/null || true
        git commit -m "wip: generator pass for $cid (iter $iteration)" --allow-empty 2>/dev/null || true

        # Phase 3: Evaluate
        save_checkpoint "evaluate" "$iteration" "$eval_retries"
        local eval_result=0
        run_evaluator "$iteration" || eval_result=$?

        # Commit evaluator updates to registry
        git add "$REGISTRY_DIR/" 2>/dev/null || true
        git commit -m "eval: registry update iter $iteration — $(count_passing)/$(count_total) passing" --allow-empty 2>/dev/null || true

        case $eval_result in
            0)
                # All pass — will be caught at top of next iteration
                ;;
            1)
                # Failures remain
                eval_retries=$((eval_retries + 1))
                if [ $eval_retries -ge $MAX_EVAL_RETRIES ]; then
                    log_warn "Evaluator sent generator back $MAX_EVAL_RETRIES times for same criterion"
                    log_warn "Moving to next criterion to avoid infinite loop"
                    eval_retries=0
                    # Mark current criterion with evidence of stuck state
                    local reg="$(registry_path)"
                    local tmp=$(mktemp)
                    jq --arg id "$cid" \
                       '.criteria |= map(if .id == $id then .evidence = "STUCK: exceeded max eval retries" else . end)' \
                       "$reg" > "$tmp"
                    mv "$tmp" "$reg"
                fi
                ;;
            2)
                # Evaluator error
                log_error "Evaluator error — stopping"
                exit 1
                ;;
        esac

        iteration=$((iteration + 1))
        save_checkpoint "build" "$iteration" "$eval_retries"

        log_info "Sleeping 3s..."
        sleep 3
    done

    log_warn "Max iterations ($MAX_ITERATIONS) reached"
    log_warn "Progress: $(count_passing)/$(count_total) criteria passing"
    log_warn "Run with --resume to continue"
    exit 1
}

# ============ PARSE ARGS ============
RESUME=false
EXISTING_REGISTRY=""
FEATURE_STORY=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --resume)
            RESUME=true
            shift
            ;;
        --registry)
            EXISTING_REGISTRY="$2"
            shift 2
            ;;
        --mcp-config)
            MCP_CONFIG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: harness.sh [options] \"feature description\""
            echo ""
            echo "Options:"
            echo "  --resume              Resume from checkpoint"
            echo "  --registry PATH       Use existing feature registry"
            echo "  --mcp-config PATH     MCP server config (JSON file or string) — gives evaluator live testing"
            echo "  --help                Show this help"
            echo ""
            echo "Environment:"
            echo "  MAX_ITERATIONS=15     Max build-eval cycles (default: 15)"
            echo "  PLANNER_MODEL=opus    Model for planning phase"
            echo "  GENERATOR_MODEL=opus  Model for generation phase"
            echo "  EVALUATOR_MODEL=opus  Model for evaluation phase"
            echo "  MCP_CONFIG=path       Same as --mcp-config"
            exit 0
            ;;
        *)
            FEATURE_STORY="$1"
            shift
            ;;
    esac
done

# ============ ENTRY POINT ============
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║   HARNESS — 3-Agent Feature Builder (Pattern C)              ║"
    echo "║                                                               ║"
    echo "║   Planner:   Claude $PLANNER_MODEL                                    ║"
    echo "║   Generator: Claude $GENERATOR_MODEL                                  ║"
    echo "║   Evaluator: Claude $EVALUATOR_MODEL                                  ║"
    echo "║                                                               ║"
    echo "║   Source: Anthropic Engineering — Harness Design              ║"
    if [ -n "$MCP_CONFIG" ]; then
    echo "║   MCP:    Enabled (evaluator gets live testing tools)         ║"
    fi
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    # Init logs
    echo "=== Harness started: $(timestamp) ===" > "$HEARTBEAT_LOG"

    validate_setup

    if [ "$RESUME" = true ]; then
        local checkpoint
        checkpoint=$(load_checkpoint)
        if [ -z "$checkpoint" ]; then
            log_error "No checkpoint found to resume"
            exit 1
        fi
        FEATURE_SLUG=$(echo "$checkpoint" | cut -d'|' -f4)
        log_info "Resuming feature: $FEATURE_SLUG"
        run_harness "" true
    elif [ -n "$EXISTING_REGISTRY" ]; then
        # Use existing registry
        if [ ! -f "$EXISTING_REGISTRY" ]; then
            log_error "Registry not found: $EXISTING_REGISTRY"
            exit 1
        fi
        FEATURE_SLUG=$(jq -r '.feature' "$EXISTING_REGISTRY")
        cp "$EXISTING_REGISTRY" "$(registry_path)"
        log_info "Using existing registry: $FEATURE_SLUG"
        run_harness "" true
    elif [ -n "$FEATURE_STORY" ]; then
        FEATURE_SLUG=$(slugify "$FEATURE_STORY")
        log_info "Feature: $FEATURE_STORY"
        log_info "Slug: $FEATURE_SLUG"
        run_harness "$FEATURE_STORY"
    else
        log_error "Provide a feature description or use --resume"
        echo "Usage: harness.sh \"feature description\""
        exit 1
    fi
}

main
