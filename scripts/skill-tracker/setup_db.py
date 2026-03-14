#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Skill Tracker - Database Setup

Run once to create tables and views in your Neon database.
Idempotent — safe to run multiple times.

Usage:
    NEON_DATABASE_URL="postgresql://..." uv run scripts/skill-tracker/setup_db.py

Or add NEON_DATABASE_URL to ~/.claude/.env
"""

import os
import sys
from pathlib import Path


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

    print("ERROR: NEON_DATABASE_URL not set.", file=sys.stderr)
    print("Set it in your environment or in ~/.claude/.env", file=sys.stderr)
    sys.exit(1)


def main():
    import psycopg

    conn_str = get_connection_string()
    print(f"Connecting to Neon...")

    schema_path = Path(__file__).parent / "schema.sql"
    schema = schema_path.read_text()

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()

    print("Schema applied successfully.")
    print()
    print("Tables created:")
    print("  - skills          (skill registry with embeddings)")
    print("  - observations    (execution records per skill run)")
    print("  - amendments      (proposed/applied skill changes)")
    print("  - evaluations     (before/after comparisons)")
    print()
    print("Views created:")
    print("  - skill_health    (dashboard: success rates, error patterns)")
    print("  - recent_failures (last 50 failures for inspection)")


if __name__ == "__main__":
    main()
