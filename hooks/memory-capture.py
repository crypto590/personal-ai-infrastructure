#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Memory Capture Hook (Stop)
Logs session activity. Spawns background auto-extraction with guards:
  1. Skip if subagent (agent_id present)
  2. Lockfile prevents concurrent extractions
  3. 5-minute cooldown between extractions per product
"""

import json
import os
import subprocess
import sys
import time
import fcntl
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

LOCK_DIR = Path("/tmp")
COOLDOWN_SECONDS = 300  # 5 minutes


def _can_extract(product: str) -> bool:
    """Check lockfile and cooldown before extraction."""
    lock_path = LOCK_DIR / f".pai-extracting-{product}.lock"
    cooldown_path = LOCK_DIR / f".pai-extract-ts-{product}"

    # Check cooldown
    if cooldown_path.exists():
        try:
            last_ts = float(cooldown_path.read_text().strip())
            if time.time() - last_ts < COOLDOWN_SECONDS:
                return False
        except (ValueError, OSError):
            pass

    # Check lockfile (non-blocking) — don't close the fd, keep lock held
    try:
        lock_fd = open(lock_path, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Intentionally keep lock_fd open — lock is released when process exits
        # Store on module so GC doesn't close it
        _can_extract._lock_fd = lock_fd
    except (IOError, OSError):
        return False

    return True


def _mark_extraction(product: str):
    """Record extraction timestamp for cooldown."""
    cooldown_path = LOCK_DIR / f".pai-extract-ts-{product}"
    try:
        cooldown_path.write_text(str(time.time()))
    except OSError:
        pass


def _spawn_extraction(transcript_path: str, product: str, cwd: str):
    """Spawn background process to extract episodes via claude CLI."""
    extractor_script = Path(__file__).parent / "memory_extract_bg.py"
    if not extractor_script.exists():
        return

    try:
        _mark_extraction(product)
        subprocess.Popen(
            [
                "uv", "run", str(extractor_script),
                "--transcript", transcript_path,
                "--product", product,
                "--cwd", cwd,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    # Guard: skip subagent stops
    if hook_input.get("is_subagent") or hook_input.get("agent_id"):
        print(json.dumps({"continue": True}))
        return

    cwd = hook_input.get("cwd", os.getcwd())
    transcript = hook_input.get("transcript_path", "")

    try:
        from memory_db import connect, detect_product, log_session_end

        product = detect_product(cwd)

        # Find the most recent session for this project
        with connect() as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE project_path = %s "
                "ORDER BY started_at DESC LIMIT 1",
                (cwd,),
            ).fetchone()
            if row:
                log_session_end(row["id"])

        # Background extraction with guards
        if transcript and Path(transcript).exists():
            if _can_extract(product):
                _spawn_extraction(transcript, product, cwd)

    except Exception:
        pass

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
