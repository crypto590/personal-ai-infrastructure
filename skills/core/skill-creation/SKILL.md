---
name: skill-creation
description: Methodology for creating PAI skills and context files. Covers decision framework for skill vs context, PAI structure compliance, progressive disclosure, and cross-referencing. Use when creating new skills, organizing knowledge, or structuring PAI content.
---

# Skill Creation

**Category:** core

**Brief Description:** Complete methodology for creating PAI-compliant skills and context files. Includes decision framework for skill vs context, progressive disclosure patterns, cross-referencing strategy, and testing approach. Based on proven PAI patterns.

---

## When to Use This Skill

Trigger this skill when:
- Creating new PAI skills or context files
- Deciding whether something should be a skill or context
- Organizing new knowledge into PAI structure
- Structuring skill files for progressive disclosure
- Adding cross-references between files
- Testing new skills for PAI compliance
- User says "create a skill for..." or "document this in PAI"
- Refactoring existing documentation into PAI format
- Questions about PAI structure or organization
- Setting up new categories or knowledge areas

---

## Core Philosophy

**Build once, use everywhere.** Every piece of knowledge should live in exactly one place in your PAI and be available to Claude across all environments (Desktop, Code CLI, API, Projects).

**Progressive disclosure.** Load the minimum needed to answer questions. Start with brief metadata, drill down to detailed content only when required.

**Skills vs Context:**
- **Skills** = "How to do things" (methodology, patterns, when/why)
- **Context** = "What things are" (reference, API docs, syntax)

---

## Decision Framework

### Is it a Skill or Context?

Use this decision tree:

```
Does it describe a methodology, approach, or pattern?
├─ YES → Is it reusable across multiple projects?
│   ├─ YES → Create a SKILL
│   └─ NO → Add to project-specific CLAUDE.md
│
└─ NO → Is it reference material or documentation?
    ├─ YES → Create CONTEXT
    └─ NO → Might be project-specific
```

### Create a SKILL when it:

✅ **Describes methodology or approach**
- How to architect applications
- When to use certain patterns
- Testing strategies
- Problem-solving frameworks
- Decision-making processes

✅ **Answers "how", "when", or "why"**
- How to structure APIs
- When to extract to services
- Why certain patterns work

✅ **Is reusable across projects**
- Applies to multiple codebases
- Generic enough to transfer
- Not project-specific

✅ **Contains decision frameworks**
- Progressive complexity approaches
- Pattern selection criteria
- Trade-off analysis

**Examples of SKILLS:**
- `swift-architecture.md` - How to structure Swift apps
- `fastify-api-development.md` - Patterns for building APIs
- `api-authentication.md` - Auth strategies and patterns
- `problem-solving.md` - General problem-solving framework

### Create CONTEXT when it:

✅ **Is reference material**
- API documentation
- Syntax reference
- Configuration options
- Command-line flags

✅ **Answers "what"**
- What methods are available
- What configuration options exist
- What the syntax is

✅ **Is framework/tool-specific**
- Library API reference
- Framework features
- Tool commands
- Language syntax

✅ **Rarely changes**
- Stable documentation
- Official specs
- Standard references

**Examples of CONTEXT:**
- `fastify/routes-api.md` - Route registration API reference
- `swift/concurrency.md` - Swift concurrency syntax
- `typescript/utility-types.md` - TypeScript utility types
- `git/commands.md` - Git command reference

---

## Skill File Structure

### Required Sections

Every skill MUST have these sections:

#### 1. YAML Frontmatter
```yaml
---
name: skill-name
description: One-sentence description including when to use. Mention key triggers.
---
```

#### 2. Title and Metadata
```markdown
# Skill Name

**Category:** [core/technical/business/domain/personal]

**Brief Description:** [1-2 sentences - metadata always loaded]
```

#### 3. When to Use This Skill
```markdown
## When to Use This Skill

Trigger this skill when:
- [Specific condition 1]
- [Specific condition 2]
- User mentions [keywords]
- [Context-specific trigger]
```

#### 4. Core Principle/Philosophy
```markdown
## Core Principle

[Brief statement of the fundamental approach or philosophy]
```

#### 5. How It Works (Brief Overview)
```markdown
## How It Works

[20-50 lines of overview - keep brief]
```

#### 6. Dependencies
```markdown
## Dependencies

**Related skills:**
- `category/skill-name.md` - Why related

**Recommended context files:**
- `/Users/coreyyoung/Claude/context/knowledge/category/file.md` - What it provides
```

### Optional Sections (As Needed)

