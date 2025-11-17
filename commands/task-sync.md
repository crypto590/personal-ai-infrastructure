---
description: Git commit and push task files
argument-hint: [message]
allowed-tools: Bash(git:*)
model: claude-3-5-haiku-20241022
gitignored: false
---

# Sync Tasks with Git

Commit and push task files to sync across machines.

## Arguments

- `[message]` - Optional custom commit message

## Usage Examples

```
/task-sync
/task-sync Sprint 1 tasks completed
/task-sync Added new feature tasks
```

---

## Instructions

### 1. Determine Working Directory

Check if `.claude/tasks/` exists in current directory:
- If yes, we're in a project (use project root)
- If no, we're in global PAI (use `~/.claude/`)

Set `$WORK_DIR` to appropriate directory.

### 2. Check for Task Files

Verify task files exist:
- If project: `.claude/tasks/*.json`
- If global: `~/.claude/tasks/*.json`

If no task files found:
```
⚠️  WARNING: No task files found

Expected location: <path>

Create tasks first using /task-add or /create-tasks
```

### 3. Run Git Operations

Execute the following git commands in `$WORK_DIR`:

**a) Add task files:**
```bash
git add .claude/tasks/*.json
```
OR (if global):
```bash
git add tasks/*.json
```

**b) Check for changes:**
```bash
git diff --cached --quiet
```

**c) If changes exist:**

Generate commit message:
- If `$ARGUMENTS` provided: use `$ARGUMENTS`
- Otherwise: `"Update tasks <ISO 8601 timestamp>"`

Create commit:
```bash
git commit -m "<message>"
```

**d) Push to remote:**

Get current branch:
```bash
git branch --show-current
```

Push changes:
```bash
git push origin <current-branch>
```

### 4. Handle Each Step Result

**Add (step a):**
- Success: ✅ Staged task files
- Error: Show git error, suggest checking file permissions

**Check changes (step b):**
- Changes exist: Proceed to commit
- No changes: ⏭️  Skip commit/push, inform user

**Commit (step c):**
- Success: ✅ Committed with message
- Error: Show git error, check for git config issues

**Push (step d):**
- Success: ✅ Pushed to remote
- Network error: ⚠️  Could not push (offline or connection issue)
- Permission error: ⚠️  Push failed (check credentials)
- Merge needed: ⚠️  Pull required (remote has changes)

### 5. Display Sync Status

**Success:**
```
🔄 TASK SYNC

Add: ✅ Staged .claude/tasks/*.json
Commit: ✅ "<commit message>"
Push: ✅ Pushed to origin/<branch>

Tasks are now synced across all machines.

Next steps:
- On other machines: git pull to get latest tasks
- Continue working with /tasks, /task-add, etc.
```

**No changes:**
```
🔄 TASK SYNC

Add: ✅ Staged task files
Commit: ⏭️  No changes to commit
Push: ⏭️  Nothing to push

Tasks are already up to date.
```

**Partial success (push failed):**
```
🔄 TASK SYNC

Add: ✅ Staged task files
Commit: ✅ "Update tasks 2025-11-17T10:00:00Z"
Push: ⚠️  Could not push to remote

Error: <git error message>

Changes are committed locally. Push will happen when connection restored.
Try: git push origin <branch> manually when online.
```

**Merge conflict:**
```
🔄 TASK SYNC

Add: ✅ Staged task files
Commit: ✅ "Update tasks 2025-11-17T10:00:00Z"
Push: ⚠️  Remote has new changes

You need to pull first:
  git pull origin <branch>

Then resolve any conflicts and push again.
```

---

## Examples

**Standard sync:**
```
> /task-sync

🔄 TASK SYNC

Add: ✅ Staged .claude/tasks/*.json
Commit: ✅ "Update tasks 2025-11-17T10:00:00Z"
Push: ✅ Pushed to origin/main

Tasks are now synced across all machines.
```

**Custom message:**
```
> /task-sync Completed sprint 1 auth tasks

🔄 TASK SYNC

Add: ✅ Staged .claude/tasks/*.json
Commit: ✅ "Completed sprint 1 auth tasks"
Push: ✅ Pushed to origin/feature/auth

Tasks are now synced across all machines.
```

**No changes:**
```
> /task-sync

🔄 TASK SYNC

Add: ✅ Staged task files
Commit: ⏭️  No changes to commit
Push: ⏭️  Nothing to push

Tasks are already up to date.
```

**Offline:**
```
> /task-sync

🔄 TASK SYNC

Add: ✅ Staged task files
Commit: ✅ "Update tasks 2025-11-17T10:00:00Z"
Push: ⚠️  Could not push to remote

Error: Could not resolve host github.com

Changes are committed locally. Push will happen when connection restored.
Try: git push origin main manually when online.
```

---

## Workflow Integration

**Recommended sync points:**

1. **After creating tasks:** `/create-tasks` → `/task-sync`
2. **After completing tasks:** `/task-complete 5` → `/task-sync`
3. **Before switching machines:** `/task-sync` on current machine
4. **After switching machines:** `git pull` on new machine
5. **End of work session:** `/task-sync` to save progress

**Multi-machine workflow:**

On Mac:
```
/create-tasks docs/sprint-1.md
/task-sync
```

On Web (Codespace):
```
git pull
/tasks
/task-update 3 in_progress
/task-sync
```

Back on Mac:
```
git pull
/tasks
```

---

## Error Recovery

**Push rejected (force push needed):**

Don't use this command. Instead:
1. Check what diverged: `git log origin/<branch>..<branch>`
2. Pull and merge: `git pull origin <branch>`
3. Resolve conflicts manually
4. Run `/task-sync` again

**Corrupted task file:**

If JSON is invalid:
1. Check syntax: `cat .claude/tasks/active.json | python -m json.tool`
2. Fix JSON manually or restore from git
3. Commit fix: `/task-sync "Fixed corrupted task file"`

**Wrong directory:**

If you accidentally synced wrong project:
1. Check git remote: `git remote -v`
2. Revert last commit: `git reset --soft HEAD~1`
3. Change to correct directory
4. Run `/task-sync` in correct location
