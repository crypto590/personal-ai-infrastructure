---
description: Generate a PR description following the PR Contract format
allowed-tools: Bash(git:*), Read, Glob, Grep
---

# PR Description Generator

Generate a comprehensive PR description that follows the **PR Contract** format for effective code review.

## Instructions

1. **Gather context** by running:
   - `git diff main...HEAD --stat` (files changed)
   - `git log main..HEAD --oneline` (commits in this PR)
   - `git diff main...HEAD` (actual changes)

2. **Analyze the changes** to determine:
   - What the PR accomplishes (intent)
   - Risk level (Low/Medium/High)
   - Which parts were AI-assisted vs hand-written
   - What areas need human reviewer focus

3. **Generate the PR description** in this exact format:

```markdown
## Intent
[1-2 sentences: What does this PR do and why?]

## Proof of Work
- [ ] Tests pass locally (`bun test` / `pytest`)
- [ ] Linter passes (`bun lint` / `ruff check`)
- [ ] Manual testing: [describe what you tested]
- [ ] Screenshots/logs: [if applicable]

## Risk Assessment
**Risk Level**: [Low | Medium | High]
- **Low**: Minor changes, well-tested, low blast radius
- **Medium**: New features, moderate complexity
- **High**: Core logic changes, security-sensitive, breaking changes

## AI Disclosure
**AI-Assisted**: [Yes | No | Partial]
- Files with AI assistance: [list files or "None"]
- Human-verified: [Yes | In Progress]

## Review Focus
Please pay special attention to:
1. [Specific area #1 - e.g., "Error handling in api/auth.ts"]
2. [Specific area #2 - e.g., "SQL query optimization in queries/"]
3. [Specific area #3 - e.g., "Edge cases in validation logic"]

## Changes
[Auto-generated from git diff --stat]

## Commits
[Auto-generated from git log]
```

4. **Output the generated PR description** ready to paste into GitHub/GitLab.

$ARGUMENTS
