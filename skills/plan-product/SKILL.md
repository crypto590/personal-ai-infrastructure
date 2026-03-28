---
name: plan-product
effort: high
argument-hint: "[EXPAND | HOLD | REDUCE]"
description: "Product strategic review of engineering plans. Evaluates scope, architecture, security, edge cases, and trajectory. Scored 0-1 per section with evaluator loop."
metadata:
  last_reviewed: 2026-03-27
  review_cycle: 90
---

# Product Strategic Review

Run this review before starting any major feature to evaluate scope, architecture, risk, and long-term trajectory. This review asks "should we build this?" and "are we building the right thing?" before engineering dives into "how."

---

## Step 0 — Select Scope Mode

Ask the user which scope mode to use before proceeding:

### EXPAND
- Dream big, 10x ambition
- Explore the platonic ideal of this feature
- Include phase 2/3 planning and future extensibility
- Consider adjacent features and platform plays
- Ask: "What would this look like if we had unlimited time?"

### HOLD
- Maximum rigor within bounded scope
- Cap complexity at 8 files and 2 new abstractions
- Ruthless deferral of anything not strictly required
- Focus on quality over breadth
- Ask: "What's the best version we can ship this sprint?"

### REDUCE
- Strip to absolute minimum viable
- Defer everything that isn't blocking launch
- Single happy path only
- Hardcoded values over configuration
- Ask: "What's the smallest thing that proves the hypothesis?"

---

## 8 Prime Directives

Apply these to every section of the review:

1. **Zero silent failures** — Every failure mode must be visible and named. No swallowed errors, no empty catches, no ignored return values.

2. **Trace all four data paths** — For every operation, map: happy path, nil/null path, empty collection path, error path. If any path is unhandled, flag it.

3. **Map edge cases for every user interaction** — What happens on double-click? Rapid navigation? Stale data? Expired session? Slow network? No network?

4. **Observability is a first-class deliverable** — Logging, metrics, alerts, and tracing are not afterthoughts. They ship with the feature.

5. **Diagrams mandatory for non-trivial flows** — If a flow involves more than 2 services or 3 steps, draw an ASCII diagram. No exceptions.

6. **Everything deferred documented in TODOS.md** — If we decide not to build something now, it goes in TODOS.md with context on why it was deferred and when to revisit.

7. **Optimize for six-month futures** — Will this decision still make sense in 6 months? Will the team understand this code in 6 months? Will this scale to 10x current load?

8. **Every error must be specifically named** — No generic "Something went wrong." Every error gets a unique name, a user-facing message, and a developer-facing message.

---

## 10-Section Review

### 1. Architecture

- What is the system design? Draw a component/service diagram (ASCII).
- How coupled are the components? Can they be tested independently?
- Where are the component boundaries? Are they in the right place?
- What is the data flow? Trace a request from user action to database and back.
- Does this introduce new dependencies? Are they justified?
- Does this change the deployment topology?

### 2. Error Map

- Enumerate EVERY failure mode in the feature.
- Name each error specifically (e.g., `PAYMENT_PROVIDER_TIMEOUT`, not `NETWORK_ERROR`).
- Trace all four data paths for each operation: happy, nil, empty, error.
- What happens when an upstream service is down?
- What happens when the database is slow or unavailable?
- What error messages does the user see? Are they actionable?

### 3. Security / Threat Model

- What are the auth boundaries? Who can access what?
- Input validation: is every user input validated server-side?
- Secrets management: are API keys, tokens, and credentials handled properly?
- OWASP top 10: does this feature introduce any of the common vulnerabilities?
- Rate limiting: can this endpoint be abused?
- Data exposure: does the API return more data than the client needs?

### 4. Edge Cases

- Empty states: what does the UI show when there's no data?
- Concurrent access: what happens if two users modify the same resource?
- Rate limits: what happens when the user hits rate limits?
- Offline/degraded: what's the experience on slow or no network?
- Timezone edge cases: does this feature handle timezones correctly?
- Unicode/i18n: does this handle international characters?

### 5. Code Quality

- DRY violations: is any logic duplicated?
- Naming: are variables, functions, and files named clearly?
- Complexity: are any functions doing too much? (cyclomatic complexity)
- Tech debt: does this introduce tech debt? Is it documented?
- Consistency: does this follow existing patterns in the codebase?

