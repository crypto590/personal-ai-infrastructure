#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
StopFailure Hook (v2.1.78+)

Fires when a turn ends due to an API error (rate limit, auth failure, etc.).
Logs the failure and saves partial state for recovery.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR = Path.home() / '.claude' / 'state'
STATE_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [stop_failure] [{level}] {message}\n"
    with open(LOGS_DIR / 'stop_failure.log', 'a') as f:
        f.write(log_entry)


def save_failure_state(data: dict):
    """Save failure context for potential recovery."""
    state = {
        'timestamp': datetime.now().isoformat(),
        'error_type': data.get('error_type', 'unknown'),
        'error_message': data.get('error_message', ''),
        'status_code': data.get('status_code', ''),
        'session_id': data.get('session_id', ''),
        'transcript_path': data.get('transcript_path', ''),
    }
    state_file = STATE_DIR / 'last_failure.json'
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    return state_file


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    error_type = data.get('error_type', 'unknown')
    error_message = data.get('error_message', '')
    status_code = data.get('status_code', '')

    log(f"Turn failed: {error_type} (status={status_code}): {error_message}", "ERROR")

    # Save state for recovery
    state_file = save_failure_state(data)
    log(f"Failure state saved to {state_file}", "INFO")

    # Rate limit specific handling
    if status_code == '429' or 'rate limit' in error_message.lower():
        log("Rate limit hit — consider reducing agent parallelism", "WARN")

    # Output for the session
    result = {"suppressOutput": True}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
