---
name: plan-eng
effort: high
description: |
  Technical engineering planning and review of implementation approach.
  Use before writing code to evaluate architecture, code quality, test coverage,
  and performance. Includes scope challenge and aggressive DRY enforcement.
  Triggers: engineering review, technical planning, implementation review, code planning.
metadata:
  last_reviewed: 2026-03-17
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
   - Check shared packages in the turborepo
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
Request → Fastify Route Handler
  → Zod Validation
    → Service Layer (business logic)
      → Drizzle Query (database)
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
- A semantic-named function with side effects (e.g., `calculate_tax()` that also writes to DB) — this is function drift
- A pragmatic function reused in 4+ places — the shared logic should be extracted into semantic functions
- A function that needs comments to explain what it does — either rename it or split it

#### Model Coherence

Data shapes should make wrong states impossible.

- **Field coherence:** Can you look at every field and know it belongs under this model's name? If not, the model is coupling unrelated concepts — split it.
- **Optional field audit:** 3+ optional fields that are only set in specific contexts → the model is doing too many jobs.
- **Compose, don't merge:** Independent concepts needed together should be composed (`UserAndWorkspace { user, workspace }`) not flattened.
- **Brand types on domain IDs:** Bare `string` or `UUID` for domain IDs → use branded/nominal types (`DocumentId`, `TeamId`) to catch cross-domain swaps at compile time.

#### Aggressive DRY Enforcement

- Search the entire codebase for duplicate logic before writing new code
- If similar logic exists in 2+ places, extract to a shared utility
- Check shared packages in the turborepo for existing abstractions
- Flag any copy-paste patterns — even across different platforms (web/iOS/Android API contracts)

#### Naming Consistency Check

- Do names follow existing conventions in the codebase?
- Are abbreviations consistent? (e.g., don't mix `usr` and `user`)
- Do function names describe what they do, not how they do it?
- Are boolean variables named as questions? (`isActive`, `hasPermission`)
- Do file names match the primary export?
- Are semantic functions named by operation and pragmatic functions named by context?

#### Complexity Analysis

- Flag functions over 40 lines — must be split (see `context/knowledge/patterns/clean-code-rules.md` Rule 2)
- Flag functions with more than 3 levels of nesting — flatten with early returns
- Flag functions with more than 4 parameters — use an options object
- Cyclomatic complexity over 10 — must be simplified
- **Bounded iteration:** Flag any loop, retry, poll, or pagination without an explicit maximum bound (see Rule 1)

#### Dead Code Detection

- Are there unused imports?
- Are there unreachable code paths?
- Are there commented-out blocks? (Remove or document why they exist)
- Are there feature flags for features that shipped months ago?

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
- [ ] Semantic functions have no comments; pragmatic functions document only unexpected behavior
- [ ] Every loop, retry, poll, and pagination has an explicit maximum bound
- [ ] All system boundary inputs validated (API responses, user input, env vars)

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

| Code Path                     | Test File              | Test Name                    | Status |
| ----------------------------- | ---------------------- | ---------------------------- | ------ |
| createUser happy path         | user.test.ts           | creates user with valid data | Done   |
| createUser duplicate email    | user.test.ts           | rejects duplicate email      | TODO   |
| createUser DB failure         | user.test.ts           | handles DB connection error  | TODO   |

#### Flag Untested Paths

- Every code path in the ASCII diagram must have a corresponding test
- Flag any path without a test — do not proceed until resolved
- Error paths are the most commonly missed — check them explicitly

#### Test Isolation Check

- Tests must not depend on each other (no shared mutable state)
- Tests must not depend on external services (mock or stub)
- Tests must be idempotent (running twice gives same result)
- Database tests must use transactions or test-specific schemas

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

#### Drizzle Query Analysis

- **Missing `.with()` calls:** Are related records being fetched in N+1 loops instead of eager loading with `.with()`?
- **Missing `.returning()` calls:** After insert/update, are you making a second query to fetch the result? Use `.returning()` instead.
- **Unbounded queries:** Is there a `.limit()` on every list query? Never fetch all records.
- **Missing indexes:** Does the WHERE clause use indexed columns? Check the Drizzle schema.
- **Transaction scope:** Are multi-step operations wrapped in transactions?

#### Bundle Size Impact

- Does this add new client-side dependencies?
- Can the dependency be loaded lazily (dynamic import)?
- Check bundle size with `bun run build` and compare before/after
- Target: no single page increase > 10KB gzipped without justification

#### Latency Estimates

For every new endpoint, estimate response time:

| Endpoint                | DB Queries | External Calls | Estimated Latency |
| ----------------------- | ---------- | -------------- | ----------------- |
| `POST /api/users`       | 1 insert   | 0              | ~20ms             |
| `GET /api/feed`         | 2 selects  | 1 (cache)      | ~50ms             |

- Target: p95 under 200ms for API routes
- Target: p95 under 100ms for cached routes
- Flag anything estimated over 500ms

#### Memory Leak Potential

- Are event listeners cleaned up? (especially in React effects and SwiftUI onAppear/onDisappear)
- Are subscriptions unsubscribed on unmount?
- Are large objects held in closures unnecessarily?
- Are WebSocket connections closed on navigation?

#### Performance Checklist

- [ ] No N+1 query patterns
- [ ] All list queries have `.limit()`
- [ ] `.returning()` used instead of re-fetching after insert/update
- [ ] New indexes added for new WHERE clauses
- [ ] Bundle size impact measured
- [ ] Latency estimates documented
- [ ] No memory leak patterns

---

## Athlead-Specific Adaptations

### Stack Mapping

| Concept               | Athlead Implementation              |
| --------------------- | ----------------------------------- |
| ORM / Models          | Drizzle schemas (`schema.ts`)       |
| API Routes (server)   | Fastify route handlers              |
| API Routes (web)      | Next.js App Router (`route.ts`)     |
| Views (web)           | React Server/Client Components      |
| Views (iOS)           | SwiftUI Views                       |
| Views (Android)       | Compose Screens                     |
| Build system          | Turborepo pipelines                 |
| Package manager       | bun                                 |
| Database              | PostgreSQL                          |
| Validation            | Zod schemas                         |

### Turbo Pipeline Awareness

- `turbo run build` — builds all packages in dependency order
- `turbo run test` — runs tests across all packages
- `turbo run lint` — lints all packages
- New packages must be added to `turbo.json` pipeline config
- Check that new package dependencies are reflected in turbo's task graph

### File-Based Routing (Next.js App Router)

- Routes defined by directory structure in `app/`
- `page.tsx` = route page, `layout.tsx` = shared layout
- `route.ts` = API route handler
- `loading.tsx` = loading UI, `error.tsx` = error boundary
- Dynamic routes: `[param]/page.tsx`
- Route groups: `(group)/` for organization without URL impact

---

## References

Consult these skills for platform-specific planning:

- **iOS/Swift architecture:** `ios-swift/architecture/` — SwiftUI patterns, MVVM, navigation
- **Android/Kotlin architecture:** `kotlin-android/architecture/` — Compose patterns, ViewModel, navigation
- **Web component planning:** `vercel-react-best-practices` — Server Components, data fetching, caching

---

## Output Format

After completing the review, produce:

1. **Scope assessment** (files touched, new abstractions, smell test result)
2. **Findings per section** (numbered, with severity: blocker/warning/note)
3. **Code path diagrams** (ASCII, with test coverage status)
4. **Performance estimates** (latency table)
5. **Action items** (prioritized: fix before coding / fix during coding / fix later)
6. **Deferred items** (for TODOS.md with context)
