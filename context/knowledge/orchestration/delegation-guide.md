# Delegation Guide

Reference for Alex when delegating to sub-agents.

## Agent Selection

| Task Type | Agent | When |
|-----------|-------|------|
| Codebase exploration | `Explore` | Finding files, patterns, "where is X" |
| Web research | `research-specialist` | Docs, best practices, external info |
| Architecture | `Plan` | Design decisions, implementation planning |
| Code writing | `code` | Multi-file coding, features, bug fixes, refactoring |
| Code review | `code` (with `/review` skill) | Pre-PR quality checks |

## Delegation Template

```
## Task: [Title]

### Instructions
[Context + constraints + existing patterns to follow]

### Tasks
1. [Specific and actionable]
2. [Specific and actionable]

### Deliverables
- [ ] [Concrete artifact]
- [ ] [Summary of what was done]

### Time Limit: 5 minutes
If approaching the limit, stop. Document progress. Deliver partial results.
```

## Proof of Work

| Task Type | Required Proof |
|-----------|---------------|
| GUI/UI | Screenshot |
| Terminal/CLI | Log output or command results |
| Research | Summary with sources |
| Code changes | Files changed + test results |
| Bug fixes | Before/after behavior + root cause |

- "I made the changes" is not proof — show the diff, test output, or screenshot
- If an agent returns without artifacts, reject and ask for proof

## Escalation

If an agent returns partial results:
1. Summarize what was completed
2. Ask user if they want to continue
3. Pass prior context to the next agent

## Parallel Execution

Launch multiple agents when tasks are independent. Use a single message with multiple Agent tool calls.

Common patterns:
- Research + Code in parallel
- Multiple research queries in parallel
- Explore current state + research-specialist for best practices
