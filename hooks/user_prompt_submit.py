#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
UserPromptSubmit Hook (v2.1.94+)

Auto-names sessions based on the first user prompt.
Returns hookSpecificOutput.sessionTitle on the first prompt of a session.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR = Path.home() / '.claude' / 'state'
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Track which sessions already have titles
TITLED_FILE = STATE_DIR / 'titled_sessions.json'


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOGS_DIR / 'user_prompt_submit.log', 'a') as f:
        f.write(f"[{timestamp}] [user_prompt_submit] [{level}] {message}\n")


def load_titled():
    try:
        return json.loads(TITLED_FILE.read_text())
    except Exception:
        return {}


def save_titled(data: dict):
    # Keep only last 50 sessions to avoid unbounded growth
    if len(data) > 50:
        sorted_keys = sorted(data, key=lambda k: data[k])
        for k in sorted_keys[:-50]:
            del data[k]
    TITLED_FILE.write_text(json.dumps(data))


def extract_title(prompt: str) -> str:
    """Extract a concise session title from the user's first prompt."""
    if not prompt or not prompt.strip():
        return ""

    text = prompt.strip()

    # Strip slash command prefixes
    if text.startswith('/'):
        parts = text.split(None, 1)
        if len(parts) > 1:
            text = parts[1]
        else:
            return parts[0][:40]

    # Remove markdown formatting
    for char in ['#', '*', '`', '_']:
        text = text.replace(char, '')

    # Take first line only
    first_line = text.split('\n')[0].strip()

    # Truncate to ~50 chars at word boundary
    if len(first_line) > 50:
        words = first_line[:55].split()
        first_line = ' '.join(words[:-1]) if len(words) > 1 else first_line[:50]

    return first_line


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"suppressOutput": True}))
        return

    session_id = data.get('session_id', '')
    prompt = data.get('prompt', '')

    if not session_id or not prompt:
        print(json.dumps({"suppressOutput": True}))
        return

    # Only title the first prompt per session
    titled = load_titled()
    if session_id in titled:
        print(json.dumps({"suppressOutput": True}))
        return

    title = extract_title(prompt)
    if not title:
        print(json.dumps({"suppressOutput": True}))
        return

    # Mark session as titled
    titled[session_id] = datetime.now().isoformat()
    save_titled(titled)

    log(f"Session {session_id[:8]} titled: {title}")

    result = {
        "suppressOutput": True,
        "hookSpecificOutput": {
            "sessionTitle": title
        }
    }
    print(json.dumps(result))


if __name__ == '__main__':
    main()
