#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
PostToolUse Hook — JSONL audit logging.

Append-only JSONL format eliminates the read-modify-write overhead
that caused the old JSON array approach to balloon to 2.5MB.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def main():
    try:
        input_data = json.load(sys.stdin)

        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'events.jsonl'

        tool_name = input_data.get('tool_name', '')
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "hook": "post",
            "tool": tool_name,
        }

        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()
