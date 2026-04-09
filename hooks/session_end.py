#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
SessionEnd Hook

Fires when a session ends. Handles:
- Final voice announcement
- Session duration logging
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from utils.voice import speak_and_notify

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOGS_DIR / 'session_end.log', 'a') as f:
        f.write(f"[{timestamp}] [session_end] [{level}] {message}\n")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    session_id = data.get('session_id', 'unknown')

    # Skip subagent sessions
    if data.get('is_subagent') or data.get('agent_id'):
        log(f"Subagent session ended: {session_id[:8]}", "DEBUG")
        return

    log(f"Session ended: {session_id[:8]}")

    speak_and_notify("Session ended, see you later", agent="alex")

    print(json.dumps({"suppressOutput": True}))


if __name__ == '__main__':
    main()
