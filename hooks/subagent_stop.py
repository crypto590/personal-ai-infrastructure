#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
Subagent Stop Hook (SubagentStop Event)

Triggers when a subagent completes its task.
Saves agent transcript for later analysis and evaluation.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Transcript storage
OUTPUT_DIR = Path.home() / '.claude' / 'agent-output-context'

def log(message: str, level: str = "INFO"):
    """Simple logging to file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [subagent_stop] [{level}] {message}\n"

    log_file = LOGS_DIR / 'subagent_stop.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)

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

        log("Hook completed successfully", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

if __name__ == '__main__':
    main()
