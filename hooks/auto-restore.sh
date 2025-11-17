#!/bin/bash

# Auto-Restore Hook (SessionStart)
# Checks for saved autopilot state and prompts Claude to restore

STATE_FILE="$HOME/.claude/autopilot/current-task.json"

# Check if saved state exists
if [ -f "$STATE_FILE" ]; then
  # Get task description from state file
  TASK_DESC=$(grep -o '"task_description":"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)

  # Get timestamp
  TIMESTAMP=$(grep -o '"timestamp":"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)

  # Output message to Claude (will be added to session context)
  cat << EOF

🔄 AUTOPILOT STATE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A saved autopilot state was found from a previous session.

Task: ${TASK_DESC}
Saved: ${TIMESTAMP}

RECOMMENDATION:
Run /restore-state to continue where you left off.

Or ignore this message if you want to start fresh.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

  # Voice notification
  curl -s -X POST http://localhost:8888/notify \
    -H "Content-Type: application/json" \
    -d '{"message":"Saved autopilot state detected","voice_id":"O4lTuRmkE5LyjL2YhMIg","voice_enabled":true}' \
    > /dev/null 2>&1 &
fi

# Clear the context warning marker from previous session
rm -f "$HOME/.claude/autopilot/.context-warning-sent"

# Exit successfully
exit 0
