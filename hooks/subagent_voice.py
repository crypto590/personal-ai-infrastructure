#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Subagent Voice Notification Hook (SubagentStop Event)

Triggers when a subagent completes its task.
Extracts agent name, maps to voice ID, and sends completion notification.
"""

import sys
import json
import re
import requests
from pathlib import Path

# Configuration
VOICE_SERVER_URL = "http://localhost:8888/notify"
LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Voice ID mapping (from SKILL.md)
VOICE_MAP = {
    'alex': 'O4lTuRmkE5LyjL2YhMIg',
    'cto-advisor': 'lpcesEa7Zyjkgsrd7I32',
    'claude-researcher': 'O4lTuRmkE5LyjL2YhMIg',  # TODO: Update when voice ID available
    'gemini-researcher': 'O4lTuRmkE5LyjL2YhMIg',  # TODO: Update when voice ID available
    'pentester': 'O4lTuRmkE5LyjL2YhMIg',          # TODO: Update when voice ID available
    'engineer': 'O4lTuRmkE5LyjL2YhMIg',            # TODO: Update when voice ID available
    'principal-engineer': 'O4lTuRmkE5LyjL2YhMIg',  # TODO: Update when voice ID available
    'designer': 'O4lTuRmkE5LyjL2YhMIg',            # TODO: Update when voice ID available
    'architect': 'O4lTuRmkE5LyjL2YhMIg',           # TODO: Update when voice ID available
    'artist': 'O4lTuRmkE5LyjL2YhMIg',              # TODO: Update when voice ID available
    'writer': 'O4lTuRmkE5LyjL2YhMIg',              # TODO: Update when voice ID available
    # Built-in agents
    'general-purpose': 'O4lTuRmkE5LyjL2YhMIg',
    'statusline-setup': 'O4lTuRmkE5LyjL2YhMIg',
    'output-style-setup': 'O4lTuRmkE5LyjL2YhMIg',
    'ui-ux-designer': 'O4lTuRmkE5LyjL2YhMIg',
    'solution-architect': 'O4lTuRmkE5LyjL2YhMIg',
    'research-specialist': 'O4lTuRmkE5LyjL2YhMIg',
    'product-manager': 'O4lTuRmkE5LyjL2YhMIg',
    'react-developer': 'O4lTuRmkE5LyjL2YhMIg',
    'fastify-specialist': 'O4lTuRmkE5LyjL2YhMIg',
    'kotlin-specialist': 'O4lTuRmkE5LyjL2YhMIg',
    'swift-specialist': 'O4lTuRmkE5LyjL2YhMIg',
    'github-manager': 'O4lTuRmkE5LyjL2YhMIg',
    'nextjs-app-developer': 'O4lTuRmkE5LyjL2YhMIg',
    'performance-engineer': 'O4lTuRmkE5LyjL2YhMIg',
    'database-engineer': 'O4lTuRmkE5LyjL2YhMIg',
    'python-web-scraper': 'O4lTuRmkE5LyjL2YhMIg',
}

# Default fallback voice (Alex)
DEFAULT_VOICE_ID = 'O4lTuRmkE5LyjL2YhMIg'

def log(message: str, level: str = "INFO"):
    """Simple logging to file"""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [subagent_voice] [{level}] {message}\n"

    log_file = LOGS_DIR / 'voice_notifications.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)

def get_voice_id(agent_name: str) -> str:
    """Get voice ID for agent, fallback to Alex"""
    agent_name_lower = agent_name.lower().strip()
    voice_id = VOICE_MAP.get(agent_name_lower, DEFAULT_VOICE_ID)

    if voice_id == DEFAULT_VOICE_ID and agent_name_lower not in VOICE_MAP:
        log(f"No voice mapping for '{agent_name}', using default (Alex)", "WARN")
    else:
        log(f"Agent '{agent_name}' mapped to voice ID: {voice_id[:8]}...", "DEBUG")

    return voice_id

def extract_completion_message(text: str, agent_name: str) -> str:
    """Extract completion message from agent output"""

    # Pattern 1: Look for 🗣️ CUSTOM COMPLETED
    pattern1 = r'🗣️\s*CUSTOM COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern1, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found CUSTOM COMPLETED: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    # Pattern 2: Look for 🎯 COMPLETED
    pattern2 = r'🎯\s*COMPLETED[:\s]+(.+?)(?:\n|$)'
    match = re.search(pattern2, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found COMPLETED: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    # Pattern 3: Look for generic "completed" statements
    pattern3 = r'completed\s+(.+?)(?:\n|\.|$)'
    match = re.search(pattern3, text, re.IGNORECASE | re.MULTILINE)
    if match:
        msg = match.group(1).strip()
        log(f"Found generic completion: {msg[:50]}...", "DEBUG")
        return clean_message(msg)

    # Fallback: Use agent name + "completed"
    log("No completion message found, using fallback", "WARN")
    return f"{agent_name} task completed"

def clean_message(message: str) -> str:
    """Clean up extracted message for voice"""
    # Remove markdown formatting
    message = re.sub(r'[*_`]+', '', message)
    # Remove [AGENT:...] tags
    message = re.sub(r'\[AGENT:[^\]]+\]', '', message)
    # Remove newlines and extra whitespace
    message = message.replace('\n', ' ').replace('\r', ' ')
    message = re.sub(r'\s+', ' ', message)
    # Limit length for voice
    return message.strip()[:100]

def send_notification(message: str, voice_id: str) -> bool:
    """Send voice notification to server"""
    try:
        log(f"Sending notification: '{message}' (voice: {voice_id[:8]}...)", "INFO")

        response = requests.post(
            VOICE_SERVER_URL,
            json={
                'message': message,
                'voice_id': voice_id,
                'voice_enabled': True
            },
            timeout=3
        )

        if response.status_code == 200:
            log("Notification sent successfully", "INFO")
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
    log("Hook triggered (SubagentStop event)", "INFO")

    try:
        # Read JSON input from stdin
        data = json.load(sys.stdin)

        # Extract agent name
        agent_name = data.get('agentName', 'unknown')
        log(f"Subagent detected: {agent_name}", "INFO")

        # Extract output text
        output_text = data.get('output', '')

        if not output_text:
            log("No output text in SubagentStop event", "WARN")
            # Still send notification with agent name
            voice_id = get_voice_id(agent_name)
            send_notification(f"{agent_name} completed", voice_id)
            return

        # Get voice ID for this agent
        voice_id = get_voice_id(agent_name)

        # Extract completion message
        message = extract_completion_message(output_text, agent_name)

        # Send notification
        send_notification(message, voice_id)

        log("Hook completed successfully", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

if __name__ == '__main__':
    main()
