#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Background episode extraction — spawned by memory-capture.py.
Reads conversation transcript, calls claude CLI for extraction, inserts episodes.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

EXTRACTION_PROMPT = """You are a memory extraction system. Analyze this conversation and extract important episodes.

For each episode, output a JSON object on its own line with these fields:
- episode_type: one of "decision", "preference", "fact", "insight", "failure", "relationship"
- subject: short identifier (max 120 chars)
- content: the memory itself (1-3 sentences)
- reasoning: WHY this matters (1 sentence, null if not applicable)
- salience: importance 1-10 (8+ for critical decisions/preferences, 5 for general facts)
- tags: array of relevant tags

Only extract episodes worth remembering in FUTURE conversations. Skip routine operations.
Output one JSON object per line, no markdown. If nothing worth extracting, output nothing."""


def extract_episodes(transcript_path: str, product: str, cwd: str):
    """Read transcript, call claude CLI, parse and insert episodes."""
    from memory_db import add_episode, connect

    # Read transcript (truncate to last ~4000 chars to stay cheap)
    text = Path(transcript_path).read_text()
    if len(text) > 8000:
        text = text[-8000:]

    # Call claude CLI for extraction
    try:
        result = subprocess.run(
            ["claude", "--bare", "-p", "--model", "haiku",
             EXTRACTION_PROMPT + "\n\n---\n\n" + text],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return

    # Parse JSON lines from output
    episodes_added = 0
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            ep = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Validate required fields
        if not all(k in ep for k in ("episode_type", "subject", "content")):
            continue

        valid_types = {"decision", "preference", "fact", "insight", "failure", "relationship"}
        if ep["episode_type"] not in valid_types:
            continue

        add_episode(
            episode_type=ep["episode_type"],
            subject=ep["subject"][:120],
            content=ep["content"],
            reasoning=ep.get("reasoning"),
            salience=min(max(int(ep.get("salience", 5)), 1), 10),
            tags=ep.get("tags", []) + ["auto-extracted"],
            product=product,
            project_path=cwd,
        )
        episodes_added += 1

    # Update session with extraction count
    if episodes_added > 0:
        try:
            with connect() as conn:
                conn.execute(
                    "UPDATE sessions SET episodes_extracted = %s "
                    "WHERE project_path = %s ORDER BY started_at DESC LIMIT 1",
                    (episodes_added, cwd),
                )
                conn.commit()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--cwd", required=True)
    args = parser.parse_args()

    extract_episodes(args.transcript, args.product, args.cwd)


if __name__ == "__main__":
    main()
