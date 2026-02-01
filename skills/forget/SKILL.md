---
name: forget
description: Remove something from project memory. Use /forget <what> to remove items or /forget all to clear everything.
argument-hint: "<what to forget | all>"
---

# Forget Command

Remove information from this project's persistent memory.

## Usage

```
/forget PostgreSQL decision
/forget todo: rate limiting
/forget all
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

2. **Parse the input**:
   - `all` → Clear all memory (reset to empty state)
   - `focus:` prefix → Clear `currentFocus`
   - `todo:` prefix → Remove matching item from `openItems`
   - Otherwise → Remove matching item from `keyDecisions`

3. **Update the JSON file**

4. **Sync to Obsidian** at `~/Desktop/The_Hub/AI-Memory/[project].md`

5. **Confirm** what was forgotten
