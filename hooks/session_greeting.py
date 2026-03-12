#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Session greeting hook - sends a voice greeting when a new session starts.
"""

import requests

ALEX_VOICE_ID = "O4lTuRmkE5LyjL2YhMIg"
VOICE_SERVER_URL = "http://localhost:8888/notify"

try:
    requests.post(
        VOICE_SERVER_URL,
        json={
            "message": "Hey Corey, ready when you are",
            "voice_id": ALEX_VOICE_ID,
            "voice_enabled": True,
        },
        timeout=3,
    )
except Exception:
    pass
