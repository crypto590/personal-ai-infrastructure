#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Session greeting hook — sends a voice greeting when a new session starts.
Skips if this is a subagent session.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.voice import speak_and_notify

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

# Skip subagent sessions
if data.get("is_subagent") or data.get("agent_id"):
    pass
else:
    speak_and_notify("Hey Corey, ready when you are", agent="alex")
