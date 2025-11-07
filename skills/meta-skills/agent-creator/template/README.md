# Agent Template Usage

This template provides a complete starting point for creating new Claude Code sub-agents.

## Quick Start

1. **Copy the template:**
   ```bash
   cp ~/Claude/skills/meta-skills/agent-creator/template/agent-template.md ~/Claude/agents/your-agent-name.md
   ```

2. **Fill in the YAML frontmatter:**
   - `name`: Your agent's identifier (kebab-case)
   - `description`: Detailed description with 2-4 `<example>` blocks
   - `model`: Choose `sonnet` (default), `opus`, `haiku`, or omit to inherit
   - `tools`: Optional - omit for all tools, or list specific ones

3. **Replace all placeholders:**
   - All text in `[brackets]` should be replaced with actual content
   - Remove or modify sections that don't apply

4. **Reference skills and knowledge:**
   - Use relative paths: `../../skills/category/name/SKILL.md`
   - Use relative paths: `../../context/knowledge/topic.md`
   - Verify referenced files exist

5. **Test your agent:**
   - Ask Claude Code: "List available agents"
   - Test invocation: "Use the [agent-name] agent to [task]"

## Template Sections Explained

### YAML Frontmatter
- **Required:** `name`, `description`
- **Optional:** `model`, `tools`, `color`
- **Critical:** Include multiple `<example>` blocks in description

### Skills & Knowledge
Link to capabilities and reference materials the agent needs. Use relative paths from the agents directory.

### Core Responsibilities
List what this agent does - its primary functions and duties.

### Development Principles
How the agent approaches its work - philosophies and methodologies.

### Code Quality Standards
Specific standards this agent follows (naming, testing, documentation, etc.).

### Workflow Section
Step-by-step process for the agent's primary task (e.g., "When Writing Code:", "When Reviewing PRs:").

### Output Expectations
What the agent should produce - be specific about deliverables.

### Additional Context
Any extra guidelines, constraints, or considerations.

## Example: Creating a Python Specialist Agent

```bash
# Copy template
cp ~/Claude/skills/meta-skills/agent-creator/template/agent-template.md ~/Claude/agents/python-specialist.md

# Edit the file (replace placeholders with):
# - name: python-specialist
# - Role: expert Python developer
# - Skills: Python best practices, testing, async programming
# - Responsibilities: Write Pythonic code, implement type hints, etc.
```

## Tips

- **Be Specific:** Vague descriptions lead to poor agent invocation
- **Multiple Examples:** Include 2-4 diverse examples in the description
- **Test Early:** Create the file and test invocation before writing the full prompt
- **Reference, Don't Duplicate:** Link to skills rather than copying their content
- **Output Focus:** Be clear about what the agent should produce

## Resources

- **Full Documentation:** [../SKILL.md](../SKILL.md) - Complete agent-creator meta-skill guide
- **Agent Template:** [agent-template.md](agent-template.md) - The actual template file
- **Existing Agents:** `/Users/coreyyoung/Claude/agents/` - Real examples to learn from
- **Available Skills:** `/Users/coreyyoung/Claude/skills/` - Skills you can reference
- **Knowledge Base:** `/Users/coreyyoung/Claude/context/knowledge/` - Reference materials
