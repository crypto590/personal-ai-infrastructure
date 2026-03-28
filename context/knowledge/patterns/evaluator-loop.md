# Evaluator-Optimizer Loop

Generic pattern for iterative quality improvement. Skills reference this file and plug in their own criteria and thresholds.

Source: [Anthropic Engineering — Harness Design](https://www.anthropic.com/engineering/harness-design-long-running-apps)

---

## How It Works

1. **Generate** — Skill produces initial output (plan, review, code)
2. **Score** — Evaluate output against criteria list. Each criterion scored 0.0–1.0
3. **Check threshold** — If weighted average >= threshold, done. If not, continue.
4. **Refine** — Feed scores + specific failures back. Regenerate only failing sections.
5. **Re-score** — Score again. Max iterations enforced (Rule 1: bounded iteration).

```
Generate → Score → [below threshold?] → Refine → Re-score → [repeat or done]
```

---

## Scoring Format

After evaluating, produce this table:

```
| Criterion | Weight | Score (0-1) | Pass | Notes |
|-----------|--------|-------------|------|-------|
| ...       | 0.XX   | 0.XX        | Y/N  | ...   |

Weighted average: 0.XX
Threshold: 0.XX
Iteration: N of M
Verdict: PASS / REFINE
```

---

## Integration Contract

Skills that use this pattern must define:

- **criteria** — list of `{name, weight, threshold}` in their scoring rubric
- **max_iterations** — integer (default 3, hard max 5)
- **overall_threshold** — float (default 0.7)
- **refine_strategy** — what information gets fed back on failure (lowest-scoring sections, specific criterion failures, etc.)

---

## Threshold Guidance

| Range | Use Case |
|-------|----------|
| 0.8–1.0 | Production gates: shipping, security review, code review |
| 0.7–0.8 | Planning and design review (good enough to proceed) |
| 0.5–0.7 | Early exploration, rough drafts, brainstorming |

If a project defines a `## Quality Contract` in its CLAUDE.md, use the project-specific threshold instead of defaults. See `quality-contract.md`.

---

## Refine Strategy

On each iteration, feed back only actionable information:

1. List the criteria that scored below their individual threshold
2. Quote the specific sections/content that caused the low score
3. State what "passing" looks like for each failing criterion
4. Do NOT re-evaluate passing sections — only refine what failed

---

## Anti-Patterns

- Scoring the same thing twice with different names (inflates dimensions)
- Setting threshold to 1.0 (forces runaway iteration)
- Scoring subjective preferences as objective criteria
- More than 10 criteria per skill (dilutes signal — collapse correlated items)
- Iterating without feeding back specific failure reasons (model can't improve blindly)

---

## Assumption Check

This pattern encodes the assumption that the model cannot self-evaluate effectively in a single pass. As models improve, test whether the loop still adds value:

1. Run the skill without the loop
2. Compare output quality to looped output
3. If single-pass quality matches, remove the loop

Re-evaluate quarterly or after model upgrades.
