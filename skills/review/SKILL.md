---
name: review
effort: high
description: |
  Multi-platform code review for Athlead. 2-pass structure: Pass 1 blocks merge (critical),
  Pass 2 improves quality (informational). Auto-fixes safe issues, asks about risky ones.
  Covers TypeScript/Fastify/Next.js, Swift/SwiftUI, and Kotlin/Compose.
  Triggers: code review, review PR, review changes, review code, pre-merge review.
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Multi-Platform Code Review

## How to Invoke

Run on current changes (staged + unstaged), specify files, or target a PR:
- `/review` — review all uncommitted changes
- `/review src/api/` — review specific path
- `/review PR #42` — review a pull request

## 2-Pass Structure

### Pass 1 — CRITICAL (blocks merge)

These issues **must** be resolved before merging:

1. **Security vulnerabilities** — injection (SQL, XSS, command), auth bypass, exposed secrets/tokens, insecure deserialization
2. **Data loss risk** — missing validation on destructive operations, wrong delete scope, unprotected cascade deletes
3. **Race conditions** — concurrent state mutation without synchronization, TOCTOU bugs, missing locks/transactions
4. **Contract violations** — Zod schema drift from API spec, response type mismatches, breaking API changes without versioning
5. **Crash-path bugs** — force unwrap (`!`), unhandled null/undefined, missing error cases in switch/when, uncaught exceptions at boundaries
6. **Unbounded iteration** — any loop, retry, poll, or pagination without an explicit maximum (see `context/knowledge/patterns/clean-code-rules.md` Rule 1)

### Pass 2 — INFORMATIONAL (improves quality, does not block)

1. **Performance** — N+1 queries, missing database indexes, unnecessary re-renders, large bundle imports, unoptimized images
2. **Code clarity** — unclear naming, missing/stale comments, complex logic without explanation, deep nesting
3. **Test coverage gaps** — untested edge cases, missing error path tests, no integration tests for new endpoints
4. **Accessibility gaps** — missing labels, insufficient contrast, touch targets below minimum, missing keyboard navigation
5. **DRY violations** — duplicated logic that should be extracted, copy-pasted code with minor variations
6. **Function drift** — semantic functions (named by what they do) that have accumulated side effects, hidden state dependencies, or need mocks to test. These should be split: pure logic stays semantic, side effects move to a pragmatic wrapper.
7. **Model drift** — models with 3+ optional fields only set in specific contexts, models whose name no longer describes all their fields, or fields that are null in most records. Signal to split the model into distinct concepts and compose when both are needed.
8. **Comment hygiene** — semantic functions should need no comments (rename or split if they do). Pragmatic functions should document only unexpected behavior, not restate the function name or describe obvious parameters. Flag stale doc comments that no longer match the implementation.
9. **Function size** — functions exceeding 40 lines of logic should be split (see `context/knowledge/patterns/clean-code-rules.md` Rule 2)
10. **Nesting depth** — code nested more than 3 levels deep should be flattened with early returns or extraction (Rule 5)

## Fix-First Heuristic

### AUTO-FIX (safe, no behavior change)
Apply these fixes directly without asking:
- Dead code removal (unused imports, unreachable branches)
- N+1 queries — add `.with()` / eager loading
- Stale or incorrect comments
- Magic numbers → named constants
- Missing input validation on internal boundaries
- Formatting/lint issues
- Unused variable cleanup

### ASK (risky or subjective)
Present the issue and proposed fix, wait for confirmation:
- Security fixes (may change behavior)
- Race condition fixes (require design decisions)
- Architectural/design changes
- Large fixes (>20 lines changed)
- Any fix that changes observable behavior
- Subjective style preferences

## Language Detection & Routing

Detect changed file extensions and route to the appropriate workflow checklist:

| Extensions | Workflow |
|---|---|
| `.ts`, `.tsx`, `.js`, `.jsx` | `workflows/typescript.md` |
| `.swift` | `workflows/swift.md` |
| `.kt`, `.kts` | `workflows/kotlin.md` |

For mixed-language changes, run **all applicable workflows** sequentially.

## Universal Checks (ALL Languages)

Apply these regardless of language:

1. **Race conditions** — concurrent state mutation without synchronization primitives
2. **Enum completeness** — switch/when statements missing cases (especially after adding new enum values)
3. **LLM trust boundaries** — if code processes LLM output, verify it is validated/sanitized before use; never trust raw LLM output
4. **Hardcoded secrets or URLs** — API keys, tokens, passwords, environment-specific URLs that should be in config/env
5. **Error handling at system boundaries** — API calls, file I/O, network requests, database queries must have error handling
6. **TODO/FIXME without linked issue** — every TODO/FIXME should reference a ticket/issue number

## Output Format

```
## Review: [scope description]

### Pass 1 — Critical (blocks merge)
[numbered list of issues with file:line references, or "No critical issues found"]

### Pass 2 — Informational
[numbered list of suggestions with file:line references]

### Auto-fixed
[list of changes made with brief descriptions, or "No auto-fixes applied"]

### Summary
- Critical issues: N
- Suggestions: N
- Auto-fixes applied: N
- Verdict: APPROVE / CHANGES REQUESTED
```

**Verdict rules:**
- Any Pass 1 issue remaining → `CHANGES REQUESTED`
- Only Pass 2 issues → `APPROVE` (with suggestions noted)
- Clean review → `APPROVE`

## Workflow References

- **TypeScript/Fastify/Next.js/Drizzle:** `workflows/typescript.md`
- **Swift/SwiftUI:** `workflows/swift.md` (orchestrates `ios-swift/review/*`)
- **Kotlin/Compose:** `workflows/kotlin.md` (orchestrates `kotlin-android/review/*`)

## Code Quality References

- `context/knowledge/patterns/clean-code-rules.md` — 6 mandatory rules (all code must pass). Rules 1 and 2 are referenced in Pass 1 above; read the full file for rules 3-6.
- `context/knowledge/patterns/self-documenting-code.md` — Semantic vs pragmatic function taxonomy, model drift detection, naming conventions.
