---
name: ship
description: |
  Build, version, and ship pipeline. Runs build/lint/test, performs pre-landing review,
  auto-versions, generates changelog, creates logical commits, and opens PR.
  Non-interactive except for merge conflicts, test failures, and major version bumps.
  Triggers: ship, ship it, deploy, release, open PR, create PR, push changes.
metadata:
  last_reviewed: 2026-03-17
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

### Step 7: Create Logical Commits

Group uncommitted changes into logical, well-scoped commits. Do NOT squash everything into one giant commit.

**Commit grouping strategy (in order):**
1. **Infrastructure/config changes** — `package.json`, `tsconfig.json`, Turborepo config, CI files, Dockerfile changes.
2. **Service/API changes** — Backend routes, handlers, middleware, database migrations, Drizzle schema changes.
3. **App/UI changes** — Frontend components, pages, styles, assets.
4. **Version bump + changelog** — The version bump and CHANGELOG.md update as a single commit.

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

---

### Step 8: Open PR

Create a pull request using the best available tool.

**Tool detection:**
- If **Graphite** is available (`gt` command exists) → use `gt submit`
- Otherwise → use `gh pr create`

**PR title:**
- Conventional format: `type(scope): description`
- Under 70 characters.
- Examples: `feat(auth): add OAuth2 login flow`, `fix(api): handle null user gracefully`

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

**Push behavior:**
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
