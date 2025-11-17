# Task Management Framework

**Version:** 1.0.0
**Purpose:** Project-local task tracking that works across Mac and Claude Code Web
**Status:** Design & Implementation Phase

---

## Problem Statement

**Current Pain Points:**
- GitHub Issues don't work in Claude Code Web (sandboxed, no `gh` CLI)
- TodoWrite is session-based only (lost after `/clear`)
- Autopilot handles context state, but not persistent task tracking
- Need task management that works remotely AND locally
- Large PRDs/plans need to be broken down into actionable tasks

**Requirements:**
1. ✅ Work on Mac (local Claude Code)
2. ✅ Work on Web (Codespace/sandboxed environments)
3. ✅ Project-local (each project has own tasks)
4. ✅ Git-synced (automatically available across machines)
5. ✅ No external dependencies (no `gh` CLI, no APIs)
6. ✅ Parse existing docs (PRDs, sprint plans) into tasks
7. ✅ Simple slash command interface

---

## Architecture

### Directory Structure

**Per Project:**
```
your-project/
├── .claude/
│   ├── tasks/
│   │   ├── active.json       # Current work
│   │   ├── backlog.json      # Planned/future work
│   │   ├── completed.json    # Archive of done tasks
│   │   └── .gitkeep          # Ensure git tracks directory
│   ├── commands/              # Project-specific commands (optional)
│   │   ├── create-tasks.md
│   │   ├── tasks.md
│   │   ├── task-add.md
│   │   ├── task-update.md
│   │   ├── task-complete.md
│   │   └── task-sync.md
│   └── TASKS.md               # Task management guide for Claude
├── docs/                      # Your planning docs
│   ├── sprint-1.md
│   └── feature-prd.md
└── .gitignore                 # DON'T ignore .claude/
```

**Global (for Mac convenience):**
```
~/.claude/
├── commands/                  # Global commands available on Mac
│   ├── create-tasks.md       # Same commands as project-local
│   ├── tasks.md
│   ├── task-add.md
│   ├── task-update.md
│   ├── task-complete.md
│   └── task-sync.md
└── docs/
    └── TASK-MANAGEMENT.md    # This file
```

---

## Task JSON Schema

### Task Object
```json
{
  "id": 1,
  "title": "Implement JWT authentication",
  "status": "pending",
  "priority": "high",
  "created": "2025-11-16T14:30:00Z",
  "updated": "2025-11-16T14:30:00Z",
  "completed": null,
  "source_file": "docs/sprint-1.md",
  "source_line": 15,
  "notes": "Use bcrypt for password hashing. Access token 15min, refresh 7 days.",
  "tags": ["backend", "auth"],
  "blocked_by": null,
  "depends_on": []
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | number | ✅ | Auto-incrementing unique ID |
| `title` | string | ✅ | Brief task description |
| `status` | enum | ✅ | `pending`, `in_progress`, `blocked`, `completed` |
| `priority` | enum | ✅ | `low`, `medium`, `high`, `critical` |
| `created` | ISO 8601 | ✅ | Creation timestamp |
| `updated` | ISO 8601 | ✅ | Last modification timestamp |
| `completed` | ISO 8601 | ❌ | Completion timestamp (null if not done) |
| `source_file` | string | ❌ | Original file task was parsed from |
| `source_line` | number | ❌ | Line number in source file |
| `notes` | string | ❌ | Additional context, acceptance criteria |
| `tags` | string[] | ❌ | Categorization tags |
| `blocked_by` | string | ❌ | Reason task is blocked |
| `depends_on` | number[] | ❌ | Task IDs this depends on |

### Container Format

**active.json / backlog.json / completed.json:**
```json
{
  "version": "1.0.0",
  "source": "docs/sprint-1.md",
  "created": "2025-11-16T14:30:00Z",
  "last_updated": "2025-11-16T15:45:00Z",
  "tasks": [
    { /* task object */ },
    { /* task object */ }
  ]
}
```

---

## Slash Commands

### `/create-tasks <file>`

**Purpose:** Parse PRD/plan/doc and auto-generate tasks

**Usage:**
```bash
/create-tasks docs/sprint-1.md
/create-tasks docs/feature-auth.md
```

**What It Does:**
1. Reads specified file
2. Intelligently parses markdown structure:
   - Headings indicate task sections
   - Bullet points become tasks
   - `[ ]` checkboxes = pending tasks
   - `[x]` checkboxes = completed tasks (go to completed.json)
   - Priority from keywords (CRITICAL, HIGH, MEDIUM, LOW) or heading level
   - Indented bullets become notes/acceptance criteria
3. Generates task objects with unique IDs
4. Writes to `.claude/tasks/active.json` (or `completed.json` for checked items)
5. Displays summary of created tasks

**Smart Parsing Rules:**

| Pattern | Action |
|---------|--------|
| `# HIGH PRIORITY` | All tasks under this = priority: high |
| `## CRITICAL:` | All tasks under this = priority: critical |
| `- [ ] Task name` | Create pending task |
| `- [x] Task name` | Create completed task |
| `  - Acceptance criteria` | Add as task notes |
| `**BLOCKED**` or `🚫` | Set status: blocked |
| Keywords in text | Extract as tags (e.g., "backend", "frontend", "auth") |

