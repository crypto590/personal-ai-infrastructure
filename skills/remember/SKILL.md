---
name: remember
description: Save a typed memory episode to Neon Postgres. Use /remember <what> to save decisions, preferences, insights, or facts.
argument-hint: "<what to remember>"
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Remember Command

Save a memory episode to the unified Neon Postgres memory system.

## Usage

```
/remember decision: Use Neon Postgres for memory because it supports pgvector
/remember preference: Always use TypeScript for new services
/remember insight: Cold starts on Neon take ~500ms after 5min idle
/remember fact: Athlead uses Clerk for authentication
/remember We chose PostgreSQL for better JSON support
```

## Instructions for Alex

When this skill is invoked with `$ARGUMENTS`:

1. **Parse the input** to determine episode type and content:
   - Starts with `decision:` → type=decision, salience=7
   - Starts with `preference:` → type=preference, salience=8
   - Starts with `insight:` → type=insight, salience=6
   - Starts with `fact:` → type=fact, salience=5
   - Starts with `failure:` → type=failure, salience=7
   - No prefix → type=fact, salience=5

2. **Extract reasoning** if present:
   - Look for "because", "since", "reason:", "why:" to split content from reasoning
   - Example: "Use X because Y" → content="Use X", reasoning="Y"

3. **Run the Python command** to save to Neon:
   ```bash
   uv run python3 -c "
   import sys; sys.path.insert(0, '$HOME/.claude/hooks')
   from memory_db import add_episode, detect_product
   product = detect_product('$CWD')
   eid = add_episode(
       episode_type='<TYPE>',
       subject='<SUBJECT_MAX_120>',
       content='<FULL_CONTENT>',
       reasoning='<REASONING_OR_NONE>',
       salience=<SALIENCE>,
       tags=[<RELEVANT_TAGS>],
       product=product,
       project_path='$CWD',
   )
   print(f'Saved: {eid}')
   "
   ```

4. **Export to Obsidian** after saving:
   ```bash
   uv run ~/.claude/hooks/memory_obsidian.py --product <PRODUCT>
   ```

5. **Confirm** what was saved with type, salience, and product.
