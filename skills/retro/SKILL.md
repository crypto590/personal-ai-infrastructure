---
name: retro
effort: medium
description: |
  Git-based engineering retrospective with monorepo awareness. Analyzes commits, PRs,
  LOC, and shipping velocity over configurable time ranges. Includes hotspot analysis,
  commit classification, and skill staleness detection.
  Triggers: retro, retrospective, what did I ship, weekly review, sprint review.
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Engineering Retrospective

## Usage

- `/retro` — default 7-day retrospective
- `/retro 24h` — daily standup summary
- `/retro 7d` — weekly retrospective
- `/retro 14d` — sprint retrospective
- `/retro 30d` — monthly review

---

## Time Range Parsing

Parse the argument as a duration:
- `24h` / `1d` — last 24 hours
- `7d` / `1w` — last 7 days (default)
- `14d` / `2w` — last 14 days
- `30d` / `1m` — last 30 days

Use `git log --since="<duration> ago"` to scope all analysis.

---

## Analysis Sections

### 1. Shipping Summary

Collect these metrics for the time range:

```bash
# Total commits
git log --since="$RANGE ago" --oneline | wc -l

# PRs (using gh CLI)
gh pr list --state all --search "created:>=$START_DATE" --json number,state,title,mergedAt

# Net LOC change
git log --since="$RANGE ago" --stat --format="" | tail -1
# Or sum per-commit: git log --since="$RANGE ago" --numstat
```

**Session detection:** Group commits by author timestamp. A gap of 45+ minutes between consecutive commits marks a new session. Sum session durations for estimated active coding hours.

**Metrics to report:**
- Total commits
- PRs opened / merged / closed
- Net lines added / removed / delta
- Estimated sessions and active hours
- Average commits per session

### 2. Monorepo Breakdown

For Turborepo monorepos, classify commits by which app/package they touch:

```bash
# Get changed files per commit, map to top-level app/package
git log --since="$RANGE ago" --name-only --format="COMMIT:%H"
```

Map file paths to apps/packages:
- `apps/athlead-tv/` — TV app
- `apps/athlead-web/` — Web app
- `apps/athlead-ios/` — iOS app (if in monorepo)
- `apps/athlead-android/` — Android app (if in monorepo)
- `packages/` — Shared packages
- Root-level — Config/CI changes

Report:
- Per-app commit count and LOC delta
- Which apps got the most attention
- Which apps were untouched (flag for awareness)

### 3. Commit Classification

Parse conventional commit prefixes from commit messages:

| Type | Pattern | Description |
|------|---------|-------------|
| feat | `feat:` `feat(scope):` | New features |
| fix | `fix:` `fix(scope):` | Bug fixes |
| chore | `chore:` | Maintenance, dependencies |
| refactor | `refactor:` | Code restructuring |
| docs | `docs:` | Documentation |
| test | `test:` | Tests |
| ci | `ci:` | CI/CD changes |
| other | No prefix | Unclassified |

**Metrics:**
- Count and percentage per type
- Feature-to-fix ratio (healthy target: >2:1)
- If ratio < 1:1, flag: "More fixes than features — possible tech debt or stability issues"

### 4. Hotspot Analysis

```bash
# Top 10 most-changed files
git log --since="$RANGE ago" --name-only --format="" | sort | uniq -c | sort -rn | head -20
```

**Flag churn patterns:**
- Files changed 5+ times in a week — potential design smell
- Files changed then reverted then changed again — indecision or flawed approach
- Test files with high churn — unstable tests
- Config files with high churn — environment instability

**Report top 10 files with:**
- Change count
- Type (source / test / config / docs)
- Churn flag if applicable

### 5. Shipping Streak

```bash
# Get unique commit dates
git log --since="$RANGE ago" --format="%ad" --date=short | sort -u
```

Calculate:
- **Current streak:** Consecutive days (up to today) with at least 1 commit
- **Best streak in period:** Longest run of consecutive commit days
- **Days without commits:** Count of zero-commit days in the range
- **Consistency score:** (days with commits / total days) * 100

### 6. Skill Staleness

Cross-reference recent commit patterns against skill topics:

1. Read all `SKILL.md` files under `~/.claude/skills/`
2. Extract `last_reviewed` and `review_cycle` from YAML frontmatter
3. Identify which skills relate to which code areas (by skill name and description)
4. Compare against monorepo breakdown from section 2

**Flag when:**
- A skill covers an area with heavy recent churn but the skill's `last_reviewed` is older than its `review_cycle`
- Example: "kotlin-android/ hasn't been updated in 4 months, but 45% of recent commits touch Android code"
- A skill references files/patterns that no longer exist in the codebase

---

## Historical Snapshots

Save each retrospective as a JSON report for trend tracking:

**Location:** `.context/retros/` (relative to project root)

**Filename:** `retro-YYYY-MM-DD.json`

**Schema:**
```json
{
  "date": "2026-03-17",
  "range": "7d",
  "commits": 42,
  "prs": { "opened": 5, "merged": 4, "closed": 1 },
  "loc": { "added": 1200, "removed": 800, "delta": 400 },
  "sessions": 12,
  "active_hours": 18.5,
  "monorepo": {
    "athlead-web": { "commits": 20, "loc_delta": 300 },
    "athlead-tv": { "commits": 15, "loc_delta": 100 }
  },
  "classification": {
    "feat": 18, "fix": 8, "chore": 6, "refactor": 4,
    "docs": 3, "test": 2, "ci": 1
  },
  "feature_fix_ratio": 2.25,
  "hotspots": ["src/app/page.tsx", "packages/ui/Button.tsx"],
  "streak": { "current": 5, "best": 7, "zero_days": 2 },
  "consistency_score": 71.4
}
```

Create the directory if it doesn't exist: `mkdir -p .context/retros/`

---

## Output Format

```
## Engineering Retrospective: [start date] — [end date]

### Shipping Summary
| Metric | Value |
|--------|-------|
| Commits | XX |
| PRs Merged | XX |
| Lines Added | +XX |
| Lines Removed | -XX |
| Net Delta | +/-XX |
| Sessions | XX |
| Active Hours | ~XX h |

### Monorepo Breakdown
| App/Package | Commits | LOC Delta | % of Total |
|-------------|---------|-----------|------------|
| athlead-web | XX | +XX | XX% |
| athlead-tv | XX | +XX | XX% |
| ... | ... | ... | ... |

Untouched: [list any apps with 0 commits]

### Commit Classification
| Type | Count | % |
|------|-------|---|
| feat | XX | XX% |
| fix | XX | XX% |
| ... | ... | ... |

Feature-to-fix ratio: X.X:1 [healthy/warning/concerning]

### Hotspots
| # | File | Changes | Flag |
|---|------|---------|------|
| 1 | path/to/file.tsx | XX | [churn/stable] |
| ... | ... | ... | ... |

### Shipping Streak
- Current streak: X days
- Best streak (in period): X days
- Zero-commit days: X
- Consistency: XX%

### Skill Staleness
[any skills needing attention, or "All skills current"]
```

---

## Notes

- All git commands run against the current repository (project root).
- If not in a git repository, report an error and exit gracefully.
- For multi-author repos, default to the current git user (`git config user.email`). Add `--all` flag to include all authors.
- Round active hours to nearest 0.5h.
- If `gh` CLI is not available, skip PR metrics and note the omission.
