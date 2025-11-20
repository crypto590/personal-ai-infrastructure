# PAI Hook System

Automated context injection and notification system for Claude Code subagents.

## Hook Architecture

### SubagentStart Hook
**File:** `subagent_start.py`
**Event:** Fires when a subagent initializes, before it does any work
**Purpose:** Auto-inject PAI context, security reminders, and current date

**What it does:**
1. Loads CORE skill from `~/.claude/skills/CORE/SKILL.md`
2. Injects security reminders (git safety, ~/.claude/ privacy)
3. Provides current date/time
4. Logs all context loading to `logs/hooks/context_loading.log`

**Token Efficiency:**
- Loads full CORE skill (~5000 chars) automatically
- Eliminates need for manual context loading in agent templates
- Ensures every subagent has consistent PAI context

### SubagentStop Hook
**File:** `subagent_stop.py`
**Event:** Fires when a subagent completes its task
**Purpose:** Handle all post-completion tasks - transcripts, notifications, validation

**What it does:**
1. **Transcript Archival**: Saves agent transcript to `agent-output-context/` for later evaluation (requires Claude Code 2.0.42+)
2. **Voice Notifications**: Extracts completion message (looks for 🗣️ CUSTOM COMPLETED or 🎯 COMPLETED) and announces via voice
3. **Voice Routing**: Maps agent name to voice ID for personalized announcements
4. **Logging**: Records all operations to `logs/hooks/subagent_stop.log`
5. **Future**: Quality gates, output format validation, completion verification

**Transcript Storage:**
- Organized by date and session ID: `agent-output-context/YYYY-MM-DD/session-id/NNN-agent-name.jsonl`
- Session ID: First 8 chars of `agent_id` (groups related agents in same workflow)
- Sequential numbering: 001, 002, 003 (order agents ran within session)
- Uses `agent_id` and `agent_transcript_path` metadata from SubagentStop event
- See `agent-output-context/README.md` for analysis workflows

**Voice ID Mapping:**
- Each agent type can have unique voice ID
- Falls back to Alex's voice (O4lTuRmkE5LyjL2YhMIg) if not mapped
- See lines 31-60 in `subagent_stop.py` for mappings

**Extensibility:**
This hook is designed as a central point for all subagent completion tasks. Future additions:
- Output format validation (check for required sections)
- Task completion verification (were all TODOs addressed?)
- Quality gates (security checks, test requirements)
- Metrics collection (execution time, token usage)

## Impact on Agent Templates

### Before SubagentStart Hook
Agents needed this boilerplate:

```markdown
# 🚨🚨🚨 MANDATORY FIRST ACTION - DO THIS IMMEDIATELY 🚨🚨🚨

**BEFORE DOING OR SAYING ANYTHING, YOU MUST:**

1. **LOAD THE PAI GLOBAL CONTEXT FILE IMMEDIATELY!**
   - Read `../../skills/core/SKILL.md` - The complete PAI context

**DO NOT LIE ABOUT LOADING THIS FILE. ACTUALLY LOAD IT FIRST.**

**EXPECTED OUTPUT UPON COMPLETION:**
"✅ PAI Context Loading Complete"
```

### After SubagentStart Hook
Simplified to:

```markdown
# Agent Context

**PAI Context:** Automatically loaded via SubagentStart hook.
**Your Identity:** Refer to PAI CORE context for global preferences and security.
```

**Result:** ~200+ lines removed from each agent template

### Before SubagentStop Hook
Agents needed this boilerplate:

```markdown
# CRITICAL OUTPUT AND VOICE SYSTEM REQUIREMENTS

After completing ANY task, you MUST:

```bash
curl -X POST http://localhost:8888/notify -H "Content-Type: application/json" \
  -d '{"message":"Agent completed task","voice_id":"...","voice_enabled":true}'
```
```

### After SubagentStop Hook
Removed entirely - voice notifications and transcript archival handled automatically by hook.

## Other Hooks

- **PreToolUse**: Pre-execution checks and validation
- **PostToolUse**: Context monitoring and post-execution tasks
- **UserPromptSubmit**: Context loader for main agent
- **SessionStart**: Auto-restore autopilot state
- **Stop**: Main agent voice notification (alex_voice.py)
- **Notification**: General notification handler
- **PreCompact**: Backup before context compaction

## Logs

All hooks write to `/Users/coreyyoung/.claude/logs/hooks/`:
- `context_loading.log` - SubagentStart context injection
- `subagent_stop.log` - SubagentStop operations (transcripts, voice, validation)
- `voice_notifications.log` - Legacy log file (can be deleted, replaced by subagent_stop.log)
- Other hook-specific logs as needed

## Configuration

Hooks configured in `/Users/coreyyoung/.claude/settings.json`:

```json
{
  "hooks": {
    "SubagentStart": [/* ... */],
    "SubagentStop": [/* ... */],
    // ... other hooks
  }
}
```

## Testing

Test SubagentStart hook:
```bash
echo '{"agentName": "test-agent"}' | \
  uv run /Users/coreyyoung/.claude/hooks/subagent_start.py
```

Test SubagentStop hook:
```bash
echo '{"agentName": "test-agent", "agent_id": "12345678", "agent_transcript_path": "/tmp/test.jsonl", "output": "🗣️ CUSTOM COMPLETED: Task done"}' | \
  uv run /Users/coreyyoung/.claude/hooks/subagent_stop.py
```

## Benefits

1. **DRY Principle**: Context loading logic in one place, not every agent
2. **Consistency**: Every subagent gets same base context automatically
3. **Token Efficiency**: No redundant instructions in agent templates
4. **Maintainability**: Update hook once, affects all agents
5. **Voice Notifications**: Automatic completion announcements
6. **Separation of Concerns**: Infrastructure (hooks) vs behavior (templates)
