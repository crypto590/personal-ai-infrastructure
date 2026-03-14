#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Skill Tracker - Observation Module

Records skill execution outcomes to Neon for the improvement loop.
Called from SubagentStop hook after each agent completes.

Handles:
- Auto-registering unknown skills
- Recording observations with structured error classification
- Cross-project tracking (includes project identifier)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import psycopg
from psycopg.rows import dict_row


def get_connection_string() -> str:
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


def ensure_skill_exists(conn, skill_name: str) -> int:
    """Register a skill if it doesn't exist yet. Returns current version."""
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT current_version FROM skills WHERE name = %s", (skill_name,))
        row = cur.fetchone()
        if row:
            return row["current_version"]

        # Auto-register with basic info — will be enriched later
        cur.execute(
            """
            INSERT INTO skills (name, description, file_path)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
            RETURNING current_version
            """,
            (skill_name, f"Auto-registered from observation", f"skills/{skill_name}/SKILL.md"),
        )
        row = cur.fetchone()
        conn.commit()
        return row["current_version"] if row else 1


def record_observation(
    skill_name: str,
    outcome: str,
    agent_name: str = None,
    project: str = None,
    task_summary: str = None,
    error_type: str = None,
    error_detail: str = None,
    duration_seconds: float = None,
    user_feedback: str = None,
    transcript_ref: str = None,
    metadata: dict = None,
) -> int | None:
    """
    Record a skill execution observation.

    Returns the observation ID, or None if DB is not configured.
    """
    conn_str = get_connection_string()
    if not conn_str:
        return None  # Silently skip if no DB configured

    try:
        with psycopg.connect(conn_str, row_factory=dict_row) as conn:
            skill_version = ensure_skill_exists(conn, skill_name)

            with conn.cursor() as cur:
                import json

                cur.execute(
                    """
                    INSERT INTO observations (
                        skill_name, project, agent_name, task_summary,
                        outcome, error_type, error_detail, duration_seconds,
                        user_feedback, transcript_ref, skill_version, metadata
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                    )
                    RETURNING id
                    """,
                    (
                        skill_name,
                        project,
                        agent_name,
                        task_summary,
                        outcome,
                        error_type,
                        error_detail,
                        duration_seconds,
                        user_feedback,
                        transcript_ref,
                        skill_version,
                        json.dumps(metadata or {}),
                    ),
                )
                row = cur.fetchone()
            conn.commit()
            return row["id"] if row else None

    except Exception as e:
        # Log but don't crash — observation is supplementary
        log_dir = Path.home() / ".claude" / "logs" / "hooks"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "skill_tracker.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] [observe] [ERROR] {e}\n")
        return None


def classify_outcome_from_transcript(transcript_path: str) -> tuple[str, str | None, str | None]:
    """
    Heuristic classification of outcome from a transcript file.

    Returns: (outcome, error_type, error_detail)

    This is a basic classifier — can be improved over time.
    """
    import json

    outcome = "unknown"
    error_type = None
    error_detail = None

    try:
        transcript = Path(transcript_path)
        if not transcript.exists():
            return outcome, error_type, error_detail

        content = transcript.read_text()
        lines = content.strip().splitlines()

        # Look for error indicators in the last few messages
        last_messages = []
        for line in lines[-20:]:
            try:
                msg = json.loads(line)
                if isinstance(msg, dict):
                    text = ""
                    msg_content = msg.get("content", "")
                    if isinstance(msg_content, str):
                        text = msg_content
                    elif isinstance(msg_content, list):
                        text = " ".join(
                            item.get("text", "") for item in msg_content if isinstance(item, dict)
                        )
                    last_messages.append(text.lower())
            except (json.JSONDecodeError, KeyError):
                continue

        combined = " ".join(last_messages)

        # Classify based on content patterns
        error_patterns = {
            "tool_call": [
                "command not found",
                "no such file",
                "permission denied",
                "exit code",
                "tool_result.*error",
                "blocked:",
            ],
            "timeout": ["time limit", "timeout", "timed out", "approaching the time limit"],
            "instruction": [
                "i don't understand",
                "unclear",
                "ambiguous",
                "not sure what",
                "could you clarify",
            ],
            "output_quality": [
                "not what i expected",
                "wrong output",
                "incorrect",
                "doesn't match",
            ],
        }

        for etype, patterns in error_patterns.items():
            for pattern in patterns:
                if pattern in combined:
                    error_type = etype
                    error_detail = f"Detected pattern: '{pattern}'"
                    outcome = "partial_failure"
                    break
            if error_type:
                break

        # If no errors detected, assume success
        if not error_type:
            outcome = "success"

    except Exception:
        pass

    return outcome, error_type, error_detail


# CLI interface for manual observation recording
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Record a skill observation")
    parser.add_argument("skill_name", help="Name of the skill")
    parser.add_argument("outcome", choices=["success", "partial_failure", "failure", "unknown"])
    parser.add_argument("--agent", help="Agent that ran the skill")
    parser.add_argument("--project", help="Project identifier")
    parser.add_argument("--task", help="Task summary")
    parser.add_argument("--error-type", choices=["routing", "instruction", "tool_call", "output_quality", "timeout"])
    parser.add_argument("--error-detail", help="Error details")
    parser.add_argument("--transcript", help="Path to transcript file")

    args = parser.parse_args()

    obs_id = record_observation(
        skill_name=args.skill_name,
        outcome=args.outcome,
        agent_name=args.agent,
        project=args.project,
        task_summary=args.task,
        error_type=args.error_type,
        error_detail=args.error_detail,
        transcript_ref=args.transcript,
    )

    if obs_id:
        print(f"Observation recorded: #{obs_id}")
    else:
        print("Observation not recorded (DB not configured or error occurred)")
