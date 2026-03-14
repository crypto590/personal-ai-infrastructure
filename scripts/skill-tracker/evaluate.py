#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Skill Tracker - Evaluation Module

Compares skill performance before and after an amendment.
Determines whether to keep or roll back the change.

Usage:
    uv run scripts/skill-tracker/evaluate.py <amendment-id>
    uv run scripts/skill-tracker/evaluate.py <amendment-id> --min-observations 5
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


def evaluate_amendment(amendment_id: int, min_observations: int = 5) -> dict:
    """
    Compare observations before and after an amendment.

    Returns evaluation result with verdict.
    """
    conn_str = get_connection_string()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Get amendment details
            cur.execute("SELECT * FROM amendments WHERE id = %s", (amendment_id,))
            amendment = cur.fetchone()

            if not amendment:
                return {"error": f"Amendment #{amendment_id} not found"}

            if amendment["status"] not in ("applied", "approved"):
                return {
                    "error": f"Amendment #{amendment_id} has status '{amendment['status']}' — must be 'applied' to evaluate"
                }

            skill_name = amendment["skill_name"]
            from_version = amendment["from_version"]
            to_version = amendment["to_version"]
            applied_at = amendment["applied_at"]

            # Observations BEFORE amendment (previous version)
            cur.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE outcome = 'success') as successes,
                    COUNT(*) FILTER (WHERE outcome IN ('failure', 'partial_failure')) as failures,
                    ARRAY_AGG(DISTINCT error_type) FILTER (WHERE error_type IS NOT NULL) as error_types
                FROM observations
                WHERE skill_name = %s AND skill_version = %s
                """,
                (skill_name, from_version),
            )
            before = cur.fetchone()

            # Observations AFTER amendment (new version)
            cur.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE outcome = 'success') as successes,
                    COUNT(*) FILTER (WHERE outcome IN ('failure', 'partial_failure')) as failures,
                    ARRAY_AGG(DISTINCT error_type) FILTER (WHERE error_type IS NOT NULL) as error_types
                FROM observations
                WHERE skill_name = %s AND skill_version = %s
                """,
                (skill_name, to_version),
            )
            after = cur.fetchone()

            # Determine verdict
            before_total = before["total"]
            after_total = after["total"]

            if after_total < min_observations:
                verdict = "insufficient_data"
                notes = f"Only {after_total}/{min_observations} observations after amendment. Need more data."
            else:
                before_rate = before["successes"] / before_total if before_total > 0 else 0
                after_rate = after["successes"] / after_total if after_total > 0 else 0

                # Check for new error types introduced
                before_errors = set(before["error_types"] or [])
                after_errors = set(after["error_types"] or [])
                new_errors = list(after_errors - before_errors)

                if after_rate > before_rate + 0.05:
                    verdict = "improved"
                    notes = f"Success rate improved from {before_rate:.1%} to {after_rate:.1%}"
                elif after_rate < before_rate - 0.05:
                    verdict = "degraded"
                    notes = f"Success rate dropped from {before_rate:.1%} to {after_rate:.1%}"
                elif new_errors:
                    verdict = "degraded"
                    notes = f"New error types introduced: {new_errors}"
                else:
                    verdict = "neutral"
                    notes = f"Success rate unchanged ({before_rate:.1%} → {after_rate:.1%})"

            before_rate = before["successes"] / before_total if before_total > 0 else None
            after_rate = after["successes"] / after_total if after_total > 0 else None

            # Check for new error types
            before_errors = set(before["error_types"] or [])
            after_errors = set(after["error_types"] or [])
            new_errors = list(after_errors - before_errors)

            # Record evaluation
            cur.execute(
                """
                INSERT INTO evaluations (
                    amendment_id, skill_name,
                    observations_before, observations_after,
                    success_rate_before, success_rate_after,
                    new_error_types, verdict, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                RETURNING id
                """,
                (
                    amendment_id,
                    skill_name,
                    before_total,
                    after_total,
                    before_rate,
                    after_rate,
                    json.dumps(new_errors),
                    verdict,
                    notes,
                ),
            )
            eval_id = cur.fetchone()["id"]

        conn.commit()

    return {
        "evaluation_id": eval_id,
        "amendment_id": amendment_id,
        "skill_name": skill_name,
        "verdict": verdict,
        "notes": notes,
        "before": {
            "version": from_version,
            "observations": before_total,
            "success_rate": round(before_rate, 3) if before_rate is not None else None,
            "error_types": list(before_errors),
        },
        "after": {
            "version": to_version,
            "observations": after_total,
            "success_rate": round(after_rate, 3) if after_rate is not None else None,
            "error_types": list(after_errors),
            "new_error_types": new_errors,
        },
    }


def rollback_amendment(amendment_id: int) -> dict:
    """Roll back an amendment — restore previous skill version."""
    conn_str = get_connection_string()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM amendments WHERE id = %s", (amendment_id,))
            amendment = cur.fetchone()

            if not amendment:
                return {"error": f"Amendment #{amendment_id} not found"}

            if amendment["status"] != "applied":
                return {"error": f"Can only roll back 'applied' amendments (current: '{amendment['status']}')"}

            skill_name = amendment["skill_name"]
            from_version = amendment["from_version"]

            # Restore skill version
            cur.execute(
                "UPDATE skills SET current_version = %s, updated_at = NOW() WHERE name = %s",
                (from_version, skill_name),
            )

            # Mark amendment as rolled back
            cur.execute(
                "UPDATE amendments SET status = 'rolled_back', rolled_back_at = NOW() WHERE id = %s",
                (amendment_id,),
            )

        conn.commit()

    return {
        "rolled_back": True,
        "amendment_id": amendment_id,
        "skill_name": skill_name,
        "restored_version": from_version,
        "message": f"Rolled back to version {from_version}. Original SKILL.md content is stored in the amendment record.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate skill amendment effectiveness")
    parser.add_argument("amendment_id", type=int, help="Amendment ID to evaluate")
    parser.add_argument("--min-observations", type=int, default=5, help="Minimum observations needed (default: 5)")
    parser.add_argument("--rollback", action="store_true", help="Roll back this amendment")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.rollback:
        result = rollback_amendment(args.amendment_id)
    else:
        result = evaluate_amendment(args.amendment_id, args.min_observations)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

        if args.rollback:
            print(f"Rolled back amendment #{result['amendment_id']}")
            print(f"Skill '{result['skill_name']}' restored to version {result['restored_version']}")
        else:
            print(f"# Evaluation: Amendment #{result['amendment_id']}")
            print(f"Skill: {result['skill_name']}")
            print(f"Verdict: **{result['verdict'].upper()}**")
            print(f"Notes: {result['notes']}")
            print()
            b = result["before"]
            a = result["after"]
            print(f"Before (v{b['version']}): {b['observations']} runs, {b['success_rate']:.1%} success" if b["success_rate"] is not None else f"Before (v{b['version']}): {b['observations']} runs")
            print(f"After  (v{a['version']}): {a['observations']} runs, {a['success_rate']:.1%} success" if a["success_rate"] is not None else f"After  (v{a['version']}): {a['observations']} runs")
            if a["new_error_types"]:
                print(f"New errors: {a['new_error_types']}")
