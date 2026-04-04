---
name: Skills cannot be nested
description: Skills must be top-level directories under ~/.claude/skills/, not nested under category subdirectories
type: feedback
---

Skills must live at `~/.claude/skills/<skill-name>/`, not `~/.claude/skills/<category>/<skill-name>/`.

**Why:** The user corrected placement of a new skill under `skills/technical/neon/` — skills can't be nested under category directories.

**How to apply:** When creating new skills, always use `~/.claude/skills/<skill-name>/SKILL.md` as the path. Ignore existing `technical/`, `business/`, `domain/` subdirectories — those may be legacy or have a different purpose.
