#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Unified Memory Database Layer (Neon Postgres + Full-Text Search)

Shared module imported by hooks and executed by skills.
All memory CRUD, search, product detection, and formatting lives here.
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import psycopg
from psycopg.rows import dict_row


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _get_database_url() -> str:
    """Get database URL from env or .env file."""
    url = os.environ.get("MEMORY_DATABASE_URL")
    if url:
        return url
    # Fallback: read from ~/.claude/.env
    env_file = Path.home() / ".claude" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("MEMORY_DATABASE_URL="):
                val = line.split("=", 1)[1].strip().strip("'\"")
                if val:
                    return val
    raise RuntimeError("MEMORY_DATABASE_URL not set. Add it to ~/.claude/.env")


def connect() -> psycopg.Connection:
    """Return a connection with dict row factory. Caller must close."""
    url = _get_database_url()
    # Remove channel_binding param if present (not supported by all drivers)
    if "channel_binding" in url:
        parts = url.split("?", 1)
        if len(parts) == 2:
            params = [p for p in parts[1].split("&") if not p.startswith("channel_binding")]
            url = parts[0] + ("?" + "&".join(params) if params else "")
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
-- Core episodes table
CREATE TABLE IF NOT EXISTS episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product TEXT,
    project_path TEXT,
    agent_type TEXT DEFAULT 'alex',
    episode_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    reasoning TEXT,
    salience INTEGER NOT NULL DEFAULT 5,
    tags TEXT[] DEFAULT '{}',
    search_vector tsvector,
    superseded_by UUID REFERENCES episodes(id),
    verified_at TIMESTAMPTZ,
    signal_type TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Full-text search trigger
