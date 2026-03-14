"""
Skill Tracker - Database Connection Module

Provides connection to Neon Postgres with pgvector for the
skill observation/improvement loop.

Works cross-project: connection string comes from environment,
so any project's hooks can write to the same centralized store.
"""

import os
from contextlib import contextmanager

# psycopg is available when run via `uv run --script` with dependencies
import psycopg
from psycopg.rows import dict_row


def get_connection_string() -> str:
    """
    Get Neon database URL from environment.

    Checks (in order):
    1. NEON_DATABASE_URL env var
    2. ~/.claude/.env file
    """
    url = os.environ.get("NEON_DATABASE_URL")
    if url:
        return url

    # Try loading from ~/.claude/.env
    env_file = os.path.expanduser("~/.claude/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("NEON_DATABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if url:
                        return url

    raise EnvironmentError(
        "NEON_DATABASE_URL not set. Add it to your environment or ~/.claude/.env"
    )


@contextmanager
def get_connection():
    """Context manager for database connections with dict rows."""
    conn = psycopg.connect(get_connection_string(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(query: str, params: tuple = None) -> list[dict]:
    """Execute a query and return results as list of dicts."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            return []


def execute_one(query: str, params: tuple = None) -> dict | None:
    """Execute a query and return a single result."""
    results = execute(query, params)
    return results[0] if results else None
