#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
PermissionDenied Hook (v2.1.90+)

Fires when auto mode classifier denies a tool call.
Logs the denial for observability. Can return {retry: true}
to let the model retry with adjusted parameters.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOGS_DIR / 'permission_denied.log', 'a') as f:
        f.write(f"[{timestamp}] [permission_denied] [{level}] {message}\n")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    tool_name = data.get('tool_name', 'unknown')
    tool_input = data.get('tool_input', {})
    reason = data.get('reason', '')

    log(f"DENIED: {tool_name} — {reason}", "WARN")

    # Log the command/path that was denied for audit
    if tool_name == 'Bash':
        log(f"  command: {tool_input.get('command', '?')[:200]}", "WARN")
    elif tool_name in ('Write', 'Edit', 'Read'):
        log(f"  path: {tool_input.get('file_path', '?')}", "WARN")

    # Don't auto-retry — let the model adapt its approach
    print(json.dumps({"suppressOutput": True}))


if __name__ == '__main__':
    main()