CREATE OR REPLACE FUNCTION episodes_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.subject, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.reasoning, '')), 'C') ||
        setweight(to_tsvector('english', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER episodes_search_update
        BEFORE INSERT OR UPDATE ON episodes
        FOR EACH ROW
        EXECUTE FUNCTION episodes_search_trigger();
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_episodes_product ON episodes(product);
CREATE INDEX IF NOT EXISTS idx_episodes_type ON episodes(episode_type);
CREATE INDEX IF NOT EXISTS idx_episodes_salience ON episodes(salience);
CREATE INDEX IF NOT EXISTS idx_episodes_created ON episodes(created_at);
CREATE INDEX IF NOT EXISTS idx_episodes_tags ON episodes USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_episodes_search ON episodes USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_episodes_active ON episodes(product, salience)
    WHERE superseded_by IS NULL;

-- Product registry
CREATE TABLE IF NOT EXISTS products (
    path_prefix TEXT PRIMARY KEY,
    product TEXT NOT NULL,
    display_name TEXT
);

-- Session tracking
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    product TEXT,
    project_path TEXT NOT NULL,
    started_at TIMESTAMPTZ DEFAULT now(),
    ended_at TIMESTAMPTZ,
    episodes_extracted INTEGER DEFAULT 0
);

-- Safe migration: add signal_type column if missing
DO $$ BEGIN
    ALTER TABLE episodes ADD COLUMN signal_type TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;
"""


def init_db():
    """Create tables, indexes, and triggers."""
    with connect() as conn:
        conn.execute(SCHEMA_SQL)
        conn.commit()


# ---------------------------------------------------------------------------
# Product Detection
# ---------------------------------------------------------------------------

# Known product prefixes (seeded at migration, editable via /memory add-product)
_BUILTIN_PRODUCTS = {
    "/Users/coreyyoung/Desktop/Projects/athlead": ("athlead", "Athlead"),
    "/Users/coreyyoung/Desktop/Projects/athlead-android": ("athlead", "Athlead"),
    "/Users/coreyyoung/Desktop/Projects/crewos": ("crewos", "CrewOS"),
    "/Users/coreyyoung/.claude": ("pai", "Personal AI Infrastructure"),
}


def detect_product(cwd: str, conn: Optional[psycopg.Connection] = None) -> str:
    """Map a directory path to a product name.

    Priority: DB products table -> builtin prefixes -> basename fallback.
    """
    # 1. Check DB products table
    if conn:
        row = conn.execute(
            "SELECT product FROM products WHERE %s LIKE path_prefix || '%%' "
            "ORDER BY length(path_prefix) DESC LIMIT 1",
            (cwd,),
        ).fetchone()
        if row:
            return row["product"]

    # 2. Check builtin prefixes (longest match first)
    for prefix in sorted(_BUILTIN_PRODUCTS, key=len, reverse=True):
        if cwd.startswith(prefix):
            return _BUILTIN_PRODUCTS[prefix][0]

    # 3. Fallback to directory basename
    return Path(cwd).name or "unknown"


def register_product(path_prefix: str, product: str, display_name: Optional[str] = None):
    """Register a product mapping in the DB."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO products (path_prefix, product, display_name) "
            "VALUES (%s, %s, %s) ON CONFLICT (path_prefix) DO UPDATE "
            "SET product = EXCLUDED.product, display_name = EXCLUDED.display_name",
            (path_prefix, product, display_name),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Write Operations
# ---------------------------------------------------------------------------

def add_episode(
    episode_type: str,
    subject: str,
    content: str,
    reasoning: Optional[str] = None,
    salience: int = 5,
    tags: Optional[list[str]] = None,
    product: Optional[str] = None,
    project_path: Optional[str] = None,
    agent_type: str = "alex",
    signal_type: Optional[str] = None,
) -> str:
    """Insert a new episode. Returns the episode UUID."""
    episode_id = str(uuid.uuid4())
    with connect() as conn:
        if not product and project_path:
            product = detect_product(project_path, conn)
        conn.execute(
            """INSERT INTO episodes
               (id, product, project_path, agent_type, episode_type,
                subject, content, reasoning, salience, tags, signal_type)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (episode_id, product, project_path, agent_type, episode_type,
             subject, content, reasoning, salience, tags or [], signal_type),
        )
        conn.commit()
    return episode_id


def supersede(old_id: str, new_episode: dict) -> str:
    """Mark old episode as superseded and create replacement. Returns new UUID."""
    new_id = add_episode(**new_episode)
    with connect() as conn:
        conn.execute(
            "UPDATE episodes SET superseded_by = %s, updated_at = now() WHERE id = %s",
            (new_id, old_id),
        )
        conn.commit()
    return new_id


def soft_delete(episode_id: str):
    """Supersede an episode without replacement (marks it inactive)."""
    with connect() as conn:
        row = conn.execute(
            "SELECT product, project_path FROM episodes WHERE id = %s", (episode_id,)
        ).fetchone()
        if not row:
            return
        tombstone_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO episodes
               (id, product, project_path, episode_type, subject, content, salience)
               VALUES (%s, %s, %s, 'tombstone', 'deleted', 'Superseded by user request', 0)""",
            (tombstone_id, row["product"], row["project_path"]),
        )
        conn.execute(
            "UPDATE episodes SET superseded_by = %s, updated_at = now() WHERE id = %s",
            (tombstone_id, episode_id),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Signal/Rating Capture
# ---------------------------------------------------------------------------

def record_signal(
    session_id: int,
    sentiment: str,
    prompt_snippet: str,
    product: Optional[str] = None,
    project_path: Optional[str] = None,
):
    """Record a positive/negative feedback signal as an episode."""
    salience = 7 if sentiment == "positive" else 6
    add_episode(
        episode_type="signal",
        subject=f"User signal: {sentiment}",
        content=prompt_snippet[:200],
        reasoning=f"Explicit {sentiment} feedback detected in prompt",
        salience=salience,
        tags=["signal", sentiment, "auto-detected"],
        product=product,
        project_path=project_path,
        signal_type=sentiment,
    )


# ---------------------------------------------------------------------------
# Memory Decay
# ---------------------------------------------------------------------------

def decay_stale(days: int = 90, min_salience: int = 5):
    """Soft-delete old, low-salience, low-access episodes.

    Episodes with salience >= 8 never decay (permanent decisions/preferences).
    """
    with connect() as conn:
        # Find stale episodes: old, low salience, not recently accessed
        rows = conn.execute(
            """SELECT id FROM episodes
               WHERE superseded_by IS NULL
                 AND episode_type != 'tombstone'
                 AND salience < %s
                 AND updated_at < now() - interval '%s days'
               ORDER BY salience ASC, updated_at ASC
               LIMIT 50""",
            (min_salience, days),
        ).fetchall()

        decayed = 0
        for row in rows:
            soft_delete(row["id"])
            decayed += 1

        return decayed


def touch_episode(episode_id: str):
    """Update updated_at when an episode is loaded into context (tracks access)."""
    try:
        with connect() as conn:
            conn.execute(
                "UPDATE episodes SET updated_at = now() WHERE id = %s",
                (episode_id,),
            )
            conn.commit()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Read Operations
# ---------------------------------------------------------------------------

_ACTIVE_FILTER = "superseded_by IS NULL AND episode_type != 'tombstone'"


def search_text(
    query: str,
    product: Optional[str] = None,
    episode_type: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """Full-text search with ts_rank scoring."""
    tsquery = " & ".join(query.strip().split())
    conditions = [_ACTIVE_FILTER, "search_vector @@ to_tsquery('english', %s)"]
    params: list = [tsquery]

    if product:
        conditions.append("product = %s")
        params.append(product)
    if episode_type:
        conditions.append("episode_type = %s")
        params.append(episode_type)

    params.append(limit)
    where = " AND ".join(conditions)

    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at,
                       ts_rank(search_vector, to_tsquery('english', %s)) AS rank
                FROM episodes
                WHERE {where}
                ORDER BY rank DESC, salience DESC
                LIMIT %s""",
            [tsquery] + params,
        ).fetchall()


def get_by_product(product: str, limit: int = 50) -> list[dict]:
    """All active episodes for a product, ordered by salience then recency."""
    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes
                WHERE {_ACTIVE_FILTER} AND product = %s
                ORDER BY salience DESC, created_at DESC
                LIMIT %s""",
            (product, limit),
        ).fetchall()


def get_hot(min_salience: int = 8, limit: int = 20) -> list[dict]:
    """Cross-project high-value episodes."""
    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes
                WHERE {_ACTIVE_FILTER} AND salience >= %s
                ORDER BY salience DESC, created_at DESC
                LIMIT %s""",
            (min_salience, limit),
        ).fetchall()


def get_preferences(limit: int = 20) -> list[dict]:
    """All active preference episodes across projects."""
    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes
                WHERE {_ACTIVE_FILTER} AND episode_type = 'preference'
                ORDER BY salience DESC, created_at DESC
                LIMIT %s""",
            (limit,),
        ).fetchall()


def get_decisions(product: Optional[str] = None, limit: int = 20) -> list[dict]:
    """Decisions with rationale."""
    conditions = [_ACTIVE_FILTER, "episode_type = 'decision'"]
    params: list = []
    if product:
        conditions.append("product = %s")
        params.append(product)
    params.append(limit)
    where = " AND ".join(conditions)

    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes
                WHERE {where}
                ORDER BY salience DESC, created_at DESC
                LIMIT %s""",
            params,
        ).fetchall()


def get_all_grouped(limit_per_product: int = 30) -> dict[str, list[dict]]:
    """All active episodes grouped by product."""
    with connect() as conn:
        rows = conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes
                WHERE {_ACTIVE_FILTER}
                ORDER BY product, salience DESC, created_at DESC"""
        ).fetchall()

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        p = row["product"] or "unknown"
        if p not in grouped:
            grouped[p] = []
        if len(grouped[p]) < limit_per_product:
            grouped[p].append(row)
    return grouped


