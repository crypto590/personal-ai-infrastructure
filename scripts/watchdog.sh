#!/bin/bash
#
# watchdog.sh — Monitor node/claude process counts
#
# Logs process counts every N seconds. Alerts when threshold exceeded.
# Run in a separate terminal alongside your work.
#
# Usage:
#   ~/.claude/scripts/watchdog.sh              # Default: 30s interval, 50 process threshold
#   ~/.claude/scripts/watchdog.sh 10 20        # 10s interval, alert at 20 processes
#   ~/.claude/scripts/watchdog.sh --kill 100   # Auto-kill orphans above 100
#

set -euo pipefail

INTERVAL="${1:-30}"
THRESHOLD="${2:-50}"
AUTO_KILL=false
KILL_THRESHOLD=100

# Parse --kill flag
for arg in "$@"; do
    case "$arg" in
        --kill) AUTO_KILL=true ;;
    esac
done
# If --kill was passed, next numeric arg is the kill threshold
if [ "$AUTO_KILL" = true ] && [[ "${3:-}" =~ ^[0-9]+$ ]]; then
    KILL_THRESHOLD="$3"
fi

LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/watchdog.log"
mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log() {
    local msg="[$(timestamp)] $1"
    echo -e "$msg"
    echo "$msg" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║  WATCHDOG — Process Monitor                   ║"
echo "║  Interval: ${INTERVAL}s | Alert: ${THRESHOLD} procs        ║"
echo "║  Log: ~/.claude/logs/watchdog.log             ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
log "Watchdog started (PID $$)"

PREV_NODE=0
PREV_CLAUDE=0

while true; do
    # Count processes
    NODE_COUNT=$(ps aux | grep -c '[n]ode' 2>/dev/null || echo 0)
    CLAUDE_COUNT=$(ps aux | grep -c '[c]laude' 2>/dev/null || echo 0)

    # Delta from last check
    NODE_DELTA=$((NODE_COUNT - PREV_NODE))
    CLAUDE_DELTA=$((CLAUDE_COUNT - PREV_CLAUDE))

    # Format delta
    NODE_DELTA_STR=""
    CLAUDE_DELTA_STR=""
    [ $NODE_DELTA -gt 0 ] && NODE_DELTA_STR=" (+$NODE_DELTA)"
    [ $NODE_DELTA -lt 0 ] && NODE_DELTA_STR=" ($NODE_DELTA)"
    [ $CLAUDE_DELTA -gt 0 ] && CLAUDE_DELTA_STR=" (+$CLAUDE_DELTA)"
    [ $CLAUDE_DELTA -lt 0 ] && CLAUDE_DELTA_STR=" ($CLAUDE_DELTA)"

    # Choose color based on count
    if [ "$NODE_COUNT" -ge "$THRESHOLD" ]; then
        COLOR="$RED"
        LEVEL="ALERT"
    elif [ "$NODE_COUNT" -ge $((THRESHOLD / 2)) ]; then
        COLOR="$YELLOW"
        LEVEL="WARN "
    else
        COLOR="$GREEN"
        LEVEL="OK   "
    fi

    log "${COLOR}[$LEVEL]${NC} node: ${NODE_COUNT}${NODE_DELTA_STR} | claude: ${CLAUDE_COUNT}${CLAUDE_DELTA_STR}"

    # Alert: log process tree when threshold exceeded
    if [ "$NODE_COUNT" -ge "$THRESHOLD" ]; then
        log "${RED}[ALERT] Threshold exceeded — logging process tree${NC}"
        {
            echo "=== PROCESS SNAPSHOT $(timestamp) ==="
            echo "--- Top node processes by memory ---"
            ps aux | grep '[n]ode' | sort -k6 -rn | head -20
            echo ""
            echo "--- Claude processes ---"
            ps aux | grep '[c]laude' | grep -v grep
            echo ""
            echo "--- Process tree (claude parent chains) ---"
            pgrep -f claude | while read pid; do
                echo "PID $pid: $(ps -o command= -p "$pid" 2>/dev/null || echo 'gone')"
                echo "  Parent: $(ps -o ppid=,command= -p "$pid" 2>/dev/null || echo 'gone')"
            done
            echo "=== END SNAPSHOT ==="
        } >> "$LOG_FILE" 2>/dev/null

        # Auto-kill if enabled and above kill threshold
        if [ "$AUTO_KILL" = true ] && [ "$NODE_COUNT" -ge "$KILL_THRESHOLD" ]; then
            log "${RED}[KILL] Auto-killing orphan node processes (count: $NODE_COUNT >= $KILL_THRESHOLD)${NC}"

            # Kill node processes NOT parented by current terminal sessions
            # Preserve: this watchdog, current shell, VS Code
            MY_PID=$$
            MY_PPID=$(ps -o ppid= -p $$ | tr -d ' ')

            ps aux | grep '[n]ode' | awk '{print $2}' | while read pid; do
                # Skip our own process tree
                [ "$pid" = "$MY_PID" ] && continue
                [ "$pid" = "$MY_PPID" ] && continue

                # Skip VS Code processes
                CMDLINE=$(ps -o command= -p "$pid" 2>/dev/null || echo "")
                echo "$CMDLINE" | grep -qi "vscode\|code-server" && continue

                kill -TERM "$pid" 2>/dev/null || true
            done

            log "[KILL] Sent SIGTERM to orphan node processes"
            sleep 5

            # Check if they died
            POST_KILL=$(ps aux | grep -c '[n]ode' 2>/dev/null || echo 0)
            log "[KILL] Post-kill count: $POST_KILL (was $NODE_COUNT)"
        fi
    fi

    # Spike detection: >20 new processes in one interval
    if [ $NODE_DELTA -gt 20 ]; then
        log "${RED}[SPIKE] +${NODE_DELTA} node processes in ${INTERVAL}s — possible runaway${NC}"
        # Log what just spawned
        {
            echo "=== SPIKE DETECTED $(timestamp) ==="
            echo "Delta: +$NODE_DELTA in ${INTERVAL}s"
            echo "--- Newest node processes ---"
            ps aux | grep '[n]ode' | sort -k9 -rn | head -10
            echo "=== END SPIKE ==="
        } >> "$LOG_FILE" 2>/dev/null
    fi

    PREV_NODE=$NODE_COUNT
    PREV_CLAUDE=$CLAUDE_COUNT

    sleep "$INTERVAL"
done
