# PAI Structure Reference

Complete directory structure and organization for Personal AI Infrastructure.

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [best-practices.md](best-practices.md) - Organizational best practices
- [skill-template.md](skill-template.md) - Skill file structure
- [context-template.md](context-template.md) - Context file structure

---

## Complete PAI Directory Structure

```
/Users/coreyyoung/Claude/
├── CLAUDE.md                       # Index pointing to context/CLAUDE.md
├── QUICKSTART.md                   # Quick start guide
│
├── context/
│   ├── CLAUDE.md                   # Master PAI documentation
│   │
│   ├── identity/
│   │   ├── profile.md              # Who you are
│   │   ├── preferences.md          # How you work
│   │   └── values.md               # Your principles
│   │
│   ├── knowledge/
│   │   ├── languages/              # Programming languages
│   │   │   ├── swift/
│   │   │   │   ├── overview.md
│   │   │   │   ├── concurrency.md
│   │   │   │   └── memory-management.md
│   │   │   ├── typescript/
│   │   │   │   ├── overview.md
│   │   │   │   └── utility-types.md
│   │   │   └── python/
│   │   │       ├── overview.md
│   │   │       └── asyncio.md
│   │   │
│   │   ├── frameworks/             # Tech frameworks
│   │   │   ├── fastify/
│   │   │   │   ├── overview.md
│   │   │   │   ├── routes-api.md
│   │   │   │   ├── schemas.md
│   │   │   │   └── hooks.md
│   │   │   ├── swiftui/
│   │   │   │   ├── overview.md
│   │   │   │   └── state-management.md
│   │   │   └── nextjs/
│   │   │       ├── overview.md
│   │   │       └── server-actions.md
│   │   │
│   │   ├── domains/                # Domain expertise
│   │   │   ├── payment-processing/
│   │   │   │   ├── overview.md
│   │   │   │   └── compliance.md
│   │   │   └── healthcare/
│   │   │       ├── overview.md
│   │   │       └── hipaa.md
│   │   │
│   │   ├── patterns/               # Design patterns
│   │   │   ├── dependency-injection/
│   │   │   │   ├── overview.md
│   │   │   │   └── containers.md
│   │   │   └── api-design/
│   │   │       ├── rest-patterns.md
│   │   │       └── graphql-patterns.md
│   │   │
│   │   ├── apis/                   # API documentation
│   │   │   ├── stripe/
│   │   │   │   ├── overview.md
│   │   │   │   └── payment-intents.md
│   │   │   └── aws-s3/
│   │   │       ├── overview.md
│   │   │       └── presigned-urls.md
│   │   │
│   │   └── pai/                    # PAI meta-knowledge
│   │       ├── structure.md        # THIS FILE
│   │       ├── skill-template.md
│   │       ├── context-template.md
│   │       ├── best-practices.md
│   │       ├── token-efficiency.md
│   │       └── examples/
│   │           ├── skill-example.md
│   │           └── context-example.md
│   │
│   ├── projects/
│   │   ├── current/                # Active projects
│   │   │   ├── project-a/
│   │   │   │   └── CLAUDE.md
│   │   │   └── project-b/
│   │   │       └── CLAUDE.md
│   │   └── archive/                # Past projects
│   │       └── old-project/
│   │           └── CLAUDE.md
│   │
│   └── resources/
│       ├── tools/                  # Tool documentation
│       │   ├── git/
│       │   │   └── commands.md
│       │   └── docker/
│       │       └── compose.md
│       └── templates/              # Reusable templates
│           ├── api-endpoint.md
│           └── component.md
│
├── skills/
│   ├── core/                       # Universal capabilities
│   │   ├── problem-solving.md
│   │   ├── research.md
│   │   ├── SKILL.md                # This skill!
│   │   └── communication.md
│   │
│   ├── technical/                  # Programming & engineering
│   │   ├── swift-architecture/
│   │   │   ├── SKILL.md
│   │   │   ├── ARCHITECTURE_LEVELS.md
│   │   │   ├── VIEWMODEL_PATTERNS.md
│   │   │   ├── SERVICE_LAYER.md
│   │   │   ├── SOLID_PRINCIPLES.md
│   │   │   ├── EXAMPLES.md
│   │   │   └── QUICK_REFERENCE.md
│   │   ├── fastify-api-development.md
│   │   ├── fastify-plugin-architecture.md
│   │   ├── api-authentication.md
│   │   └── typescript-patterns.md
│   │
│   ├── business/                   # Business-focused
│   │   ├── business-analysis.md
│   │   ├── stakeholder-management.md
│   │   └── strategy-development.md
│   │
│   ├── domain/                     # Domain-specific expertise
│   │   ├── payment-processing.md
│   │   ├── compliance-review.md
│   │   └── financial-analysis.md
│   │
│   └── personal/                   # Personal productivity
│       ├── task-management.md
│       ├── note-taking.md
│       └── learning-strategies.md
│
├── commands/                       # Custom workflows (optional)
├── hooks/                          # Context loader (optional)
└── agents/                         # Agent configurations (existing)
```

