---
name: workflow
effort: high
model: claude-opus-4-6
context: fork
argument-hint: "[feature description | phase name]"
description: |
  Unified development workflow: research > spec > plan > code > verify > review > ship > retro.
  HITL gates at every phase transition. Advisor pattern (Opus advises, Sonnet executes).
  Evaluator loops run until each phase meets its quality threshold.
  Invoke with /workflow to start a new feature, or /workflow <phase> to jump to a phase.
metadata:
  last_reviewed: 2026-04-09
  review_cycle: 60
---

# Workflow — Unified Development Lifecycle

Opinionated, gated workflow that takes a feature from idea to shipped code. Every phase produces a deliverable, every transition requires human approval, and sub-agents run evaluator loops until quality thresholds are met.

## Philosophy

1. **Prove it, don't promise it.** Every phase produces artifacts the human can inspect.
2. **Stop the line.** A failing gate blocks the pipeline. No skipping.
3. **Advisor pattern.** Opus advises on hard decisions; Sonnet/Haiku executes the work. Near-Opus quality at a fraction of the cost.
4. **Anti-rationalization.** Each gate has explicit excuse/rebuttal pairs to prevent reasoning around steps.
5. **Source-driven.** Framework code cites official docs, not training data.

---

## Invocation

- `/workflow` — Start from the beginning (Research phase) with a feature description
- `/workflow spec` — Jump to the Spec phase (assumes research is done)
- `/workflow plan` — Jump to Plan phase
- `/workflow code` — Jump to Code phase
- `/workflow verify` — Jump to Verify phase
- `/workflow review` — Jump to Review phase
- `/workflow ship` — Jump to Ship phase
- `/workflow retro` — Jump to Retro phase

When invoked without a phase, ask for the feature description if not provided.

---

## Architecture: Advisor + Evaluator Pattern

```
                    ┌─────────────┐
                    │   HUMAN     │
                    │  (approver) │
                    └──────┬──────┘
                           │ approve / reject + feedback
                           ▼
┌──────────────────────────────────────────────────┐
│              ORCHESTRATOR (Opus)                  │
│  Routes phases, enforces gates, advises on hard  │
│  decisions, runs evaluator loops                 │
└──────────┬───────────────────────────┬───────────┘
           │ delegate                  │ delegate
           ▼                           ▼
┌─────────────────┐        ┌─────────────────┐
│ EXECUTOR AGENT  │        │ EXECUTOR AGENT  │
│ (Sonnet/Haiku)  │        │ (Sonnet/Haiku)  │
│ Does the work   │        │ Parallel tasks  │
└─────────────────┘        └─────────────────┘
```

### Advisor Pattern (from Claude Platform)

When an executor agent hits a hard decision mid-task, it consults the orchestrator (Opus) for guidance:

- **Architecture choices** — "Should I use server actions or API routes here?"
- **Ambiguous requirements** — "The spec says X but the codebase does Y"
- **Security-sensitive decisions** — "This auth flow needs a design call"
- **Performance tradeoffs** — "Eager vs lazy loading for this data"

The advisor returns a plan, not code. The executor continues with the plan.

### Evaluator Loop

Every phase runs an evaluator loop:

```
EXECUTE ──→ SCORE ──→ threshold met? ──→ YES ──→ HITL GATE
                         │
                         NO
                         │
                         ▼
                    FEEDBACK ──→ RE-EXECUTE (max 3 iterations)
                                     │
                                     ▼
                               still failing?
                                     │
                                     ▼
                              ESCALATE TO HUMAN
```

Scoring uses the rubric defined per phase. Max 3 iterations before escalating — infinite loops are a bug, not a feature.

---

## Phase 1: RESEARCH

**Goal:** Understand the problem space, technology landscape, and existing codebase patterns before committing to an approach.

**Skills activated:** `research`, `defuddle`, `source-driven-development`, `gitnexus-exploring`

**Sub-agent strategy:** Spawn parallel research agents:
- Agent 1 (Sonnet): Codebase exploration — existing patterns, adjacent code, conventions
- Agent 2 (Sonnet): External research — framework docs, library options, prior art

**Deliverable:**
```markdown
## Research Summary: [feature]

### Codebase Context
- Existing patterns relevant to this feature
- Adjacent code and conventions to follow
- Dependencies and their versions

### Technology Assessment
- Framework capabilities (with doc citations)
- Library options evaluated (if applicable)
- Known constraints or limitations

### Recommendations
- Recommended approach with rationale
- Alternatives considered and why they were rejected

### Open Questions
- [Questions that need human input before proceeding]
```

