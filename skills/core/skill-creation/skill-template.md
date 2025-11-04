# Skill Template

Copy-paste template for creating new PAI-compliant skills.

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [context-template.md](context-template.md) - Context file template
- [structure.md](structure.md) - PAI structure reference
- [best-practices.md](best-practices.md) - Best practices

---

## When to Use This Template

Use this template when:
- Creating a new skill file
- Refactoring existing documentation into PAI format
- Ensuring PAI compliance
- Setting up bundled skill structure

---

## Simple Skill Template

For skills that fit in a single file (<500 lines):

```markdown
---
name: skill-name
description: One-sentence description including when to use it. Should mention key triggers and use cases.
---

# Skill Name

**Category:** [core/technical/business/domain/personal]

**Brief Description:** [1-2 sentence overview - this is metadata always loaded]

---

## When to Use This Skill

Trigger this skill when:
- [Specific condition 1 - be concrete]
- [Specific condition 2 - be concrete]
- [Specific condition 3 - be concrete]
- User mentions [specific keywords or phrases]
- [Context-specific trigger - when does this apply?]
- [Action-based trigger - what user wants to do]

---

## Core Principle

[1-3 paragraphs explaining the fundamental philosophy or approach]

**Key insight:** [The central idea in one sentence]

---

## How It Works

[Brief overview - keep under 50 lines]

### Approach 1: [Name]

[Brief description of this approach]
[When to use it]

### Approach 2: [Name]

[Brief description of this approach]
[When to use it]

### Decision Framework

[How to choose between approaches]

```
[Decision tree or flowchart if helpful]
```

---

## Common Patterns

### Pattern 1: [Name]

**When to use:** [Specific scenario]

**Example:**
```[language]
[Code example if applicable]
```

### Pattern 2: [Name]

**When to use:** [Specific scenario]

**Example:**
```[language]
[Code example if applicable]
```

---

## Dependencies

**Related skills:**
- `category/related-skill.md` - [Why it's related / what it provides]

**Recommended context files:**
- `/Users/coreyyoung/Claude/context/knowledge/category/file.md` - [What information it contains]

**Future skill connections:**
- `potential-skill.md` - [What it would cover]

---

## Quick Reference

[Optional: Quick decision tree, lookup table, or cheat sheet]

| Scenario | Use | Example |
|----------|-----|---------|
| [Scenario 1] | [Approach] | [Brief example] |
| [Scenario 2] | [Approach] | [Brief example] |

---

## Notes

[Any additional context, philosophy, or learning notes]

**Philosophy:** [Why this approach matters]

**Evolution:** [How this skill might evolve]

**Reference Example:** [Point to exemplar if exists]
```

---

## Bundled Skill Template

For complex skills that need multiple files (>500 lines total):

### Main SKILL.md

```markdown
---
name: skill-name
description: One-sentence description including when to use it. Mention key triggers.
---

# Skill Name

**Category:** [core/technical/business/domain/personal]

**Brief Description:** [1-2 sentence overview - this is metadata always loaded]

---

## When to Use This Skill

Trigger this skill when:
- [Specific trigger 1]
- [Specific trigger 2]
- [Specific trigger 3]

---

## Core Principle

[Brief statement of fundamental approach]

---

## Overview

[Brief 20-30 line overview of the skill]

### Key Concept 1

[One paragraph]

### Key Concept 2

[One paragraph]

### Key Concept 3

[One paragraph]

---

## Detailed Documentation

**For complete details see:**
- **[TOPIC_1.md](TOPIC_1.md)** - [What this covers]
  - [Subtopic A]
  - [Subtopic B]

- **[TOPIC_2.md](TOPIC_2.md)** - [What this covers]
  - [Subtopic C]
  - [Subtopic D]

- **[EXAMPLES.md](EXAMPLES.md)** - Real-world examples
  - [Example type 1]
  - [Example type 2]

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup
  - [Quick ref type 1]
  - [Quick ref type 2]

---

## Dependencies

**Related skills:**
- `category/skill.md` - [Relationship]

**Recommended context files:**
- `/Users/coreyyoung/Claude/context/knowledge/category/file.md` - [What it provides]

---

## Quick Reference

[Minimal quick reference - full version in QUICK_REFERENCE.md]

---

## Common Usage Patterns

### Pattern 1: [Name]

[Brief description]

See [TOPIC_1.md](TOPIC_1.md#pattern-1) for details.

### Pattern 2: [Name]

[Brief description]

See [TOPIC_2.md](TOPIC_2.md#pattern-2) for details.

---

## Notes

**Philosophy:** [Core philosophy]

**Structure:** This skill uses progressive disclosure - start here, drill down as needed.
```

