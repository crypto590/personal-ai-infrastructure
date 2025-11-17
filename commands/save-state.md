---
description: Save current task state for autopilot continuation
allowed-tools: [Read, Write, Bash, TodoWrite]
model: sonnet
---

# Save Autopilot State

You are being asked to checkpoint the current work state so that it can be resumed after a context clear.

## Instructions

1. **Capture Current State:**
   - Read the current todo list from `~/.claude/todos/` (if exists)
   - Identify the active task being worked on
   - Summarize progress made so far
   - List key decisions and findings

2. **Save State Files:**

   Create `~/.claude/autopilot/current-task.json`:
   ```json
   {
     "timestamp": "ISO-8601 timestamp",
     "task_description": "What we're working on",
     "progress_summary": "What's been completed",
     "next_steps": ["Step 1", "Step 2"],
     "context_token_usage": "Current token count",
     "todos": [/* copy of todo list */],
     "key_files": [/* paths to important files */]
   }
   ```

   Create `~/.claude/autopilot/decisions-log.md`:
   ```markdown
   # Decision Log - [Date]

   ## Task Overview
   [Description]

   ## Key Decisions Made
   - Decision 1: [rationale]
   - Decision 2: [rationale]

   ## Important Findings
   - Finding 1
   - Finding 2

   ## Challenges Encountered
   - Challenge 1: [how resolved]
   ```

   Create `~/.claude/autopilot/resume-plan.md`:
   ```markdown
   # Resume Plan

   ## Where We Left Off
   [Last action taken]

   ## Next Immediate Steps
   1. [Step]
   2. [Step]

   ## Context to Reload
   - Files: [list]
   - Commands run: [list]
   - Dependencies: [list]
   ```

3. **Create Context Snapshot:**

   Save metadata in `~/.claude/autopilot/context-snapshot.json`:
   ```json
   {
     "working_directory": "pwd output",
     "git_status": "git status output",
     "git_branch": "current branch",
     "recent_commands": [/* last 5 bash commands */],
     "modified_files": [/* files changed this session */]
   }
   ```

4. **Verify Save:**
   - Confirm all 4 files created
   - Display summary of what was saved
   - Tell user: "State saved. Ready for /clear - run /restore-state after clearing."

## Success Criteria

- All state files created in `~/.claude/autopilot/`
- Task can be resumed from these files alone
- User understands next steps (run /clear, then work resumes)