def get_stats() -> dict:
    """Counts by product, type, and salience buckets."""
    with connect() as conn:
        total = conn.execute(
            f"SELECT count(*) as n FROM episodes WHERE {_ACTIVE_FILTER}"
        ).fetchone()["n"]

        by_product = conn.execute(
            f"""SELECT product, count(*) as n FROM episodes
                WHERE {_ACTIVE_FILTER} GROUP BY product ORDER BY n DESC"""
        ).fetchall()

        by_type = conn.execute(
            f"""SELECT episode_type, count(*) as n FROM episodes
                WHERE {_ACTIVE_FILTER} GROUP BY episode_type ORDER BY n DESC"""
        ).fetchall()

        by_salience = conn.execute(
            f"""SELECT
                    CASE WHEN salience >= 8 THEN 'hot (8-10)'
                         WHEN salience >= 5 THEN 'warm (5-7)'
                         ELSE 'cold (1-4)' END as tier,
                    count(*) as n
                FROM episodes WHERE {_ACTIVE_FILTER}
                GROUP BY tier ORDER BY tier"""
        ).fetchall()

        session_count = conn.execute("SELECT count(*) as n FROM sessions").fetchone()["n"]

    return {
        "total_episodes": total,
        "by_product": {r["product"]: r["n"] for r in by_product},
        "by_type": {r["episode_type"]: r["n"] for r in by_type},
        "by_salience": {r["tier"]: r["n"] for r in by_salience},
        "total_sessions": session_count,
    }