### Detail File Template (TOPIC_1.md, etc.)

```markdown
# [Topic Name] - Detailed Guide

[Description of what this file covers]

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [TOPIC_2.md](TOPIC_2.md) - [How related]
- [EXAMPLES.md](EXAMPLES.md) - [Relevant examples]

---

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
- [Section 3](#section-3)

---

## Section 1

[Detailed content]

### Subsection 1.1

[Content]

### Subsection 1.2

[Content]

**Related**: See [SKILL.md](SKILL.md#overview) for context.

---

## Section 2

[Detailed content]

---

[Continue with detailed content...]

---

## Summary

[Brief summary of key points]

**Related Resources**:
- [SKILL.md](SKILL.md) - Main overview
- [TOPIC_2.md](TOPIC_2.md) - [Related topic]
- [EXAMPLES.md](EXAMPLES.md) - [Practical examples]
```

---

## Customization Guide

### Choosing Sections

**Required sections:**
- YAML frontmatter
- Title and metadata
- When to Use This Skill
- Core Principle
- How It Works
- Dependencies

**Optional sections (use as needed):**
- Common Patterns
- Quick Reference
- Examples
- Decision Framework
- Testing Strategy
- Anti-Patterns
- Notes

### Adapting for Different Skill Types

#### For Architecture/Pattern Skills
Include:
- Progressive complexity levels
- Decision tree
- File organization
- Examples of each level
- When to refactor between levels

**Example:** `swift-architecture.md`

#### For Methodology Skills
Include:
- Step-by-step process
- When to use each step
- Common pitfalls
- Success criteria

**Example:** `problem-solving.md`

#### For Technology Selection Skills
Include:
- Decision criteria
- Comparison of options
- When to choose each
- Trade-off analysis

**Example:** `api-authentication.md`

---

## Validation Checklist

Before finalizing a skill, verify:

- [ ] YAML frontmatter is complete
- [ ] Category is correct (core/technical/business/domain/personal)
- [ ] Brief description is 1-2 sentences
- [ ] "When to Use" section has 5+ concrete triggers
- [ ] Core principle is clearly stated
- [ ] Overview is brief (under 50 lines for simple, under 150 for bundled)
- [ ] Dependencies section lists related skills and context
- [ ] Cross-references are working
- [ ] File follows naming convention (kebab-case.md)
- [ ] Token count is reasonable (~1,500 for main file)
- [ ] Triggers are tested with Claude

---

## Examples

See complete real-world examples:
- [examples/skill-example.md](examples/skill-example.md) - Simple skill
- `/Users/coreyyoung/Claude/skills/technical/swift-architecture/` - Bundled skill (gold standard)

---

## Tips

**Writing triggers:**
- Be specific, not generic
- Include keywords users might say
- Cover different ways to ask the same thing
- Include context-based triggers

**Good triggers:**
- "Building REST APIs with Fastify"
- "Questions about route organization"
- "User mentions 'where should this logic live'"

**Bad triggers:**
- "Programming questions" (too vague)
- "Web development" (too broad)
- "When user needs help" (not specific)

**Writing core principle:**
- One clear philosophical statement
- Explains the "why" not just the "how"
- Should be memorable
- Should guide all patterns in the skill

**Progressive disclosure:**
- Keep SKILL.md brief - resist the urge to include everything
- One level of references (SKILL → detail, not SKILL → detail → more detail)
- Use clear navigation between files
- Table of contents in longer files

---

## Related Resources

**Other templates:**
- [context-template.md](context-template.md) - For reference files

**Guidelines:**
- [best-practices.md](best-practices.md) - Detailed best practices
- [structure.md](structure.md) - PAI organization
- [token-efficiency.md](token-efficiency.md) - Token optimization

**Examples:**
- [examples/](examples/) - Complete examples
