# /evaluate-skill — Evaluate Skill Amendment

Compare skill performance before and after an amendment was applied.

## Usage

```
/evaluate-skill <amendment-id>
/evaluate-skill <amendment-id> --rollback
```

## Instructions

When the user runs this command:

1. **Run the evaluation script**:
   ```bash
   uv run ~/.claude/scripts/skill-tracker/evaluate.py <amendment-id> --json
   ```

2. **Present the verdict**:
   - **IMPROVED**: Amendment is working. Success rate increased. Recommend keeping it.
   - **DEGRADED**: Amendment made things worse. Offer to roll back.
   - **NEUTRAL**: No significant change. Consider keeping but monitoring.
   - **INSUFFICIENT_DATA**: Not enough observations yet. Suggest waiting.

3. **If `--rollback` is requested**:
   ```bash
   uv run ~/.claude/scripts/skill-tracker/evaluate.py <amendment-id> --rollback --json
   ```
   This restores the previous skill version in the database. Remind the user
   to also restore the SKILL.md file from the amendment record's `original_content`.

## Output Format

```
# Evaluation: Amendment #7
Skill: code-review | Verdict: IMPROVED

Before (v1): 25 runs, 72% success rate
After  (v2): 18 runs, 89% success rate

The amendment improved success rate by 17 percentage points.
No new error types were introduced.

Recommendation: Keep this amendment.
```

## Requirements

- NEON_DATABASE_URL must be set in environment or ~/.claude/.env
- Amendment must have status 'applied' to evaluate
- Minimum 5 observations after amendment (configurable with --min-observations)
