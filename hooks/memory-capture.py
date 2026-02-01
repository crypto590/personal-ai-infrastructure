#!/usr/bin/env python3
"""
Memory Capture Hook (Stop)
Captures context after each Claude response and persists to memory file.
Syncs to Obsidian for human-readable access.
"""

import json
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

# Directories
MEMORY_DIR = Path.home() / ".claude" / "memory"
PROJECTS_DIR = MEMORY_DIR / "projects"
OBSIDIAN_DIR = Path.home() / "Desktop" / "The_Hub" / "AI-Memory"

def get_project_hash(path: str) -> str:
    """Generate consistent hash for project path."""
    return hashlib.sha256(path.encode()).hexdigest()[:12]

def get_project_name(path: str) -> str:
    """Extract human-readable project name from path."""
    return Path(path).name or "root"

def load_memory(memory_file: Path) -> dict:
    """Load existing memory or create new."""
    if memory_file.exists():
        try:
            with open(memory_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_memory(memory_file: Path, memory: dict):
    """Save memory to JSON file."""
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    with open(memory_file, "w") as f:
        json.dump(memory, f, indent=2, default=str)

def sync_to_obsidian(memory: dict, project_name: str):
    """Sync memory to Obsidian as human-readable markdown."""
    OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)

    # Sanitize project name for filename
    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in project_name)
    obsidian_file = OBSIDIAN_DIR / f"{safe_name}.md"

    # Build markdown content
    lines = [
        f"# {project_name}",
        "",
        f"**Last Updated:** {memory.get('project', {}).get('lastUpdated', 'Unknown')}",
        f"**Sessions:** {memory.get('sessionCount', 0)}",
        f"**Path:** `{memory.get('project', {}).get('path', 'Unknown')}`",
        "",
    ]

    if memory.get("currentFocus"):
        lines.extend([
            "## Current Focus",
            memory["currentFocus"],
            "",
        ])

    if memory.get("keyDecisions"):
        lines.extend([
            "## Key Decisions",
            "",
        ])
        for decision in memory["keyDecisions"]:
            lines.append(f"- {decision}")
        lines.append("")

    if memory.get("openItems"):
        lines.extend([
            "## Open Items",
            "",
        ])
        for item in memory["openItems"]:
            lines.append(f"- [ ] {item}")
        lines.append("")

    if memory.get("recentFiles"):
        lines.extend([
            "## Recent Files",
            "",
        ])
        for f in memory["recentFiles"][:10]:
            lines.append(f"- `{f}`")
        lines.append("")

    with open(obsidian_file, "w") as f:
        f.write("\n".join(lines))


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    # Get current working directory (project)
    cwd = hook_input.get("cwd", os.getcwd())
    project_hash = get_project_hash(cwd)
    project_name = get_project_name(cwd)

    # Memory file path
    memory_file = PROJECTS_DIR / f"{project_hash}.json"

    # Load existing memory
    memory = load_memory(memory_file)

    # Update project info
    memory["project"] = {
        "path": cwd,
        "name": project_name,
        "lastUpdated": datetime.now().isoformat(),
    }

    # Increment session count (each stop is a response)
    memory["sessionCount"] = memory.get("sessionCount", 0) + 1

    # Initialize arrays if not present
    memory.setdefault("recentFiles", [])
    memory.setdefault("keyDecisions", [])
    memory.setdefault("openItems", [])
    memory.setdefault("currentFocus", "")

    # Save memory
    save_memory(memory_file, memory)

    # Sync to Obsidian
    try:
        sync_to_obsidian(memory, project_name)
    except Exception:
        # Don't fail the hook if Obsidian sync fails
        pass

    # Hook output - no blocking, no output injection
    print(json.dumps({"continue": True}))

if __name__ == "__main__":
    main()
