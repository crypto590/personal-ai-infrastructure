# Commands Directory

Custom workflows and command sequences for common tasks.

## What Goes Here

**Commands** are reusable workflow sequences - step-by-step processes you follow regularly.

Unlike **skills** (capabilities/approaches) or **context** (knowledge), commands are **concrete sequences of actions**.

## Examples

- `deploy-app.md` - Standard deployment checklist and commands
- `code-review.md` - Code review workflow and checklist
- `setup-project.md` - New project setup sequence
- `debug-process.md` - Systematic debugging workflow
- `release-process.md` - Release checklist and steps
- `onboarding.md` - Onboarding to a new codebase
- `research-task.md` - Research methodology steps

## Command File Format

```markdown
# Command Name

**Purpose:** [What this command workflow achieves]

**When to use:** [Trigger conditions]

---

## Prerequisites

- [Requirement 1]
- [Requirement 2]

---

## Steps

### 1. [Step Name]

**Action:** [What to do]

**Command/Code:**
\`\`\`bash
command here
\`\`\`

**Expected outcome:** [What should happen]

### 2. [Step Name]

**Action:** [What to do]

**Expected outcome:** [What should happen]

### 3. [Continue...]

---

## Verification

How to verify the workflow completed successfully:

- [ ] Check 1
- [ ] Check 2
- [ ] Check 3

---

## Common Issues

**Issue:** [Problem that might occur]
**Solution:** [How to resolve]

---

## Related

- Skills: [Related skills]
- Context: [Related knowledge]
```

## Commands vs. Skills vs. Context

| Type | Purpose | Example |
|------|---------|---------|
| **Command** | Step-by-step workflow | "Deploy App" sequence |
| **Skill** | Capability/approach | "Deployment Strategy" skill |
| **Context** | Knowledge/reference | "Vercel Platform" knowledge |

**You might use all three together:**
1. Load **skill** `deployment.md` (deployment strategy)
2. Load **context** `knowledge/tools/vercel.md` (Vercel knowledge)
3. Execute **command** `deploy-app.md` (actual deployment steps)

## Current Status

**This directory is currently empty.**

As you develop recurring workflows, add them here as command files.

## Tips

1. **Create commands for processes you repeat:** If you do it more than 3 times, make it a command
2. **Be specific:** Commands should be concrete step-by-step instructions
3. **Include verification:** Always add verification steps
4. **Document gotchas:** Add common issues and solutions
5. **Keep updated:** Update commands when processes change

---

**Questions?** See `/Users/coreyyoung/Claude/context/CLAUDE.md` for complete PAI documentation.