**Example Input:**
```markdown
# Sprint 1: Authentication System

## HIGH PRIORITY
- [ ] Implement JWT authentication
  - Use bcrypt for password hashing
  - Access token: 15min expiry
  - Refresh token: 7 days expiry
- [ ] Add refresh token endpoint
- [x] Set up user model

## MEDIUM PRIORITY
- [ ] Rate limiting on /auth/login
- [ ] Session management

## LOW PRIORITY
- [ ] Remember me functionality
```

**Example Output:**
```
✅ TASKS CREATED FROM: docs/sprint-1.md

📊 SUMMARY:
- Created: 5 tasks in active.json
- Completed: 1 task in completed.json
- Total: 6 tasks parsed

🔥 HIGH PRIORITY (2 tasks)
#1 - Implement JWT authentication
#2 - Add refresh token endpoint

📋 MEDIUM PRIORITY (2 tasks)
#3 - Rate limiting on /auth/login
#4 - Session management

📌 LOW PRIORITY (1 task)
#5 - Remember me functionality

✅ ALREADY COMPLETED (1 task)
#6 - Set up user model

---
Run /tasks to view active tasks
```

---

### `/tasks`

**Purpose:** Display active tasks

**Usage:**
```bash
/tasks
/tasks high          # Filter by priority
/tasks in_progress   # Filter by status
```

**Output Format:**
```
🎯 ACTIVE TASKS

🔥 HIGH PRIORITY
#1 - Implement JWT authentication [pending]
     Created: 2025-11-16 | Source: docs/sprint-1.md:4
     Notes: Use bcrypt for password hashing. Access token 15min, refresh 7 days.

#2 - Add refresh token endpoint [in_progress]
     Created: 2025-11-16 | Updated: 2025-11-16 15:30

📋 MEDIUM PRIORITY
#3 - Rate limiting on /auth/login [pending]
#4 - Session management [blocked]
     Blocked by: Need to decide on session store (Redis vs Postgres)

📌 LOW PRIORITY
#5 - Remember me functionality [pending]

---
Total: 5 tasks (1 in_progress, 3 pending, 1 blocked)
```

---

### `/task-add`

**Purpose:** Manually add a single task

**Usage:**
```bash
/task-add
```

**Interactive Prompt:**
1. Title (required)
2. Priority (default: medium)
3. Status (default: pending)
4. Notes (optional)
5. Tags (optional)

**Output:**
```
✅ TASK ADDED

#6 - Write integration tests for auth
Priority: high
Status: pending
Tags: testing, backend
Created: 2025-11-16 15:45

Run /tasks to view all active tasks
```

---

### `/task-update <id>`

**Purpose:** Update task status, priority, or details

**Usage:**
```bash
/task-update 2
/task-update 3 in_progress     # Quick status update
/task-update 4 blocked "Waiting on API design review"
```

**Interactive Prompt (if no args provided):**
1. Select field to update: status, priority, notes, tags, blocked_by
2. Provide new value

**Output:**
```
✅ TASK UPDATED

#2 - Add refresh token endpoint
Status: pending → in_progress
Updated: 2025-11-16 15:50

Run /tasks to view all active tasks
```

