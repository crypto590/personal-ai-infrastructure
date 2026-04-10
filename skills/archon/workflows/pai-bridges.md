# PAI Skills as Archon Workflows

Bridge existing PAI skills into deterministic Archon workflows. Each bridge wraps a PAI skill's methodology in Archon's DAG structure with proper gates and isolation.

---

## Ship Pipeline → Archon Workflow

Maps the `ship/` skill's 8-step pipeline into a deterministic DAG.

```yaml
# .archon/workflows/pai-ship.yaml
nodes:
  - id: detect-base
    bash: |
      BASE=$(gh pr view --json baseRefName -q '.baseRefName' 2>/dev/null \
        || gh repo view --json defaultBranchRef -q '.defaultBranchRef.name' 2>/dev/null \
        || echo "main")
      echo "Base branch: $BASE"

  - id: merge-upstream
    depends_on: [detect-base]
    bash: "git fetch origin $(git log --format=%s -1 .archon/base) && git merge origin/main"

  - id: build-lint-test
    depends_on: [merge-upstream]
    bash: "turbo run build && turbo run lint && turbo run check-types && turbo run test"

  - id: pre-landing-review
    depends_on: [build-lint-test]
    prompt: |
      Run the PAI 2-pass code review on all changes vs the base branch:
      - Pass 1 (Critical): security, data loss, race conditions, crash paths
      - Pass 2 (Informational): performance, clarity, test gaps, DRY
      Reference: skills/review/SKILL.md

  - id: version-changelog
    depends_on: [pre-landing-review]
    prompt: |
      Analyze commits since last tag. Apply version bump:
      - fix: → PATCH (auto)
      - feat: → MINOR (confirm)
      - BREAKING CHANGE → MAJOR (confirm)
      Generate changelog with user-friendly language.
    loop:
      until: APPROVED
      interactive: true

  - id: logical-commits
    depends_on: [version-changelog]
    prompt: |
      Group changes into logical commits by layer:
      1. Infrastructure/config
      2. DB/schema
      3. Service/API
      4. App/UI
      5. Version + changelog

  - id: open-pr
    depends_on: [logical-commits]
    prompt: "Create PR with conventional title and structured body (Summary, Changes, Test Plan)."
```

---

## Plan → Archon Workflow

Maps the `plan/` skill's 3-agent planning pipeline into parallel Archon nodes.

```yaml
# .archon/workflows/pai-plan.yaml
nodes:
  - id: intake
    prompt: |
      Gather requirements for the feature request.
      Identify scope, constraints, and success criteria.

  - id: product-plan
    depends_on: [intake]
    prompt: |
      Product planning perspective:
      - User stories and acceptance criteria
      - Edge cases and error states
      - Success metrics
      Reference: skills/plan-product/SKILL.md

  - id: design-plan
    depends_on: [intake]
    prompt: |
      Design planning perspective:
      - Component hierarchy and layout
      - Interaction patterns
      - Accessibility requirements
      Reference: skills/plan-design/SKILL.md

  - id: eng-plan
    depends_on: [product-plan, design-plan]
    prompt: |
      Engineering planning — synthesize product + design into:
      - Technical architecture decisions
      - File-level implementation plan
      - Test strategy
      - Feature registry JSON
      Reference: skills/plan-eng/SKILL.md

  - id: review-plan
    depends_on: [eng-plan]
    prompt: "Present the complete plan for approval."
    loop:
      until: APPROVED
      interactive: true
```

---

## Review → Archon Self-Fixing Review

Extends PAI's 2-pass review with automatic fix loops.

```yaml
# .archon/workflows/pai-review-fix.yaml
nodes:
  - id: review-critical
    prompt: |
      Pass 1 — Critical issues only:
      Security vulnerabilities, data loss risks, race conditions,
      contract violations, crash paths, unbounded loops.
      Reference: skills/review/SKILL.md

  - id: fix-critical
    depends_on: [review-critical]
    prompt: "Fix all critical issues identified in the review."
    loop:
      until: ALL_TASKS_COMPLETE
      fresh_context: true

  - id: verify-fixes
    depends_on: [fix-critical]
    bash: "npm run test && npm run lint && npm run check-types"

  - id: review-informational
    depends_on: [verify-fixes]
    prompt: |
      Pass 2 — Informational:
      Performance, clarity, test gaps, accessibility, DRY, drift.
      Score using the 8-criteria rubric from skills/review/SKILL.md

  - id: human-decision
    depends_on: [review-informational]
    prompt: "Present review summary with scores. Ask whether to fix informational issues."
    loop:
      until: APPROVED
      interactive: true
```

---

## Issue → PR (End-to-End)

Complete pipeline: GitHub issue to merged PR, using PAI skills at each stage.

```yaml
# .archon/workflows/pai-issue-to-pr.yaml
nodes:
  - id: classify
    prompt: |
      Read the GitHub issue. Classify as: bug, feature, refactor, docs.
      Estimate effort: small (<1hr), medium (1-4hr), large (4hr+).

  - id: investigate
    depends_on: [classify]
    prompt: |
      Investigate the codebase. Identify:
      - Root cause (bugs) or affected areas (features)
      - Related files and dependencies
      - Existing tests covering this area

  - id: plan
    depends_on: [investigate]
    prompt: |
      Create implementation plan with file-level detail.
      Include test strategy.
      Reference: skills/plan-eng/SKILL.md

  - id: implement
    depends_on: [plan]
    prompt: "Implement the plan. Write tests for each change."
    loop:
      until: ALL_TASKS_COMPLETE
      fresh_context: true

  - id: gate-tests
    depends_on: [implement]
    bash: "npm run test && npm run lint && npm run check-types"

  - id: self-review
    depends_on: [gate-tests]
    prompt: |
      Run 2-pass review on your own changes.
      Fix any critical issues. Log informational items.
      Reference: skills/review/SKILL.md

  - id: approval
    depends_on: [self-review]
    prompt: "Present changes summary and review results for approval."
    loop:
      until: APPROVED
      interactive: true

  - id: ship
    depends_on: [approval]
    prompt: |
      Create logical commits, version bump if needed, open PR.
      Reference: skills/ship/SKILL.md
```

---

## Tips for Bridging PAI Skills

1. **Reference skills in prompts** — `Reference: skills/review/SKILL.md` tells the AI to load and follow that skill
2. **Use bash nodes as gates** — deterministic pass/fail before proceeding
3. **Interactive nodes at decision points** — version bumps, plan approval, PR creation
4. **Fresh context in implement loops** — prevents context pollution across iterations
5. **Parallel nodes for independent work** — product + design planning can run simultaneously
