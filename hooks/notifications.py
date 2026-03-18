#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Notification Hook (Notification Event)

Triggers when Claude Code sends system notifications.
Sends voice notification + macOS system notification.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.voice import speak_and_notify


def main():
    try:
        data = json.load(sys.stdin)
        message = data.get('message', 'Notification')
        message = ' '.join(message.split())[:80]
        speak_and_notify(message, agent="alex")
    except Exception:
        speak_and_notify("Notification", agent="alex")


if __name__ == '__main__':
    main()
