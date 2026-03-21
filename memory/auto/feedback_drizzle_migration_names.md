---
name: drizzle-migration-naming
description: Always use --name flag when generating Drizzle migrations to keep names descriptive
type: feedback
---

Always use `--name` when generating Drizzle migrations: `bunx drizzle-kit generate --name=descriptive-name`.

**Why:** Without `--name`, Drizzle generates random comic-book-character names (e.g., `0033_pale_silvermane.sql`) that are meaningless. The codebase convention is descriptive names (e.g., `0029_coach_search_trgm_indexes.sql`). Migrations 0030-0032 slipped through without names and can't be renamed since they're already applied.

**How to apply:** Every time I run `drizzle-kit generate`, include `--name=kebab-case-description`. Never rely on the default random name.
