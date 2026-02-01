#!/usr/bin/env python3
"""
Memory Restore Hook (SessionStart)
Loads project memory at session start and injects context.
"""

import json
import hashlib
import os
import sys
from pathlib import Path

# Directories
MEMORY_DIR = Path.home() / ".claude" / "memory"
PROJECTS_DIR = MEMORY_DIR / "projects"

def get_project_hash(path: str) -> str:
    """Generate consistent hash for project path."""
    return hashlib.sha256(path.encode()).hexdigest()[:12]

def load_memory(memory_file: Path) -> dict | None:
    """Load existing memory or return None."""
    if memory_file.exists():
        try:
            with open(memory_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return None

def format_memory_context(memory: dict) -> str:
    """Format memory as context string for injection."""
    lines = ["<memory-context>"]

    project = memory.get("project", {})
    lines.append(f"📍 Project: {project.get('name', 'Unknown')}")
    lines.append(f"📊 Sessions: {memory.get('sessionCount', 0)}")

    if memory.get("currentFocus"):
        lines.append(f"🎯 Focus: {memory['currentFocus']}")

    if memory.get("keyDecisions"):
        lines.append("📋 Key Decisions:")
        for d in memory["keyDecisions"][-5:]:  # Last 5 decisions
            lines.append(f"  • {d}")

    if memory.get("openItems"):
        lines.append("⏳ Open Items:")
        for item in memory["openItems"][-5:]:  # Last 5 items
            lines.append(f"  • {item}")

    if memory.get("recentFiles"):
        lines.append("📁 Recent Files:")
        for f in memory["recentFiles"][:5]:  # Last 5 files
            lines.append(f"  • {f}")

    lines.append("</memory-context>")

    return "\n".join(lines)

def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        hook_input = {}

    # Get current working directory (project)
    cwd = hook_input.get("cwd", os.getcwd())
    project_hash = get_project_hash(cwd)

    # Memory file path
    memory_file = PROJECTS_DIR / f"{project_hash}.json"

    # Load memory
    memory = load_memory(memory_file)

    if memory:
        # Format and output memory context
        context = format_memory_context(memory)

        # Output for hook - inject into session
        result = {
            "continue": True,
            "output": context
        }
    else:
        # No memory for this project yet
        result = {"continue": True}

    print(json.dumps(result))

if __name__ == "__main__":
    main()
