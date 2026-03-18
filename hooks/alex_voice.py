#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Alex Voice Notification Hook (Stop Event)

Triggers when Alex (main AI) completes a response.
Extracts completion message and sends voice notification.
Skips subagent stops to avoid noise.
"""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.voice import speak_and_notify

LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def log(message: str, level: str = "INFO"):
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [alex_voice] [{level}] {message}\n"
    log_file = LOGS_DIR / 'voice_notifications.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)


def is_subagent(data: dict) -> bool:
    """Check if this Stop event is from a subagent."""
    if data.get("is_subagent"):
        return True
    if data.get("agent_id"):
        return True
    return False


def extract_custom_completed(text: str) -> str:
    """Extract completion message from response, or generate a smart summary."""

    # Pattern 1: CUSTOM COMPLETED: message (with or without emoji prefix)
    pattern1 = r'CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern1, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return clean_message(match.group(1).strip())

    # Pattern 2: COMPLETED: message
    pattern2 = r'COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern2, text, re.IGNORECASE | re.MULTILINE)
    if match:
        return clean_message(match.group(1).strip())

    # No marker -- try smart summary
    summary = extract_smart_summary(text)
    if summary:
        return summary

    return ""


def extract_smart_summary(text: str) -> str:
    """Extract a natural conversational summary from response text."""
    if not text or len(text.strip()) < 20:
        return ""

    lines = text.strip().split('\n')
    candidate_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#'):
            continue
        if re.match(r'^[-=*_]{3,}$', stripped):
            continue
        if stripped.startswith('```'):
            continue
        if re.match(r'^(/|\.\.?/|\w+/)', stripped) and '/' in stripped and ' ' not in stripped:
            continue
        if re.match(r'^[-*+]\s*$', stripped):
            continue
        candidate_lines.append(stripped)

    if not candidate_lines:
        return ""

    first_line = candidate_lines[0]

    if '?' in first_line and not first_line.startswith(('I ', 'The ', 'This ', 'That ', 'All ')):
        return ""

    if re.match(r'^(import |from |def |class |func |const |let |var |return |\{|\[)', first_line):
        return ""

    cleaned = re.sub(r'[*_`#]+', '', first_line)
    cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'^[-*+]\s+', '', cleaned)
    cleaned = re.sub(r'^\d+\.\s+', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    if not cleaned or len(cleaned) < 10:
        return ""

    words = cleaned.split()
    if len(words) > 15:
        cleaned = ' '.join(words[:15])

    return cleaned


def clean_message(message: str) -> str:
    """Clean up extracted message for voice."""
    message = re.sub(r'[*_`]+', '', message)
    message = message.replace('\n', ' ').replace('\r', ' ')
    message = re.sub(r'\s+', ' ', message)
    words = message.split()
    if len(words) > 8:
        message = ' '.join(words[:8])
    return message.strip()[:80]


def main():
    log("Hook triggered (Stop event)", "INFO")

    try:
        data = json.load(sys.stdin)

        # Skip subagent stops
        if is_subagent(data):
            log("Skipping voice for subagent stop", "DEBUG")
            return

        # Extract response text
        response_text = ""
        if isinstance(data, dict):
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
            return

        message = extract_custom_completed(response_text)

        if not message:
            log("No voice message to send, skipping", "INFO")
            return

        speak_and_notify(message, agent="alex")
        log(f"Sent: '{message}'", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")


if __name__ == '__main__':
    main()