---

### `/task-complete <id>`

**Purpose:** Mark task as completed and archive

**Usage:**
```bash
/task-complete 1
```

**What It Does:**
1. Finds task in `active.json`
2. Updates task:
   - `status: "completed"`
   - `completed: "<timestamp>"`
   - `updated: "<timestamp>"`
3. Moves task from `active.json` to `completed.json`
4. Writes both files

**Output:**
```
✅ TASK COMPLETED

#1 - Implement JWT authentication
Completed: 2025-11-16 16:00
Duration: 2 hours (created → completed)

Task moved to archive (completed.json)

Run /tasks to view remaining active tasks
```

---

### `/task-sync`

**Purpose:** Git commit and push task files

**Usage:**
```bash
/task-sync
/task-sync "Sprint 1 tasks completed"   # Custom commit message
```

**What It Does:**
1. `cd` to project root
2. `git add .claude/tasks/*.json`
3. Check for changes: `git diff --cached --quiet`
4. If changes exist:
   - Commit with message: `"Update tasks [timestamp]"` or custom message
   - `git push origin <current-branch>`
5. Display sync status

**Output:**
```
🔄 TASK SYNC

Add: ✅ Staged .claude/tasks/*.json
Commit: ✅ "Update tasks 2025-11-16T16:05"
Push: ✅ Pushed to origin/main

Tasks are now synced across all machines.
```

**Error Handling:**
- No internet: Show error, suggest retrying later
- Merge conflicts: Display conflict info, suggest manual resolution
- No changes: Skip commit/push, inform user

---

## Implementation Guide

### Phase 1: Core Structure (5 min)

**Goal:** Set up basic task storage

```bash
# Create task directories
mkdir -p .claude/tasks

# Create base JSON files
cat > .claude/tasks/active.json << 'EOF'
{
  "version": "1.0.0",
  "tasks": []
}
EOF

cat > .claude/tasks/backlog.json << 'EOF'
{
  "version": "1.0.0",
  "tasks": []
}
EOF

cat > .claude/tasks/completed.json << 'EOF'
{
  "version": "1.0.0",
  "tasks": []
}
EOF

# Ensure git tracks directory
touch .claude/tasks/.gitkeep

# Verify .gitignore doesn't exclude .claude/
grep -q "^\.claude/$" .gitignore && echo "⚠️  Remove .claude/ from .gitignore" || echo "✅ .claude/ not ignored"
```

---

### Phase 2: Command Files (15 min)

**Goal:** Create slash command definitions

Create files in `~/.claude/commands/` (for Mac) or `.claude/commands/` (for project-specific on Web):

**File:** `create-tasks.md`
```markdown
---
description: Parse PRD/plan and auto-generate tasks
scope: project
gitignored: false
---

# Create Tasks from Document

Parse a markdown file (PRD, sprint plan, etc.) and automatically generate tasks.

## What to do:

1. **Validate Input**
   - Check file path provided as argument
   - Read file contents
   - Verify file is readable markdown

2. **Parse Document**
   - Identify heading levels for priority:
     - "CRITICAL" or "HIGH PRIORITY" → priority: high
     - "MEDIUM PRIORITY" → priority: medium
     - "LOW PRIORITY" → priority: low
     - Default: medium

   - Parse task markers:
     - `- [ ]` → pending task in active.json
     - `- [x]` → completed task in completed.json
     - Indented bullets → task notes

   - Extract metadata:
     - Line numbers for source_line
     - Keywords for tags (backend, frontend, auth, etc.)
     - Blocked indicators (🚫, **BLOCKED**, "waiting on")

3. **Generate Tasks**
   - Read current active.json and completed.json
   - Find highest existing task ID
   - Create task objects with incremental IDs
   - Include: title, status, priority, created, updated, source_file, source_line, notes, tags

4. **Write Files**
   - Update active.json with new pending/in_progress tasks
   - Update completed.json with checked tasks
   - Update container metadata (last_updated, source)

5. **Display Summary**
   - Show tasks created by priority
   - Show tasks already completed
   - Provide total count
   - Suggest next command (/tasks)

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

**File:** `tasks.md`
```markdown
---
description: View and manage active tasks
scope: project
gitignored: false
---

