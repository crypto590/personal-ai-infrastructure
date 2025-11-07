# Context Directory

The "brain" of your Personal AI Infrastructure - central repository for all knowledge, identity, and reference material.

## 📂 Structure

```
context/
├── CLAUDE.md                    # Master PAI documentation (READ THIS FIRST!)
├── identity/                    # Who you are and how you work
├── knowledge/                   # Technical and domain knowledge
├── projects/                    # Project references
└── resources/                   # Tools and templates
```

---

## 🧠 What Goes Here

**Context vs. Skills:**
- **Context** = Knowledge and reference material (WHAT you know)
- **Skills** = Capabilities and approaches (HOW you do things)

This directory contains the **what you know**, while `/Users/coreyyoung/Claude/skills/` contains the **how you work**.

---

## 📁 Subdirectories

### `/identity/` - Who You Are

Your personal and professional identity:

- `profile.md` - Background, expertise, current focus
- `preferences.md` - How you like to work and communicate
- `values.md` - Principles and decision-making frameworks

**When to update:** As you gain new skills, change preferences, or refine your approach

---

### `/knowledge/` - Your Knowledge Base

Reference material and domain knowledge organized by category:

#### `/knowledge/languages/`
Programming language knowledge and patterns
- `typescript/` - TypeScript specifics
- `python/` - Python knowledge
- `swift/` - Swift/iOS knowledge

#### `/knowledge/frameworks/`
Framework-specific knowledge and documentation
- `nextjs/` - Next.js patterns and features
- `react/` - React knowledge
- `django/` - Django patterns

#### `/knowledge/domains/`
Domain and industry expertise
- `payment-processing/` - Payment systems knowledge
- `underwriting/` - Underwriting domain knowledge
- `compliance/` - Regulatory compliance knowledge

#### `/knowledge/patterns/`
Design patterns and architectural approaches
- `api-design/` - API design patterns
- `database/` - Database patterns
- `security/` - Security patterns

#### `/knowledge/apis/`
API documentation and integration guides
- `stripe/` - Stripe API knowledge
- `twilio/` - Twilio integration
- Custom APIs you work with

**When to add:** When you learn something you'll reference again

---

### `/projects/` - Project References

#### `/projects/current/`
Active projects for quick reference
- Link to repos
- Key technical decisions
- Project-specific context

#### `/projects/archive/`
Completed projects for lessons learned
- What worked well
- What didn't
- Patterns to reuse or avoid

**When to add:** At project start (current) or completion (archive)

---

### `/resources/` - Tools & Templates

#### `/resources/tools/`
Tool configurations and documentation
- Editor configs
- CLI tool setups
- Development environment docs

#### `/resources/templates/`
Reusable code templates and boilerplates
- Project starter templates
- Component templates
- Configuration templates

**When to add:** When you create something reusable

---

## 🎯 How to Use This Directory

### Adding New Knowledge

1. **Identify the category:**
   - Personal identity? → `identity/`
   - Programming language? → `knowledge/languages/`
   - Framework? → `knowledge/frameworks/`
   - Domain expertise? → `knowledge/domains/`
   - Pattern? → `knowledge/patterns/`
   - API? → `knowledge/apis/`

2. **Create focused files:**
   - One topic per file
   - Use descriptive names
   - Link to related files

3. **Keep it current:**
   - Update as you learn
   - Remove outdated information
   - Mark deprecated approaches

### Organizing Knowledge

**Good structure example:**
```
knowledge/
  frameworks/
    nextjs/
      server-actions.md
      routing.md
      data-fetching.md
      deployment.md
```

**Bad structure example:**
```
knowledge/
  frameworks/
    nextjs-everything.md  # Too broad, hard to navigate
```

---

## 🔗 Linking Context Together

Use relative links to connect related knowledge:

```markdown
## Related
- [API Design Patterns](../patterns/api-design/rest.md)
- [TypeScript Types](../languages/typescript/advanced-types.md)
```

---

## 📊 Progressive Loading

Context files are loaded **on demand** based on conversation needs:

- **Identity:** Loaded at start (~500 tokens)
- **Knowledge:** Loaded when specific topic is needed (~2000 tokens per topic)
- **Projects:** Loaded when discussing specific project
- **Resources:** Loaded when accessing specific tool/template

This keeps token usage low while maintaining full access to knowledge.

---

## 🛠️ Maintenance

### Regular Updates

**After each project:**
- Add new knowledge gained
- Update relevant knowledge files
- Archive project learnings

**Monthly:**
- Review and update identity files
- Clean up outdated knowledge
- Reorganize if structure is unclear

**Quarterly:**
- Review values.md
- Update major knowledge areas
- Consolidate duplicate information

### Quality Checks

```bash
# Find TODO markers (unfilled sections)
grep -r "TODO" /Users/coreyyoung/Claude/context/

# List all knowledge files
find /Users/coreyyoung/Claude/context/knowledge -name "*.md"

# Search for specific knowledge
grep -r "search term" /Users/coreyyoung/Claude/context/knowledge/
```

---

## 💡 Tips

1. **Start with Identity:** Fill in profile and preferences first
2. **Add as You Learn:** Don't wait - add knowledge immediately
3. **Keep Files Focused:** Better to have many small files than few large ones
4. **Link Generously:** Connect related concepts
5. **Use Examples:** Concrete examples make knowledge more useful
6. **Update Often:** Knowledge should reflect current understanding

---

**Questions?** See `CLAUDE.md` in this directory for complete PAI documentation.
