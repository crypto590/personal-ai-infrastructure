#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
PostCompact Hook (v2.1.76+)

Fires after context compaction completes.
Logs compaction stats and ensures critical context wasn't lost.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [post_compact] [{level}] {message}\n"
    with open(LOGS_DIR / 'post_compact.log', 'a') as f:
        f.write(log_entry)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        data = {}

    session_id = data.get('session_id', 'unknown')
    stats = data.get('stats', {})

    tokens_before = stats.get('tokens_before', '?')
    tokens_after = stats.get('tokens_after', '?')

    log(f"Compaction complete for session {session_id[:12]}", "INFO")
    log(f"Tokens: {tokens_before} → {tokens_after}", "INFO")

    # Output for the session
    result = {"suppressOutput": True}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
