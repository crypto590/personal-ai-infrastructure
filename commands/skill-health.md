Scan all SKILL.md files under ~/.claude/skills/ and produce a health report.

For each skill:
1. Read the YAML frontmatter for `last_reviewed` and `review_cycle` (default: 90 days)
2. Calculate days since last review
3. Check if past review cycle → flag as OVERDUE
4. Check if `last_reviewed` is missing → flag as "needs metadata"
5. Check git log for recent commits touching the skill directory
6. Verify reference integrity: if the skill body contains file path references (like `ios-swift/review/concurrency.md`), check those files exist

Output format:
```
Skill Health Report
───────────────────
review/              ✓ reviewed 12d ago (cycle: 90d)
plan-product/        ✓ reviewed 12d ago (cycle: 90d)
ios-swift/           ⚠ reviewed 95d ago (cycle: 90d) — OVERDUE
email/               ✓ reviewed 30d ago (cycle: 90d)
research/            ⚠ no last_reviewed date — needs metadata

Reference Integrity:
  review/workflows/swift.md → ios-swift/review/concurrency.md ✓
  review/workflows/swift.md → ios-swift/review/missing.md ✗ NOT FOUND

Summary: 18 skills checked, 2 overdue, 1 missing metadata, 1 broken reference
```

Report issues ranked by severity:
1. Broken references (files referenced but don't exist)
2. Overdue reviews (past review_cycle)
3. Missing metadata (no last_reviewed date)
4. Stale content (no git commits in 6+ months)
