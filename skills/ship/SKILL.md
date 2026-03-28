---
name: ship
effort: high
argument-hint: "[commit message]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
description: "Build, version, and ship pipeline. Runs build/lint/test, pre-landing review, auto-versions, changelog, logical commits, and opens PR."
metadata:
  last_reviewed: 2026-03-20
  review_cycle: 90
---

# Ship — Build, Version, Ship Pipeline

Non-interactive pipeline that takes code from "ready" to "PR opened."
Pauses only for: merge conflicts, test failures, MINOR/MAJOR version bumps, critical review issues.

---

## Pipeline Steps

### Step 1: Detect Base Branch

Determine the target branch for the PR:

1. **Check for existing PR** — If the current branch already has an open PR, use that PR's base branch.
2. **Fall back to repo default** — Query `gh repo view --json defaultBranchRef` for the repository's default branch.
3. **Fall back to `main`** — If neither of the above resolves, use `main`.

Store the resolved base branch for all subsequent steps.

```bash
# Check for existing PR base
gh pr view --json baseRefName -q '.baseRefName' 2>/dev/null

# Repo default branch
gh repo view --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null

# Ultimate fallback
echo "main"
```

---

### Step 2: Merge Upstream Changes

Bring the current branch up to date with the base branch.

```bash
git fetch origin <base>
git merge origin/<base>
```

- If **Graphite** is detected (`gt` command available), use `gt sync` instead.
- **PAUSE** if merge conflicts occur:
  - Show the list of conflicting files.
  - Wait for user to resolve conflicts or ask for help.
  - Do not proceed until all conflicts are resolved and committed.

---

### Step 3: Run Turbo Pipeline

Run the full build/lint/type-check/test pipeline through Turborepo:

```bash
turbo run build && turbo run lint && turbo run check-types && turbo run test
```

**Behavior:**
- **PAUSE** if any step fails — show the full error output and ask the user how to proceed.
- If only **lint warnings** (not errors) are present, **continue** — warnings do not block the pipeline.
- If all steps pass cleanly, proceed to the next step.

---

### Step 4: Pre-Landing Review

Run the `/review` skill on the staged changes (diff against base branch).

- **PAUSE** if critical issues are found (Pass 1 blockers from the review skill).
  - Show the critical issues to the user.
  - Wait for acknowledgment or fixes before proceeding.
- **Continue** if only informational issues are found (Pass 2 suggestions).
  - Log the informational items but do not block.

---

### Step 5: Version Bump

Detect the scope of changes from commits since the last version tag and apply the appropriate version bump.

**Detection logic (from conventional commits):**
- Commits with `fix:` prefix → **PATCH** bump (automatic, no confirmation needed)
- Commits with `feat:` prefix → **MINOR** bump (ask user to confirm)
- Commits with `BREAKING CHANGE` in body or `!` after type → **MAJOR** bump (ask user to confirm)
- Commits with only `chore:`, `docs:`, `ci:`, `build:` → **No version bump** (infra/docs only)

**Actions:**
- Update `version` field in the appropriate `package.json` file(s).
- For monorepo packages, only bump the packages that actually changed.
- **PAUSE** for MINOR bumps — ask: "Bumping to vX.Y.0 — confirm? (y/n)"
- **PAUSE** for MAJOR bumps — ask: "MAJOR version bump to vX.0.0 — this indicates breaking changes. Confirm? (y/n)"
- PATCH bumps proceed automatically without confirmation.

---

### Step 6: Generate Changelog

Parse all commits since the last version tag and generate a human-friendly changelog.

**Process:**
1. Get commits since last tag: `git log <last-tag>..HEAD --oneline`
2. Group by conventional commit type:
   - `feat:` → **New Features**
   - `fix:` → **Bug Fixes**
   - `perf:` → **Performance**
   - `chore:`, `ci:`, `build:` → **Maintenance**
   - `docs:` → **Documentation**
   - `refactor:` → **Improvements**
3. Write to `CHANGELOG.md` at the project root (prepend new entry, preserve existing entries).

**Language style:**
- Use user-friendly language: "You can now..." instead of "Added feature X"
- Use "Fixed an issue where..." instead of "fix: bug in handler"
- Keep entries concise — one line per commit, grouped under headers.

**Format:**
```markdown
## [vX.Y.Z] - YYYY-MM-DD

### New Features
- You can now do X when Y happens

### Bug Fixes
- Fixed an issue where Z would fail under certain conditions

### Maintenance
- Updated build configuration for faster compilation
```

---

### Step 7: Assess Scope — Single PR or Stacked PRs

