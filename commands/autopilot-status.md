---
description: Check autopilot system status and saved state
allowed-tools: [Read, Bash]
model: haiku
---

# Autopilot Status

Check the current status of the autopilot system.

## Instructions

1. **Check for Saved State:**
   - Look for `~/.claude/autopilot/current-task.json`
   - If exists, read and display key information

2. **Check Context Usage:**
   - Display current context token usage from environment
   - Show threshold status (75% = 150k tokens)

3. **Display Status:**

   ```
   🤖 AUTOPILOT STATUS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📊 Context Usage: [current] / 200,000 tokens ([percentage]%)
   ⚠️  Threshold: 150,000 tokens (75%)

   💾 Saved State: [YES/NO]

   [If saved state exists:]
   📋 Task: [task description]
   ⏰ Saved: [timestamp]
   📈 Progress: [summary]

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Available Commands:
   • /save-state - Checkpoint current work
   • /restore-state - Resume saved work
   • /autopilot-status - View this status
   ```

4. **Provide Recommendations:**
   - If context > 75%: suggest running /save-state
   - If saved state exists: suggest /restore-state
   - If context < 50%: system healthy, continue working
