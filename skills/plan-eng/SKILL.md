---
name: plan-eng
effort: high
context: fork
agent: plan-architect
description: "Technical engineering planning before writing code. Evaluates architecture, code quality, test coverage, performance. Scored 0-1 with evaluator loop."
metadata:
  last_reviewed: 2026-03-27
  review_cycle: 90
---

# Technical Engineering Planning

Run this review before writing code. It evaluates the implementation approach for architecture soundness, code quality, test coverage, and performance. This is the engineering-minded review — it asks "how should we build this?" after product has decided "what to build."

---

## Step 0 — Scope Challenge (Always Run First)

Before reviewing anything, challenge the scope:

### Questions to Answer

1. **What existing code already solves this?**
   - Search the codebase for similar patterns, utilities, or components
   - Check shared packages for existing abstractions
   - Look for prior art that can be extended rather than rewritten

2. **What's the absolute minimum change needed?**
   - Can this be solved with configuration instead of code?
   - Can this be solved by composing existing functions?
   - Is a new abstraction actually needed, or is this premature?

3. **Smell test: Does the plan touch >8 files or introduce >2 new abstractions?**
   - If yes: flag immediately and justify each file/abstraction
   - Large surface area = more bugs, more tests, more review time
   - Every new abstraction is a maintenance commitment

### After Scope Challenge, Offer 3 Paths

**(A) Aggressive Scope Reduction**
- Strip to minimum viable change
- Defer everything that isn't strictly required
- Target: 3-5 files changed, 0-1 new abstractions
- Best for: small features, bug fixes, incremental improvements

**(B) Interactive Review**
- Full 4-section review with stop-on-fail
- Discuss each finding before proceeding
- Target: thorough review of medium-to-large features
- Best for: new features, architectural changes, complex integrations

**(C) Compressed Small-Change Review**
- Quick pass through all 4 sections
- Focus on gotchas and common mistakes
- Target: fast review for well-understood changes
- Best for: changes that follow established patterns

---

## 4 Review Sections (Stop-on-Fail)

**Stop-on-fail protocol:** After completing each section, report all findings. If any issues are found, stop and resolve them before proceeding to the next section. Do not continue reviewing if there are unresolved architecture or code quality issues — they will compound.

---

### Section 1: Architecture

Evaluate system design, coupling, and data flow.

#### Core Question: "Can this be simpler?"

- **Component boundaries:** Are responsibilities clearly separated? Does each module do one thing?
- **Dependency direction:** Do dependencies point inward (toward core business logic)? Are there circular dependencies?
- **Coupling analysis:** Can each component be tested in isolation? Can it be replaced without rewriting consumers?
- **Interface contracts:** Are the boundaries between components defined by types/schemas, not implementation details?
- **State management:** Where does state live? Is it the simplest location possible?

#### Data Flow Diagrams

For any non-trivial flow (more than 2 services or 3 steps), draw an ASCII diagram:

```
Request → Route Handler
  → Input Validation
    → Service Layer (business logic)
      → Data Access (database)
        → Response Serialization
          → Client
```

#### Architecture Checklist

- [ ] No circular dependencies between modules
- [ ] Each module has a single responsibility
- [ ] State lives in the simplest possible location
- [ ] Dependencies point inward toward business logic
- [ ] New abstractions are justified (not speculative)
- [ ] Data flow diagram drawn for non-trivial flows

---

### Section 2: Code Quality

Evaluate function structure, data modeling, DRY violations, error handling, and naming.

Reference: `context/knowledge/patterns/self-documenting-code.md` for full taxonomy.

#### Function Classification (Semantic vs Pragmatic)

Every function should be clearly one of two types:

**Semantic functions** — building blocks. Minimal, pure, self-describing, no comments needed.
- Take all inputs as parameters, return all outputs directly
- No hidden side effects or dependency on external state
- Named by what they do: `calculate_tax()`, `parse_iso_date()`
- Unit testable in isolation

**Pragmatic functions** — processes. Compose semantic functions + unique logic for a specific use case.
- Named by where/when they're used: `handle_signup_webhook()`, `provision_workspace()`
- Doc comments for unexpected behavior only (not restating the name)
- Integration tested, expected to change over time

