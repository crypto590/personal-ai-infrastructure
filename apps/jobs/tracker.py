# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pyyaml>=6.0",
# ]
# ///
"""
PAI Job Tracker — Track agent job status via YAML files.

Usage:
    uv run tracker.py create "Research auth best practices"
    uv run tracker.py list
    uv run tracker.py list --status running
    uv run tracker.py get <job-id>
    uv run tracker.py update <job-id> --status running
    uv run tracker.py complete <job-id> --summary "Found 3 viable approaches"
    uv run tracker.py fail <job-id> --summary "Timed out after 5 minutes"
"""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import click
import yaml

JOBS_DIR = Path.home() / ".claude" / "jobs"


def ensure_jobs_dir():
    """Create the jobs directory if it doesn't exist."""
    JOBS_DIR.mkdir(parents=True, exist_ok=True)


def generate_id() -> str:
    """Generate a short, readable job ID."""
    return datetime.now(timezone.utc).strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6]


def load_job(job_id: str) -> dict | None:
    """Load a job by ID."""
    job_file = JOBS_DIR / f"{job_id}.yaml"
    if not job_file.exists():
        return None
    with open(job_file) as f:
        return yaml.safe_load(f)


def save_job(job: dict):
    """Save a job to its YAML file."""
    ensure_jobs_dir()
    job_file = JOBS_DIR / f"{job['id']}.yaml"
    with open(job_file, "w") as f:
        yaml.dump(job, f, default_flow_style=False, sort_keys=False)


def now_iso() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


@click.group()
def cli():
    """PAI Job Tracker — Manage agent job status."""
    pass


@cli.command()
@click.argument("prompt")
@click.option("--status", default="pending", help="Initial status (default: pending)")
def create(prompt: str, status: str):
    """Create a new job with the given prompt."""
    job_id = generate_id()
    job = {
        "id": job_id,
        "status": status,
        "prompt": prompt,
        "summary": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    save_job(job)
    click.echo(f"Created job: {job_id}")
    click.echo(f"  Status: {status}")
    click.echo(f"  Prompt: {prompt}")
    click.echo(f"  File:   {JOBS_DIR / f'{job_id}.yaml'}")


@cli.command()
@click.argument("job_id")
def get(job_id: str):
    """Get details of a job by ID."""
    job = load_job(job_id)
    if not job:
        click.echo(f"Job not found: {job_id}", err=True)
        raise SystemExit(1)
    click.echo(yaml.dump(job, default_flow_style=False, sort_keys=False).strip())


@cli.command(name="list")
@click.option("--status", default=None, help="Filter by status")
@click.option("--limit", default=20, help="Max jobs to show (default: 20)")
def list_jobs(status: str | None, limit: int):
    """List all jobs, optionally filtered by status."""
    ensure_jobs_dir()
    jobs = []
    for f in sorted(JOBS_DIR.glob("*.yaml"), reverse=True):
        job = yaml.safe_load(f.open())
        if job and (status is None or job.get("status") == status):
            jobs.append(job)
        if len(jobs) >= limit:
            break

    if not jobs:
        click.echo("No jobs found.")
        return

    # Table header
    click.echo(f"{'ID':<20} {'STATUS':<12} {'PROMPT':<50}")
    click.echo("-" * 82)
    for job in jobs:
        prompt_short = job.get("prompt", "")[:48]
        click.echo(f"{job['id']:<20} {job.get('status', '?'):<12} {prompt_short}")

    click.echo(f"\nTotal: {len(jobs)} job(s)")


@cli.command()
@click.argument("job_id")
@click.option("--status", required=True, type=click.Choice(["pending", "running", "completed", "failed", "stopped"]))
@click.option("--summary", default=None, help="Optional summary update")
def update(job_id: str, status: str, summary: str | None):
    """Update a job's status."""
    job = load_job(job_id)
    if not job:
        click.echo(f"Job not found: {job_id}", err=True)
        raise SystemExit(1)

    job["status"] = status
    job["updated_at"] = now_iso()
    if summary is not None:
        job["summary"] = summary

    save_job(job)
    click.echo(f"Updated job {job_id}: status={status}")


@cli.command()
@click.argument("job_id")
@click.option("--summary", required=True, help="Completion summary")
def complete(job_id: str, summary: str):
    """Mark a job as completed with a summary."""
    job = load_job(job_id)
    if not job:
        click.echo(f"Job not found: {job_id}", err=True)
        raise SystemExit(1)

    job["status"] = "completed"
    job["summary"] = summary
    job["updated_at"] = now_iso()

    save_job(job)
    click.echo(f"Completed job {job_id}")
    click.echo(f"  Summary: {summary}")


@cli.command()
@click.argument("job_id")
@click.option("--summary", required=True, help="Failure reason")
def fail(job_id: str, summary: str):
    """Mark a job as failed with a reason."""
    job = load_job(job_id)
    if not job:
        click.echo(f"Job not found: {job_id}", err=True)
        raise SystemExit(1)

    job["status"] = "failed"
    job["summary"] = summary
    job["updated_at"] = now_iso()

    save_job(job)
    click.echo(f"Failed job {job_id}")
    click.echo(f"  Reason: {summary}")


if __name__ == "__main__":
    cli()
