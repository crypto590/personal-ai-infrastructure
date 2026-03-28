---
name: review
model: claude-opus-4-6
effort: high
context: fork
argument-hint: "[path | PR #number]"
description: "Unified code review. 2-pass critical/informational with 0-1 scoring. Pattern consistency, AI detection, platform routing, auto-fix."
metadata:
  last_reviewed: 2026-03-27
  review_cycle: 90
---

# Code Review

## How to Invoke

- `/review` — review all uncommitted changes
- `/review src/api/` — review specific path
- `/review PR #42` — review a pull request

---

## Step 1: Gather the Diff

Determine what to review based on invocation:

- **No argument** — review all uncommitted changes: `git diff HEAD`
- **Path argument** — review changes in that path: `git diff HEAD -- <path>`
- **PR #number** — fetch PR diff: `gh pr diff <number>`

## Step 2: Read Existing PR Comments (PR only)

When reviewing a PR by number, read the existing comment thread before forming opinions:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate
gh api repos/{owner}/{repo}/pulls/{number}/reviews --paginate
```

- **Don't duplicate** — If a reviewer already flagged an issue, reference their comment instead
- **Check resolution** — Verify whether prior requested changes were made
- **Build on the thread** — Weigh in on open architectural discussions
- **Note resolved threads** — Don't re-open explicitly resolved issues

## Step 3: Understand Patterns on Main

Before judging any change, understand the existing patterns:

1. **Identify the modules being touched** — which directories, which layers (API, service, UI, data)
2. **Read the surrounding code on main** — sibling files, adjacent functions, existing patterns in the module
3. **Note the established conventions** — naming, error handling, state management, test structure, imports, file layout

The question is not just "is this code correct?" but "does this code fit how we already do things here?"

## Step 4: Detect Languages and Load Platform Checklists

Detect changed file extensions and load the applicable checklist:

| Extensions | Checklist |
|---|---|
| `.ts`, `.tsx`, `.js`, `.jsx` | `workflows/typescript.md` |
| `.swift` | `workflows/swift.md` |
| `.kt`, `.kts` | `workflows/kotlin.md` |

For mixed-language changes, run **all applicable workflows** sequentially.

## Step 5: Apply Pattern Rules

Read and apply as review criteria:

- `context/knowledge/patterns/clean-code-rules.md` — 6 mandatory rules. **Rules 1 (bounded iteration) and 4 (validate boundaries) are Critical. Rules 2, 3, 5, 6 are Code Quality.**
- `context/knowledge/patterns/self-documenting-code.md` — semantic vs pragmatic functions, model coherence, naming conventions, function/model drift detection

These are engineering standards, not suggestions.

---

## 2-Pass Review

### Pass 1 — Critical (blocks merge)

These issues **must** be resolved before merging:

1. **Security vulnerabilities** — injection (SQL, XSS, command), auth bypass, exposed secrets/tokens, insecure deserialization
2. **Data loss risk** — missing validation on destructive operations, wrong delete scope, unprotected cascade deletes
3. **Race conditions** — concurrent state mutation without synchronization, TOCTOU bugs, missing locks/transactions
4. **Contract violations** — schema drift from API spec, response type mismatches, breaking API changes without versioning
5. **Crash-path bugs** — force unwrap, unhandled null/undefined, missing error cases in switch/when, uncaught exceptions at boundaries
6. **Unbounded iteration** — any loop, retry, poll, or pagination without an explicit maximum (Rule 1)

### Pass 2 — Informational (improves quality, does not block)

1. **Performance** — N+1 queries, missing indexes, unnecessary re-renders, large bundle imports, unoptimized images
2. **Code clarity** — unclear naming, missing/stale comments, complex logic without explanation, deep nesting
3. **Test coverage gaps** — untested edge cases, missing error path tests, no integration tests for new endpoints
4. **Accessibility gaps** — missing labels, insufficient contrast, touch targets below minimum, missing keyboard navigation
5. **DRY violations** — duplicated logic that should be extracted, copy-pasted code with minor variations
6. **Function drift** — semantic functions that have accumulated side effects or hidden state dependencies
7. **Model drift** — models with 3+ optional fields only set in specific contexts, names that no longer describe all fields
8. **Comment hygiene** — semantic functions with unnecessary comments, pragmatic functions missing unexpected behavior docs
9. **Function size** — functions exceeding 40 lines (Rule 2)
10. **Nesting depth** — code nested more than 3 levels deep (Rule 5)
11. **Layer mixing** — PR combines DB schema + API + UI beyond ~200 lines — flag for layer-based stack split

---

## AI Pattern Detection

Look for these patterns that suggest AI generation:

- Excessive inline comments explaining obvious code
- Over-engineered error handling for simple operations
- Generic variable names (`data`, `result`, `response`, `item`)
- Unnecessary abstractions or wrapper functions
- Defensive checks that can't fail given the context
- Copy-paste patterns with slight variations
- Gratuitous type annotations on values with clear inference

If detected, flag specific files and verify:
- Logic errors in AI-generated sections
- Missing edge cases
- Overly defensive code that obscures intent

---

## Risk Assessment

After completing the review, assess overall risk:

- **Low** — Small change, follows existing patterns, good test coverage
- **Medium** — New patterns introduced, moderate scope, some gaps
- **High** — Architectural changes, security-sensitive, poor coverage, multiple critical issues

Include one sentence of reasoning.

---

## Human Focus Areas

Flag specific `file:line` ranges that need human review attention, with reasons:
- Complex business logic
- Security-sensitive operations
- Architectural decisions that set precedent
- Areas where AI pattern detection fired

---

## Fix-First Heuristic

### AUTO-FIX (safe, no behavior change)
Apply these fixes directly without asking:
- Dead code removal (unused imports, unreachable branches)
- N+1 queries — add eager loading
- Stale or incorrect comments
- Magic numbers → named constants
- Formatting/lint issues
- Unused variable cleanup

### ASK (risky or subjective)
Present the issue and proposed fix, wait for confirmation:
- Security fixes (may change behavior)
- Race condition fixes (require design decisions)
- Architectural/design changes
- Large fixes (>20 lines changed)
- Any fix that changes observable behavior

---

## Universal Checks (ALL Languages)

1. **Race conditions** — concurrent state mutation without synchronization primitives
2. **Enum completeness** — switch/when statements missing cases (especially after adding new enum values)
3. **LLM trust boundaries** — if code processes LLM output, verify it is validated/sanitized before use
4. **Hardcoded secrets or URLs** — API keys, tokens, passwords, environment-specific URLs
5. **Error handling at system boundaries** — API calls, file I/O, network requests, database queries
6. **TODO/FIXME without linked issue** — every TODO/FIXME should reference a ticket/issue number

---

## Scoring Rubric

Reference: `context/knowledge/patterns/evaluator-loop.md`

Score each criterion 0.0 to 1.0:

| Criterion | Weight | What to measure |
|-----------|--------|-----------------|
| Security | 0.20 | No vulnerabilities, auth correct, secrets safe |
| Correctness | 0.20 | No crash paths, contract violations, race conditions |
| Pattern consistency | 0.15 | Matches main conventions, uses established abstractions |
| Code quality | 0.15 | Clean code rules, self-documenting patterns, no drift |
| Test coverage | 0.10 | Paths tested, edge cases covered, tests isolated |
| Performance | 0.10 | No N+1, no re-render issues, queries bounded |
| Accessibility | 0.05 | Labels, contrast, touch targets, keyboard nav |
| AI code quality | 0.05 | No slop patterns, logic verified, no over-engineering |

## Evaluator Loop

After producing the initial review:

1. Score each criterion against the rubric
2. If weighted average < 0.8 (or project's Quality Contract `review` threshold), refine the lowest-scoring areas
3. Max 2 iterations (reviews should be thorough on first pass)

If a `## Quality Contract` exists in the project CLAUDE.md, use its thresholds and priority weights. See `context/knowledge/patterns/quality-contract.md`.

