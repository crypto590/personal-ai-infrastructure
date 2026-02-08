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
from datetime import datetime

# PAI directories
CLAUDE_HOME = Path("/Users/coreyyoung/.claude")
CORE_SKILL = CLAUDE_HOME / "skills" / "CORE" / "SKILL.md"
HOOK_LOG = CLAUDE_HOME / "debug" / "hook.log"

def log(msg: str):
    """Log to debug file (set HOOK_LOG to enable)"""
    try:
        HOOK_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(HOOK_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except:
        pass

def main():
    """Load CORE skill context automatically for all prompts"""
    log("=== Hook invoked ===")
    log(f"CWD: {Path.cwd()}")

    # Read hook input from stdin (provided by Claude Code)
    try:
        hook_input = json.load(sys.stdin)
        log(f"Hook input keys: {list(hook_input.keys()) if isinstance(hook_input, dict) else type(hook_input)}")
        if isinstance(hook_input, dict):
            log(f"  session_id: {hook_input.get('session_id', 'N/A')}")
            log(f"  hook_event: {hook_input.get('hook_event_name', 'N/A')}")
            log(f"  prompt preview: {str(hook_input.get('prompt', ''))[:100]}...")
    except (json.JSONDecodeError, EOFError) as e:
        log(f"No valid input from stdin: {e}")
        sys.exit(0)

    # Check if CORE skill exists
    if not CORE_SKILL.exists():
        log(f"CORE skill not found at {CORE_SKILL}")
        print("⚠️  PAI Setup: CORE skill not found", file=sys.stderr)
        print(f"   Expected: {CORE_SKILL}", file=sys.stderr)
        print("   Run: Create CORE skill to set up your identity", file=sys.stderr)
        sys.exit(0)

    # Load and inject CORE skill context
    try:
        core_content = CORE_SKILL.read_text()
        content_lines = len(core_content.splitlines())
        content_chars = len(core_content)
        log(f"Loaded CORE skill: {content_lines} lines, {content_chars} chars")
        # Output the CORE skill content to stdout for Claude Code to inject
        print(core_content)
        log("CORE skill injected to stdout")
    except Exception as e:
        log(f"Error loading CORE skill: {e}")
        print(f"⚠️  Error loading CORE skill: {e}", file=sys.stderr)

    log("=== Hook complete ===")
    sys.exit(0)

if __name__ == "__main__":
    main()
