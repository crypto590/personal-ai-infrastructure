#!/bin/bash
# cc-obs-retention.sh — daily retention for the disler observability SQLite DB
#
# Deletes events older than RETENTION_DAYS from events.db. Uses WAL-mode-safe
# DELETE with a busy timeout so it cooperates with the live Bun server.
# Does NOT vacuum (vacuum can't run while connections are open in WAL mode);
# SQLite reuses freed pages on subsequent inserts.
#
# Wired via launchd at ~/Library/LaunchAgents/com.coreyoung.cc-obs-retention.plist
# Logs to ~/.claude/logs/cc-obs-retention.log

set -uo pipefail

DB="/Users/coreyyoung/Desktop/Projects/claude-code-hooks-multi-agent-observability/apps/server/events.db"
LOG="/Users/coreyyoung/.claude/logs/cc-obs-retention.log"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

if [ ! -f "$DB" ]; then
  echo "$(ts) ERROR db missing: $DB" >> "$LOG"
  exit 1
fi

# Cutoff in epoch milliseconds (matches the timestamp column format)
CUTOFF_MS=$(( ( $(date -u +%s) - RETENTION_DAYS * 86400 ) * 1000 ))

before=$(sqlite3 -cmd ".timeout 5000" "$DB" "SELECT COUNT(*) FROM events;" 2>/dev/null || echo "0")
sqlite3 -cmd ".timeout 5000" "$DB" "DELETE FROM events WHERE timestamp < ${CUTOFF_MS};" 2>/dev/null
after=$(sqlite3 -cmd ".timeout 5000" "$DB" "SELECT COUNT(*) FROM events;" 2>/dev/null || echo "0")
deleted=$(( before - after ))
size=$(du -h "$DB" 2>/dev/null | awk '{print $1}')

echo "$(ts) before=${before} deleted=${deleted} after=${after} size=${size} retention=${RETENTION_DAYS}d" >> "$LOG"
