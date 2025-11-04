# PAI Best Practices

Detailed best practices for maintaining and growing your Personal AI Infrastructure.

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [structure.md](structure.md) - PAI organization
- [token-efficiency.md](token-efficiency.md) - Token optimization
- [skill-template.md](skill-template.md) - Skill template
- [context-template.md](context-template.md) - Context template

---

## Table of Contents

- [Organizational Best Practices](#organizational-best-practices)
- [Writing Best Practices](#writing-best-practices)
- [Cross-Referencing Best Practices](#cross-referencing-best-practices)
- [Maintenance Best Practices](#maintenance-best-practices)
- [Testing Best Practices](#testing-best-practices)

---

## Organizational Best Practices

### Keep Files Focused

✅ **DO:**
- One topic per file
- Clear, descriptive file names
- Logical categorization

❌ **DON'T:**
- Combine unrelated topics
- Create monolithic "everything" files
- Use generic file names

**Example:**

Good structure:
```
frameworks/fastify/
├── routes-api.md      # Just routes
├── schemas.md         # Just schemas
└── hooks.md           # Just hooks
```

Bad structure:
```
frameworks/fastify/
└── everything.md      # All Fastify knowledge (hard to navigate)
```

### Use Consistent Naming

✅ **DO:**
- Use kebab-case for all files: `api-development.md`
- Use descriptive names: `fastify-plugin-architecture.md`
- Match content to filename

❌ **DON'T:**
- Mix naming conventions: `API_Development.md`, `api-development.md`
- Use abbreviations: `fp-arch.md`
- Use generic names: `stuff.md`, `notes.md`

### Choose the Right Category

**Skills:**
- `core/` - Universal, applies everywhere (problem-solving, communication)
- `technical/` - Programming/engineering (architecture, APIs, testing)
- `business/` - Business capabilities (analysis, strategy, communication)
- `domain/` - Industry-specific (payments, healthcare, your domain)
- `personal/` - Personal productivity (tasks, learning, health)

**Context:**
- `languages/` - Programming language specifics
- `frameworks/` - Framework documentation
- `domains/` - Domain knowledge
- `patterns/` - Reusable patterns
- `apis/` - Third-party API docs
- `pai/` - PAI meta-knowledge

**When in doubt:** Start with your best guess, refactor later if needed.

### Avoid Deep Nesting

✅ **DO:**
- Keep hierarchy 2-3 levels deep max
- `knowledge/frameworks/fastify/routes-api.md`

❌ **DON'T:**
- Create deep hierarchies
- `knowledge/backend/nodejs/frameworks/fastify/api/routes/registration.md`

**Why:** Deep nesting makes files hard to find and reference.

---

## Writing Best Practices

### Write for Progressive Disclosure

✅ **DO:**
- Front-load important information
- Use clear headings
- Add table of contents for long files (>100 lines)
- Keep main skill files brief (50-150 lines)

❌ **DON'T:**
- Bury important info deep in files
- Create wall-of-text files
- Skip structural elements

**Why:** Claude often previews files with `head` to decide what to load. Important info should be visible early.

### Use Clear, Descriptive Headers

✅ **DO:**
- Descriptive: "When to Use ViewModels"
- Action-oriented: "Creating Your First Plugin"
- Specific: "JWT Authentication Setup"

❌ **DON'T:**
- Generic: "Overview"
- Vague: "Stuff"
- Redundant: "This Section Explains..."

### Provide Complete Examples

✅ **DO:**
- Include complete, runnable code
- Comment non-obvious parts
- Show real-world usage
- Include both good and bad examples

❌ **DON'T:**
- Use pseudocode for language-specific content
- Omit critical imports
- Show only toy examples
- Leave edge cases unexplained

**Good example:**
```typescript
import Fastify from 'fastify';

const fastify = Fastify({ logger: true });

// Define route with schema validation
fastify.get('/users/:id', {
  schema: {
    params: {
      type: 'object',
      properties: {
        id: { type: 'string' }
      },
      required: ['id']
    }
  }
}, async (request, reply) => {
  const { id } = request.params;
  const user = await getUserById(id);
  return user;
});
```

**Bad example:**
```typescript
// Get user endpoint
fastify.get('/users/:id', handler);
```

### Be Specific About When to Use Things

✅ **DO:**
- "Use ViewModel when you need API calls or validation"
- "Extract to Service when logic is shared across 2+ features"
- "Use this pattern for paginated data with infinite scroll"

❌ **DON'T:**
- "Use ViewModel for complex things"
- "Extract to Service when appropriate"
- "Use this pattern sometimes"

### Document Trade-offs

✅ **DO:**
- Explain pros and cons
- Mention when NOT to use something
- Show alternatives

❌ **DON'T:**
- Present only benefits
- Ignore edge cases
- Skip context about alternatives

**Example:**

```markdown
## Approach 1: Client-side Validation

**Pros:**
- Immediate feedback
- Reduces server load
- Better UX

**Cons:**
- Can be bypassed
- Duplicates logic (also need server-side)
- More complex client code

**When to use:** Always implement for UX, but NEVER as the only validation.
```

---

## Cross-Referencing Best Practices

### Reference Appropriately

✅ **DO:**
- Link to related skills and context
- Explain WHY references are relevant
- Use descriptive link text
- Link to specific sections when possible

❌ **DON'T:**
- Create circular references
- Link without context
- Use generic link text
- Over-link (link to everything remotely related)

**Good:**
```markdown
See [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md#dependency-inversion-principle) 
for details on dependency injection patterns.
```

**Bad:**
```markdown
See [here](SOLID_PRINCIPLES.md) for more info.
```

### Maintain Bidirectional Links

✅ **DO:**
- Main file links to details
- Detail files link back to main
- Cross-link between related files

❌ **DON'T:**
- Create one-way references
- Forget to update references when renaming

**Structure:**
```
SKILL.md
  ↓ references
DETAIL_FILE.md
  ↑ "Referenced from"
```

### Use Relative Links

✅ **DO:**
- `[file.md](file.md)` (same directory)
- `[file.md](../other/file.md)` (different directory)
- `[file.md](../../skills/core/file.md)` (from context to skills)

❌ **DON'T:**
- Use absolute paths: `/Users/coreyyoung/Claude/skills/core/file.md`
- Use URLs to local files

**Why:** Relative links work regardless of PAI location.

### Keep References One Level Deep

✅ **DO:**
- `SKILL.md` → `DETAIL_FILE.md`
- `DETAIL_FILE.md` ↔ other detail files

❌ **DON'T:**
- `SKILL.md` → `DETAIL.md` → `MORE_DETAIL.md`

**Why:** Claude may partially load nested references, missing content.

---

## Maintenance Best Practices

### Update Regularly

**After each project:**
- Capture new patterns discovered
- Add context for new frameworks/APIs used
- Update skills with refined approaches

**Weekly:**
- Review recent work for patterns
- Add any new knowledge to appropriate files
- Update project-specific CLAUDE.md files

**Monthly:**
- Review and update identity files (profile, preferences)
- Clean up outdated context
- Refactor skills that have grown too large
- Archive completed projects

**Quarterly:**
- Review values.md
- Major cleanup of outdated knowledge
- Reorganize if categories no longer make sense
- Consolidate duplicate information

### Version-Specific Content

✅ **DO:**
- Note version numbers
- Mark deprecated features
- Use collapsible sections for old patterns

❌ **DON'T:**
- Mix old and new without noting
- Keep outdated info without marking
- Delete historical context entirely

**Example:**

```markdown
## Authentication (v2.0+)

Use the new JWT middleware:
```typescript
await fastify.register(require('@fastify/jwt'), { secret: 'key' });
```

<details>
<summary>Legacy v1.x authentication (deprecated)</summary>

The old pattern used custom decorators:
```typescript
// This approach is no longer recommended
```
</details>
```

### Remove, Don't Accumulate

✅ **DO:**
- Delete truly outdated information
- Archive old project learnings
- Consolidate duplicate knowledge
- Refactor when files get messy

❌ **DON'T:**
- Keep everything forever "just in case"
- Let files grow indefinitely
- Duplicate information across files
- Ignore organizational debt

### Refactor Proactively

**When to refactor:**
- File exceeds 500 lines → Split into bundled pattern
- Multiple files cover same topic → Consolidate
- Category no longer makes sense → Reorganize
- Cross-references are confusing → Simplify structure

**How to refactor:**
1. Plan new structure
2. Create new files
3. Update references
4. Test with Claude
5. Delete old files

---

## Testing Best Practices

### Test Trigger Conditions

✅ **DO:**
- Ask questions that should trigger the skill
- Verify correct skill loads
- Test with different phrasings
- Check that skills don't over-trigger

❌ **DON'T:**
- Assume triggers work without testing
- Test only with exact trigger phrases
- Forget to test that wrong skills don't load

**Test examples:**

```
Test 1: "How should I structure my Swift app?"
Expected: Loads swift-architecture.md
Check: Only swift-architecture loads, not fastify or other skills

Test 2: "Where should I put my Fastify validation logic?"
Expected: Loads fastify-api-development.md
Check: Correct file loads, gets appropriate answer

Test 3: "Help me understand SOLID principles"
Expected: Loads SOLID_PRINCIPLES.md (or swift-architecture → SOLID)
Check: Principles are explained correctly
```

### Test Progressive Loading

✅ **DO:**
- Verify only needed files load
- Check token counts
- Test that detail files load when referenced
- Ensure main file is sufficient for basic questions

❌ **DON'T:**
- Assume progressive disclosure works
- Skip token count verification
- Forget to test basic vs deep questions

**Test examples:**

```
Basic question: "What's MVVM?"
Expected: Loads just SKILL.md (~1,500 tokens)

Deep question: "Show me SOLID principles in ViewModels"
Expected: Loads SKILL.md + SOLID_PRINCIPLES.md (~6,000 tokens)

Specific question: "How do I validate in Fastify?"
Expected: Loads skill + maybe schemas.md context (~5,000 tokens)
```

### Test Cross-References

✅ **DO:**
- Click all links to verify they work
- Test navigation between files
- Verify "Referenced from" links
- Check that anchor links work

❌ **DON'T:**
- Assume links work after renaming files
- Skip manual verification
- Forget to test bidirectional links

### Test Content Accuracy

✅ **DO:**
- Verify code examples run
- Check that advice is current
- Test that Claude's answers are correct
- Validate against official docs

❌ **DON'T:**
- Trust that old content is still correct
- Skip verification of code examples
- Assume Claude interprets correctly without testing

---

## Common Pitfalls

### Pitfall 1: Over-Engineering Too Early

**Problem:** Creating complex bundled structures for simple skills

**Solution:** Start simple (single file). Refactor to bundled pattern only when >500 lines.

### Pitfall 2: Under-Specifying Triggers

**Problem:** Generic triggers like "programming questions"

**Solution:** Be specific: "Swift architecture decisions", "Fastify route organization"

### Pitfall 3: Duplicating Knowledge

**Problem:** Same information in multiple places

**Solution:** One source of truth. Reference, don't repeat.

### Pitfall 4: Ignoring Token Efficiency

**Problem:** Loading entire skill suite for simple questions

**Solution:** Keep SKILL.md brief. Extract details. Test token usage.

### Pitfall 5: Breaking Links When Refactoring

**Problem:** Renaming files without updating references

**Solution:** Search for old filename before deleting. Update all references.

### Pitfall 6: Missing Cross-References

**Problem:** Related files don't link to each other

**Solution:** Add "Related" sections. Explain why related.

### Pitfall 7: Unclear File Organization

**Problem:** Can't find files or can't decide where new files go

**Solution:** Follow structure.md categories. Use descriptive names.

---

## Quality Checklist

Before considering a skill/context "done":

**Structure:**
- [ ] Correct category (skills/ or context/)
- [ ] Follows naming convention (kebab-case)
- [ ] Uses appropriate template
- [ ] Has all required sections
- [ ] Under token limits (1,500 for skill main, 5,000 for details)

**Content:**
- [ ] Clear, specific triggers (skills only)
- [ ] Concrete examples, not just theory
- [ ] Complete code examples that run
- [ ] Trade-offs explained
- [ ] When to use / when NOT to use

**Cross-References:**
- [ ] "Referenced from" at top of detail files
- [ ] "Related" section with explanations
- [ ] Links are relative, not absolute
- [ ] Bidirectional links work
- [ ] All links tested and working

**Testing:**
- [ ] Triggers work as expected
- [ ] Progressive loading verified
- [ ] Token counts checked
- [ ] Claude provides correct answers
- [ ] Code examples verified

**Maintenance:**
- [ ] Version noted if applicable
- [ ] Deprecations marked
- [ ] Date of last update (optional but helpful)
- [ ] Known issues documented

---

## Related Resources

**Templates:**
- [skill-template.md](skill-template.md) - Skill template
- [context-template.md](context-template.md) - Context template

**Organization:**
- [structure.md](structure.md) - Complete PAI structure
- [token-efficiency.md](token-efficiency.md) - Token optimization

**Examples:**
- [examples/](examples/) - Complete examples
- `/Users/coreyyoung/Claude/skills/technical/swift-architecture/` - Gold standard skill
