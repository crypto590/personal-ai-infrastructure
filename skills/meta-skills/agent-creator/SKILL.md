---
name: agent-creator
description: Meta-skill for creating Claude Code sub-agents with proper skill and context references using PAI architecture
key_info: "Agents go in ~/Claude/agents/, reference skills via relative paths (../../skills/), auto-discovered via ~/.claude/ symlinks"
metadata:
  author: coreyyoung
  version: 1.0.0
  category: meta
  tags: [agent, creation, pai-architecture, scaffolding]
---

# Agent Creator Meta-Skill

**Purpose:** Generate Claude Code sub-agents with proper skill and context integration within your PAI architecture.

---

## Quick Reference

**Agent File Location:** `/Users/coreyyoung/Claude/agents/`
**Discovery Path:** `~/.claude/agents/` (symlinked)
**Skill References:** Use relative paths `../../skills/skill-name/SKILL.md`
**Knowledge References:** Use relative paths `../../context/knowledge/topic.md`

---

## Agent File Structure

```markdown
---
name: agent-name
description: When to invoke this agent with examples
tools: Read, Write, Edit, Bash, Grep, Glob  # Optional, omit for all tools
model: sonnet  # Optional: sonnet, opus, haiku, or inherit
color: blue  # Optional: visual indicator
---

You are a [role description] specializing in [expertise areas].

**Skills & Knowledge:**
- [Skill Name](../../skills/category/skill-name/SKILL.md) - Brief description
- [Knowledge Topic](../../context/knowledge/topic.md) - Brief description

**Core Responsibilities:**
[What this agent does]

**Development Principles:**
[How this agent works]

[Rest of detailed system prompt]
```

---

## Creating a New Agent: Step-by-Step

### 1. Define Agent Purpose

Ask yourself:
- What specific problem does this agent solve?
- When should the main AI invoke this agent?
- What expertise/domain does it specialize in?
- What skills and knowledge does it need?

### 2. Identify Required Skills & Knowledge

**Skills** (capabilities):
- Check `/Users/coreyyoung/Claude/skills/` for existing skills
- Use `find ~/Claude/skills -name "SKILL.md"` to list all skills
- Create new skills if needed

**Knowledge** (reference materials):
- Check `/Users/coreyyoung/Claude/context/knowledge/` for existing docs
- Common categories: languages, frameworks, domains, patterns

### 3. Choose Tools Access

**Two approaches:**

1. **Omit `tools` field** - Agent inherits ALL tools from main conversation
   - Best for general-purpose agents
   - Includes MCP server tools automatically

2. **Specify tools** - Granular control for security/focus
   - Only grant necessary tools
   - Common tools: `Read, Write, Edit, Bash, Grep, Glob, Task, WebSearch, WebFetch`
   - See full list in Claude Code docs

### 4. Select Model

- `sonnet` - Default, balanced performance (Claude Sonnet 4.5)
- `opus` - Most capable, for complex strategic decisions (Claude Opus 4)
- `haiku` - Fast and cost-effective for simple tasks
- `inherit` or omit - Uses same model as parent conversation

### 5. Write Description with Examples

The `description` field should include:
- Clear trigger conditions
- 2-3 `<example>` blocks showing when to invoke
- Include `<commentary>` explaining the reasoning

Example:
```yaml
description: Use this agent when you need to create, modify, or optimize Kotlin code for Android applications. This includes implementing Android UI components, managing app lifecycle, integrating with Android APIs, and following Android/Kotlin best practices. <example>\nContext: User needs Android-specific implementation\nuser: "Create a RecyclerView adapter for a list of users"\nassistant: "I'll use the kotlin-specialist agent to implement this Android component"\n<commentary>\nThis requires Kotlin and Android SDK knowledge, use the specialized agent.\n</commentary>\n</example>
```

### 6. Reference Skills & Knowledge

**In the agent body, include a section:**

```markdown
**Skills & Knowledge:**
- [Kotlin Best Practices](../../skills/technical/kotlin/SKILL.md) - Modern Kotlin patterns
- [Android Development](../../skills/technical/android/SKILL.md) - Android SDK expertise
- [Testing Patterns](../../context/knowledge/testing/android-testing.md) - Unit/UI testing
```

**Why relative paths?**
- Agents live in `/Users/coreyyoung/Claude/agents/`
- Skills are in `/Users/coreyyoung/Claude/skills/`
- Go up two levels (`../../`) to reach the root, then navigate to target

### 7. Write System Prompt

Structure your prompt:
1. **Role definition** - Who is this agent?
2. **Skills & Knowledge** - Links to relevant resources
3. **Core Responsibilities** - What it does
4. **Development Principles** - How it works
5. **Best Practices** - Standards to follow
6. **Output Expectations** - What to produce

---

## Agent Template

A complete agent template is available with all required sections and guidance:

**📁 Template Files:**
- **Agent Template:** [template/agent-template.md](template/agent-template.md)
- **Usage Guide:** [template/README.md](template/README.md)

**Quick Start:**
```bash
# Copy template to create new agent
cp ~/Claude/skills/meta-skills/agent-creator/template/agent-template.md ~/Claude/agents/your-agent-name.md
```

