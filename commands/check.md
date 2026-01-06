---
description: Run project validation (types, lint, tests) before PR
allowed-tools: Bash, Read, Glob
---

# Pre-PR Check

Run validation checks appropriate for this project before creating a PR.

## Instructions

1. **Detect project type** by checking for:
   - `package.json` + `bun.lock` → Bun/Node project
   - `package.json` + `turbo.json` → Turborepo monorepo
   - `pyproject.toml` → Python/uv project
   - `Package.swift` → Swift project
   - `build.gradle.kts` → Kotlin project

2. **Run checks in order** (fast → slow):

   **For Bun/Turbo projects:**
   ```
   bun run check-types    # TypeScript validation
   bun lint               # ESLint
   bun test               # Tests (if requested)
   ```

   **For Python/uv projects:**
   ```
   uv run ruff check .    # Linting
   uv run pyright         # Type checking
   uv run pytest -x       # Tests (if requested)
   ```

   **For Swift projects:**
   ```
   swift build            # Type checking
   swift test             # Tests (if requested)
   ```

3. **Report results** in this format:
   ```
   ## Pre-PR Check Results

   | Check | Status | Details |
   |-------|--------|---------|
   | Types | ✅/❌ | [errors if any] |
   | Lint  | ✅/❌ | [warnings/errors] |
   | Tests | ✅/❌/⏭️ | [failures or skipped] |

   **Ready for PR**: Yes/No
   ```

4. **If issues found**: List them with file:line references and offer to fix.

## Arguments

- No args: Run types + lint only (fast)
- `--full` or `all`: Include tests
- `--fix`: Auto-fix lint issues where possible

$ARGUMENTS
