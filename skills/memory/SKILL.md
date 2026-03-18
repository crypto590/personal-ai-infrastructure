---
name: memory
description: Query the unified memory system. Subcommands — search, product, decisions, preferences, all, stats, add-product.
argument-hint: "[search <query> | product <name> | decisions | preferences | all | stats | add-product <name> <path>]"
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Memory Command

Query the unified Neon Postgres memory system.

## Usage

```
/memory                         — Show memories for current product
/memory search <query>          — Full-text search across all products
/memory product <name>          — All memories for a specific product
/memory decisions               — Decisions with rationale
/memory preferences             — Cross-project preferences
/memory all                     — Everything grouped by product
/memory stats                   — Counts by product/type/salience
/memory add-product <name> <path> — Register product grouping
```

## Instructions for Alex

When this skill is invoked with `$ARGUMENTS`:

### Default (no args) — Current product memories
```bash
uv run python3 -c "
import sys, json; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import detect_product, get_by_product, format_episode_display
product = detect_product('$CWD')
episodes = get_by_product(product, limit=30)
print(f'=== {product} — {len(episodes)} episodes ===\n')
for ep in episodes:
    print(format_episode_display(ep))
    print()
if not episodes:
    print('No memories yet. Use /remember to start.')
"
```

### `search <query>` — Full-text search
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import search_text, format_episode_display
results = search_text('$QUERY', limit=20)
print(f'Found {len(results)} results:\n')
for ep in results:
    print(format_episode_display(ep))
    print()
"
```

### `product <name>` — Product-specific
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import get_by_product, format_episode_display
episodes = get_by_product('$PRODUCT', limit=50)
print(f'=== $PRODUCT — {len(episodes)} episodes ===\n')
for ep in episodes:
    print(format_episode_display(ep))
    print()
"
```

### `decisions` — Decisions with rationale
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import get_decisions, detect_product, format_episode_display
product = detect_product('$CWD')
episodes = get_decisions(product=product, limit=20)
print(f'=== Decisions ({product}) ===\n')
for ep in episodes:
    print(format_episode_display(ep))
    print()
"
```

### `preferences` — Cross-project preferences
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import get_preferences, format_episode_display
episodes = get_preferences(limit=20)
print(f'=== Preferences ({len(episodes)}) ===\n')
for ep in episodes:
    print(format_episode_display(ep))
    print()
"
```

### `all` — Everything grouped by product
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import get_all_grouped, format_episode_display
grouped = get_all_grouped()
for product, episodes in grouped.items():
    print(f'=== {product} ({len(episodes)} episodes) ===\n')
    for ep in episodes:
        print(format_episode_display(ep))
        print()
"
```

### `stats` — Statistics
```bash
uv run python3 -c "
import sys, json; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import get_stats
stats = get_stats()
print(json.dumps(stats, indent=2, default=str))
"
```

### `add-product <name> <path>` — Register product
```bash
uv run python3 -c "
import sys; sys.path.insert(0, '$HOME/.claude/hooks')
from memory_db import register_product
register_product('$PATH_PREFIX', '$PRODUCT_NAME', '$DISPLAY_NAME')
print('Product registered: $PRODUCT_NAME → $PATH_PREFIX')
"
```

## Related Commands

- `/remember <what>` — Save a new memory
- `/forget <what>` — Remove a memory
