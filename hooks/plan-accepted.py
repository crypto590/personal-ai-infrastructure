#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Plan Accepted Context Loader — runs on ExitPlanMode (plan accepted).

Injects CORE skill gotchas and delegation guide so execution is
well-informed after plan approval.
"""

import json
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"

def load_file(rel_path: str, max_chars: int = 2000) -> str:
    """Load a file relative to ~/.claude/, return empty string on failure."""
    try:
        content = (CLAUDE_DIR / rel_path).read_text()
        return content[:max_chars]
    except Exception:
        return ""

def main():
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        pass

    parts = []

    # Load CORE gotchas
    core_body = load_file("skills/core/SKILL.md")
    if core_body:
        # Extract just the body (after the frontmatter closing ---)
        sections = core_body.split("---")
        if len(sections) >= 3:
            body = "---".join(sections[2:]).strip()
            parts.append(body)

    # Load delegation guide
    delegation = load_file("context/knowledge/orchestration/delegation-guide.md")
    if delegation:
        parts.append(delegation)

    output = "\n\n".join(parts)
    if output:
        print(json.dumps({"continue": True, "output": output}))
    else:
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