# Task Management - List Active Tasks

Display all active tasks from `.claude/tasks/active.json`.

## What to do:

1. Read `.claude/tasks/active.json`
2. Parse tasks array
3. Group by priority (high → medium → low)
4. Sort within groups by:
   - Status priority: in_progress > blocked > pending
   - Then by created timestamp (oldest first)
5. Display formatted output with:
   - ID, title, status
   - Created date, updated date if modified
   - Source file and line if available
   - Notes if present
   - Blocked reason if status is blocked

## Optional Filters:

If argument provided:
- Priority filter: `high`, `medium`, `low`
- Status filter: `pending`, `in_progress`, `blocked`

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

**File:** `task-add.md`
```markdown
---
description: Add a new task to active tasks
scope: project
gitignored: false
---

# Task Management - Add New Task

Manually add a single task to active.json.

## What to do:

1. Read `.claude/tasks/active.json`
2. Find next available ID (max current ID + 1, or 1 if empty)
3. Prompt user for:
   - **Title** (required): Task description
   - **Priority** (optional, default: medium): low/medium/high/critical
   - **Status** (optional, default: pending): pending/in_progress/blocked
   - **Notes** (optional): Additional context
   - **Tags** (optional): Comma-separated tags
4. Create task object with ISO 8601 timestamps
5. Append to tasks array
6. Update container metadata (last_updated)
7. Write back to active.json
8. Display confirmation

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

**File:** `task-update.md`
```markdown
---
description: Update an existing task
scope: project
gitignored: false
---

# Task Management - Update Task

Update task status, priority, notes, or other fields.

## Usage Patterns:

- `/task-update <id>` - Interactive update
- `/task-update <id> <status>` - Quick status change
- `/task-update <id> blocked "<reason>"` - Mark blocked with reason

## What to do:

1. Read `.claude/tasks/active.json`
2. Find task by ID
3. Display current task details
4. If arguments provided, apply them directly
5. Otherwise, prompt for field to update and new value
6. Update task object
7. Update `updated` timestamp
8. Write back to active.json
9. Display confirmation showing old → new values

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

**File:** `task-complete.md`
```markdown
---
description: Mark task completed and archive
scope: project
gitignored: false
---

# Task Management - Complete Task

Mark a task as completed and move to archive.

## What to do:

1. Read `.claude/tasks/active.json`
2. Read `.claude/tasks/completed.json`
3. Find task by ID in active.json
4. Update task:
   - `status: "completed"`
   - `completed: "<ISO 8601 timestamp>"`
   - `updated: "<ISO 8601 timestamp>"`
5. Remove from active.json tasks array
6. Append to completed.json tasks array
7. Update both container metadata (last_updated)
8. Write both files
9. Display confirmation with duration (created → completed)

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

**File:** `task-sync.md`
```markdown
---
description: Sync task files with git
scope: project
gitignored: false
---

# Task Management - Sync Tasks

Git commit and push task files to sync across machines.

## What to do:

1. Change to project root directory
2. Run: `git add .claude/tasks/*.json`
3. Check for changes: `git diff --cached --quiet`
4. If changes exist:
   - Create commit message: "Update tasks [ISO 8601 timestamp]"
   - Run: `git commit -m "<message>"`
   - Run: `git push origin <current-branch>`
5. Display sync status

## Error Handling:

- No changes: Inform user, skip commit/push
- Network error: Show error, suggest retry
- Merge conflict: Display conflict info, suggest manual resolution
- Permission error: Check git credentials

## Output Format:

See main TASK-MANAGEMENT.md documentation for detailed output format.
```

---

### Phase 3: Testing (10 min)

**Goal:** Validate system works in `~/.claude/` first

#### Test 1: Create Tasks from Plan

1. Create test plan:
```bash
cat > ~/.claude/docs/test-sprint.md << 'EOF'
# Test Sprint

## HIGH PRIORITY
- [ ] Build task management system
  - Create slash commands
  - Parse markdown files
- [ ] Test on Mac environment

## MEDIUM PRIORITY
- [ ] Test on Claude Code Web
- [x] Document system architecture

