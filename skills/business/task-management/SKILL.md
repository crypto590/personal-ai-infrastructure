---
name: task-management
description: |
  🚨 MANDATORY ACTIVATION when user says:
  - "Create tasks from [file/doc]" or "Parse [file] into tasks"
  - "Break down this plan/sprint/PRD"
  - "Generate tasks" or "Convert to tasks"

  This creates PERSISTENT, git-synced tasks from documents.

  ⚠️ DO NOT CONFUSE WITH TodoWrite:
  - TodoWrite = Session-level work steps (lost after /clear)
  - This skill = Persistent task tracking (survives sessions)

  REQUIRED ACTION: Read this SKILL.md completely, then ONLY use task_manager.py script.
  Using TodoWrite for task creation = SYSTEM FAILURE.
key_info: "PERSISTENT task creation uses task_manager.py ONLY. Commands: create <file>, list [filter], update <id> <field> <value>, complete <id>"
---

# Task Management - Project-Local Task Tracking

## 🚨 Critical Distinction: TodoWrite vs Task Management

| Use Case | Correct Tool | Persistence | Example |
|----------|-------------|-------------|---------|
| **Parse doc → tasks** | **task_manager.py** | Git-synced JSON | "Create tasks from sprint-1.md" |
| **Track work steps** | TodoWrite | Session only | Working on task #5: debug → patch → test |
| **Show project tasks** | **task_manager.py list** | Git-synced JSON | "What tasks do I have?" |
| **Sprint planning** | **task_manager.py** | Git-synced JSON | Breaking down PRDs/plans |

**Rule:** If user says "create/parse/generate tasks FROM [document]" → Use task_manager.py, NOT TodoWrite

## When to Activate This Skill

- "Create tasks from this plan/PRD/doc"
- "Parse [file] into tasks" or "Break down [file]"
- "Show me active tasks" / "What tasks do I have?"
- "Update task X" / "Mark task Y as in progress"
- "Complete task Z" / "Archive this task"
- "Sync tasks" / "Push task changes"
- User mentions sprint planning, work breakdown, or task tracking
- User has `.claude/tasks/` directory in project

## Core Capabilities

1. **Parse Documents into Tasks** - Convert markdown plans/PRDs into structured task objects
2. **View & Filter Tasks** - Display active tasks grouped by priority and status
3. **Update Task State** - Change status, priority, notes, blocking reasons
4. **Complete & Archive** - Move finished tasks to completed.json with timestamps
5. **Git Sync** - Commit and push task changes for cross-machine availability

## Task File Structure

```
.claude/tasks/
├── active.json      # Current work (pending, in_progress, blocked)
├── backlog.json     # Future/planned work
├── completed.json   # Archived completed tasks
└── .gitkeep
```

## Usage

All task operations use a unified Python script with subcommands:

**Script:** `~/.claude/skills/business/task-management/scripts/task_manager.py`

**Commands:**
```bash
# Parse markdown file into tasks
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py create <file>

# Display active tasks (optionally filter by priority/status)
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py list [filter]

# Update task field
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py update <id> <field> <value>

# Mark task completed and archive
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py complete <id>
```

**Subcommands:**
- `create <file>` - Parse markdown → JSON tasks
- `list [filter]` - Display active tasks (optionally filtered)
- `update <id> <field> <value>` - Modify task fields atomically
- `complete <id>` - Mark complete and archive to completed.json

**Why unified script with uv?**
- Self-contained via `uv run --script` (no cross-imports)
- Atomic JSON operations (no partial writes)
- Built-in validation and error handling
- Consistent behavior across all operations
- No `__pycache__` directories

## Task Object Schema

```json
{
  "id": 1,
  "title": "Implement JWT authentication",
  "status": "pending",
  "priority": "high",
  "created": "2025-11-17T15:00:00Z",
  "updated": "2025-11-17T15:00:00Z",
  "completed": null,
  "source_file": "docs/sprint-1.md",
  "source_line": 15,
  "notes": "Use bcrypt for hashing",
  "tags": ["backend", "auth"],
  "blocked_by": null,
  "depends_on": []
}
```

**Status values:** `pending`, `in_progress`, `blocked`, `completed`
**Priority values:** `low`, `medium`, `high`, `critical`

## Workflow Examples

### 1. Start New Sprint from Plan

```bash
# Parse sprint plan into tasks
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py create docs/sprint-2.md

# View all active tasks
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py list

# Start working on first task
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py update 1 status in_progress
```

### 2. Update Task as You Work

```bash
# Mark blocked with reason
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py update 3 status blocked
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py update 3 blocked_by "Waiting on API review"

# Add notes
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py update 3 notes "Need to confirm error handling approach"

# Complete when done
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py complete 3
```

### 3. Daily Sync Workflow

```bash
# At session start
git pull

# View what's active
uv run ~/.claude/skills/business/task-management/scripts/task_manager.py list

# At session end (manual git commit/push)
cd .claude/tasks
git add *.json
git commit -m "Update tasks $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push
```

## Smart Markdown Parsing

When using the `create` command, the parser recognizes:

- `# HIGH PRIORITY` / `## CRITICAL` headings → set priority
- `- [ ]` unchecked → pending task in active.json
- `- [x]` checked → completed task in completed.json
- Indented bullets → task notes/acceptance criteria
- Keywords (`backend`, `frontend`, `auth`) → extracted as tags
- `**BLOCKED**` or 🚫 → status: blocked

## Integration with TodoWrite

Task management complements TodoWrite:

- **TodoWrite**: Session-specific work tracking (lost after `/clear`)
- **Task Management**: Persistent project tracking (git-synced, cross-session)

**Best practice:**
1. Use `task_manager.py create` to structure work from plans
2. Use TodoWrite during active session to track current progress
3. Use `task_manager.py complete` to archive when fully done

## Supplementary Resources

For comprehensive documentation including:
- Complete schema definitions
- Advanced parsing rules
- Error handling patterns
- Migration guides
- Best practices

Read: `/Users/coreyyoung/.claude/skills/business/task-management/CLAUDE.md`

## Key Principles

1. **Python for reliability** - All JSON operations use validated Python scripts
2. **Git-synced by default** - Tasks available across all environments
3. **Project-local** - Each project has own `.claude/tasks/` directory
4. **Status-based organization** - Active/backlog/completed separation
5. **Source tracking** - Tasks link back to originating documents
6. **No external dependencies** - Works offline, no `gh` CLI needed
