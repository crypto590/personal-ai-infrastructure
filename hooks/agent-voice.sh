#!/bin/bash
# Universal agent voice notification hook
# Automatically announces when any agent completes a task

# Read JSON input from stdin
INPUT=$(cat)

# Extract agent name and output from the subagent stop event
AGENT_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('agentName', 'unknown'))
except:
    print('unknown')
" 2>/dev/null)

# Map agent names to voice IDs (from voices.json and SKILL.md)
case "$AGENT_NAME" in
    "cto-advisor")
        VOICE_ID="lpcesEa7Zyjkgsrd7I32"
        ;;
    "alex"|"")
        VOICE_ID="O4lTuRmkE5LyjL2YhMIg"
        ;;
    *)
        # Default to Alex voice if agent not configured
        VOICE_ID="O4lTuRmkE5LyjL2YhMIg"
        ;;
esac

# Extract a brief description of what was done
# Look for common completion patterns in the output
MESSAGE=$(echo "$INPUT" | python3 -c "
import sys, json, re
try:
    data = json.load(sys.stdin)
    output = data.get('output', '')

    # Try to find completion message patterns
    patterns = [
        r'COMPLETED[:\s]+(.+?)(?:\n|$)',
        r'🎯[^\n]*?COMPLETED[:\s]+(.+?)(?:\n|$)',
        r'completed (.+?)(?:\n|\.|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
        if match:
            msg = match.group(1).strip()
            # Clean up the message
            msg = re.sub(r'\[AGENT:[^\]]+\]', '', msg)
            msg = re.sub(r'[*_]+', '', msg)
            msg = msg.replace('\n', ' ').replace('\r', ' ')  # Remove newlines
            msg = re.sub(r'\s+', ' ', msg)  # Collapse multiple spaces
            print(msg[:100])  # Limit to 100 chars
            sys.exit(0)

    # Fallback: use agent name
    agent = data.get('agentName', 'Agent')
    print(f'{agent} task completed')
except:
    print('Task completed')
" 2>/dev/null)

# Send to voice server
if [ -n "$MESSAGE" ]; then
    curl -s -X POST http://localhost:8888/notify \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"$MESSAGE\",\"voice_id\":\"$VOICE_ID\",\"voice_enabled\":true}" \
        > /dev/null 2>&1 &
fi
