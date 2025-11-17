# Task Management Framework - Supplementary Documentation

**Version:** 1.0.0
**Primary Reference:** `~/.claude/skills/business/task-management/SKILL.md`
**Implementation:** `~/.claude/skills/business/task-management/scripts/task_manager.py`

---

## Purpose

This file provides **design decisions and historical context**. For active usage, always reference SKILL.md first.

---

## Quick Reference

### Commands
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

### Task JSON Schema
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

### Container Format
```json
{
  "version": "1.0.0",
  "source": "docs/sprint-1.md",
  "created": "2025-11-16T14:30:00Z",
  "last_updated": "2025-11-16T15:45:00Z",
  "tasks": [
    { /* task object */ }
  ]
}
```

---

## Design Decisions

### Why Python Script vs Slash Commands?
- **Atomic operations** - No partial JSON writes
- **Validation built-in** - Type checking, field validation
- **Self-contained** - `uv run --script` needs no cross-imports
- **No cache pollution** - No `__pycache__` directories
- **Consistent behavior** - Same tool across all environments

### Why `uv run --script`?
- Zero setup - runs inline with dependencies declared in script
- No virtual environment management
- Fast execution
- Works identically on Mac and Claude Code Web

### Why Project-Local (`.claude/tasks/`)?
- Works in sandboxed environments (Claude Code Web/Codespaces)
- No `gh` CLI dependency
- Git-synced automatically with project
- Each project has isolated task tracking

### Why active/backlog/completed Split?
- **active.json** - Current sprint/work (pending, in_progress, blocked)
- **backlog.json** - Future work, not yet started
- **completed.json** - Archive for retrospectives, metrics

---

## Smart Markdown Parsing

The `create` command recognizes:

| Pattern | Action |
|---------|--------|
| `# HIGH PRIORITY` or `## CRITICAL` | Set priority: high/critical |
| `- [ ]` unchecked | Create pending task in active.json |
| `- [x]` checked | Create completed task in completed.json |
| Indented bullets | Add as task notes |
| Keywords (backend, frontend, auth) | Extract as tags |
| `**BLOCKED**` or 🚫 | Set status: blocked |

---

## Troubleshooting

### Tasks not syncing to Web
**Problem:** Changes on Mac not visible on Web

**Solution:**
1. On Mac: Commit and push task changes
2. On Web: `git pull` to get latest
3. Verify `.claude/tasks/` is not in `.gitignore`

### Duplicate Task IDs
**Problem:** Two tasks have same ID after parallel edits

**Solution:**
1. Manually edit JSON file
2. Reassign IDs sequentially (find max ID + increment)
3. Commit and push fix

### Script Not Found
**Problem:** `uv run` can't find task_manager.py

**Solution:**
- Use absolute path: `~/.claude/skills/business/task-management/scripts/task_manager.py`
- Verify file exists: `ls -la ~/.claude/skills/business/task-management/scripts/`

---

## Integration with Other Tools

### TodoWrite (Session Tracking)
- **Task Management** creates persistent tasks from documents
- **TodoWrite** tracks sub-steps within a single task during active session
- Example: Task #5 "Fix auth bug" → TodoWrite: [debug, patch, test, commit]

### Autopilot (State Management)
- Autopilot handles context state across sessions
- Task Management handles work item tracking
- Complementary, not overlapping

### GitHub Issues
- GitHub Issues: Public bug reports, community features
- Task Management: Internal sprint work, private tasks
- Can export GitHub Issues → markdown → parse with task_manager.py

---

## Best Practices

### Regular Syncing
- Start session: `git pull`
- End session: Commit and push task changes
- Before switching machines: Sync

### Granular Tasks
- Keep tasks small (1-4 hours of work)
- Large tasks → break into subtasks
- Use notes field for acceptance criteria

### Priority Discipline
- **Critical:** Production issues, blockers
- **High:** Sprint commitments
- **Medium:** Nice to have this sprint
- **Low:** Future work, backlog

### Clean Archives
- Archive old completed tasks monthly
- Keep last 2 sprints in completed.json
- Export older tasks to docs/archive/

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

---

## Version History

- **v1.0.0** (2025-11-17): Simplified documentation, focus on design decisions
- **v0.1.0** (2025-11-16): Initial comprehensive guide (1010 lines - replaced by this version)

---

**For Implementation Details:** See SKILL.md
**For Script Source:** See scripts/task_manager.py
