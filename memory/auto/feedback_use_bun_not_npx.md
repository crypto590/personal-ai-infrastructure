---
name: feedback_use_bun_not_npx
description: Always use bun/bunx instead of npm/npx in the athlead project
type: feedback
---

Use `bun` and `bunx` for all package management and script running — never `npx` or `npm`.

**Why:** The project uses Bun workspaces (not npm), and the user expects consistency with their toolchain.

**How to apply:** Replace any `npx` with `bunx` and `npm` with `bun` when running commands in the athlead project.
