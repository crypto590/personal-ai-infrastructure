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
    """Extract 🗣️ CUSTOM COMPLETED message from response, or generate a smart summary"""

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

    # No marker found - try smart conversational summary
    log("No completion marker found, attempting smart summary", "DEBUG")
    summary = extract_smart_summary(text)
    if summary:
        log(f"Using smart summary: {summary}", "INFO")
        return summary

    log("No suitable summary found, skipping voice", "WARN")
    return ""


def extract_smart_summary(text: str) -> str:
    """Extract a natural conversational summary from response text.

    Returns empty string if the response shouldn't be spoken.
    """
    if not text or len(text.strip()) < 20:
        return ""

    # Split into lines and filter out noise
    lines = text.strip().split('\n')
    candidate_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip markdown headers
        if stripped.startswith('#'):
            continue
        # Skip lines that are just formatting/separators
        if re.match(r'^[-=*_]{3,}$', stripped):
            continue
        # Skip lines that are just code fence markers
        if stripped.startswith('```'):
            continue
        # Skip lines that look like file paths or tool output
        if re.match(r'^(/|\.\.?/|\w+/)', stripped) and '/' in stripped and ' ' not in stripped:
            continue
        # Skip bullet-only lines that are just list markers
        if re.match(r'^[-*+]\s*$', stripped):
            continue
        candidate_lines.append(stripped)

    if not candidate_lines:
        return ""

    # Take the first meaningful line
    first_line = candidate_lines[0]

    # Skip if it's a question - let the user read those
    if '?' in first_line and not first_line.startswith(('I ', 'The ', 'This ', 'That ', 'All ')):
        return ""

    # Skip if it looks like pure code
    if re.match(r'^(import |from |def |class |func |const |let |var |return |\{|\[)', first_line):
        return ""

    # Clean markdown formatting
    cleaned = re.sub(r'[*_`#]+', '', first_line)
    # Remove markdown links but keep text: [text](url) -> text
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    # Remove bullet/list markers at start
    cleaned = re.sub(r'^[-*+]\s+', '', cleaned)
    # Remove numbered list markers
    cleaned = re.sub(r'^\d+\.\s+', '', cleaned)
    # Clean extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned or len(cleaned) < 10:
        return ""

    # Truncate to ~15 words for natural speech
    words = cleaned.split()
    if len(words) > 15:
        cleaned = ' '.join(words[:15])

    return cleaned

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

        # Extract response text from Stop event data
        if isinstance(data, dict):
            # The Stop event uses 'last_assistant_message' for the response text
            if 'last_assistant_message' in data:
                response_text = data['last_assistant_message']
            elif 'content' in data:
                content = data['content']
                if isinstance(content, str):
                    response_text = content
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and 'text' in block:
                            response_text += block['text'] + '\n'
            elif 'text' in data:
                response_text = data['text']
            elif 'message' in data:
                response_text = data['message']

        if not response_text:
            log("No response text found in Stop event data", "WARN")
            log(f"Event data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}", "DEBUG")
            return

        # Extract custom completed message or smart summary
        message = extract_custom_completed(response_text)

        # Skip voice if no suitable message (empty string means don't speak)
        if not message:
            log("No voice message to send, skipping", "INFO")
            return

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
