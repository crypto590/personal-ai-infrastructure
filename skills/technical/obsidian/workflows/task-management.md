# Task Management Workflow

## Purpose

Read, create, and update tasks in Obsidian from Claude Code sessions. Keeps Obsidian as the single source of truth for task tracking.

## When to Use

- Starting a work session (pull current tasks)
- After completing work (mark tasks done)
- When discovering new work during a session (create tasks)
- Reviewing progress across projects

## Task Format

Obsidian uses standard markdown checkboxes:

```markdown
- [ ] Incomplete task
- [x] Completed task
- [ ] Task with #tag and [[link]]
- [ ] Task with due date [due:: 2025-12-01]
```

## Patterns

### 1. Session Start: Pull Current Tasks

Review open tasks before beginning work.

```bash
# Get all incomplete tasks
obsidian vault=The_Hub tasks status=todo

# Get tasks from a specific project
obsidian vault=The_Hub tasks file="Project Alpha"

# Get all tasks (done and todo) for a full picture
obsidian vault=The_Hub tasks
```

Report the task list to the user and ask which to work on, or pick the highest-priority item.

### 2. Task Filtering

Narrow down tasks by scope.

```bash
# All open tasks across the vault
obsidian vault=The_Hub tasks status=todo

# Tasks in a specific note
obsidian vault=The_Hub tasks file="Sprint 12 Board"

# Search for tasks with specific keywords
obsidian vault=The_Hub search query="- [ ] refactor"
obsidian vault=The_Hub search query="- [ ] API"
```

### 3. Mark Tasks Complete

After finishing work, update the task status. Use append/prepend to modify task lists, or update individual tasks.

```bash
# View the individual task for modification
obsidian vault=The_Hub task

# Alternative: read the note, then rewrite the task line
obsidian vault=The_Hub read file="Project Alpha"
```

For bulk task completion, read the file, identify the task lines, and use file operations to update them.

### 4. Create New Tasks

When you discover new work during a session, add tasks to the appropriate note.

```bash
# Add tasks to a project note
obsidian vault=The_Hub append file="Project Alpha" content="\n### Discovered During Auth Refactor\n- [ ] Update API docs for new JWT endpoints\n- [ ] Add rate limiting to token refresh\n- [ ] Write integration tests for token expiry"

# Add a task to the daily note
obsidian vault=The_Hub daily:append content="\n## Tasks Added\n- [ ] Review PR #456 -- blocking deployment\n- [ ] Update environment variables in staging"
```

### 5. Task Triage

Organize tasks found across the vault.

```bash
# Find all open tasks
obsidian vault=The_Hub tasks status=todo

# Check for orphaned tasks in notes that may be stale
obsidian vault=The_Hub orphans

# Find tasks with specific tags
obsidian vault=The_Hub search query="- [ ] #urgent"
obsidian vault=The_Hub search query="- [ ] #blocked"
```

## Full Session Workflow

### Start of Session

```bash
# 1. Check what's open
obsidian vault=The_Hub tasks status=todo

# 2. Read the project context
obsidian vault=The_Hub read file="Project Alpha"

# 3. Pick a task and begin work
```

### During Session

```bash
# Found new work? Add it
obsidian vault=The_Hub append file="Project Alpha" content="\n- [ ] Handle edge case: expired refresh token during active session"
```

### End of Session

```bash
# 1. Log what was done (update task status in the note)
obsidian vault=The_Hub read file="Project Alpha"
# Update completed tasks from - [ ] to - [x]

# 2. Summarize in daily note
obsidian vault=The_Hub daily:append content="\n## Tasks Completed\n- [x] Implement JWT authentication\n- [x] Add token refresh endpoint\n\n## Tasks Remaining\n- [ ] Integration tests for token expiry\n- [ ] Update API documentation"

# 3. Verify remaining tasks
obsidian vault=The_Hub tasks status=todo file="Project Alpha"
```

## Tips

- Keep tasks in the note they belong to (project notes, meeting notes, etc.)
- Use the daily note for session-scoped task tracking
- Add `#blocked`, `#urgent`, or `#waiting` tags to tasks for easier filtering
- Link related notes in tasks: `- [ ] Implement [[Auth Architecture]] refresh flow`
- When a task spawns subtasks, nest them in the same note for context
