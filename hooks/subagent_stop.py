#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Subagent Stop Hook (SubagentStop Event)

Triggers when a subagent completes its task.
Saves agent transcript for later analysis and evaluation.
Records skill observations to Neon (if configured) for the improvement loop.
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

def get_neon_connection_string() -> str:
    """Get Neon database URL from environment or ~/.claude/.env"""
    import os
    url = os.environ.get("NEON_DATABASE_URL")
    if url:
        return url

    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("NEON_DATABASE_URL="):
                url = line.split("=", 1)[1].strip().strip('"').strip("'")
                if url:
                    return url
    return ""


def classify_outcome_from_transcript(transcript_path: str) -> tuple:
    """
    Heuristic classification of outcome from transcript content.
    Returns: (outcome, error_type, error_detail, task_summary)
    """
    outcome = "unknown"
    error_type = None
    error_detail = None
    task_summary = None

    try:
        tpath = Path(transcript_path)
        if not tpath.exists():
            return outcome, error_type, error_detail, task_summary

        lines = tpath.read_text().strip().splitlines()

        # Extract task summary from first user message
        for line in lines[:10]:
            try:
                msg = json.loads(line)
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content", "")
                    if isinstance(content, str) and content.strip():
                        task_summary = content[:500]
                        break
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("text", "").strip():
                                task_summary = item["text"][:500]
                                break
                        if task_summary:
                            break
            except (json.JSONDecodeError, KeyError):
                continue

        # Analyze last messages for errors
        last_texts = []
        for line in lines[-20:]:
            try:
                msg = json.loads(line)
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        last_texts.append(content.lower())
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                last_texts.append(item.get("text", "").lower())
            except (json.JSONDecodeError, KeyError):
                continue

        combined = " ".join(last_texts)

        error_patterns = {
            "tool_call": ["command not found", "no such file", "permission denied",
                         "exit code", "blocked:", "not installed"],
            "timeout": ["time limit", "timeout", "timed out", "approaching the time limit"],
            "instruction": ["i don't understand", "unclear", "ambiguous",
                          "could you clarify", "not sure what you mean"],
            "output_quality": ["not what i expected", "wrong output", "incorrect",
                             "doesn't match", "not quite right"],
        }

        for etype, patterns in error_patterns.items():
            for pattern in patterns:
                if pattern in combined:
                    error_type = etype
                    error_detail = f"Pattern: '{pattern}'"
                    outcome = "partial_failure"
                    break
            if error_type:
                break

        if not error_type:
            outcome = "success"

    except Exception as e:
        log(f"Error classifying transcript: {e}", "DEBUG")

    return outcome, error_type, error_detail, task_summary


def record_observation_to_neon(
    agent_name: str,
    transcript_path: str,
    transcript_ref: str = None,
    cwd: str = "",
):
    """Record a skill observation to Neon. Fails silently if DB not configured."""
    conn_str = get_neon_connection_string()
    if not conn_str:
        log("Neon not configured, skipping observation recording", "DEBUG")
        return

    try:
        import psycopg

        # Classify outcome from transcript
        outcome, error_type, error_detail, task_summary = "unknown", None, None, None
        if transcript_path:
            outcome, error_type, error_detail, task_summary = classify_outcome_from_transcript(transcript_path)

        # Use agent_name as skill_name (agents map to skills)
        skill_name = agent_name

        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Ensure skill exists
                cur.execute(
                    """
                    INSERT INTO skills (name, description, file_path)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (skill_name, f"Auto-registered from {agent_name}", f"agents/{agent_name}.md"),
                )

                # Get current skill version
                cur.execute("SELECT current_version FROM skills WHERE name = %s", (skill_name,))
                row = cur.fetchone()
                skill_version = row[0] if row else 1

                # Insert observation
                cur.execute(
                    """
                    INSERT INTO observations (
                        skill_name, project, agent_name, task_summary,
                        outcome, error_type, error_detail,
                        transcript_ref, skill_version, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING id
                    """,
                    (
                        skill_name,
                        cwd or None,
                        agent_name,
                        task_summary,
                        outcome,
                        error_type,
                        error_detail,
                        transcript_ref,
                        skill_version,
                        json.dumps({"source": "subagent_stop_hook"}),
                    ),
                )
                obs_id = cur.fetchone()[0]

            conn.commit()
            log(f"Observation #{obs_id} recorded for {skill_name} ({outcome})", "INFO")

    except Exception as e:
        log(f"Failed to record observation to Neon: {e}", "WARN")


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
        transcript_ref = None
        if transcript_path and agent_id:
            save_transcript(agent_name, transcript_path, agent_id)
            # Build transcript reference path for observation
            today = datetime.now().strftime('%Y-%m-%d')
            session_id = agent_id[:8]
            existing = list((OUTPUT_DIR / today / session_id).glob('*.jsonl')) if (OUTPUT_DIR / today / session_id).exists() else []
            transcript_ref = f"{today}/{session_id}/{len(existing):03d}-{agent_name}.jsonl"
        else:
            log("Transcript metadata not available (Claude Code < 2.0.42?)", "DEBUG")

        # Record observation to Neon (skill improvement loop)
        record_observation_to_neon(
            agent_name=agent_name,
            transcript_path=transcript_path,
            transcript_ref=transcript_ref,
            cwd=data.get('cwd', ''),
        )

        log("Hook completed successfully", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

if __name__ == '__main__':
    main()