- Quick Reference table
- Common Usage Patterns
- Examples
- Notes

---

## Progressive Disclosure Pattern

**Goal:** Keep SKILL.md brief (50-150 lines), extract details to separate files.

### When to Use Bundled Pattern

Use bundled pattern (main SKILL.md + detail files) when:
- Total content exceeds ~500 lines
- Multiple distinct sub-topics
- Some content is rarely needed
- Want to minimize token usage

**Example structure:**
```
skill-name/
├── SKILL.md              # Main file: overview + references
├── DETAILED_TOPIC_1.md   # Deep dive on topic 1
├── DETAILED_TOPIC_2.md   # Deep dive on topic 2
└── EXAMPLES.md           # Real-world examples
```

### Bundled Pattern Best Practices

1. **Keep SKILL.md under 150 lines**
   - Brief overview only
   - Clear references to detail files
   - Enough to answer basic questions

2. **One level deep for references**
   - SKILL.md → detail files (good)
   - SKILL.md → detail → more detail (bad - Claude may partially load)

3. **Use table of contents in detail files**
   - Helps when Claude previews with `head`
   - Shows full scope even in partial reads

4. **Clear navigation**
   - Link from SKILL.md to details
   - Link back from details to SKILL.md
   - Cross-link between detail files

---

## Cross-Referencing Strategy

### Reference Types

**1. Referenced from** (at top of detail files):
```markdown
**Referenced from**: [SKILL.md](SKILL.md), [OTHER_FILE.md](OTHER_FILE.md)
```

**2. Related** (shows connections):
```markdown
**Related**:
- [OTHER_SKILL.md](OTHER_SKILL.md) - Why related
- [CONTEXT_FILE.md](../../context/knowledge/category/file.md) - What it provides
```

**3. See also** (within content):
```markdown
See [EXAMPLES.md](EXAMPLES.md#specific-example) for implementation details.
```

### Cross-Reference Best Practices

✅ **DO:**
- Link to specific sections with anchors (`#section-name`)
- Explain WHY files are related
- Keep links relative
- Use descriptive link text

❌ **DON'T:**
- Create circular references
- Link to same file multiple times
- Use generic link text ("click here")
- Break links when renaming files

---

## Context File Structure

### Basic Context File

```markdown
# Topic Name

[Brief description of what this context covers]

**Referenced from**: [skill-name.md](../../skills/category/skill-name.md)

**Related**:
- [related-context.md](related-context.md) - What it covers

---

## [Main Section 1]

[Reference content]

## [Main Section 2]

[Reference content]
```

### Context Organization

**By category:**
```
/Users/coreyyoung/Claude/context/knowledge/
├── languages/
│   ├── swift/
│   │   ├── overview.md
│   │   ├── concurrency.md
│   │   └── memory-management.md
│   └── typescript/
│       ├── overview.md
│       └── utility-types.md
├── frameworks/
│   ├── fastify/
│   │   ├── overview.md
│   │   ├── routes-api.md
│   │   └── schemas.md
│   └── swiftui/
│       ├── overview.md
│       └── state-management.md
└── domains/
    └── payment-processing/
        ├── overview.md
        └── compliance.md
```

---

## Skill Categories

### Core (`skills/core/`)
Universal skills that apply everywhere:
- Problem-solving frameworks
- Communication patterns
- Research methodologies
- Learning approaches

### Technical (`skills/technical/`)
Programming and engineering skills:
- Architecture patterns
- API development
- Testing strategies
- Code organization

### Business (`skills/business/`)
Business-focused capabilities:
- Analysis frameworks
- Strategy development
- Communication patterns
- Decision-making

### Domain (`skills/domain/`)
Industry-specific expertise:
- Payment processing
- Healthcare compliance
- Financial regulations
- Your specific domain knowledge

### Personal (`skills/personal/`)
Personal productivity skills:
- Task management
- Note-taking systems
- Learning strategies
- Health tracking

---

## Testing New Skills

### Test Checklist

- [ ] **Trigger test**: Ask Claude a question that should trigger the skill
- [ ] **Loading test**: Verify only SKILL.md loads initially
- [ ] **Progressive disclosure test**: Verify detail files load only when needed
- [ ] **Cross-reference test**: Click/follow links to ensure they work
- [ ] **Token efficiency test**: Check token usage (should be ~1,500 for SKILL.md)
- [ ] **Content test**: Verify skill provides useful, actionable guidance
- [ ] **Consistency test**: Ensure follows PAI patterns from other skills