Before committing, determine whether the changes should ship as a single PR or a layer-based stack.

**Threshold:**
- **< ~200 lines total** → single PR (proceed to Step 7a)
- **> ~200 lines or 3+ files per layer** → stacked PRs by layer (proceed to Step 7b)
- **Infra/config changes** → always their own PR at the bottom of the stack

---

### Step 7a: Single PR — Create Logical Commits

Group uncommitted changes into logical, well-scoped commits. Do NOT squash everything into one giant commit.

**Commit grouping strategy (in order):**
1. **Infrastructure/config changes** — `package.json`, `tsconfig.json`, Turborepo config, CI files, Dockerfile changes.
2. **DB/schema changes** — Drizzle schema changes, database migrations, seed data.
3. **Service/API changes** — Backend routes, handlers, middleware, Zod schemas.
4. **App/UI changes** — Frontend components, pages, styles, assets.
5. **Version bump + changelog** — The version bump and CHANGELOG.md update as a single commit.

**Commit message format:**
- Use conventional commit format: `type(scope): description`
- Keep subject line under 72 characters.
- Add body for non-obvious changes.

**Examples:**
```
chore(config): update turbo pipeline for parallel builds
feat(api): add user preferences endpoint
feat(web): add settings page with preference controls
chore(release): bump to v1.2.0 and update changelog
```

Then proceed to Step 8.

---

### Step 7b: Stacked PRs — Create Layer-Based Branches

For large features crossing architectural layers, create a Graphite stack with one branch per layer.

**Layer order (bottom to top of stack):**
1. **Infra/config** — CI, build config, env, package deps
2. **DB/schema** — Drizzle schema changes, migrations, seed data
3. **API/services** — Route handlers, service layer, middleware, Zod schemas
4. **UI/app** — Frontend components, pages, styles (one branch per platform if multi-platform)

**Process:**
```bash
# Start from trunk
gt sync

# Layer 1: DB/schema
gt create feature/<name>-schema
# Stage only schema/migration files
git add <schema-files>
gt modify -c -m "feat(db): add athlete profile schema and migration"

# Layer 2: API/services
gt create feature/<name>-api
# Stage only API/service files
git add <api-files>
gt modify -c -m "feat(api): add athlete profile endpoints"

# Layer 3: UI/app
gt create feature/<name>-web
# Stage only UI files
git add <ui-files>
gt modify -c -m "feat(web): add athlete profile page"
```

Each branch should be ≤ 400 lines of meaningful diff. If a single layer exceeds 400 lines, split it further within that layer.

Then proceed to Step 8.

---

### Step 8: Open PR

Create pull request(s) using the best available tool.

**Tool detection:**
- If **Graphite** is available (`gt` command exists) → use `gt submit` (preferred)
- Otherwise → fall back to `gh pr create`

**For stacked PRs (Step 7b):** `gt submit` automatically creates linked, dependency-annotated PRs for the entire stack. Each PR in the stack gets its own title and body.

**PR title:**
- Conventional format: `type(scope): description`
- Under 70 characters.
- Use monorepo prefixes when applicable: `[shared]`, `[web]`, `[android]`, `[infra]`
- Examples: `[shared] feat(db): add athlete profile schema`, `feat(api): add profile endpoints`, `[web] feat(profiles): add profile page`

**PR body structure:**
```markdown
## Summary
- [1-3 bullet points describing what this PR does]

## Changes
- [Grouped list of notable changes]

## Test Plan
- [ ] [Checklist of testing steps]

## Breaking Changes
[Only include this section if there are breaking changes]
- [Description of what breaks and migration path]
```

**Push behavior (gh fallback only):**
- Push the branch with `git push -u origin <branch>` before creating the PR.
- If the branch already tracks a remote, use `git push`.

---

## Pause Conditions Summary

The pipeline is non-interactive EXCEPT for these conditions:

| Condition | Action | Resume |
|-----------|--------|--------|
| Merge conflicts | Show conflicting files | User resolves conflicts |
| Build failure | Show error output | User fixes the issue |
| Test failure | Show failing tests | User fixes tests |
| Lint errors | Show lint errors | User fixes lint issues |
| Critical review issues | Show Pass 1 blockers | User acknowledges/fixes |
| MINOR version bump | Ask for confirmation | User confirms y/n |
| MAJOR version bump | Ask for confirmation | User confirms y/n |

---

## References

- `graphite/` — Use for stacked PR workflows; prefer `gt submit` when Graphite is available.
- `review/` — Invoked automatically in Step 4 for pre-landing code review.
