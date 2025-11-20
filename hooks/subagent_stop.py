#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Subagent Stop Hook (SubagentStop Event)

Triggers when a subagent completes its task.
Handles multiple completion tasks:
- Saves agent transcript for later analysis and evaluation
- Extracts completion message and sends voice notification
- Future: Add quality gates, validation, output format checks, etc.
"""

import sys
import json
import re
import requests
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
VOICE_SERVER_URL = "http://localhost:8888/notify"
LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Transcript storage
OUTPUT_DIR = Path.home() / '.claude' / 'agent-output-context'

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
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [subagent_stop] [{level}] {message}\n"

    log_file = LOGS_DIR / 'subagent_stop.log'
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

def extract_agent_name_from_parent_session(parent_session_path: str, agent_id: str = '') -> str:
    """
    Extract agent name from parent session transcript.

    The hook provides 'transcript_path' which is the parent session transcript.
    We look for the most recent Task tool invocation with subagent_type.
    """
    try:
        session_file = Path(parent_session_path)
        if not session_file.exists():
            log(f"Parent session file not found: {parent_session_path}", "WARN")
            return 'unknown'

        # Read parent session looking for Task tool invocations
        # Use the LAST one found since multiple agents could be spawned
        last_subagent_type = None

        with open(session_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    message = data.get('message', {})
                    content = message.get('content', [])

                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'tool_use' and item.get('name') == 'Task':
                            input_params = item.get('input', {})
                            if 'subagent_type' in input_params:
                                last_subagent_type = input_params['subagent_type']
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

        if last_subagent_type:
            log(f"Extracted agent type: {last_subagent_type}", "DEBUG")
            return last_subagent_type
        else:
            log("No Task tool invocation found in parent session", "WARN")
            return 'unknown'

    except Exception as e:
        log(f"Error extracting agent name from parent session: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "DEBUG")
        return 'unknown'

def save_transcript(agent_name: str, transcript_path: str, agent_id: str) -> bool:
    """Save agent transcript for later analysis and evaluation"""
    try:
        # Validate inputs
        if not transcript_path:
            log("No transcript path provided", "DEBUG")
            return False

        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            log(f"Transcript file not found: {transcript_path}", "WARN")
            return False

        if not agent_id:
            log("No agent ID provided, skipping transcript save", "WARN")
            return False

        # agent_name should already be extracted before calling save_transcript
        # If still unknown, we can't do anything more here

        # Organize by date and session ID
        today = datetime.now().strftime('%Y-%m-%d')
        session_id = agent_id[:8]  # First 8 chars of agent ID
        session_dir = OUTPUT_DIR / today / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Sequential naming within session
        existing = list(session_dir.glob('*.jsonl'))
        next_num = len(existing) + 1

        # Save transcript
        dest = session_dir / f"{next_num:03d}-{agent_name}.jsonl"
        shutil.copy(transcript_path, dest)

        log(f"Transcript saved: {dest} ({transcript_file.stat().st_size} bytes)", "INFO")
        return True

    except Exception as e:
        log(f"Error saving transcript: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return False

def main():
    """Main hook execution"""
    log("Hook triggered (SubagentStop event)", "INFO")

    try:
        # Read JSON input from stdin
        data = json.load(sys.stdin)

        # Note: Hook data keys available: session_id, transcript_path, cwd,
        # permission_mode, hook_event_name, stop_hook_active, agent_id, agent_transcript_path

        # Extract agent information - try multiple possible key names
        agent_name = (
            data.get('agentName') or
            data.get('agent_name') or
            data.get('subagent_type') or
            data.get('subagentType') or
            'unknown'
        )
        agent_id = data.get('agent_id', '')
        transcript_path = data.get('agent_transcript_path', '')

        log(f"Subagent detected: {agent_name}", "INFO")
        log(f"Agent ID: {agent_id[:16] if agent_id else 'none'}...", "DEBUG")
        log(f"Transcript path: {transcript_path if transcript_path else 'none'}", "DEBUG")

        # Extract agent name from parent session transcript if unknown
        parent_session_path = data.get('transcript_path', '')
        if agent_name == 'unknown' and parent_session_path:
            log(f"Extracting agent name from parent session: {parent_session_path}", "DEBUG")
            agent_name = extract_agent_name_from_parent_session(parent_session_path, agent_id)

        # Save transcript for analysis (new in 2.0.42)
        if transcript_path and agent_id:
            save_transcript(agent_name, transcript_path, agent_id)
        else:
            log("Transcript metadata not available (Claude Code < 2.0.42?)", "DEBUG")

        # Extract output text for voice notification
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