**Quality threshold:** 0.7 — research must cite sources and identify codebase patterns.

**HITL Gate:**
- Present the research summary
- Ask: "Does this research cover the problem space? Any areas to dig deeper?"
- Wait for explicit approval before proceeding

| Rationalization | Reality |
|---|---|
| "I already know this framework" | Training data goes stale. Verify against current docs. |
| "Research slows us down" | 10 minutes of research prevents hours of rework on the wrong approach. |
| "The codebase is simple enough" | Every codebase has conventions. Miss them and the PR gets rejected. |

---

## Phase 2: SPEC

**Goal:** Convert the approved research into a concrete specification with testable success criteria and clear boundaries.

**Skills activated:** `spec-driven-development`

**Sub-agent strategy:** Single Sonnet agent writes the spec. Opus reviews for completeness.

**Deliverable:** A spec document saved to `docs/specs/<feature-slug>.md` covering:
1. Objective and success criteria (concrete, measurable)
2. Tech stack with exact versions (from lockfiles)
3. Project structure (where new code goes)
4. Code style (one example snippet matching codebase conventions)
5. Testing strategy (what levels, what coverage)
6. Boundaries: Always / Ask First / Never
7. Not Doing list (explicit scope exclusions)

**Quality threshold:** 0.8 — spec must have measurable success criteria and explicit boundaries.

**Evaluator criteria:**
- Success criteria are testable (not "make it fast" but "LCP < 2.5s")
- Boundaries section has all three tiers populated
- Not Doing list exists and is non-empty
- Assumptions are surfaced, not hidden

**HITL Gate:**
- Present the full spec
- Surface assumptions explicitly: "I'm assuming X, Y, Z — correct?"
- Ask: "Does this spec capture what you want? Any scope changes?"
- Wait for explicit approval

| Rationalization | Reality |
|---|---|
| "This is too small for a spec" | Small tasks need small specs (2 lines of acceptance criteria). They still need them. |
| "We'll figure it out as we go" | That's how features bloat. A spec lets you say "that's out of scope." |
| "The research already covers this" | Research is understanding. Spec is commitment. Different artifacts. |

---

## Phase 3: PLAN

**Goal:** Break the spec into an ordered task list with dependencies, risk assessment, and vertical slices.

**Skills activated:** `plan` (spawns product/design/eng sub-agents), `plan-eng`

**Sub-agent strategy:** The `plan` skill already spawns 3 sub-agents (product, design, engineering). Each contributes criteria to a shared feature registry.

**Deliverable:** Feature registry at `docs/feature-registry/<feature-slug>.json` plus a task breakdown:
- Tasks ordered by dependency (not importance)
- Each task: description, acceptance criteria, verify step, files touched
- Tasks sized XS/S/M/L — any XL must be broken down further
- Risk items flagged with mitigation strategies
- Vertical slices preferred over horizontal layers

**Quality threshold:** 0.8 — no XL tasks, every task has acceptance criteria.

**Evaluator criteria:**
- No task touches more than ~5 files
- Every task has a verify step (test command, build, manual check)
- Dependencies form a valid DAG (no cycles)
- First task is implementable without waiting on anything

