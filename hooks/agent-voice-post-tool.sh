#!/bin/bash
# PostToolUse hook for Task tool - triggers voice notifications after agents complete

INPUT=$(cat)

# Extract agent name and result from Task tool output
RESULT=$(echo "$INPUT" | python3 -c "
import sys, json, re

try:
    data = json.load(sys.stdin)

    # Get the tool parameters to find agent type
    params = data.get('parameters', {})
    agent_name = params.get('subagent_type', 'unknown')

    # Get the result/output
    result_data = data.get('result', {})
    output = result_data.get('content', [{}])[0].get('text', '') if isinstance(result_data.get('content'), list) else str(result_data)

    # Map agent names to voice IDs
    voice_map = {
        'cto-advisor': 'lpcesEa7Zyjkgsrd7I32',
        'alex': 'O4lTuRmkE5LyjL2YhMIg',
    }
    voice_id = voice_map.get(agent_name, 'O4lTuRmkE5LyjL2YhMIg')

    # Try to extract completion message
    patterns = [
        r'CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)',
        r'🗣️[^\n]*?CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)',
        r'COMPLETED[:\s]+(.+?)(?:\n|$)',
    ]

    message = None
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE | re.MULTILINE)
        if match:
            message = match.group(1).strip()
            message = re.sub(r'\[AGENT:[^\]]+\]', '', message)
            message = re.sub(r'[*_]+', '', message)
            message = message.replace('\n', ' ').replace('\r', ' ')
            message = re.sub(r'\s+', ' ', message)
            break

    if not message:
        # Fallback: use first sentence or agent name
        first_line = output.split('\n')[0][:100] if output else f'{agent_name} completed'
        message = first_line.strip()

    print(json.dumps({'agent': agent_name, 'voice_id': voice_id, 'message': message[:100]}))

except Exception as e:
    print(json.dumps({'agent': 'unknown', 'voice_id': 'O4lTuRmkE5LyjL2YhMIg', 'message': 'Task completed'}))
" 2>/dev/null)

# Parse the result
AGENT=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('agent', 'unknown'))" 2>/dev/null)
VOICE_ID=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('voice_id', 'O4lTuRmkE5LyjL2YhMIg'))" 2>/dev/null)
MESSAGE=$(echo "$RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Task completed'))" 2>/dev/null)

# Send to voice server
if [ -n "$MESSAGE" ] && [ "$AGENT" != "unknown" ]; then
    curl -s -X POST http://localhost:8888/notify \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"$MESSAGE\",\"voice_id\":\"$VOICE_ID\",\"voice_enabled\":true}" \
        > /dev/null 2>&1 &
fi
