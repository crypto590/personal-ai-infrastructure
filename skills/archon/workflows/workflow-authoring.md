# Authoring Custom Archon Workflows

## Workflow File Structure

Workflows are YAML files in `.archon/workflows/`. Each defines a directed acyclic graph (DAG) of nodes.

```yaml
# .archon/workflows/my-workflow.yaml
nodes:
  - id: step-1
    prompt: "Analyze the codebase and create a plan"

  - id: step-2
    depends_on: [step-1]
    bash: "npm run test"

  - id: step-3
    depends_on: [step-2]
    prompt: "Review test results and fix any failures"
    loop:
      until: ALL_TASKS_COMPLETE
      fresh_context: true
```

---

## Node Types

### AI Node (prompt)
Sends a prompt to the AI assistant. The AI has full access to the codebase and tools.

```yaml
- id: plan
  prompt: |
    Analyze the GitHub issue and create an implementation plan.
    Break it into concrete steps with file paths.
```

### Bash Node
Runs a deterministic shell command. No AI involvement.

```yaml
- id: run-tests
  depends_on: [implement]
  bash: "npm run test 2>&1"
```

### Loop Node
Repeats until a condition is met. Useful for implement-test-fix cycles.

```yaml
- id: implement-loop
  depends_on: [plan]
  prompt: "Implement the next task from the plan. Run tests after each change."
  loop:
    until: ALL_TASKS_COMPLETE    # AI decides when done
    fresh_context: true           # Clean context each iteration
```

### Interactive Node
Pauses for human input before continuing.

```yaml
- id: human-review
  depends_on: [implement-loop]
  prompt: "Present the changes for review"
  loop:
    until: APPROVED
    interactive: true             # Waits for human response
```

---

## Dependencies

Use `depends_on` to control execution order. Nodes without dependencies run first. Independent nodes can run in parallel.

```yaml
nodes:
  - id: plan
    prompt: "Create implementation plan"

  # These two run in PARALLEL after plan completes
  - id: implement-frontend
    depends_on: [plan]
    prompt: "Implement the frontend changes"

  - id: implement-backend
    depends_on: [plan]
    prompt: "Implement the backend changes"

  # This waits for BOTH to complete
  - id: integration-test
    depends_on: [implement-frontend, implement-backend]
    bash: "npm run test:integration"
```

---

## Loop Conditions

| Condition | Meaning |
|---|---|
| `ALL_TASKS_COMPLETE` | AI determines all planned tasks are done |
| `APPROVED` | Human approves (requires `interactive: true`) |
| `TESTS_PASS` | All tests pass |

### `fresh_context: true`
Each loop iteration starts with a clean AI context. Prevents context pollution from failed attempts. The AI still sees the codebase and previous changes via git.

---

## Overriding Default Workflows

To customize a built-in workflow:

```bash
# Copy the default
cp ~/.archon/workflows/defaults/archon-fix-github-issue.yaml \
   .archon/workflows/archon-fix-github-issue.yaml

# Edit your copy — same filename overrides the default
```

Your repo-level file takes precedence over the bundled default.

---

## Example: Full Feature Workflow

```yaml
# .archon/workflows/feature-with-review.yaml
nodes:
  - id: classify
    prompt: |
      Read the feature request. Classify complexity as small/medium/large.
      Identify affected areas of the codebase.

  - id: plan
    depends_on: [classify]
    prompt: |
      Create a detailed implementation plan with:
      1. Files to create/modify
      2. Tests to write
      3. Migration steps if needed

  - id: implement
    depends_on: [plan]
    prompt: "Implement the plan. Write tests for each change."
    loop:
      until: ALL_TASKS_COMPLETE
      fresh_context: true

  - id: test
    depends_on: [implement]
    bash: "npm run test && npm run lint && npm run check-types"

  - id: self-review
    depends_on: [test]
    prompt: |
      Review all changes against the original request.
      Check for: security issues, missing edge cases, test coverage.
      Fix any issues found.

  - id: approval
    depends_on: [self-review]
    prompt: "Present a summary of all changes for human review."
    loop:
      until: APPROVED
      interactive: true

  - id: create-pr
    depends_on: [approval]
    prompt: "Create a pull request with a clear title and description."
```

---

## Tips

1. **Start from defaults** — copy and modify built-in workflows rather than writing from scratch
2. **Use bash nodes for gates** — `bash: "npm run test"` fails fast if tests break
3. **Fresh context in loops** — prevents accumulated confusion in long implement-fix cycles
4. **Parallel branches** — split independent work into parallel nodes for speed
5. **Interactive gates before PRs** — always add a human approval node before creating PRs