### 6. Test Review

- Coverage gaps: what code paths are untested?
- Missing scenarios: are edge cases covered in tests?
- Test isolation: do tests depend on each other or external services?
- Test speed: will these tests slow down CI?
- Snapshot vs behavioral: are we testing behavior or implementation?

### 7. Performance

- N+1 queries: are database queries efficient?
- Caching strategy: what should be cached? For how long?
- Bundle size: does this increase client-side bundle significantly?
- Latency estimates: what's the expected response time?
- Load testing: has this been tested under expected load?

### 8. Observability

- Logging: are key operations logged with structured data?
- Metrics: what should be measured? (latency, error rate, throughput)
- Alerts: what conditions should trigger alerts?
- Tracing: can a request be traced across services?
- Health checks: does this feature have a health check endpoint?

### 9. Deployment / Rollout

- Feature flags: is this behind a feature flag?
- Migration plan: does this require database migrations? Are they reversible?
- Rollback strategy: how do we undo this if it breaks?
- Canary/gradual rollout: can we roll this out to a subset of users first?
- Documentation: is the runbook updated?
- **PR layering:** Does this feature cross architectural layers (DB + API + UI)? If so and it exceeds ~200 lines, plan for a layer-based stack: DB/schema → API/services → UI/app.

### 10. Long-Term Trajectory

- Maintainability at 6 months: will a new team member understand this?
- Scalability: does this work at 10x current load? 100x?
- Team ownership: who owns this feature going forward?
- Platform implications: does this create precedent for other features?
- Migration path: if we need to change this later, how hard is it?

---

## Scoring Rubric

Reference: `context/knowledge/patterns/evaluator-loop.md`

Score each section 0.0 to 1.0:

| Section | Criterion | Weight |
|---------|-----------|--------|
| Architecture | Components have clear boundaries, justified dependencies, data flow diagrammed | 0.15 |
| Error Map | All failure modes enumerated, all 4 data paths traced per operation | 0.10 |
| Security | Auth boundaries defined, inputs validated, no OWASP gaps | 0.15 |
| Edge Cases | Empty/concurrent/offline/timezone scenarios covered | 0.10 |
| Code Quality | No DRY violations, consistent naming, appropriate complexity | 0.10 |
| Test Review | All code paths have tests, tests are isolated | 0.10 |
| Performance | No N+1, caching strategy defined, latency estimated | 0.10 |
| Observability | Logging, metrics, alerts, tracing addressed | 0.05 |
| Deployment | Feature flags, migration plan, rollback strategy defined | 0.05 |
| Long-Term | Maintainable at 6mo, scales to 10x, migration path clear | 0.10 |

## Evaluator Loop

After producing the initial review:

1. Score each section against the rubric above
2. If overall weighted score < 0.7 (or project's Quality Contract threshold), identify the 3 lowest-scoring sections
3. Re-analyze those sections with deeper investigation
4. Re-score. Max 3 iterations.

If a `## Quality Contract` exists in the project CLAUDE.md, use its `planning` threshold and priority weights instead of defaults. See `context/knowledge/patterns/quality-contract.md`.

---

## Decision Protocol

When an issue is found during review:

1. **One question per issue** — Don't bundle multiple decisions.

2. **3-4 lettered options with tradeoff analysis:**
   - **(A)** Option name — Description
     - Effort: Low/Medium/High
     - Risk: Low/Medium/High
     - Maintenance: Low/Medium/High
   - **(B)** Option name — Description
     - Effort: ...
     - Risk: ...
     - Maintenance: ...

3. **Never silently decide** — Every architectural decision, every scope cut, every deferral is surfaced to the user with options.

4. **Document decisions** — After the user decides, record the decision and rationale in the plan output.

---

## Output Format

After completing the review, produce:

1. **Score table** (all 10 sections with 0-1 scores, weighted average, iteration count)
2. **Architecture diagram** (ASCII)
3. **Error map** (table of all failure modes)
4. **Risk summary** (top 3 risks with mitigation)
5. **Scope recommendation** (based on selected mode)
6. **Deferred items** (for TODOS.md)
7. **Action items** (prioritized list of what to build)
