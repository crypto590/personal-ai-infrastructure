# Skill Testing Guide

Based on Anthropic's recommended testing framework for Claude skills.

## Three Types of Tests

### 1. Triggering Tests

Verify the skill loads when it should and doesn't when it shouldn't.

**How to test:** Ask Claude these queries and check if the skill auto-loads.

| Test Type | Expected | Example |
|-----------|----------|---------|
| Obvious trigger | Loads | "Run iOS code quality checks" -> ios-check loads |
| Paraphrased trigger | Loads | "Check my Swift code" -> ios-check loads |
| Unrelated query | Does NOT load | "Write a Python script" -> ios-check stays dormant |

**Target:** 90% trigger rate on relevant queries (test 10-20 queries per skill).

**Quick diagnostic:** Ask Claude "When would you use [skill-name]?" to verify it understands the skill's purpose from the description alone.

**If undertriggering:** Make the description more "pushy" - add more trigger phrases, be more explicit about when to use.

**If overtriggering:** Add negative triggers ("NOT for X"), narrow the scope of the description.

### 2. Functional Tests

Verify the skill produces correct output.

**Test structure:** Given -> When -> Then

```
Given: [precondition - e.g., iOS project exists]
When:  [action - e.g., /ios-check --test]
Then:  [expected result - e.g., SwiftLint runs, build succeeds, tests pass]
```

**Checklist per skill:**
- [ ] Valid outputs generated for happy path
- [ ] Error handling works for common failures
- [ ] External tool calls succeed (API, MCP, CLI)
- [ ] Edge cases handled (empty input, missing files, no data)
- [ ] Output format matches expected structure

### 3. Performance Comparison

Compare task completion with and without the skill.

| Metric | Without Skill | With Skill | Target |
|--------|--------------|------------|--------|
| Messages/turns needed | ? | ? | 50% reduction |
| Failed tool calls | ? | ? | 0 |
| Token consumption | ? | ? | Lower |
| User corrections needed | ? | ? | 0 |
| Consistent across runs | ? | ? | 3/3 identical |

## Testing Workflow

### For New Skills
1. Write 10 triggering test queries (mix of obvious, paraphrased, and unrelated)
2. Run 3 functional tests (happy path, error case, edge case)
3. Run the same task 3 times and check consistency

### For Existing Skills (Quarterly Review)
1. Re-run triggering tests - has anything changed?
2. Check if descriptions need updating for new use cases
3. Verify external dependencies still work
4. Run validate_skill.py for structural issues

## Test Template

Create a `tests.md` file in your skill directory:

```markdown
# [skill-name] Test Cases

## Triggering Tests
| # | Query | Should Load? | Result |
|---|-------|-------------|--------|
| 1 | "[obvious trigger]" | Yes | |
| 2 | "[paraphrased trigger]" | Yes | |
| 3 | "[edge case trigger]" | Yes | |
| 4 | "[unrelated query]" | No | |
| 5 | "[similar but wrong domain]" | No | |

## Functional Tests
| # | Given | When | Then | Result |
|---|-------|------|------|--------|
| 1 | [precondition] | [action] | [expected] | |
| 2 | [error condition] | [action] | [error handled] | |
| 3 | [edge case] | [action] | [graceful output] | |

## Performance Notes
- Baseline (without skill): ___ messages, ___ tokens
- With skill: ___ messages, ___ tokens
- Consistency: ___/3 identical results
```

## Anti-Patterns to Watch For

- **Vague descriptions** → Low trigger rate
- **Missing negative triggers** → False positive triggers on unrelated tasks
- **Overly long SKILL.md** → Token waste, Claude may miss key instructions
- **No error handling** → Skill fails silently on edge cases
- **Hardcoded paths** → Breaks on different machines/projects
