#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
PostToolUseFailure Hook

Fires when a tool call fails (error response).
Logs failures for observability and pattern detection.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOGS_DIR / 'tool_failures.log', 'a') as f:
        f.write(f"[{timestamp}] [post_tool_use_failure] [{level}] {message}\n")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    tool_name = data.get('tool_name', 'unknown')
    error = data.get('error', '')
    tool_input = data.get('tool_input', {})

    # Truncate error for logging
    error_short = str(error)[:300] if error else 'no error message'

    log(f"FAILED: {tool_name} — {error_short}", "ERROR")

    # Log context for common failure types
    if tool_name == 'Bash':
        cmd = tool_input.get('command', '?')[:200]
        log(f"  command: {cmd}", "ERROR")
    elif tool_name in ('Write', 'Edit', 'Read'):
        log(f"  path: {tool_input.get('file_path', '?')}", "ERROR")

    print(json.dumps({"suppressOutput": True}))


if __name__ == '__main__':
    main()