**Flag these anti-patterns:**
- A semantic-named function with side effects (function drift)
- A pragmatic function reused in 4+ places — extract shared logic into semantic functions
- A function that needs comments to explain what it does — rename or split it

#### Model Coherence

Data shapes should make wrong states impossible.

- **Field coherence:** Can you look at every field and know it belongs under this model's name? If not, split it.
- **Optional field audit:** 3+ optional fields only set in specific contexts → the model is doing too many jobs.
- **Compose, don't merge:** Independent concepts needed together should be composed, not flattened.
- **Brand types on domain IDs:** Bare `string` or `UUID` for domain IDs → use branded/nominal types to catch cross-domain swaps at compile time.

#### Aggressive DRY Enforcement

- Search the entire codebase for duplicate logic before writing new code
- If similar logic exists in 2+ places, extract to a shared utility
- Check shared packages for existing abstractions
- Flag any copy-paste patterns

#### Complexity Analysis

- Flag functions over 40 lines — must be split (see `context/knowledge/patterns/clean-code-rules.md` Rule 2)
- Flag functions with more than 3 levels of nesting — flatten with early returns
- Flag functions with more than 4 parameters — use an options object
- Cyclomatic complexity over 10 — must be simplified
- **Bounded iteration:** Flag any loop, retry, poll, or pagination without an explicit maximum bound (Rule 1)

#### Code Quality Checklist

- [ ] Functions classified as semantic or pragmatic — naming matches type
- [ ] No semantic functions with hidden side effects (function drift)
- [ ] Models make wrong states impossible — no incoherent optional fields
- [ ] Domain IDs use branded types (not bare strings/UUIDs)
- [ ] No duplicated logic (checked across codebase)
- [ ] Naming follows existing conventions
- [ ] No function exceeds 40 lines
- [ ] No nesting deeper than 3 levels
- [ ] No function has more than 4 parameters
- [ ] No dead code or stale comments
- [ ] Every loop, retry, poll, and pagination has an explicit maximum bound
- [ ] All system boundary inputs validated

---

### Section 3: Test Coverage

Diagram all new code paths and ensure each has test coverage.

#### ASCII Diagrams of New Code Paths

For every new function or endpoint, draw the code paths:

```
createUser()
  ├─ happy: valid input → insert → return user ✓
  ├─ nil: missing required field → validation error ✓
  ├─ empty: empty string name → validation error ✓
  ├─ error: DB constraint violation → conflict error ✓
  └─ error: DB connection failure → internal error ✓
```

#### Path-to-Test Mapping

| Code Path | Test File | Test Name | Status |
|-----------|-----------|-----------|--------|
| createUser happy path | user.test.ts | creates user with valid data | Done |
| createUser duplicate email | user.test.ts | rejects duplicate email | TODO |
| createUser DB failure | user.test.ts | handles DB connection error | TODO |

#### Test Checklist

- [ ] All new code paths diagrammed
- [ ] Every path mapped to a specific test
- [ ] Error paths explicitly tested
- [ ] Tests are isolated and idempotent
- [ ] No tests depend on external services
- [ ] Test names describe the scenario, not the implementation

---

### Section 4: Performance

Evaluate queries, caching, memory, and latency.

#### Query Analysis

- **N+1 detection:** Queries inside loops should use eager loading or batch queries
- **Missing projections:** After insert/update, use returning clauses instead of re-fetching
- **Unbounded queries:** Every list query must have a limit
- **Missing indexes:** WHERE clause columns should be indexed
- **Transaction scope:** Multi-step operations should be wrapped in transactions

#### Bundle Size Impact

- Does this add new client-side dependencies?
- Can the dependency be loaded lazily (dynamic import)?
- Compare bundle size before/after
- Target: no single page increase > 10KB gzipped without justification

#### Latency Estimates

For every new endpoint, estimate response time:

| Endpoint | DB Queries | External Calls | Estimated Latency |
|----------|-----------|----------------|-------------------|
| `POST /api/users` | 1 insert | 0 | ~20ms |
| `GET /api/feed` | 2 selects | 1 (cache) | ~50ms |

- Target: p95 under 200ms for API routes
- Target: p95 under 100ms for cached routes
- Flag anything estimated over 500ms

#### Memory Leak Potential

- Are event listeners cleaned up?
- Are subscriptions unsubscribed on unmount?
- Are large objects held in closures unnecessarily?
- Are WebSocket connections closed on navigation?

