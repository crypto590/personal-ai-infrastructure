#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///

"""
Subagent Context Loading Hook (SubagentStart Event)

Triggers when a subagent initializes, before it does any work.
Automatically injects PAI context, security reminders, and current date.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
PAI_DIR = Path.home() / '.claude'
CORE_SKILL = PAI_DIR / 'skills' / 'CORE' / 'SKILL.md'
LOGS_DIR = PAI_DIR / 'logs' / 'hooks'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def log(message: str, level: str = "INFO"):
    """Simple logging to file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [subagent_start] [{level}] {message}\n"

    log_file = LOGS_DIR / 'context_loading.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)

def load_pai_context() -> str:
    """Load PAI CORE context"""
    try:
        if not CORE_SKILL.exists():
            log(f"CORE skill not found at {CORE_SKILL}", "ERROR")
            return "⚠️ PAI CORE context not available"

        with open(CORE_SKILL, 'r') as f:
            content = f.read()

        log(f"Loaded CORE skill ({len(content)} chars)", "INFO")
        return content

    except Exception as e:
        log(f"Error loading CORE skill: {e}", "ERROR")
        return f"⚠️ Error loading PAI context: {e}"

def get_current_date() -> str:
    """Get current date/time"""
    now = datetime.now()
    # CST is UTC-6 (standard) or UTC-5 (daylight)
    return now.strftime('%Y-%m-%d %H:%M:%S %Z')

def main():
    """Main hook execution"""
    log("Hook triggered (SubagentStart event)", "INFO")

    try:
        # Read JSON input from stdin
        data = json.load(sys.stdin)

        # Extract agent name
        agent_name = data.get('agentName', 'unknown')
        log(f"Subagent starting: {agent_name}", "INFO")

        # Build context output
        output = []

        output.append("=" * 60)
        output.append("🚨 PAI CONTEXT LOADED AUTOMATICALLY")
        output.append("=" * 60)
        output.append("")

        # Load CORE skill
        pai_context = load_pai_context()
        output.append(pai_context)
        output.append("")

        # Security reminder
        output.append("=" * 60)
        output.append("🔒 SECURITY REMINDER")
        output.append("=" * 60)
        output.append("- Run 'git remote -v' BEFORE every commit")
        output.append("- ~/.claude/ is PRIVATE - never commit to public repos")
        output.append("- Always verify directory before git operations")
        output.append("")

        # Current date
        output.append("=" * 60)
        output.append("📅 CURRENT DATE")
        output.append("=" * 60)
        output.append(get_current_date())
        output.append("")

        output.append("=" * 60)
        output.append("✅ PAI Context Loading Complete")
        output.append("=" * 60)

        # Print to stdout (this goes to the subagent's context)
        print("\n".join(output))

        log(f"Context injected successfully for {agent_name}", "INFO")

    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}", "ERROR")
        print("⚠️ Error: Invalid JSON input to SubagentStart hook")

    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        print(f"⚠️ Error loading PAI context: {e}")

if __name__ == '__main__':
    main()
