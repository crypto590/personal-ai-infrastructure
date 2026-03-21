#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["requests"]
# ///

"""
Subagent Stop Hook (SubagentStop Event)

Triggers when a subagent completes its task.
Saves agent transcript and announces completion in the agent's mapped voice.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))


# Configuration
LOGS_DIR = Path.home() / '.claude' / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path.home() / '.claude' / 'agent-output-context'


def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [subagent_stop] [{level}] {message}\n"
    log_file = LOGS_DIR / 'subagent_stop.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)


def extract_agent_name_from_parent_session(parent_session_path: str, agent_id: str = '') -> str:
    """Extract agent name from parent session transcript."""
    try:
        session_file = Path(parent_session_path)
        if not session_file.exists():
            return 'unknown'

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

        return last_subagent_type or 'unknown'
    except Exception:
        return 'unknown'


def save_transcript(agent_name: str, transcript_path: str, agent_id: str) -> bool:
    """Save agent transcript for later analysis."""
    try:
        if not transcript_path:
            return False

        transcript_file = Path(transcript_path)
        if not transcript_file.exists() or not agent_id:
            return False

        today = datetime.now().strftime('%Y-%m-%d')
        session_id = agent_id[:8]
        session_dir = OUTPUT_DIR / today / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        existing = list(session_dir.glob('*.jsonl'))
        next_num = len(existing) + 1
        dest = session_dir / f"{next_num:03d}-{agent_name}.jsonl"
        shutil.copy(transcript_path, dest)

        log(f"Transcript saved: {dest}", "INFO")
        return True
    except Exception as e:
        log(f"Error saving transcript: {e}", "ERROR")
        return False


def main():
    log("Hook triggered (SubagentStop event)", "INFO")

    try:
        data = json.load(sys.stdin)

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

        # Extract agent name from parent session if unknown
        parent_session_path = data.get('transcript_path', '')
        if agent_name == 'unknown' and parent_session_path:
            agent_name = extract_agent_name_from_parent_session(parent_session_path, agent_id)

        # Save transcript
        if transcript_path and agent_id:
            save_transcript(agent_name, transcript_path, agent_id)

        log(f"Subagent completed: {agent_name}", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")


if __name__ == '__main__':
    main()