---

## Naming Conventions

### Skills

**Format:** `kebab-case.md`

**Examples:**
- `api-development.md`
- `swift-architecture.md`
- `problem-solving.md`

**Location:** `/Users/coreyyoung/Claude/skills/{category}/`

**For bundled skills:**
```
skill-name/
├── SKILL.md              # Main entry point (all caps)
├── DETAIL_FILE_1.md     # Detail files (all caps)
└── DETAIL_FILE_2.md
```

### Context Files

**Format:** `kebab-case.md`

**Examples:**
- `routes-api.md`
- `overview.md`
- `state-management.md`

**Location:** `/Users/coreyyoung/Claude/context/knowledge/{category}/{subcategory}/`

### Projects

**Format:** Match project name (can use any case)

**Examples:**
- `MyApp/CLAUDE.md`
- `website-redesign/CLAUDE.md`

**Location:** `/Users/coreyyoung/Claude/context/projects/current/` or `archive/`

---

## File Size Guidelines

### Skills

**SKILL.md (main file):**
- Target: 50-150 lines
- Maximum: 200 lines
- ~1,000-1,500 tokens

**Detail files:**
- Target: 200-500 lines per file
- ~3,000-5,000 tokens per file

**Total skill (all files):**
- Maximum: ~15,000 tokens if all loaded
- Typical usage: ~4,500 tokens (main + one detail)

### Context Files

**Single topic:**
- Target: 100-300 lines
- ~1,500-3,000 tokens

**Reference documentation:**
- Target: 200-500 lines
- ~3,000-5,000 tokens
- Use table of contents if >100 lines

---

## Organization Principles

### 1. Single Source of Truth

Each piece of knowledge lives in exactly ONE place:
- ✅ Knowledge in PAI, referenced by projects
- ❌ Duplicate knowledge in multiple places

### 2. Category by Purpose

**Skills** organized by usage type:
- core = Universal (problem-solving, communication)
- technical = Programming (architecture, APIs)
- business = Business (analysis, strategy)
- domain = Industry-specific (payments, healthcare)
- personal = Productivity (tasks, learning)

**Context** organized by knowledge type:
- languages = Language-specific
- frameworks = Framework-specific
- domains = Domain knowledge
- patterns = Reusable patterns
- apis = Third-party API docs
- pai = PAI meta-knowledge

### 3. Progressive Disclosure

**Information hierarchy:**
1. Skill metadata (always loaded) - ~1,500 tokens
2. Skill overview (loaded when triggered)
3. Detail files (loaded when needed) - ~3,000-5,000 tokens each
4. Context reference (loaded when referenced)

### 4. Clear Navigation

**Every file should:**
- Link back to parent/referencing files
- Cross-reference related files
- Explain WHY references are relevant
- Use descriptive link text

---

## Migration Guidelines

### Moving Existing Documentation to PAI

1. **Identify type:**
   - Methodology/pattern? → Skill
   - Reference/docs? → Context
   - Project-specific? → Project file

2. **Choose category:**
   - Universal? → core
   - Programming? → technical
   - Business? → business
   - Industry? → domain
   - Productivity? → personal

3. **Structure appropriately:**
   - Create SKILL.md with overview
   - Extract details to separate files if >500 lines
   - Add cross-references

4. **Test:**
   - Verify triggers work
   - Check progressive loading
   - Validate cross-references

### Adding New Knowledge

**When learning something new:**

1. **Capture immediately:**
   - Don't wait for perfect organization
   - Create rough file in appropriate location

2. **Refine structure:**
   - Add proper headers
   - Include cross-references
   - Follow templates

3. **Test integration:**
   - Ask Claude to use the new knowledge
   - Verify it loads correctly
   - Check token efficiency

4. **Update related files:**
   - Add references from related skills
   - Link from relevant context
   - Update indexes if needed

---

## Related Resources

**Templates:**
- [skill-template.md](skill-template.md) - Copy-paste skill template
- [context-template.md](context-template.md) - Copy-paste context template

**Guidelines:**
- [best-practices.md](best-practices.md) - Detailed best practices
- [token-efficiency.md](token-efficiency.md) - Token optimization

**Examples:**
- [examples/skill-example.md](examples/skill-example.md) - Complete skill example
- [examples/context-example.md](examples/context-example.md) - Complete context example

---

## Quick Reference

| Item | Location | Format |
|------|----------|--------|
| Skills | `/Users/coreyyoung/Claude/skills/{category}/` | `kebab-case.md` |
| Context | `/Users/coreyyoung/Claude/context/knowledge/{category}/` | `kebab-case.md` |
| Projects | `/Users/coreyyoung/Claude/context/projects/current/` | `ProjectName/CLAUDE.md` |
| Identity | `/Users/coreyyoung/Claude/context/identity/` | Fixed names |
| PAI Meta | `/Users/coreyyoung/Claude/context/knowledge/pai/` | Various |
