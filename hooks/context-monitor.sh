#!/bin/bash

# Context Monitor Hook (PostToolUse)
# Monitors context usage and triggers save-state when threshold reached

# Get context usage from environment variable
CONTEXT_USAGE="${CLAUDE_CONTEXT_USAGE:-0}"

# Define threshold (75% of 200k token limit = 150k tokens)
THRESHOLD=150000

# State file to track if we've already notified
STATE_FILE="$HOME/.claude/autopilot/.context-warning-sent"

# Check if context exceeds threshold
if [ "$CONTEXT_USAGE" -ge "$THRESHOLD" ]; then
  # Check if we've already warned in this session
  if [ ! -f "$STATE_FILE" ]; then
    # Create marker file
    touch "$STATE_FILE"

    # Output warning message (will be shown to Claude)
    cat << EOF

⚠️  AUTOPILOT CONTEXT WARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current context usage: ${CONTEXT_USAGE} tokens
Threshold reached: ${THRESHOLD} tokens (75% of limit)

ACTION REQUIRED:
1. Run /save-state to checkpoint current work
2. User will run /clear to reset context
3. Run /restore-state to resume task

This warning will only show once per session.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

    # Voice notification
    curl -s -X POST http://localhost:8888/notify \
      -H "Content-Type: application/json" \
      -d '{"message":"Context limit approaching - save state recommended","voice_id":"O4lTuRmkE5LyjL2YhMIg","voice_enabled":true}' \
      > /dev/null 2>&1 &
  fi
fi

# Exit successfully (don't block tool execution)
exit 0
