#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["psycopg[binary]>=3.1"]
# ///

"""
Skill Tracker - Inspection Module

Queries observations for a skill and surfaces patterns in failures.
Used by the /inspect-skill command.

Usage:
    uv run scripts/skill-tracker/inspect.py <skill-name>
    uv run scripts/skill-tracker/inspect.py <skill-name> --days 30
    uv run scripts/skill-tracker/inspect.py --all
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
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


def inspect_skill(skill_name: str, days: int = 30, conn_str: str = None) -> dict:
    """
    Generate an inspection report for a skill.

    Returns a structured report with:
    - Overall health metrics
    - Error pattern analysis
    - Recurring failures
    - Recommendations
    """
    if not conn_str:
        conn_str = get_connection_string()

    since = datetime.now() - timedelta(days=days)

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # Overall metrics
            cur.execute(
                """
                SELECT
                    COUNT(*) as total_runs,
                    COUNT(*) FILTER (WHERE outcome = 'success') as successes,
                    COUNT(*) FILTER (WHERE outcome = 'partial_failure') as partial_failures,
                    COUNT(*) FILTER (WHERE outcome = 'failure') as failures,
                    COUNT(*) FILTER (WHERE outcome = 'unknown') as unknowns,
                    COUNT(DISTINCT project) as projects,
                    AVG(duration_seconds) FILTER (WHERE duration_seconds IS NOT NULL) as avg_duration,
                    MIN(created_at) as first_run,
                    MAX(created_at) as last_run
                FROM observations
                WHERE skill_name = %s AND created_at >= %s
                """,
                (skill_name, since),
            )
            metrics = cur.fetchone()

            # Error type distribution
            cur.execute(
                """
                SELECT
                    error_type,
                    COUNT(*) as count,
                    ARRAY_AGG(DISTINCT error_detail) FILTER (WHERE error_detail IS NOT NULL) as details
                FROM observations
                WHERE skill_name = %s AND created_at >= %s AND error_type IS NOT NULL
                GROUP BY error_type
                ORDER BY count DESC
                """,
                (skill_name, since),
            )
            error_distribution = cur.fetchall()

            # Recent failures with context
            cur.execute(
                """
                SELECT
                    task_summary,
                    outcome,
                    error_type,
                    error_detail,
                    project,
                    agent_name,
                    transcript_ref,
                    created_at
                FROM observations
                WHERE skill_name = %s AND created_at >= %s
                    AND outcome IN ('failure', 'partial_failure')
                ORDER BY created_at DESC
                LIMIT 10
                """,
                (skill_name, since),
            )
            recent_failures = cur.fetchall()

            # Success rate trend (weekly buckets)
            cur.execute(
                """
                SELECT
                    DATE_TRUNC('week', created_at) as week,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE outcome = 'success') as successes,
                    ROUND(
                        COUNT(*) FILTER (WHERE outcome = 'success')::NUMERIC /
                        NULLIF(COUNT(*), 0), 3
                    ) as success_rate
                FROM observations
                WHERE skill_name = %s AND created_at >= %s
                GROUP BY week
                ORDER BY week
                """,
                (skill_name, since),
            )
            trend = cur.fetchall()

            # Skill metadata
            cur.execute("SELECT * FROM skills WHERE name = %s", (skill_name,))
            skill_info = cur.fetchone()

    # Build report
    total = metrics["total_runs"]
    if total == 0:
        return {
            "skill_name": skill_name,
            "status": "no_data",
            "message": f"No observations found for '{skill_name}' in the last {days} days.",
        }

    success_rate = metrics["successes"] / total if total > 0 else 0

    # Determine health status
    if success_rate >= 0.9:
        health = "healthy"
    elif success_rate >= 0.7:
        health = "degraded"
    else:
        health = "failing"

    # Generate recommendations
    recommendations = []
    if error_distribution:
        top_error = error_distribution[0]
        if top_error["error_type"] == "tool_call":
            recommendations.append(
                f"Most failures are tool_call errors ({top_error['count']}/{total} runs). "
                "Check if tool dependencies have changed or paths are outdated in the skill instructions."
            )
        elif top_error["error_type"] == "instruction":
            recommendations.append(
                f"Instruction clarity issues detected ({top_error['count']}/{total} runs). "
                "Consider rewriting ambiguous steps in the SKILL.md."
            )
        elif top_error["error_type"] == "timeout":
            recommendations.append(
                f"Timeout issues ({top_error['count']}/{total} runs). "
                "Consider breaking the skill into smaller steps or increasing time limits."
            )
        elif top_error["error_type"] == "output_quality":
            recommendations.append(
                f"Output quality issues ({top_error['count']}/{total} runs). "
                "Review output format requirements and add explicit examples to the skill."
            )

    if trend and len(trend) >= 2:
        latest_rate = float(trend[-1]["success_rate"]) if trend[-1]["success_rate"] else 0
        prev_rate = float(trend[-2]["success_rate"]) if trend[-2]["success_rate"] else 0
        if latest_rate < prev_rate - 0.1:
            recommendations.append(
                f"Success rate is declining: {prev_rate:.0%} → {latest_rate:.0%}. "
                "Recent environment changes may be breaking this skill."
            )

    if not recommendations:
        if health == "healthy":
            recommendations.append("Skill is performing well. No action needed.")
        else:
            recommendations.append("Review recent failure transcripts for specific issues.")

    report = {
        "skill_name": skill_name,
        "period_days": days,
        "health": health,
        "metrics": {
            "total_runs": total,
            "successes": metrics["successes"],
            "partial_failures": metrics["partial_failures"],
            "failures": metrics["failures"],
            "success_rate": round(success_rate, 3),
            "projects_used_in": metrics["projects"],
            "avg_duration_seconds": round(float(metrics["avg_duration"]), 1) if metrics["avg_duration"] else None,
            "first_run": metrics["first_run"].isoformat() if metrics["first_run"] else None,
            "last_run": metrics["last_run"].isoformat() if metrics["last_run"] else None,
        },
        "error_distribution": [
            {
                "type": e["error_type"],
                "count": e["count"],
                "details": e["details"] or [],
            }
            for e in error_distribution
        ],
        "recent_failures": [
            {
                "task": f["task_summary"][:200] if f["task_summary"] else None,
                "outcome": f["outcome"],
                "error_type": f["error_type"],
                "error_detail": f["error_detail"],
                "project": f["project"],
                "date": f["created_at"].isoformat(),
                "transcript": f["transcript_ref"],
            }
            for f in recent_failures
        ],
        "trend": [
            {
                "week": t["week"].strftime("%Y-%m-%d"),
                "total": t["total"],
                "successes": t["successes"],
                "success_rate": float(t["success_rate"]) if t["success_rate"] else 0,
            }
            for t in trend
        ],
        "recommendations": recommendations,
        "skill_version": skill_info["current_version"] if skill_info else None,
    }

    return report


def inspect_all(days: int = 30) -> list[dict]:
    """Get health summary for all skills."""
    conn_str = get_connection_string()

    with psycopg.connect(conn_str, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM skill_health ORDER BY success_rate ASC NULLS LAST")
            rows = cur.fetchall()

    return [dict(r) for r in rows]


def format_report(report: dict) -> str:
    """Format an inspection report as human-readable text."""
    if report.get("status") == "no_data":
        return report["message"]

    lines = []
    lines.append(f"# Inspection Report: {report['skill_name']}")
    lines.append(f"Period: last {report['period_days']} days | Health: **{report['health'].upper()}**")
    lines.append("")

    m = report["metrics"]
    lines.append("## Metrics")
    lines.append(f"- Runs: {m['total_runs']} ({m['successes']} success, {m['partial_failures']} partial, {m['failures']} failure)")
    lines.append(f"- Success rate: {m['success_rate']:.1%}")
    lines.append(f"- Projects: {m['projects_used_in']}")
    if m["avg_duration_seconds"]:
        lines.append(f"- Avg duration: {m['avg_duration_seconds']}s")
    lines.append(f"- Version: {report['skill_version']}")
    lines.append("")

    if report["error_distribution"]:
        lines.append("## Error Patterns")
        for e in report["error_distribution"]:
            lines.append(f"- **{e['type']}**: {e['count']} occurrences")
            for d in e["details"][:3]:
                lines.append(f"  - {d}")
        lines.append("")

    if report["trend"]:
        lines.append("## Weekly Trend")
        for t in report["trend"]:
            bar = "#" * int(t["success_rate"] * 20)
            lines.append(f"  {t['week']}: {bar} {t['success_rate']:.0%} ({t['total']} runs)")
        lines.append("")

    if report["recent_failures"]:
        lines.append("## Recent Failures")
        for f in report["recent_failures"][:5]:
            lines.append(f"- [{f['date'][:10]}] {f['outcome']} ({f['error_type']})")
            if f["task"]:
                lines.append(f"  Task: {f['task'][:100]}...")
            if f["error_detail"]:
                lines.append(f"  Detail: {f['error_detail']}")
        lines.append("")

    lines.append("## Recommendations")
    for r in report["recommendations"]:
        lines.append(f"- {r}")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect skill health and failure patterns")
    parser.add_argument("skill_name", nargs="?", help="Name of skill to inspect")
    parser.add_argument("--days", type=int, default=30, help="Lookback period in days (default: 30)")
    parser.add_argument("--all", action="store_true", help="Show health summary for all skills")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of formatted text")

    args = parser.parse_args()

    if args.all:
        results = inspect_all(args.days)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("# Skill Health Dashboard")
            print()
            if not results:
                print("No skills with observations found.")
            else:
                print(f"{'Skill':<30} {'Runs':>6} {'Success':>8} {'Failures':>9} {'Rate':>6} {'Top Error':<20}")
                print("-" * 85)
                for r in results:
                    rate = f"{float(r['success_rate']):.0%}" if r.get("success_rate") is not None else "N/A"
                    print(
                        f"{r['name']:<30} {r.get('total_runs', 0):>6} "
                        f"{r.get('successes', 0):>8} {r.get('failures', 0):>9} "
                        f"{rate:>6} {r.get('most_common_error', '-'):<20}"
                    )
    elif args.skill_name:
        report = inspect_skill(args.skill_name, args.days)
        if args.json:
            print(json.dumps(report, indent=2, default=str))
        else:
            print(format_report(report))
    else:
        parser.print_help()
