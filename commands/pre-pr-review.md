---
description: Multi-AI code review using Claude, Gemini, and Codex CLIs in parallel
allowed-tools: Bash, Read
---

# Pre-PR Review

Run parallel code reviews using three AI assistants (Claude, Gemini, Codex) to get diverse perspectives on your branch changes before creating a PR.

## Instructions

1. **Execute the review script**:
   ```bash
   ~/.claude/scripts/pre-pr-review.sh $ARGUMENTS
   ```

2. **Read the generated review file** and present its contents to the user.

3. **Provide a brief summary** highlighting:
   - Any consensus issues (flagged by multiple reviewers)
   - Critical issues that must be addressed
   - The overall verdict from reviewers

## Arguments

- No args: Review current branch against `main`
- `--base <branch>`: Review against a different base branch (e.g., `--base develop`)

## Output

Reviews are saved to `docs/reviews/pre-pr-review-{timestamp}.md` in the project directory.

$ARGUMENTS
