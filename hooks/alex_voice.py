#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Alex Voice Notification Hook (Stop Event)

Triggers when Alex (main AI) completes a response.
Extracts 🗣️ CUSTOM COMPLETED message and sends voice notification.
Always uses Alex's voice ID.
"""

import sys
import json
import re
import requests
from pathlib import Path

# Configuration
ALEX_VOICE_ID = "O4lTuRmkE5LyjL2YhMIg"
VOICE_SERVER_URL = "http://localhost:8888/notify"
LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log(message: str, level: str = "INFO"):
    """Simple logging to file"""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [alex_voice] [{level}] {message}\n"

    log_file = LOGS_DIR / 'voice_notifications.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)

def extract_custom_completed(text: str) -> str:
    """Extract 🗣️ CUSTOM COMPLETED message from response"""

    # Pattern 1: Look for 🗣️ CUSTOM COMPLETED: message
    pattern1 = r'🗣️\s*CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern1, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found CUSTOM COMPLETED message: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    # Pattern 2: Look for 🎯 COMPLETED: message as fallback
    pattern2 = r'🎯\s*COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern2, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found COMPLETED message as fallback: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    # Pattern 3: Look for just "CUSTOM COMPLETED:" without emoji
    pattern3 = r'CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern3, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found plain CUSTOM COMPLETED: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    log("No completion message found, using default", "WARN")
    return "Task completed"

def clean_message(message: str) -> str:
    """Clean up extracted message for voice"""
    # Remove markdown formatting
    message = re.sub(r'[*_`]+', '', message)
    # Remove newlines and extra whitespace
    message = message.replace('\n', ' ').replace('\r', ' ')
    message = re.sub(r'\s+', ' ', message)
    # Limit length for voice (8 words or ~60 chars)
    words = message.split()
    if len(words) > 8:
        message = ' '.join(words[:8])
    return message.strip()[:80]

def send_notification(message: str) -> bool:
    """Send voice notification to server"""
    try:
        log(f"Sending notification: '{message}'", "INFO")

        response = requests.post(
            VOICE_SERVER_URL,
            json={
                'message': message,
                'voice_id': ALEX_VOICE_ID,
                'voice_enabled': True
            },
            timeout=3
        )

        if response.status_code == 200:
            log(f"Notification sent successfully (voice: Alex)", "INFO")
            return True
        else:
            log(f"Notification failed: HTTP {response.status_code}", "ERROR")
            return False

    except requests.exceptions.Timeout:
        log("Notification timeout - voice server may be unavailable", "WARN")
        return False
    except Exception as e:
        log(f"Notification error: {e}", "ERROR")
        return False

def main():
    """Main hook execution"""
    log("Hook triggered (Stop event)", "INFO")

    try:
        # Read JSON input from stdin
        data = json.load(sys.stdin)

        # Extract the response text
        # Stop event includes the full response content
        response_text = ""

        # Try different possible JSON structures
        if isinstance(data, dict):
            # Check for 'content' field
            if 'content' in data:
                content = data['content']
                if isinstance(content, str):
                    response_text = content
                elif isinstance(content, list):
                    # Content might be array of message blocks
                    for block in content:
                        if isinstance(block, dict) and 'text' in block:
                            response_text += block['text'] + '\n'

            # Check for 'text' field directly
            elif 'text' in data:
                response_text = data['text']

            # Check for 'message' field
            elif 'message' in data:
                response_text = data['message']

        if not response_text:
            log("No response text found in Stop event data", "WARN")
            log(f"Event data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}", "DEBUG")
            # Still send default notification
            send_notification("Response completed")
            return

        # Extract custom completed message
        message = extract_custom_completed(response_text)

        # Send notification
        send_notification(message)

        log("Hook completed successfully", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

if __name__ == '__main__':
    main()