## LOW PRIORITY
- [ ] Add advanced features (dependencies, tags)
EOF
```

2. Run: `/create-tasks ~/.claude/docs/test-sprint.md`

3. Verify:
   - `~/.claude/tasks/active.json` has 4 tasks
   - `~/.claude/tasks/completed.json` has 1 task
   - IDs are sequential
   - Priorities match headings
   - Source file/line recorded

#### Test 2: View Tasks

1. Run: `/tasks`
2. Verify output shows grouped/sorted tasks

#### Test 3: Update Task

1. Run: `/task-update 1 in_progress`
2. Run: `/tasks`
3. Verify task #1 status changed

#### Test 4: Complete Task

1. Run: `/task-complete 1`
2. Verify task moved to completed.json
3. Run: `/tasks` - task #1 should be gone

#### Test 5: Add Manual Task

1. Run: `/task-add`
2. Fill in details
3. Run: `/tasks`
4. Verify new task appears

#### Test 6: Sync

1. Run: `/task-sync`
2. Verify git commit created
3. Check GitHub for pushed changes

---

### Phase 4: Project Rollout (5 min per project)

**Goal:** Deploy to real projects

For each project:

1. **Copy structure:**
```bash
cd ~/dev/your-project
mkdir -p .claude/tasks
cp ~/.claude/tasks/*.json .claude/tasks/
touch .claude/tasks/.gitkeep
```

2. **Copy commands (optional for Web support):**
```bash
mkdir -p .claude/commands
cp ~/.claude/commands/task*.json .claude/commands/
cp ~/.claude/commands/create-tasks.md .claude/commands/
```

3. **Create guide:**
```bash
cat > .claude/TASKS.md << 'EOF'
# Project Task Management

This project uses `.claude/tasks/` for tracking work.

See: ~/.claude/docs/TASK-MANAGEMENT.md for full documentation.

## Quick Reference:
- `/create-tasks <file>` - Parse plan into tasks
- `/tasks` - Show active tasks
- `/task-add` - Add single task
- `/task-update <id>` - Update task
- `/task-complete <id>` - Mark done
- `/task-sync` - Git sync
EOF
```

4. **Verify .gitignore:**
```bash
# Ensure .claude/ is NOT ignored
grep -v "^\.claude/$" .gitignore > .gitignore.tmp && mv .gitignore.tmp .gitignore
```

5. **Initial commit:**
```bash
git add .claude/
git commit -m "Add task management system"
git push
```

---

## Advanced Features (Future)

### Task Dependencies

```json
{
  "id": 5,
  "title": "Deploy auth to production",
  "depends_on": [1, 2, 3],
  "status": "blocked"
}
```

Commands:
- Auto-block tasks when dependencies incomplete
- Auto-unblock when dependencies done
- `/task-deps 5` - Show dependency tree

### Task Templates

Create `.claude/tasks/templates/` with common patterns:
```json
{
  "name": "backend-api-endpoint",
  "tasks": [
    {"title": "Create route handler", "priority": "high"},
    {"title": "Add input validation", "priority": "high"},
    {"title": "Write unit tests", "priority": "medium"},
    {"title": "Update API docs", "priority": "low"}
  ]
}
```

Command: `/create-tasks --template backend-api-endpoint --context "user registration"`

### Integration with TodoWrite

Auto-sync between `.claude/tasks/active.json` and session todos:

- `/task-start 3` - Mark task in_progress + add to TodoWrite
- When TodoWrite item completed, auto-complete task in active.json
- Preserve task continuity across sessions

### Recurring Tasks

```json
{
  "id": 10,
  "title": "Weekly dependency updates",
  "recurrence": "weekly",
  "next_occurrence": "2025-11-23T00:00:00Z"
}
```

### Task Reports

- `/task-report` - Generate markdown report of completed tasks
- Group by time period, priority, tags
- Useful for sprint retrospectives, status updates

---

## Troubleshooting

### Tasks not syncing to Web

**Problem:** Changes on Mac not visible on Web

**Solution:**
1. On Mac: Run `/task-sync` to push
2. On Web: `git pull` to get latest
3. Verify `.claude/tasks/` is not in `.gitignore`

### Duplicate task IDs

**Problem:** Two tasks have same ID after parallel edits

**Solution:**
1. Manually edit JSON file
2. Reassign IDs sequentially
3. `/task-sync` to push fix

### Command not found on Web

**Problem:** `/create-tasks` doesn't work on Codespace

**Solution:**
1. Copy commands from `~/.claude/commands/` to project `.claude/commands/`
2. Commit and push
3. Pull on Web

---

## Migration Path

### From GitHub Issues

Export issues to markdown, then parse:

```bash
# Use GitHub API to export
gh issue list --json title,body,labels --state open > issues.json

# Convert to markdown plan
# Then: /create-tasks issues.md
```

### From Existing Todo Files

If you have TODO.md, BACKLOG.md, etc.:

```bash
/create-tasks TODO.md
/create-tasks BACKLOG.md --target backlog
```

---

## Best Practices

### 1. Regular Syncing
- Sync at start of session: `git pull`
- Sync at end of session: `/task-sync`
- Sync before switching machines

### 2. Granular Tasks
- Keep tasks small (1-4 hours of work)
- Large tasks → break into subtasks
- Use notes for acceptance criteria

### 3. Priority Discipline
- **Critical:** Production issues, blockers
- **High:** Sprint commitments
- **Medium:** Nice to have this sprint
- **Low:** Future work

### 4. Clean Completed Tasks
- Archive old completed tasks monthly
- Keep last 2 sprints in completed.json
- Export older tasks to docs/archive/

### 5. Source Linking
- Always link tasks to source docs
- Keep PRDs/plans updated
- Re-run `/create-tasks` when plans change (skip duplicates)

---

## Security & Privacy

### What to Track
✅ Feature work
✅ Bug fixes
✅ Technical debt
✅ Documentation tasks

### What NOT to Track
❌ Sensitive customer names
❌ API keys, passwords
❌ Private business strategy
❌ Personal tasks in work projects

### Public vs Private Repos

**Public Repos:**
- Use generic task descriptions
- No customer/company-specific details
- Sanitize notes before committing

**Private Repos:**
- Full context is safe
- Still avoid credentials in tasks

---

## Comparison with Alternatives

| Feature | This System | GitHub Issues | TodoWrite | Autopilot |
|---------|-------------|---------------|-----------|-----------|
| Works on Web | ✅ | ❌ | ✅ | ✅ |
| Works on Mac | ✅ | ✅ | ✅ | ✅ |
| Offline support | ✅ | ❌ | ✅ | ✅ |
| No external deps | ✅ | ❌ (`gh` CLI) | ✅ | ✅ |
| Parse PRDs | ✅ | ❌ | ❌ | ❌ |
| Persistent | ✅ | ✅ | ❌ | ✅ |
| Project-local | ✅ | ❌ | ✅ | ❌ |
| Cross-session | ✅ | ✅ | ❌ | ✅ |
| Git-synced | ✅ | ✅ | ❌ | ✅ |
| Use case | Task tracking | Issue management | Active session | Context state |

**When to use each:**
- **This system:** Project tasks, sprint planning, PRD execution
- **GitHub Issues:** Public bug reports, feature requests, community management
- **TodoWrite:** Active session work, real-time progress tracking
- **Autopilot:** Context preservation, resume after `/clear`

---

## Success Metrics

After implementation, you should be able to:

✅ Parse a 50-line PRD into tasks in < 30 seconds
✅ Work on Mac, push, pull on Web seamlessly
✅ Never lose task state (always in git)
✅ See what you worked on last week via completed.json
✅ Break down large projects systematically
✅ Sync tasks across machines in < 10 seconds

---

## Next Steps

1. **Phase 1:** Test in `~/.claude/` (PAI workspace)
2. **Phase 2:** Create global commands in `~/.claude/commands/`
3. **Phase 3:** Test with real PAI tasks (skills, agents, docs)
4. **Phase 4:** Roll out to first real project
5. **Phase 5:** Iterate based on real usage
6. **Phase 6:** Add advanced features (dependencies, templates)

---

**Version History:**
- v1.0.0 (2025-11-16): Initial design and implementation guide

**Author:** Alex (Your PAI)
**Tested:** Not yet - awaiting implementation
**Status:** 📝 Documentation complete, ready for implementation
