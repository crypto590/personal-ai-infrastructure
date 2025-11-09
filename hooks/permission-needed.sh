#!/bin/bash
# Notify when permission is needed (Notification hook)

# Read JSON input from stdin
INPUT=$(cat)

# Extract the notification message
MESSAGE=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    msg = data.get('message', 'Permission needed')
    # Truncate for voice
    print(msg[:80])
except:
    print('Permission needed')
" 2>/dev/null)

# Send notification with Alex voice
if [ -n "$MESSAGE" ]; then
    curl -s -X POST http://localhost:8888/notify \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"$MESSAGE\",\"voice_id\":\"O4lTuRmkE5LyjL2YhMIg\",\"voice_enabled\":true}" \
        > /dev/null 2>&1 &
fi
