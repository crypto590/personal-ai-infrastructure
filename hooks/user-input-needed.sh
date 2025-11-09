#!/bin/bash
# Notify when user input is required (AskUserQuestion tool)

# Read JSON input from stdin
INPUT=$(cat)

# Debug: save input to file
echo "$INPUT" > /tmp/pretool-input.json
date >> /tmp/pretool-debug.log

# Always send a simple notification
curl -s -X POST http://localhost:8888/notify \
    -H 'Content-Type: application/json' \
    -d '{"message":"Your input is needed","voice_id":"O4lTuRmkE5LyjL2YhMIg","voice_enabled":true}' \
    > /dev/null 2>&1 &

echo "Hook executed at $(date)" >> /tmp/pretool-debug.log
