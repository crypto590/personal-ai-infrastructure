---
name: remember
description: Add something to project memory for future sessions. Use /remember <what> to save decisions, focus areas, or open items.
argument-hint: "<what to remember>"
---

# Remember Command

Add information to this project's persistent memory.

## Usage

```
/remember We chose PostgreSQL for better JSON support
/remember focus: Building the auth system
/remember todo: Add rate limiting to API
```

## Instructions for Alex

When this skill is invoked with `$ARGUMENTS`:

1. **Read the memory file** for current project:
   ```python
   import hashlib
   from pathlib import Path
   cwd = "<current working directory>"
   project_hash = hashlib.sha256(cwd.encode()).hexdigest()[:12]
   memory_file = Path.home() / ".claude" / "memory" / "projects" / f"{project_hash}.json"
   ```

2. **Parse the input** and categorize:
   - Starts with `focus:` → Update `currentFocus`
   - Starts with `todo:` → Add to `openItems` array
   - Otherwise → Add to `keyDecisions` array

3. **Update the JSON file** with the new information

4. **Sync to Obsidian** at `~/Desktop/The_Hub/AI-Memory/[project].md`

5. **Confirm** what was remembered