**HITL Gate:**
- Present the task list with time estimates removed (we don't estimate)
- Ask: "Does this breakdown make sense? Any tasks missing or mis-scoped?"
- Wait for explicit approval

| Rationalization | Reality |
|---|---|
| "I can hold this in my head" | If it's in your head, the next agent can't pick it up. Write it down. |
| "Planning is waterfall" | 15 minutes of planning prevents 15 hours of debugging. This is agile, not BDUF. |
| "Tasks will change anyway" | Yes. A living task list is still better than no task list. |

---

## Phase 4: CODE

**Goal:** Implement each task from the plan, one at a time, with source-verified framework patterns and incremental commits.

**Skills activated:** `source-driven-development`, `debugging-and-error-recovery`, platform skills (ios-swift, kotlin-android, vercel-react-best-practices)

**Sub-agent strategy:**
- Spawn a code agent (Sonnet) per task or per parallel-safe task group
- Each agent gets: the spec, the current task, and relevant source files only (not the whole plan)
- Agent consults Opus advisor for architectural decisions or ambiguous requirements
- Agent uses `source-driven-development`: detect versions from lockfiles, fetch docs, cite in code

**Per-task cycle:**
```
1. Read the task from the plan
2. Detect framework versions (source-driven-development)
3. Fetch relevant docs if framework-specific
4. Implement following documented patterns
5. Write/update tests (test must fail without the change, pass with it)
6. Run tests: all pass?
   ├── YES → Commit with conventional message
   └── NO → Apply debugging-and-error-recovery triage
7. Move to next task
```

**Hard limit:** No more than 100 lines of new code without running tests.

**Quality threshold:** 0.8 — all tests pass, framework patterns cite sources, no unbounded iteration.

**HITL Gate:**
- After each major task group (not every micro-task), present:
  - Diff summary (what changed and why)
  - Source citations for framework decisions
  - Test results
- Ask: "Ready to continue to the next group, or changes needed?"

| Rationalization | Reality |
|---|---|
| "I know this API from training data" | Training data contains deprecated patterns that compile but are wrong. Verify. |
| "Tests slow me down" | Tests slow you down less than debugging a broken feature for an hour. |
| "I'll write tests after" | After never comes. Test as you go or the coverage gaps compound. |
| "This is a simple change" | Simple changes with wrong patterns become templates copied into 10 files. |

---

## Phase 5: VERIFY

**Goal:** Comprehensive quality verification: tests, security audit, performance check, and QA health score.

**Skills activated:** `qa`, `security-and-hardening`, `performance-optimization`, `debugging-and-error-recovery`

**Sub-agent strategy:** Spawn parallel verification agents:
- Agent 1 (Sonnet): Run `/qa report` — 8-category health score
- Agent 2 (Sonnet): Security audit — OWASP Top 10 checklist, npm audit, secret scanning
- Agent 3 (Sonnet): Performance check — bundle size, N+1 queries, Core Web Vitals (if applicable)

**Deliverable:**
```markdown
## Verification Report: [feature]

### QA Health Score: X.XX / 1.00
[8-category breakdown from qa skill]

### Security Audit
- [ ] Input validation at boundaries
- [ ] No secrets in code
- [ ] Auth/authz on protected endpoints
- [ ] npm audit clean (or triaged)
[Findings listed with severity]

### Performance Check
- Bundle size delta: +/- X KB
- N+1 queries: none / [list]
- Core Web Vitals impact: [assessment]

### Issues Found
#### Critical (blocks ship)
[list or "none"]

#### Informational (improve later)
[list]
```

**Quality threshold:** 0.85 — no critical security issues, QA health > 0.8, no N+1 queries.

**Evaluator loop:** If threshold not met, the agent attempts auto-fixes for safe issues (dead code, missing indexes, lint). Re-scores. Escalates critical issues to human.

**HITL Gate:**
- Present the verification report
- Flag any critical issues that need human decision
- Ask: "Verification complete. Approve for review, or fix issues first?"

| Rationalization | Reality |
|---|---|
| "Security review is overkill for this" | Automated scanners find every endpoint. Security review is cheap insurance. |
| "Performance is fine, it's a small feature" | Small features add up. Check the delta, not the absolute. |
| "Tests pass, that's enough" | Tests check correctness. Verify checks security, performance, and quality. Different axes. |

---

## Phase 6: REVIEW

**Goal:** Code review with severity-labeled findings, AI pattern detection, and a clear verdict.

**Skills activated:** `review`, `gitnexus-pr-review`, `humanizer` (for documentation)

**Sub-agent strategy:**
- Agent 1 (Opus): Primary code review — 2-pass critical/informational, scoring rubric
- Agent 2 (Sonnet): GitNexus impact analysis — blast radius, dependency tracing

**Deliverable:** Full review output from the `review` skill:
- Pass 1: Critical issues (blocks merge)
- Pass 2: Informational (improves quality)
- AI pattern detection results
- 8-criterion scoring rubric
- Risk assessment (Low/Medium/High)
- Human focus areas (file:line with reasons)
- Verdict: APPROVE / APPROVE WITH NITS / CHANGES REQUESTED / HARD NO

**Quality threshold:** Weighted average >= 0.8 across the 8-criterion rubric.

**Evaluator loop:** If CHANGES REQUESTED, the orchestrator:
1. Routes critical issues back to a code agent for fixing
2. Re-runs the review (max 2 review iterations)
3. If still failing after 2 iterations, escalates to human with full context

**HITL Gate:**
- Present the review with verdict
- If APPROVE or APPROVE WITH NITS: "Review passed. Ready to ship?"
- If CHANGES REQUESTED after agent fixes: "Agent addressed [N] issues. [M] remain. Your call."
- Wait for explicit ship approval

| Rationalization | Reality |
|---|---|
| "I wrote the code, I don't need to review it" | You also wrote the bugs. Fresh eyes (even agent eyes) catch what you missed. |
| "The tests pass, review is formality" | Tests check behavior. Review checks architecture, security, patterns, and clarity. |
| "Review takes too long" | A 5-minute review prevents a 5-hour production incident. |

---

## Phase 7: SHIP

**Goal:** Version, changelog, commit, and open PR with the full pipeline from the `ship` skill.

**Skills activated:** `ship`, `graphite` (if available), `document-release`

**Sub-agent strategy:** Single agent runs the `ship` pipeline (already non-interactive except for defined pause points).

**Pipeline:** (from ship skill)
1. Detect base branch
2. Merge upstream changes
3. Run turbo pipeline (build/lint/type-check/test)
4. Pre-landing review (already done in Phase 6 — skip if no new changes)
5. Version bump (PATCH auto, MINOR/MAJOR ask)
6. Generate changelog
7. Create logical commits or stacked PRs
8. Open PR

**HITL Gate (built into ship):**
- Merge conflicts → pause
- Build/test failures → pause
- MINOR/MAJOR version bumps → confirm
- PR body → present for review before opening

| Rationalization | Reality |
|---|---|
| "I'll just push directly" | PRs create a review record. Even solo developers benefit from the paper trail. |
| "Changelog is busywork" | Changelogs are for your future self and your users. Write them now or reconstruct them later. |
| "Stacked PRs are overkill" | For > 200 lines across layers, stacked PRs get faster reviews and safer merges. |

---

## Phase 8: RETRO

**Goal:** Capture lessons learned, update skills, and close the loop.

**Skills activated:** `retro`, `document-release`, `memory`

**Sub-agent strategy:** Single Sonnet agent runs the retro analysis.

**Deliverable:**
```markdown
## Retro: [feature]

### What went well
- [Specific things that worked]

### What could improve
- [Specific friction points]

### Lessons for next time
- [Actionable takeaways]

### Skill updates needed
- [Any skills that need updating based on what we learned]
```

**HITL Gate:**
- Present the retro summary
- Ask: "Anything to add? Should any of these lessons become permanent memories?"
- Save approved lessons via `/remember`

| Rationalization | Reality |
|---|---|
| "We already shipped, retro is waste" | The retro is 5 minutes. The lessons compound across every future feature. |
| "I'll remember what went wrong" | You won't. Write it down. Memory is a lossy protocol. |

---

## Phase Summary

```
┌──────────┐    ┌──────┐    ┌──────┐    ┌──────┐
│ RESEARCH │───→│ SPEC │───→│ PLAN │───→│ CODE │
│ 0.7 min  │ ✋ │ 0.8  │ ✋ │ 0.8  │ ✋ │ 0.8  │
└──────────┘    └──────┘    └──────┘    └──────┘
                                            │
     ┌──────────┐    ┌────────┐    ┌────────┐
     │  RETRO   │←───│  SHIP  │←───│ REVIEW │←───│ VERIFY │
     │  (end)   │ ✋ │  ship  │ ✋ │  0.8   │ ✋ │  0.85  │
     └──────────┘    └────────┘    └────────┘    └────────┘

✋ = HITL gate (human approval required)
0.X = quality threshold for evaluator loop
```

---

## Skipping Phases

Some work doesn't need all 8 phases. Use judgment:

| Scenario | Start at |
|---|---|
| New feature, unclear requirements | Phase 1: Research |
| Feature with clear spec from PM | Phase 3: Plan |
| Bug fix with known root cause | Phase 4: Code |
| Code complete, needs QA | Phase 5: Verify |
| Ready to merge | Phase 7: Ship |

**Rule:** You can skip forward, never backward. If Phase 5 reveals the spec was wrong, go back to Phase 2 and re-spec — don't patch around it.

---

## Quick Reference: Skills by Phase

| Phase | Primary Skill | Supporting Skills |
|---|---|---|
| Research | `research` | `defuddle`, `source-driven-development`, `gitnexus-exploring` |
| Spec | `spec-driven-development` | — |
| Plan | `plan` | `plan-eng`, `plan-product`, `plan-design` |
| Code | `source-driven-development` | platform skills, `debugging-and-error-recovery` |
| Verify | `qa` | `security-and-hardening`, `performance-optimization` |
| Review | `review` | `gitnexus-pr-review`, `humanizer` |
| Ship | `ship` | `graphite`, `document-release` |
| Retro | `retro` | `memory`, `remember` |
