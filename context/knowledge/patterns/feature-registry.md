# Feature Registry Convention

JSON file that defines acceptance criteria for a feature before implementation begins. The generator works through criteria one at a time. The evaluator verifies and flips the `passes` field.

Source: [Anthropic Engineering — Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

Key insight: Models are "less likely to inappropriately change or overwrite JSON files compared to Markdown." JSON format enforces discipline.

---

## File Location

```
<project-root>/.feature-registry/<feature-name>.json
```

---

## Schema

```json
{
  "feature": "user-authentication",
  "created": "2026-03-27",
  "criteria": [
    {
      "id": "C1",
      "description": "User can create account with email and password",
      "category": "functional",
      "passes": false,
      "evidence": null
    },
    {
      "id": "C2",
      "description": "Password is hashed with bcrypt before storage",
      "category": "security",
      "passes": false,
      "evidence": null
    },
    {
      "id": "C3",
      "description": "Login fails gracefully with invalid credentials",
      "category": "edge-case",
      "passes": false,
      "evidence": null
    },
    {
      "id": "C4",
      "description": "Auth endpoints respond under 200ms at p95",
      "category": "performance",
      "passes": false,
      "evidence": null
    }
  ],
  "summary": {
    "total": 4,
    "passing": 0,
    "failing": 4
  }
}
```

---

## Categories

| Category | What it checks |
|----------|---------------|
| functional | Does it do what it should? |
| edge-case | Does it handle unexpected input, empty states, concurrent access? |
| security | Is it safe from injection, auth bypass, data exposure? |
| performance | Is it fast enough under expected load? |
| accessibility | Is it usable by everyone (screen readers, keyboard, contrast)? |

---

## Rules

1. **Criteria are defined BEFORE implementation begins** — during the planning phase
2. **Agents can only modify the `passes` and `evidence` fields** — never add, remove, or edit criteria descriptions
3. **Evidence must contain proof** — test name, screenshot path, log output, or command that verified it
4. **Summary is recalculated after each evaluation pass**
5. **Feature is "done" when all criteria pass**
6. **One feature per file** — don't combine unrelated features

---

## Workflow

```
Plan phase:     Define criteria → create .feature-registry/<name>.json
Build phase:    Generator implements one criterion at a time
Evaluate phase: Evaluator tests each criterion, flips passes, records evidence
Ship phase:     All criteria pass → feature is ready for PR
```

---

## When to Use

- Non-trivial features (3+ acceptance criteria)
- Features that span multiple files or layers
- Features where "done" is ambiguous without explicit criteria

Do NOT use for:
- Bug fixes with a single clear fix
- Config changes
- Documentation updates

---

## Integration with Planning Skills

When `/plan-product` or `/plan-eng` is run for a feature, they can output a feature registry file as part of their deliverable. This turns the plan's action items into a machine-readable contract.
