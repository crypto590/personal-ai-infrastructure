# Anthropic Skills Technical Reference

Technical specifications and requirements for creating Anthropic Skills.

**For general PAI philosophy**, see: `~/Claude/context/knowledge/pai/philosophy.md`

---

## Official Documentation

- [Agent Skills Overview](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview)
- [Skills Best Practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skills API Guide](https://docs.anthropic.com/en/api/skills-guide)

---

## YAML Frontmatter Requirements

### Required Fields

**`name`:**
- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only
- No XML tags
- Cannot contain: "anthropic", "claude"

**`description`:**
- Maximum 1024 characters
- Must be non-empty
- No XML tags
- Should include both WHAT the skill does AND WHEN to use it

### Example
```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

---

## Three-Level Progressive Disclosure

### Level 1: Metadata (~100 tokens per skill)
- YAML frontmatter
- Always loaded into system prompt
- Claude knows skill exists and when to trigger

### Level 2: Instructions (~5000 tokens)
- SKILL.md body
- Loaded when skill is triggered
- Main instructions and guidance

### Level 3: Resources (effectively unlimited)
- Additional markdown files
- Scripts and code
- Reference materials
- Loaded only when specifically needed

---

## File Structure

### Basic Structure
```
skill-name/
└── SKILL.md
```

### Bundled Structure
```
skill-name/
├── SKILL.md           # Main instructions
├── TOPIC_1.md         # Detailed topic 1
├── TOPIC_2.md         # Detailed topic 2
├── EXAMPLES.md        # Comprehensive examples
└── scripts/
    └── utility.py     # Executable scripts
```

---

## Runtime Environment

### Available Across Surfaces

**Claude.ai:**
- Network access (varies by settings)
- Can install npm/PyPI packages

**Claude API:**
- No network access
- No runtime package installation
- Pre-installed packages only

**Claude Code:**
- Full network access
- Can install packages locally

### Pre-installed Packages

See: [Code Execution Tool Documentation](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool)

---

## Best Practices (from Anthropic)

### Concise is Key
- Context window is shared resource
- Only include what Claude doesn't already know
- Challenge every paragraph's token cost

### Set Appropriate Degrees of Freedom

**High freedom** (text instructions):
- Multiple approaches valid
- Decisions depend on context

**Low freedom** (specific scripts):
- Operations are fragile
- Consistency is critical

### Token Budget
- Keep SKILL.md under 500 lines
- Use additional files for more content

---

## Security Considerations

**Only use Skills from trusted sources:**
- Skills you created yourself
- Skills from Anthropic
- Thoroughly audited Skills from others

**Risks of untrusted Skills:**
- Malicious tool invocation
- Data exfiltration
- Unauthorized system access

---

## Related

**Implementation in this PAI:**
- [skill-template.md](skill-template.md) - Template following these specs
- [best-practices.md](best-practices.md) - Our best practices
- [token-efficiency.md](token-efficiency.md) - Token optimization

**General PAI concepts:**
- `~/Claude/context/knowledge/pai/philosophy.md` - Overall PAI philosophy