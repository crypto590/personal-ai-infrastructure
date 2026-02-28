---
name: memory
description: View current project memory - what Alex remembers about this project across sessions.
allowed-tools: Bash(python:*), Read, Glob
compatibility: "Requires Python 3.10+ for hashlib-based project hashing"
metadata:
  author: coreyyoung
  version: 1.0.0
  category: memory
  tags: [memory, persistence, project-state, read-only]
---

# Memory Command

Display the current memory state for this project.

## Related Commands

- `/remember <what>` - Add to memory
- `/forget <what>` - Remove from memory

## Instructions for Alex

When this skill is invoked:

1. **Read the memory file** for current project:
   ```python
   import hashlib
   from pathlib import Path
   cwd = "<current working directory>"
   project_hash = hashlib.sha256(cwd.encode()).hexdigest()[:12]
   memory_file = Path.home() / ".claude" / "memory" / "projects" / f"{project_hash}.json"
   ```

2. **Display memory contents** in a formatted way:
   - Project info (name, path, last updated)
   - Session count
   - Current focus (if set)
   - Key decisions (if any)
   - Open items (if any)
   - Recent files (if any)

3. If no memory exists, inform user and suggest using `/remember` to start.

## Memory Structure

```json
{
  "project": {
    "path": "/path/to/project",
    "name": "project-name",
    "lastUpdated": "2026-01-31T..."
  },
  "currentFocus": "What we're working on",
  "recentFiles": ["src/foo.ts", "lib/bar.py"],
  "keyDecisions": ["Chose X because Y"],
  "openItems": ["TODO: finish X"],
  "sessionCount": 5
}
```

## File Locations

- **Memory Storage:** `~/.claude/memory/projects/[hash].json`
- **Obsidian Sync:** `~/Desktop/The_Hub/AI-Memory/[project].md`
