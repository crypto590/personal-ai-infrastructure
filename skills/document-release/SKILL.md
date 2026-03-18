---
name: document-release
description: |
  Post-ship documentation updater. Analyzes diffs to find outdated docs, auto-fixes
  factual corrections, asks about narrative changes. Polishes changelog and ensures
  cross-doc consistency.
  Triggers: document release, update docs, post-release docs, release notes, update documentation.
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Post-Ship Documentation Updater

## Purpose

After shipping a release, analyze what changed and ensure all documentation is accurate, consistent, and user-friendly. Auto-fix safe factual corrections; ask before making narrative changes.

---

## Workflow

Execute these steps in order after a release ships.

### Step 1: Analyze Diff

Determine what changed using git diff or PR diff:

```bash
# If given a version/tag
git diff v1.2.0..v1.3.0 --stat
git diff v1.2.0..v1.3.0

# If given a PR number
gh pr diff <number>

# If given a branch
git diff main...<branch> --stat
git diff main...<branch>
```

**Classify each change:**

| Classification | Description | Example |
|---------------|-------------|---------|
| New feature | Entirely new capability | New API endpoint, new UI component |
| Bug fix | Corrects broken behavior | Fix crash on empty input |
| Breaking change | Existing behavior changes | Renamed API field, removed option |
| Deprecation | Feature marked for removal | Old auth method deprecated |
| Config change | Settings/env vars modified | New required env var |
| Performance | Speed/resource improvement | Query optimization |
| Refactor | Internal restructuring | No user-facing change |

### Step 2: Audit Docs Directory

Scan the project's documentation for outdated content:

```bash
# Find all docs
find docs/ -name "*.md" -type f 2>/dev/null
find . -name "README.md" -type f 2>/dev/null

# Search for references to changed code
# For each changed file/function/API, grep docs for mentions
```

**For each doc file, check:**
- Does it reference any changed files, functions, or APIs?
- Does it describe behavior that changed?
- Does it list features/capabilities that were added or removed?
- Does it contain version numbers that need updating?
- Does it have code examples that use changed APIs?

**Build an audit list:**
```
| Doc File | Issue | Type | Auto-fixable? |
|----------|-------|------|---------------|
| docs/api.md | Endpoint /v1/users renamed to /v2/users | Path change | Yes |
| docs/setup.md | Missing new DATABASE_URL env var | New requirement | Yes |
| docs/architecture.md | Auth flow description outdated | Narrative | No — ask first |
```

### Step 3: Auto-Fix Factual Corrections

These are safe to fix without asking because they are objective, verifiable facts:

- **File paths** that moved or were renamed
- **Command names** that changed (CLI commands, npm scripts)
- **Feature counts** ("supports 5 auth methods" -> "supports 6 auth methods")
- **Config option names** and their default values
- **API endpoint paths** (routes, methods)
- **Import paths** that changed
- **Version numbers** in installation instructions
- **Package names** that were renamed
- **Environment variable names** that changed

**Process:**
1. Make each correction
2. Log every change made for the summary report
3. Use exact replacement (no rewording surrounding text)

### Step 4: Ask About Narrative Edits

These require user approval because they involve judgment:

- **Security-related documentation** — Any change to auth, permissions, or data handling docs
- **Architecture description updates** — System design, data flow, component relationships
- **Large rewrites** — Changes affecting >50% of a doc section
- **Tone or audience changes** — Technical level, formality, target reader
- **Removing content** — Deleting sections, deprecation notices

**Process:**
1. Present a diff preview for each proposed narrative change
2. Explain why the change is needed
3. Wait for approval before applying
4. If rejected, note in the summary as "skipped — user declined"

### Step 5: Polish Changelog

Transform technical commit messages into user-friendly changelog entries:

**Voice guidelines:**
- Use second person: "You can now..." instead of "Added..."
- Be specific about benefit: "Fixed an issue where large uploads would timeout" not "Fix upload bug"
- Include context: "Passwords now require 12+ characters (previously 8)" not "Update password validation"

**Grouping order (by impact):**
1. **Breaking Changes** — What will break, migration steps
2. **New Features** — What's new and how to use it
3. **Improvements** — What got better
4. **Bug Fixes** — What was broken and is now fixed
5. **Deprecations** — What's going away and when

**Breaking change format:**
```markdown
### Breaking Changes

- **API: User endpoint path changed** — `/v1/users` is now `/v2/users`.
  Migration: Update all API calls to use the new path. The old path returns 301 redirects
  until v2.0, after which it will return 404.
```

**Feature format:**
```markdown
### New Features

- **Dashboard: Export to CSV** — You can now export any dashboard table to CSV.
  Click the download icon in the top-right corner of any data table.
```

### Step 6: Cross-Doc Consistency Check

After all edits, verify consistency across all documentation:

- **Same feature described consistently** — If the auth flow is described in 3 docs, all 3 match
- **Version numbers consistent** — All docs reference the same version
- **No contradictions** — Doc A doesn't say "requires Node 18" while Doc B says "requires Node 20"
- **Internal links valid** — All `[link text](path)` references point to existing files
- **Code examples work** — Snippets reference current API signatures and imports
- **Terminology consistent** — Same concept uses same name everywhere (not "user" in one doc and "account" in another)

**Check links:**
```bash
# Extract markdown links and verify targets exist
# For each doc, find [text](path) patterns and check if path exists
```

### Step 7: Commit Updated Docs

Bundle all documentation changes into a single commit:

```bash
git add docs/ README.md CHANGELOG.md
git commit -m "docs: update documentation for [version/feature]"
```

**Commit message format:**
- `docs: update documentation for v1.3.0`
- `docs: update API docs after auth refactor`
- `docs: add migration guide for breaking database changes`

Include a summary in the commit body listing all files changed and why.

---

## Output Format

After completing all steps, present this summary:

```
## Documentation Update: [version/feature]

### Changes Analyzed
- X commits / Y files changed
- Classifications: [list]

### Auto-Fixed (applied)
1. [file]: [what was fixed]
2. ...

### Narrative Changes (asked/applied)
1. [file]: [what was changed] — [approved/declined/pending]
2. ...

### Changelog
[polished changelog content]

### Consistency Check
- [X] Feature descriptions consistent
- [X] Version numbers consistent
- [X] No contradictions found
- [X] Internal links valid
- [ ] Issue: [description of any inconsistency found]

### Commit
[commit hash]: docs: update documentation for [version/feature]
```

---

## Edge Cases

- **No docs directory:** Report that no documentation was found. Suggest creating baseline docs.
- **No breaking changes:** Skip the breaking changes section in changelog.
- **Monorepo:** Check docs in each app/package directory, not just root `/docs/`.
- **Multiple changelogs:** Some monorepos have per-package changelogs. Update all relevant ones.
- **Pre-existing inconsistencies:** If docs were already inconsistent before this release, flag them but don't try to fix everything — focus on changes related to this release.

---

## References

- `technical/obsidian/` for syncing release notes to Obsidian vault
- Project stack: Turborepo + Next.js 16 + Fastify 5 + Swift/SwiftUI + Kotlin/Compose + Drizzle/PostgreSQL
