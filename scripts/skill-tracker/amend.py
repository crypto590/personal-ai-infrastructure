#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Skill Tracker - Amendment Module

Records proposed amendments to skills with evidence and rationale.
Handles applying amendments and version bumping.

Usage:
    uv run scripts/skill-tracker/amend.py \
        --skill "code-review" \
        --type "fix_tool_call" \
        --rationale "SwiftLint path fails in Mint projects" \
        --evidence "[101, 103, 105]" \
        --original-file "~/.claude/skills/technical/code-review/SKILL.md"

    uv run scripts/skill-tracker/amend.py --apply <amendment-id>
    uv run scripts/skill-tracker/amend.py --list <skill-name>
"""

import argparse
import json
import os
import sys
from pathlib import Path

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
    print("ERROR: NEON_DATABASE_URL not set.", file=sys.stderr)
    sys.exit(1)


def propose_amendment(
    skill_name: str,
    change_type: str,
    rationale: str,
    evidence: list[int] = None,
    original_file: str = None,
    amended_content: str = None,
    diff_summary: str = None,
) -> dict:
    """Record a proposed amendment."""
    conn_str = get_connection_string()

    # Read original skill content if file path provided
    original_content = None
    if original_file:
        path = Path(original_file).expanduser()
        if path.exists():
            original_content = path.read_text()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Get current version
            cur.execute("SELECT current_version FROM skills WHERE name = %s", (skill_name,))
            row = cur.fetchone()
            if not row:
                return {"error": f"Skill '{skill_name}' not found in database"}

            from_version = row["current_version"]
            to_version = from_version + 1

            cur.execute(
                """
                INSERT INTO amendments (
                    skill_name, from_version, to_version, change_type,
                    rationale, evidence, diff_summary,
                    original_content, amended_content, status
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, 'proposed')
                RETURNING id
                """,
                (
                    skill_name,
                    from_version,
                    to_version,
                    change_type,
                    rationale,
                    json.dumps(evidence or []),
                    diff_summary,
                    original_content,
                    amended_content,
                ),
            )
            amendment_id = cur.fetchone()["id"]

        conn.commit()

    return {
        "amendment_id": amendment_id,
        "skill_name": skill_name,
        "from_version": from_version,
        "to_version": to_version,
        "status": "proposed",
        "message": f"Amendment #{amendment_id} proposed. Review and apply with: --apply {amendment_id}",
    }


def apply_amendment(amendment_id: int) -> dict:
    """Apply a proposed amendment — bump skill version."""
    conn_str = get_connection_string()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM amendments WHERE id = %s", (amendment_id,))
            amendment = cur.fetchone()

            if not amendment:
                return {"error": f"Amendment #{amendment_id} not found"}

            if amendment["status"] != "proposed":
                return {"error": f"Amendment #{amendment_id} has status '{amendment['status']}' — can only apply 'proposed'"}

            # Bump skill version
            cur.execute(
                "UPDATE skills SET current_version = %s, updated_at = NOW() WHERE name = %s",
                (amendment["to_version"], amendment["skill_name"]),
            )

            # Mark as applied
            cur.execute(
                "UPDATE amendments SET status = 'applied', applied_at = NOW() WHERE id = %s",
                (amendment_id,),
            )

        conn.commit()

    return {
        "applied": True,
        "amendment_id": amendment_id,
        "skill_name": amendment["skill_name"],
        "new_version": amendment["to_version"],
        "message": (
            f"Amendment #{amendment_id} applied. "
            f"Skill '{amendment['skill_name']}' is now version {amendment['to_version']}. "
            f"Run /evaluate-skill {amendment_id} after ~5 more executions to verify improvement."
        ),
    }


def list_amendments(skill_name: str) -> list[dict]:
    """List all amendments for a skill."""
    conn_str = get_connection_string()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, from_version, to_version, change_type,
                       rationale, status, created_at, applied_at, rolled_back_at
                FROM amendments
                WHERE skill_name = %s
                ORDER BY created_at DESC
                """,
                (skill_name,),
            )
            return [dict(r) for r in cur.fetchall()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage skill amendments")
    parser.add_argument("--skill", help="Skill name")
    parser.add_argument("--type", dest="change_type",
                       choices=["tighten_trigger", "add_condition", "reorder_steps",
                               "change_format", "fix_tool_call", "rewrite", "other"])
    parser.add_argument("--rationale", help="Why this change is needed")
    parser.add_argument("--evidence", help="JSON array of observation IDs")
    parser.add_argument("--original-file", help="Path to current SKILL.md")
    parser.add_argument("--diff-summary", help="Human-readable summary of changes")
    parser.add_argument("--apply", type=int, metavar="ID", help="Apply a proposed amendment")
    parser.add_argument("--list", metavar="SKILL", help="List amendments for a skill")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.apply:
        result = apply_amendment(args.apply)
    elif args.list:
        result = list_amendments(args.list)
    elif args.skill and args.change_type and args.rationale:
        evidence = json.loads(args.evidence) if args.evidence else []
        result = propose_amendment(
            skill_name=args.skill,
            change_type=args.change_type,
            rationale=args.rationale,
            evidence=evidence,
            original_file=args.original_file,
            diff_summary=args.diff_summary,
        )
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if isinstance(result, list):
            print(f"# Amendments for '{args.list}'")
            print()
            for a in result:
                status_icon = {"proposed": "?", "applied": "+", "rolled_back": "!", "rejected": "x"}.get(a["status"], " ")
                print(f"  [{status_icon}] #{a['id']}: v{a['from_version']}→v{a['to_version']} ({a['change_type']}) — {a['status']}")
                print(f"      {a['rationale'][:80]}")
                print(f"      Created: {a['created_at']}")
                print()
        elif "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print(result.get("message", json.dumps(result, indent=2, default=str)))