def find_matching(query: str, product: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Find episodes matching a query -- tries FTS first, falls back to ILIKE."""
    results = search_text(query, product=product, limit=limit)
    if results:
        return results

    # Fallback: substring match
    conditions = [_ACTIVE_FILTER, "(subject ILIKE %s OR content ILIKE %s)"]
    pattern = f"%{query}%"
    params: list = [pattern, pattern]
    if product:
        conditions.append("product = %s")
        params.append(product)
    params.append(limit)
    where = " AND ".join(conditions)

    with connect() as conn:
        return conn.execute(
            f"""SELECT id, product, episode_type, subject, content, reasoning,
                       salience, tags, created_at
                FROM episodes WHERE {where}
                ORDER BY salience DESC, created_at DESC
                LIMIT %s""",
            params,
        ).fetchall()


# ---------------------------------------------------------------------------
# Session Tracking
# ---------------------------------------------------------------------------

def log_session_start(product: str, project_path: str) -> int:
    """Log a new session, return session ID."""
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO sessions (product, project_path) VALUES (%s, %s) RETURNING id",
            (product, project_path),
        ).fetchone()
        conn.commit()
        return row["id"]


def log_session_end(session_id: int, episodes_extracted: int = 0):
    """Mark session as ended."""
    with connect() as conn:
        conn.execute(
            "UPDATE sessions SET ended_at = now(), episodes_extracted = %s WHERE id = %s",
            (episodes_extracted, session_id),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Formatting for Context Injection
# ---------------------------------------------------------------------------

def format_for_injection(episodes: list[dict], budget_chars: int = 1200) -> str:
    """Format episodes as token-budgeted markdown for session injection."""
    if not episodes:
        return ""

    lines: list[str] = []
    char_count = 0

    for i, ep in enumerate(episodes):
        etype = ep.get("episode_type", "")
        subject = ep.get("subject", "")
        content = ep.get("content", "")
        reasoning = ep.get("reasoning", "")
        product = ep.get("product", "")

        # Compact format: [type] subject: content (reason)
        line = f"[{etype}] {subject}: {content}"
        if reasoning:
            line += f" (Why: {reasoning})"
        if product:
            line = f"({product}) {line}"

        # Truncate long lines to fit budget (keep at least first episode)
        if char_count + len(line) + 1 > budget_chars:
            if i == 0:
                lines.append(line[:budget_chars])
            break
        lines.append(line)
        char_count += len(line) + 1

    return "\n".join(lines)


def format_episode_display(ep: dict) -> str:
    """Format a single episode for human display."""
    etype = ep.get("episode_type", "unknown")
    subject = ep.get("subject", "")
    content = ep.get("content", "")
    reasoning = ep.get("reasoning", "")
    salience = ep.get("salience", 5)
    product = ep.get("product", "")
    tags = ep.get("tags", [])
    created = ep.get("created_at", "")

    lines = [
        f"**{subject}**",
        f"  Type: {etype} | Salience: {salience}/10 | Product: {product}",
        f"  {content}",
    ]
    if reasoning:
        lines.append(f"  Why: {reasoning}")
    if tags:
        lines.append(f"  Tags: {', '.join(tags)}")
    if created:
        ts = created if isinstance(created, str) else created.isoformat()
        lines.append(f"  Created: {ts[:10]}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI for direct testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("Initializing database schema...")
        init_db()
        print("Done. Tables and indexes created.")

        # Seed known products
        for prefix, (prod, display) in _BUILTIN_PRODUCTS.items():
            register_product(prefix, prod, display)
        print(f"Seeded {len(_BUILTIN_PRODUCTS)} product mappings.")

    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2, default=str))

    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Testing connection...")
        with connect() as conn:
            row = conn.execute("SELECT 1 as ok").fetchone()
            print(f"Connection OK: {row}")

    elif len(sys.argv) > 1 and sys.argv[1] == "decay":
        n = decay_stale()
        print(f"Decayed {n} stale episodes.")

    else:
        print("Usage: memory_db.py [init|stats|test|decay]")
