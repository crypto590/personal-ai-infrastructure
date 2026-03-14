# Propose Amendment Workflow

Step-by-step process for proposing a skill amendment.

## Prerequisites

- NEON_DATABASE_URL configured
- Skill has observations in the database
- Inspection report shows degraded/failing health

## Steps

### Step 1: Run Inspection

```bash
uv run ~/.claude/scripts/skill-tracker/inspect.py "<skill-name>" --json
```

Save the output — you'll reference it in the rationale.

### Step 2: Read Current Skill

Read the SKILL.md that needs amendment. Note the current version number.

### Step 3: Identify Root Cause

From the inspection report, answer:
1. What is the most common error type?
2. What specific error details repeat?
3. Is the failure in the skill instructions, tool calls, or trigger routing?
4. Is it project-specific or universal?

### Step 4: Draft the Change

Write the minimum diff that addresses the root cause.

Rules:
- Change as little as possible
- Don't restructure the entire skill
- Focus on the specific failure pattern
- Add, don't remove (unless something is clearly wrong)
- Preserve the skill's existing voice and format

### Step 5: Record in Database

Use the amend.py script or record directly:

```python
# Via the amend.py script
uv run ~/.claude/scripts/skill-tracker/amend.py \
  --skill "code-review" \
  --type "fix_tool_call" \
  --rationale "SwiftLint path not found in 4/7 runs..." \
  --evidence "[101, 103, 105, 107]" \
  --original-file "~/.claude/skills/technical/code-review/SKILL.md"
```

### Step 6: Present to User

Format the proposal as:

```
## Proposed Amendment: <skill-name>

**Type:** fix_tool_call
**Evidence:** 4 failures in last 7 runs (observations #101, #103, #105, #107)
**Root cause:** SwiftLint path assumes global installation

### Current:
[relevant section of SKILL.md]

### Proposed:
[amended section]

### Risk:
- Low: Change is additive (fallback path)
- No impact on projects where SwiftLint is globally installed

Apply this amendment? [Yes / No / Modify]
```

### Step 7: Apply if Approved

1. Store current SKILL.md as `original_content` in the amendment record
2. Apply the diff to the file
3. Update `skills.current_version` in the database
4. Mark amendment status as 'applied'
5. Set `applied_at` timestamp
