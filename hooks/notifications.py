#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Notification Hook (Notification Event)

Triggers when Claude Code sends system notifications (permission requests, warnings, etc).
Sends voice notification to keep user informed.
Always uses Alex's voice.
"""

import sys
import json
import requests

# Configuration
ALEX_VOICE_ID = "O4lTuRmkE5LyjL2YhMIg"
VOICE_SERVER_URL = "http://localhost:8888/notify"

def send_notification(message: str) -> bool:
    """Send voice notification to server"""
    try:
        response = requests.post(
            VOICE_SERVER_URL,
            json={
                'message': message,
                'voice_id': ALEX_VOICE_ID,
                'voice_enabled': True
            },
            timeout=3
        )
        return response.status_code == 200
    except:
        return False

def main():
    """Main hook execution"""
    try:
        # Read JSON input from stdin
        data = json.load(sys.stdin)

        # Extract notification message
        message = data.get('message', 'Notification')

        # Clean and truncate message for voice
        message = ' '.join(message.split())[:80]

        # Send notification
        send_notification(message)

    except:
        # Fallback: send generic notification
        send_notification("Notification")

if __name__ == '__main__':
    main()
