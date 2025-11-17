---
description: Restore saved task state and resume autopilot work
allowed-tools: [Read, Write, Bash, TodoWrite]
model: sonnet
---

# Restore Autopilot State

You are being asked to restore a previously saved work state and continue where you left off.

## Instructions

1. **Check for Saved State:**
   - Verify `~/.claude/autopilot/current-task.json` exists
   - If not found, inform user no saved state available

2. **Load State Files:**
   - Read `current-task.json` - get task description, progress, next steps
   - Read `decisions-log.md` - understand decisions made
   - Read `resume-plan.md` - get immediate next actions
   - Read `context-snapshot.json` - understand working context

3. **Restore Working Context:**
   - Change to working directory if needed
   - Check git status matches expected state
   - Verify key files still exist
   - Load any necessary files mentioned in key_files

4. **Restore Todo List:**
   - Recreate TodoList from saved todos using TodoWrite tool
   - Mark appropriate task as in_progress
   - Ensure continuity from saved state

5. **Provide Resumption Summary:**
   Display to user:
   ```
   📋 RESTORED FROM CHECKPOINT

   🔍 TASK: [task description]

   ✅ PROGRESS COMPLETED:
   - [summary of what was done]

   🎯 NEXT STEPS:
   1. [immediate next action]
   2. [following action]

   📊 CONTEXT:
   - Working directory: [path]
   - Files modified: [list]
   - Time since save: [duration]

   ➡️ Resuming work now...
   ```

6. **Resume Execution:**
   - Begin executing the first item in "next steps"
   - Continue working as if no interruption occurred
   - Update todo list as you progress

7. **Clean Up State Files:**
   - After successful restoration, you can optionally:
     - Move state files to `~/.claude/autopilot/history/[timestamp]/`
     - Or keep them for manual review
   - Don't delete until task fully completes

## Success Criteria

- State successfully loaded from all 4 files
- TodoList restored and active
- Work continues seamlessly from where it stopped
- User sees clear resumption summary
- No context or progress lost
