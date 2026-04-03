"""TaskCreated hook — fires when a task is created via TaskCreate.

Logs task creation for tracking. Can be extended to sync with
external task systems or enforce task naming conventions.
"""

import json
import sys


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    task_subject = event.get("input", {}).get("subject", "untitled")
    print(f"Task created: {task_subject}", file=sys.stderr)

    json.dump({}, sys.stdout)


if __name__ == "__main__":
    main()
