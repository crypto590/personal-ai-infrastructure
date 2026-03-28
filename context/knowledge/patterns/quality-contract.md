# Quality Contract Convention

Projects declare their quality priorities in their CLAUDE.md. PAI skills read these priorities at runtime and adjust scoring weights accordingly.

This keeps the PAI generic (defines the process) while projects provide the config (what to care about).

Source: [Anthropic Engineering — Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

---

## Format

Add this section to any project's CLAUDE.md:

```markdown
## Quality Contract

priorities:
  security: high
  test-coverage: high
  performance: medium
  accessibility: medium
  contract-integrity: medium
  code-quality: medium

thresholds:
  planning: 0.7
  review: 0.8
  qa: 0.75

known-issues:
  - N+1 queries in user feed endpoint
  - Auth token refresh race condition on iOS
  - Model drift in billing domain (3+ optional fields)

planning-weights:
  architecture: 0.30
  code-quality: 0.25
  test-coverage: 0.25
  performance: 0.20
```

---

## How Skills Use It

1. Skill checks for `## Quality Contract` section in the project's CLAUDE.md
2. If found:
   - Read priority levels and adjust category weights
   - Use project-specific thresholds instead of defaults
   - Weight known-issues higher during review (actively look for recurrence)
3. If not found:
   - Use skill defaults — no error, no warning
   - Skills must work without a Quality Contract

---

## Priority Mapping

| Priority | Weight Multiplier |
|----------|------------------|
| high | 1.5x |
| medium | 1.0x (default) |
| low | 0.5x |

After applying multipliers, renormalize weights to sum to 1.0.

---

## Known Issues

The `known-issues` list tells skills what to watch for. These are recurring problems the team has identified — not a bug tracker.

Skills should:
- Check for recurrence of known issues during review
- Weight findings related to known issues as higher severity
- Report when a known issue appears to be resolved (so the team can remove it)

---

## Examples

### Security-critical fintech project

```markdown
## Quality Contract

priorities:
  security: high
  test-coverage: high
  contract-integrity: high
  performance: medium
  accessibility: medium
  code-quality: medium

thresholds:
  planning: 0.8
  review: 0.9
  qa: 0.85
```

### Rapid-prototype consumer app

```markdown
## Quality Contract

priorities:
  performance: high
  accessibility: medium
  security: medium
  test-coverage: low
  contract-integrity: low
  code-quality: medium

thresholds:
  planning: 0.6
  review: 0.7
  qa: 0.65
```

---

## Maintenance

- Review the Quality Contract when project priorities shift
- Remove known-issues entries when they're confirmed resolved
- Adjust thresholds based on team velocity and quality trends
- The contract is a living document, not a one-time setup
