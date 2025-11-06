#!/usr/bin/env python3
"""
PAI Context Loader Hook (Minimal Version - Nov 2025)

This hook provides zero-overhead context loading with the new Skills-as-Containers architecture.
Identity is now loaded via CORE skill YAML frontmatter (~300 tokens, always available).
Full context loads only when CORE skill is explicitly invoked (~4000 tokens on-demand).

"""

import json
import sys
from pathlib import Path

# PAI directories
CLAUDE_HOME = Path("/Users/coreyyoung/Claude")
CORE_SKILL = CLAUDE_HOME / "skills" / "CORE" / "SKILL.md"

def main():
    """Minimal hook - just verify PAI is accessible"""

    # Read hook input from stdin (provided by Claude Code)
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # Exit silently if no valid input
        sys.exit(0)

    # Check if CORE skill exists (silent check, no output if it does)
    if not CORE_SKILL.exists():
        # Only warn if CORE skill is missing
        print("⚠️  PAI Setup: CORE skill not found")
        print(f"   Expected: {CORE_SKILL}")
        print("   Run: Create CORE skill to set up your identity")

    # Exit successfully (no forced context loading)
    sys.exit(0)

if __name__ == "__main__":
    main()
