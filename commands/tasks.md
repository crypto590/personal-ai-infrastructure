---
description: View and manage active tasks
argument-hint: [filter]
allowed-tools: Bash
---

# List Active Tasks

Display all active tasks using the Python task management system.

## Arguments

- `[filter]` - Optional filter (high, medium, low, critical, pending, in_progress, blocked)

## Usage Examples

```
/tasks
/tasks high
/tasks in_progress
/tasks blocked
```

---

## What to do

Execute the unified task_manager.py script with list subcommand:

```bash
~/.claude/skills/business/task-management/scripts/task_manager.py list $ARGUMENTS
```

The script will:
1. Auto-detect task directory (project-local `.claude/tasks/` or global `~/.claude/tasks/`)
2. Read and parse active.json
3. Apply filter if provided
4. Group by priority (critical → high → medium → low)
5. Sort by status (in_progress > blocked > pending) then by created date
6. Display formatted output with metadata
7. Show summary with total counts

## Notes

- The Python script handles all JSON parsing and formatting
- No manual file reading or data manipulation needed
- Filter is optional - if not provided, shows all active tasks