### Example Test Scenarios

**Test 1: Basic trigger**
```
You: "How should I structure my Swift app?"
Expected: Loads swift-architecture.md
Token usage: ~1,500 tokens
```

**Test 2: Deep dive**
```
You: "Show me SOLID principles in Swift"
Expected: Loads swift-architecture.md + SOLID_PRINCIPLES.md
Token usage: ~6,000 tokens
```

**Test 3: Cross-reference**
```
You: "What ViewModel patterns should I use?"
Expected: Navigates swift-architecture → VIEWMODEL_PATTERNS.md
Token usage: ~4,500 tokens
```

---

## Common Patterns

### Pattern 1: Progressive Complexity Skill

**Use for:** Skills that scale from simple to complex (like swift-architecture)

**Structure:**
```markdown
## Level 1: Simple Approach
[When to use, examples]

## Level 2: Intermediate Approach
[When to upgrade, examples]

## Level 3: Advanced Approach
[When to extract, examples]

## Decision Tree
[How to choose level]
```

**Examples:** API development, architecture, testing strategies

### Pattern 2: Decision Framework Skill

**Use for:** Skills that help choose between options

**Structure:**
```markdown
## Decision Criteria
[Key factors to consider]

## Option 1: Approach A
[When to use, pros/cons]

## Option 2: Approach B
[When to use, pros/cons]

## Decision Tree
[How to choose]
```

**Examples:** Technology selection, pattern choice, architecture decisions

### Pattern 3: Methodology Skill

**Use for:** Step-by-step processes

**Structure:**
```markdown
## Overview
[What this methodology achieves]

## Step 1: [Action]
[How to do it, why it matters]

## Step 2: [Action]
[How to do it, why it matters]

## Common Pitfalls
[What to avoid]
```

**Examples:** Problem-solving, research process, testing approach

---

## Token Efficiency Guidelines

### Target Token Counts

**Skills:**
- SKILL.md (main file): 50-150 lines = ~1,000-1,500 tokens
- Detail files: 200-500 lines = ~3,000-5,000 tokens each
- Total skill (if all loaded): ~10,000-15,000 tokens max

**Context files:**
- Single topic: 100-300 lines = ~1,500-3,000 tokens
- Reference docs: 200-500 lines = ~3,000-5,000 tokens

### Optimization Strategies

1. **Front-load important content**
   - Key information in first 100 lines
   - Claude can preview with `head`

2. **Use table of contents**
   - Shows structure even in partial reads
   - Helps Claude find specific sections

3. **Extract rarely-needed content**
   - Move edge cases to separate files
   - Link from main file

4. **Avoid duplication**
   - Reference, don't repeat
   - Link to detailed coverage

---

## Detailed Documentation

**For complete details see:**
- [structure.md](structure.md) - Complete PAI directory structure
- [skill-template.md](skill-template.md) - Copy-paste skill template
- [context-template.md](context-template.md) - Copy-paste context template
- [best-practices.md](best-practices.md) - Detailed best practices
- [token-efficiency.md](token-efficiency.md) - Token optimization guide
- [examples/](examples/) - Complete real-world examples

---

## Dependencies

**Related skills:**
- None yet (this is the meta-skill that enables all others)

**Required context files:**
- `/Users/coreyyoung/Claude/skills/core/skill-creation/structure.md` - PAI directory structure
- `/Users/coreyyoung/Claude/skills/core/skill-creation/skill-template.md` - Skill template
- `/Users/coreyyoung/Claude/skills/core/skill-creation/best-practices.md` - Best practices

**Recommended context files:**
- `/Users/coreyyoung/Claude/skills/core/skill-creation/examples/` - Real examples
- `/Users/coreyyoung/Claude/skills/core/skill-creation/token-efficiency.md` - Optimization guide

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Methodology or reference? | Methodology → Skill, Reference → Context |
| Reusable across projects? | Yes → Skill, No → Project file |
| Answers how/when/why? | Skill |
| Answers what? | Context |
| > 500 lines? | Use bundled pattern |
| Framework-specific syntax? | Context |
| Decision framework? | Skill |

---

## Notes

**Philosophy:** This skill embodies the PAI principle of "build once, use everywhere." By establishing clear patterns for skill creation, you ensure consistency across all environments and over time.

**Evolution:** As you create more skills, patterns will emerge. Update this skill to capture those patterns. The skill-creation skill itself should evolve based on your experience.

**Reference Example:** The `swift-architecture` skill is the gold standard for PAI compliance - use it as a reference when creating new skills.
