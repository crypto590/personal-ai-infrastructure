---
name: forget
description: Remove a memory episode (append-only supersession). Use /forget <query> to find and deactivate memories.
argument-hint: "<what to forget | all>"
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Forget Command

Supersede (soft-delete) memory episodes. Uses append-only supersession — nothing is hard deleted.

## Usage

```
/forget PostgreSQL decision
/forget rate limiting todo
/forget all athlead
```

## Instructions for Alex

When this skill is invoked with `$ARGUMENTS`:

1. **Search for matching episodes**:
   ```bash
   uv run python3 -c "
   import sys, json; sys.path.insert(0, '$HOME/.claude/hooks')
   from memory_db import find_matching, detect_product, format_episode_display
   product = detect_product('$CWD')
   results = find_matching('$QUERY', product=product, limit=10)
   for ep in results:
       print(format_episode_display(ep))
       print('  ID:', ep['id'])
       print()
   if not results:
       print('No matching episodes found.')
   "
   ```

2. **Show matches** to user and confirm which to forget.

3. **Supersede selected episodes**:
   ```bash
   uv run python3 -c "
   import sys; sys.path.insert(0, '$HOME/.claude/hooks')
   from memory_db import soft_delete
   soft_delete('<EPISODE_UUID>')
   print('Episode superseded.')
   "
   ```

4. **Export updated state** to Obsidian:
   ```bash
   uv run ~/.claude/hooks/memory_obsidian.py --product <PRODUCT>
   ```

5. **Confirm** what was forgotten.

## Special Cases

- `all` → Search broadly, confirm before batch supersession
- If query matches multiple episodes, show all and let user choose
