# /inspect-skill — Skill Health Inspection

Analyze a skill's execution history and surface failure patterns.

## Usage

```
/inspect-skill <skill-name>
/inspect-skill --all
```

## Instructions

When the user runs this command:

1. **If a specific skill name is provided**, run the inspection script:
   ```bash
   uv run ~/.claude/scripts/skill-tracker/inspect.py "<skill-name>" --json
   ```
   Parse the JSON output and present it as a readable report with:
   - Health status (healthy / degraded / failing)
   - Success rate and run count
   - Error pattern breakdown
   - Weekly trend
   - Recent failures with context
   - Recommendations for improvement

2. **If `--all` is provided**, show the dashboard:
   ```bash
   uv run ~/.claude/scripts/skill-tracker/inspect.py --all --json
   ```
   Present as a sorted table, worst-performing skills first.

3. **After presenting the report**, ask the user:
   - "Would you like me to propose an amendment for this skill?" (if health is degraded/failing)
   - "Would you like to see the full transcript for any of these failures?"

## Output Format

```
# Skill Inspection: <skill-name>
Health: DEGRADED | Period: 30 days

## Metrics
- 42 total runs (35 success, 5 partial, 2 failure)
- Success rate: 83.3%
- Used across 3 projects

## Error Patterns
- tool_call: 5 occurrences
  - "SwiftLint not found"
  - "permission denied on /usr/local/bin"
- timeout: 2 occurrences

## Trend
  2026-03-01: ################ 80% (10 runs)
  2026-03-08: ################## 90% (12 runs)
  2026-03-15: ############ 60% (10 runs)  ← declining

## Recommendations
- Tool call failures dominate. Check if SwiftLint install path changed.
- Success rate declining this week — investigate recent environment changes.
```

## Requirements

- NEON_DATABASE_URL must be set in environment or ~/.claude/.env
- Database must be initialized: `uv run ~/.claude/scripts/skill-tracker/setup_db.py`
