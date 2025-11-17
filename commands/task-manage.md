---
description: Manage persistent tasks (create, list, update, complete)
argument-hint: [operation] [args...]
allowed-tools: Bash, Read
---

# Task Management - Persistent Project Tasks

Intelligent task management using the task-management skill. This command loads the full skill context and handles all task operations.

## Arguments

- `[operation]` - Optional: create, list, update, complete, or file path
- `[args...]` - Additional arguments depending on operation

## Usage Examples

```
/task-manage                              # Load skill, ask what to do
/task-manage list                         # List all active tasks
/task-manage list high                    # Filter by priority
/task-manage create docs/sprint.md        # Parse markdown into tasks
/task-manage docs/sprint.md               # Smart: detects .md, runs create
/task-manage update 5 status in_progress  # Update task field
/task-manage complete 7                   # Mark task complete and archive
```

---

## What to do

1. **Load the task management skill** by reading:
   ```
   /Users/coreyyoung/.claude/skills/business/task-management/SKILL.md
   ```

2. **Analyze the user's intent** from the arguments provided:
   - No args or "help" → Explain capabilities and ask what they want
   - "list" or filter word (high/medium/low/critical/pending/in_progress/blocked) → Run list
   - "create <file>" or just "<file>" ending in .md → Run create
   - "update <id> <field> <value>" → Run update
   - "complete <id>" → Run complete
   - Ambiguous → Ask for clarification

3. **Execute the appropriate task_manager.py subcommand**:
   ```bash
   uv run ~/.claude/skills/business/task-management/scripts/task_manager.py <subcommand> <args>
   ```

4. **Display results** formatted appropriately for the operation

## Key Differences from TodoWrite

- **TodoWrite**: Session-level work tracking (lost after /clear)
- **This command**: Persistent git-synced tasks (survive sessions, work across machines)

Use this for sprint planning, PRD breakdown, and cross-session task tracking.

## Smart Detection Logic

The command should intelligently detect intent:

| User Input | Detected Operation | Explanation |
|------------|-------------------|-------------|
| `/task-manage` | Help | No args, show options |
| `/task-manage list` | list | Explicit subcommand |
| `/task-manage high` | list high | Filter keyword detected |
| `/task-manage docs/plan.md` | create docs/plan.md | .md file detected |
| `/task-manage create docs/plan.md` | create docs/plan.md | Explicit subcommand |
| `/task-manage update 5 status blocked` | update 5 status blocked | Starts with "update" |
| `/task-manage complete 7` | complete 7 | Starts with "complete" |

## Implementation Notes

- Always read SKILL.md first to get full context
- Use the unified task_manager.py script for ALL operations
- Auto-detect project-local `.claude/tasks/` vs global `~/.claude/tasks/`
- Tasks are JSON files tracked in git
- Each task has unique ID across all files (active, backlog, completed)

## Related Commands

- `/tasks` - Quick view of active tasks (no skill context loading)
- `/task-sync` - Commit and push task changes to remote