---

## Output Format

```
## Review: [scope description]

### Prior Review Status (PR only)
- [N] existing comments, [M] resolved, [K] still open
- Unresolved items: [list with status]

### Pass 1 — Critical (blocks merge)
[numbered list with file:line references, or "No critical issues found"]

### Pass 2 — Informational
[numbered list with file:line references]

### AI Pattern Detection
[files flagged, or "No AI patterns detected"]

### Auto-fixed
[list of changes made, or "No auto-fixes applied"]

### Scoring

| Criterion | Score | Pass |
|-----------|-------|------|
| Security | 0.XX | Y/N |
| Correctness | 0.XX | Y/N |
| ...       | ...   | ... |

Weighted average: 0.XX | Threshold: 0.XX | Iteration: N of 2

### Risk Assessment
**Level:** [Low | Medium | High]
**Reasoning:** [one sentence]

### Human Focus Areas
1. [file:line] — [why: complex logic, security-sensitive, architectural]

### What's Done Well
[genuine callouts of non-obvious good decisions]

### Verdict: APPROVE | APPROVE WITH NITS | CHANGES REQUESTED | HARD NO

### Bottom Line
[2-3 sentences on overall state and key takeaway]
```

---

## Verdict Criteria

- **APPROVE** — Ship it. Code is clean, consistent, and correct.
- **APPROVE WITH NITS** — Ship it, but address small things in a follow-up or before merge.
- **CHANGES REQUESTED** — Good direction, but issues need resolving. Be specific.
- **HARD NO** — Fundamental problems with the approach. Needs rethinking, not just fixes. Rare.

**Rules:** Any Pass 1 issue remaining → CHANGES REQUESTED. Only Pass 2 issues → APPROVE (with suggestions noted). Clean → APPROVE.

---

## Tone

- Be direct, not hostile. "This will break under concurrent access" not "This is clearly wrong."
- Explain the why. "Extract this — at 60 lines, it's hard to hold in working memory (Rule 2)."
- Acknowledge good work. If something was non-obviously good, say so.
- Pick battles. Distinguish "must fix" from "should fix."
- Be specific. Reference exact lines, exact files, exact patterns on main.
- Offer alternatives. A 3-line code suggestion is worth more than a paragraph.

---

## References

- `context/knowledge/patterns/clean-code-rules.md` — 6 mandatory rules
- `context/knowledge/patterns/self-documenting-code.md` — function/model taxonomy and drift detection
- `workflows/typescript.md` — TypeScript/Fastify/Next.js/Drizzle checklist
- `workflows/swift.md` — Swift/SwiftUI checklist
- `workflows/kotlin.md` — Kotlin/Compose checklist
