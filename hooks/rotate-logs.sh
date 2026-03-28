#!/bin/bash
# Log rotation for PAI hooks
# Run periodically (e.g., via SessionStart or cron) to keep disk usage bounded.
#
# Policy:
#   - agent-output-context: keep last 30 days
#   - logs/*.jsonl: truncate to last 10,000 lines
#   - logs/hooks/*.log: truncate to last 5,000 lines

PAI_DIR="$HOME/.claude"

# --- Agent output transcripts: delete dirs older than 30 days ---
if [ -d "$PAI_DIR/agent-output-context" ]; then
  find "$PAI_DIR/agent-output-context" -maxdepth 1 -type d -name "20*" -mtime +30 -exec rm -r {} + 2>/dev/null
fi

# --- JSONL logs: keep last 10,000 lines ---
for f in "$PAI_DIR"/logs/*.jsonl; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 10000 ]; then
    tail -10000 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  fi
done

# --- Hook logs: keep last 5,000 lines ---
for f in "$PAI_DIR"/logs/hooks/*.log; do
  [ -f "$f" ] || continue
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 5000 ]; then
    tail -5000 "$f" > "$f.tmp" && mv "$f.tmp" "$f"
  fi
done

# --- Archived files: clean up ---
find "$PAI_DIR/logs" -name "*.archived" -mtime +7 -delete 2>/dev/null

echo "Log rotation complete"
