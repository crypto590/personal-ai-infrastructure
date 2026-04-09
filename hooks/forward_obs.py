#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Lean observability forwarder for PAI global hooks.

Reshapes raw Claude Code hook events into the schema expected by
the disler multi-agent observability server (localhost:4000).

Fails silently if the server isn't running — never blocks Claude Code.
No LLM calls, no summarization, no external dependencies.

Usage in settings.json:
  "command": "uv run ~/.claude/hooks/forward_obs.py --event-type PreToolUse"
"""

import json
import sys
import os
import argparse
import urllib.request
import urllib.error
from datetime import datetime

SERVER_URL = os.environ.get('CC_OBS_URL', 'http://localhost:4000/events')
# Derive source-app from project dir or fall back to "pai-global"
SOURCE_APP = os.environ.get('CLAUDE_PROJECT_DIR', '').split('/')[-1] or 'pai-global'


def forward(event_data: dict, url: str = SERVER_URL) -> bool:
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(event_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-type', required=True)
    parser.add_argument('--source-app', default=SOURCE_APP)
    args = parser.parse_args()

    try:
        raw = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    event = {
        'source_app': args.source_app,
        'session_id': raw.get('session_id', 'unknown'),
        'hook_event_type': args.event_type,
        'payload': raw,
        'timestamp': int(datetime.now().timestamp() * 1000),
    }

    # Promote commonly-queried fields
    for key in ('tool_name', 'agent_id', 'agent_type', 'error'):
        if key in raw:
            event[key] = raw[key]

    forward(event)


if __name__ == '__main__':
    main()
