#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Memory Restore Hook (SessionStart)

Loads context ONCE at session start (not per-prompt):
  1. Full CORE skill identity (~2300 tokens, one-time)
  2. Hot memory: high-salience (8+) + preferences -- cross-project
  3. Warm memory: product-specific episodes for current project

Touches loaded episodes to track access (prevents decay).
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

CORE_SKILL = Path.home() / ".claude" / "skills" / "core" / "SKILL.md"


def load_core_identity() -> str:
    """Load the full CORE skill for one-time session injection."""
    if not CORE_SKILL.exists():
        alt = Path.home() / ".claude" / "skills" / "CORE" / "SKILL.md"
        if alt.exists():
            return alt.read_text()
        return ""
    return CORE_SKILL.read_text()


def touch_loaded_episodes(episodes: list[dict]):
    """Update updated_at for loaded episodes to track access."""
    try:
        from memory_db import touch_episode
        for ep in episodes:
            eid = ep.get("id")
            if eid:
                touch_episode(str(eid))
    except Exception:
        pass


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    cwd = hook_input.get("cwd", os.getcwd())

    try:
        from memory_db import (
            connect, detect_product, get_hot, get_preferences,
            get_by_product, format_for_injection, log_session_start,
        )

        with connect() as conn:
            product = detect_product(cwd, conn)

        # Log session start
        session_id = log_session_start(product, cwd)

        # --- 1. CORE Identity (one-time) ---
        core_identity = load_core_identity()

        # --- 2. Hot tier: high-salience globals + preferences (~400 chars) ---
        hot_episodes = get_hot(min_salience=8, limit=10)
        prefs = get_preferences(limit=10)

        # Deduplicate (preferences might overlap with hot)
        hot_ids = {str(ep["id"]) for ep in hot_episodes}
        prefs = [p for p in prefs if str(p["id"]) not in hot_ids]

        all_hot = hot_episodes + prefs
        hot_text = format_for_injection(all_hot, budget_chars=600)

        # --- 3. Warm tier: product-specific episodes (~600 chars) ---
        warm_episodes = get_by_product(product, limit=20)
        warm_episodes = [e for e in warm_episodes if str(e["id"]) not in hot_ids]
        warm_text = format_for_injection(warm_episodes, budget_chars=600)

        # Touch loaded episodes to track access (prevents decay)
        touch_loaded_episodes(all_hot + warm_episodes)

        # Build context block
        lines = []

        if core_identity:
            lines.append(core_identity)
            lines.append("")

        lines.append("<memory-context>")
        lines.append(f"Product: {product} | Session: {session_id}")

        if hot_text:
            lines.append("")
            lines.append("Global Memory:")
            lines.append(hot_text)

        if warm_text:
            lines.append("")
            lines.append(f"{product.title()} Memory:")
            lines.append(warm_text)

        if not hot_text and not warm_text:
            lines.append("No memories loaded. Use /remember to save memories.")

        lines.append("</memory-context>")
        context = "\n".join(lines)

        result = {
            "continue": True,
            "output": context,
        }

    except Exception:
        core_identity = load_core_identity()
        if core_identity:
            result = {"continue": True, "output": core_identity}
        else:
            result = {"continue": True}

    print(json.dumps(result))


if __name__ == "__main__":
    main()