**What's Included:**
- Complete YAML frontmatter with example syntax
- All recommended sections (Skills, Responsibilities, Principles, etc.)
- Placeholder text in `[brackets]` for easy replacement
- Relative path examples for skills/knowledge references
- PAI context loading instructions
- Voice system integration (if applicable)

**See Also:**
- Example agents in `/Users/coreyyoung/Claude/agents/`
- Full template documentation in [template/README.md](template/README.md)

---

## Agent Lifecycle Management

### Creating

```bash
# Option 1: Use this meta-skill
# Just describe the agent you want and invoke this skill

# Option 2: Copy from template
cp ~/Claude/skills/meta-skills/agent-creator/template/agent-template.md ~/Claude/agents/your-agent-name.md
# Edit and replace all [placeholder] values

# Option 3: Manual creation from scratch
cd /Users/coreyyoung/Claude/agents
touch agent-name.md
# Edit with your favorite editor
```

**See:** [template/README.md](template/README.md) for detailed template usage guide

### Testing

After creating an agent:
1. Ask Claude Code: "List available agents"
2. Test invocation: "Use the [agent-name] agent to [task]"
3. Verify it loads proper skills/knowledge
4. Check output quality

### Maintenance

- **Version Control**: Agents in `~/Claude/agents/` are git-tracked
- **Iteration**: Update based on performance and feedback
- **Skill Updates**: When skills change, agents auto-inherit updates via references

---

## Best Practices

### Agent Design

✅ **DO:**
- Create focused agents with single, clear purposes
- Write detailed descriptions with multiple examples
- Reference relevant skills and knowledge explicitly
- Use the minimum necessary tools for security
- Include code quality standards and output expectations

❌ **DON'T:**
- Create overly broad agents (defeats specialization)
- Skip examples in description (main AI won't know when to invoke)
- Hard-code knowledge in prompt (reference skills/knowledge instead)
- Grant all tools unnecessarily (security risk)
- Forget to specify expected output format

### Skill/Knowledge References

✅ **DO:**
- Use relative paths (`../../skills/`, `../../context/knowledge/`)
- Link to specific SKILL.md files for capabilities
- Link to knowledge docs for reference materials
- Organize skills by category (technical, business, domain, meta)

❌ **DON'T:**
- Use absolute paths (breaks portability)
- Duplicate skill content in agent prompt (use references)
- Create circular references (agent → skill → agent)
- Forget to create referenced skills/knowledge if they don't exist

### Model Selection

- **Opus**: Strategic decisions, complex architecture, CTO-level thinking
- **Sonnet**: Most use cases, balanced cost/performance
- **Haiku**: Simple, focused tasks like formatting or simple analysis
- **Inherit**: When you want consistency with parent conversation model

---

## Troubleshooting

### "Agent not found"
- Check file exists in `/Users/coreyyoung/Claude/agents/`
- Verify symlink: `ls -la ~/.claude/ | grep agents`
- Ensure `.md` extension

### "Skill reference broken"
- Verify relative path from agents dir
- Check skill file exists: `ls /Users/coreyyoung/Claude/skills/category/skill-name/SKILL.md`
- Create missing skill if needed

### "Agent doesn't invoke"
- Review `description` field - add clearer trigger conditions
- Add more `<example>` blocks showing when to use
- Make examples diverse to cover use cases

### "Agent lacks context"
- Add more skill/knowledge references
- Ensure referenced skills have detailed content
- Consider creating new knowledge docs for domain-specific info

---

## Quick Checklist

When creating a new agent, ensure:

- [ ] File created in `/Users/coreyyoung/Claude/agents/[name].md`
- [ ] YAML frontmatter with `name` and detailed `description`
- [ ] Examples in description showing when to invoke
- [ ] Model selected (or inherit default)
- [ ] Tools specified or omitted for all tools
- [ ] Skills referenced using `../../skills/category/name/SKILL.md`
- [ ] Knowledge referenced using `../../context/knowledge/topic.md`
- [ ] System prompt includes role, responsibilities, principles
- [ ] Output expectations clearly defined
- [ ] Tested invocation from main conversation

---

## Resources

- **Claude Code Sub-agents Docs:** https://code.claude.com/docs/en/sub-agents
- **PAI Architecture:** `/Users/coreyyoung/Claude/context/CLAUDE.md`
- **Existing Agents:** `/Users/coreyyoung/Claude/agents/`
- **Available Skills:** `/Users/coreyyoung/Claude/skills/`
- **Knowledge Base:** `/Users/coreyyoung/Claude/context/knowledge/`

---

## Template

A complete, production-ready agent template is available:

**📁 Template Location:**
`/Users/coreyyoung/Claude/skills/meta-skills/agent-creator/template/agent-template.md`

**Quick Copy:**
```bash
cp ~/Claude/skills/meta-skills/agent-creator/template/agent-template.md ~/Claude/agents/your-agent-name.md
```

**Template Features:**
- Complete YAML frontmatter with multiple example blocks
- All recommended sections pre-formatted
- Placeholder text in `[brackets]` for easy replacement
- PAI context loading instructions
- Voice system integration
- Relative path examples for skills and knowledge references

**Full Documentation:**
See [template/README.md](template/README.md) for:
- Step-by-step usage guide
- Section explanations
- Tips and best practices
- Example workflows

---

**Usage:** Invoke this skill when creating new Claude Code sub-agents, or ask for guidance on agent design within your PAI architecture.
