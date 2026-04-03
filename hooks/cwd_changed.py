"""CwdChanged hook — fires when working directory changes during a session.

Logs directory transitions for context awareness. Can be extended to
trigger project-specific configuration loading (e.g., direnv-style).
"""

import json
import sys


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    old_cwd = event.get("oldCwd", "unknown")
    new_cwd = event.get("newCwd", "unknown")

    # Log the transition (visible in verbose mode)
    print(f"Directory changed: {old_cwd} -> {new_cwd}", file=sys.stderr)

    # Return empty JSON — no blocking, no context injection
    json.dump({}, sys.stdout)


if __name__ == "__main__":
    main()
