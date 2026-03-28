#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
PreToolUse Security Hook

Matcher: Bash|Write|Edit|Read (only fires for file/command tools)

Three tiers:
  blocked  -- exit(2), tool call rejected
  confirm  -- exit(1), user must approve
  alert    -- logged but allowed

Also enforces file path access control and JSONL audit logging.
Security config is inlined (no YAML parse overhead per invocation).
"""

import json
import sys
import re
import fnmatch
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Security Config (inlined from security.yaml — edit here, not the YAML)
# ---------------------------------------------------------------------------

SECURITY_CONFIG = {
    "commands": {
        "blocked": [
            {"pattern": r"rm\s+.*-[a-z]*r[a-z]*f", "description": "rm -rf variants"},
            {"pattern": r"rm\s+.*-[a-z]*f[a-z]*r", "description": "rm -fr variants"},
            {"pattern": r"rm\s+--recursive\s+--force", "description": "rm --recursive --force"},
            {"pattern": r"rm\s+--force\s+--recursive", "description": "rm --force --recursive"},
            {"pattern": r"rm\s+-r\s+.*-f", "description": "rm -r ... -f (split flags)"},
            {"pattern": r"rm\s+-f\s+.*-r", "description": "rm -f ... -r (split flags)"},
            {"pattern": r"chmod\s+777", "description": "World-writable permissions"},
            {"pattern": r"mkfs\.", "description": "Filesystem format"},
            {"pattern": r":\(\)\{.*\|.*&.*\};:", "description": "Fork bomb"},
        ],
        "confirm": [
            {"pattern": r"git\s+push\s+.*--force", "description": "Force push"},
            {"pattern": r"drop\s+(table|database)", "description": "Drop table/database"},
            {"pattern": r"truncate\s+table", "description": "Truncate table"},
            {"pattern": r"git\s+reset\s+--hard", "description": "Hard reset"},
        ],
        "alert": [
            {"pattern": r"curl.*\|.*sh", "description": "Pipe curl to shell"},
            {"pattern": r"wget.*\|.*sh", "description": "Pipe wget to shell"},
        ],
    },
    "files": {
        "zero_access": ["~/.ssh/*", "~/.gnupg/*", "~/.aws/credentials", "~/.aws/config"],
        "read_only": [".env", ".env.*", "*.pem", "*.key", "*.p12"],
        "no_delete": ["*.sqlite", "*.db", "*.sqlite3"],
    },
}


def load_security_config() -> dict:
    return SECURITY_CONFIG


# ---------------------------------------------------------------------------
# Env var stripping (bypass prevention)
# ---------------------------------------------------------------------------

def strip_env_vars(cmd: str) -> str:
    """Strip leading env var assignments: LANG=C rm -rf / -> rm -rf /"""
    return re.sub(r'^(\w+=[^\s]*\s+)*', '', cmd.strip())


# ---------------------------------------------------------------------------
# Command security
# ---------------------------------------------------------------------------

def check_command_security(command: str, config: dict) -> tuple:
    """Check command against security patterns. Returns (action, description)."""
    normalized = strip_env_vars(command)

    for rule in config.get("commands", {}).get("blocked", []):
        if re.search(rule["pattern"], normalized, re.IGNORECASE):
            return "blocked", rule.get("description", "Dangerous command")

    for rule in config.get("commands", {}).get("confirm", []):
        if re.search(rule["pattern"], normalized, re.IGNORECASE):
            return "confirm", rule.get("description", "Risky command")

    for rule in config.get("commands", {}).get("alert", []):
        if re.search(rule["pattern"], normalized, re.IGNORECASE):
            return "alert", rule.get("description", "Notable command")

    return "allow", ""


# ---------------------------------------------------------------------------
# File path access control
# ---------------------------------------------------------------------------

def expand_path(pattern: str) -> str:
    """Expand ~ in path patterns."""
    if pattern.startswith("~"):
        return str(Path.home()) + pattern[1:]
    return pattern


def check_file_access(tool_name: str, file_path: str, config: dict) -> tuple:
    """Check file path against access rules. Returns (action, description)."""
    if not file_path:
        return "allow", ""

    try:
        resolved = str(Path(file_path).expanduser().resolve())
    except Exception:
        resolved = file_path

    basename = Path(file_path).name
    file_rules = config.get("files", {})

    # Zero access: block all operations
    for pattern in file_rules.get("zero_access", []):
        expanded = expand_path(pattern)
        parent_dir = expanded.rstrip("/*")
        if fnmatch.fnmatch(resolved, expanded) or resolved.startswith(parent_dir + "/"):
            return "blocked", f"Access denied: {pattern}"

    # Read only: block Write/Edit, allow Read
    if tool_name in ("Write", "Edit", "MultiEdit"):
        for pattern in file_rules.get("read_only", []):
            expanded = expand_path(pattern)
            if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(resolved, expanded):
                if not file_path.endswith('.env.sample'):
                    return "blocked", f"Read-only file: {pattern}"

    return "allow", ""


# ---------------------------------------------------------------------------
# JSONL Audit Log
# ---------------------------------------------------------------------------

def log_event(tool_name: str, action: str, details: str = ""):
    """Append event to JSONL audit log (append-only, no read overhead)."""
    try:
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / 'events.jsonl'

        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "action": action,
        }
        if details:
            entry["details"] = details[:200]

        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        config = load_security_config()

        # --- Command security (Bash tool) ---
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            action, desc = check_command_security(command, config)

            if action == "blocked":
                log_event(tool_name, "blocked", desc)
                print(f"BLOCKED: {desc}", file=sys.stderr)
                sys.exit(2)
            elif action == "confirm":
                log_event(tool_name, "confirm", desc)
                print(f"CONFIRM: {desc} -- requires user approval", file=sys.stderr)
                sys.exit(1)
            elif action == "alert":
                log_event(tool_name, "alert", desc)
                print(f"ALERT: {desc}", file=sys.stderr)

            # Check no_delete patterns in rm commands
            stripped = strip_env_vars(command)
            if re.search(r'\brm\s+', stripped):
                for pattern in config.get("files", {}).get("no_delete", []):
                    ext = pattern.lstrip("*")
                    if ext and ext in stripped:
                        log_event(tool_name, "blocked", f"Delete protected: {pattern}")
                        print(f"BLOCKED: Cannot delete {pattern} files", file=sys.stderr)
                        sys.exit(2)

            # Check env file modifications via bash
            env_write_patterns = [
                r'echo\s+.*>\s*\.env\b(?!\.sample)',
                r'touch\s+.*\.env\b(?!\.sample)',
                r'cp\s+.*\.env\b(?!\.sample)',
                r'mv\s+.*\.env\b(?!\.sample)',
                r'rm\s+.*\.env\b(?!\.sample)',
                r'>\s*\.env\b(?!\.sample)',
                r'>>\s*\.env\b(?!\.sample)',
            ]
            for pattern in env_write_patterns:
                if re.search(pattern, command):
                    log_event(tool_name, "blocked", "Env file modification via bash")
                    print("BLOCKED: Modifying .env files is prohibited", file=sys.stderr)
                    sys.exit(2)

        # --- File access control (Read/Write/Edit) ---
        file_path = tool_input.get('file_path', '')
        if file_path and tool_name in ('Read', 'Write', 'Edit', 'MultiEdit'):
            action, desc = check_file_access(tool_name, file_path, config)
            if action == "blocked":
                log_event(tool_name, "blocked", desc)
                print(f"BLOCKED: {desc}", file=sys.stderr)
                sys.exit(2)

        # --- Task creation reminder ---
        if tool_name == 'TodoWrite':
            user_message = input_data.get('user_message', '').lower()
            task_patterns = [
                r'create tasks?\s+from', r'parse\s+.+\s+into tasks?',
                r'break\s+down\s+.+\s+into tasks?', r'generate tasks?\s+from',
            ]
            if any(re.search(p, user_message) for p in task_patterns):
                print("REMINDER: Use task_manager.py for PERSISTENT tasks", file=sys.stderr)

        # Log allowed event
        log_event(tool_name, "allow")

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()