#### Performance Checklist

- [ ] No N+1 query patterns
- [ ] All list queries have a limit
- [ ] Returning clauses used instead of re-fetching after insert/update
- [ ] New indexes added for new WHERE clauses
- [ ] Bundle size impact measured
- [ ] Latency estimates documented
- [ ] No memory leak patterns

---

## Scoring Rubric

Reference: `context/knowledge/patterns/evaluator-loop.md`

Score each section 0.0 to 1.0:

| Section | Criterion | Weight |
|---------|-----------|--------|
| Architecture | Simplest design, no circular deps, justified abstractions, data flow clear | 0.30 |
| Code Quality | Functions classified, no drift, DRY, naming consistent, complexity controlled | 0.25 |
| Test Coverage | All paths diagrammed, every path has a test, error paths covered | 0.25 |
| Performance | No N+1, limits on queries, latency estimated, no leaks | 0.20 |

## Evaluator Loop

After producing the initial review:

1. Score each section against the rubric above
2. If overall weighted score < 0.7 (or project's Quality Contract threshold), identify the lowest-scoring sections
3. Re-analyze those sections with deeper investigation
4. Re-score. Max 3 iterations.

If a `## Quality Contract` exists in the project CLAUDE.md, use its `planning` threshold and `planning-weights` instead of defaults. See `context/knowledge/patterns/quality-contract.md`.

---

## References

Consult these skills for platform-specific planning:

- **iOS/Swift architecture:** `ios-swift/architecture/` — SwiftUI patterns, MVVM, navigation
- **Android/Kotlin architecture:** `kotlin-android/architecture/` — Compose patterns, ViewModel, navigation
- **Web component planning:** `vercel-react-best-practices` — Server Components, data fetching, caching

---

## PR Stack Planning

After the scope challenge and before diving into sections, determine the PR strategy:

### Threshold
- **< ~200 lines total** → single PR, even if cross-layer
- **> ~200 lines or 3+ files per layer** → layer-based stack

### Layer-Based Stack Template

When stacking is warranted:

| # | Branch | Layer | Key Files | ~Lines |
|---|--------|-------|-----------|--------|
| 1 | feature/<name>-infra | Infra/config | CI, env, packages | ~X |
| 2 | feature/<name>-schema | DB/schema | Schema, migrations | ~X |
| 3 | feature/<name>-api | API/services | Routes, handlers, schemas | ~X |
| 4 | feature/<name>-ui | UI/app | Components, pages | ~X |

Layer order matters: each layer depends on the one below it. Skip layers that don't apply. Each entry should be ≤ 400 lines of meaningful diff.

---

## Feature Registry Output

Reference: `context/knowledge/patterns/feature-registry.md`

After completing the review, write a feature registry to `docs/feature-registry/<feature-slug>.json`.

Create the directory if it doesn't exist. Use the schema from the pattern file:

```json
{
  "feature": "<slug>",
  "created": "<YYYY-MM-DD>",
  "story": "<original user request>",
  "plan": "<2-3 sentence high-level approach>",
  "criteria": [
    {
      "id": "C1",
      "description": "<specific testable behavior>",
      "category": "functional|edge-case|security|performance|accessibility",
      "passes": false,
      "evidence": null
    }
  ],
  "summary": { "total": N, "passing": 0, "failing": N }
}
```

Rules:
- 4-8 criteria per feature
- Only include **engineering** criteria (architecture, code quality, test coverage, performance)
- Design and product criteria belong in `/plan-design` and `/plan-product` registries
- Each criterion must be independently testable by a separate evaluator agent
- The registry is the contract between planning and implementation

---

## Output Format

After completing the review, produce:

1. **Score table** (4 sections with 0-1 scores, weighted average, iteration count)
2. **Scope assessment** (files touched, new abstractions, smell test result)
3. **PR stack recommendation** (single PR or layer-based stack with branch names and line estimates)
4. **Findings per section** (numbered, with severity: blocker/warning/note)
5. **Code path diagrams** (ASCII, with test coverage status)
6. **Performance estimates** (latency table)
7. **Action items** (prioritized: fix before coding / fix during coding / fix later)
8. **Feature registry** (written to `docs/feature-registry/<slug>.json`)
9. **Deferred items** (for TODOS.md with context)
