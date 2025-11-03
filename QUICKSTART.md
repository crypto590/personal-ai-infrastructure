# PAI Quick Start Guide

**Personal AI Infrastructure** - Your "build once, use everywhere" AI system.

---

## 🎯 What is PAI?

PAI is a central knowledge and skills repository that makes AI assistance consistent, personalized, and efficient across all your projects.

**Key Benefits:**
- ✅ AI knows who you are and how you work
- ✅ Skills and knowledge available everywhere
- ✅ 86%+ reduction in token usage (progressive disclosure)
- ✅ Single source of truth - update once, use everywhere
- ✅ Projects stay lightweight and focused

---

## 📁 Directory Structure at a Glance

```
~/.claude/
├── CLAUDE.md                      # Index (points to context/CLAUDE.md)
├── QUICKSTART.md                  # This file
│
├── skills/                        # Reusable capabilities
│   ├── core/                     # Universal (problem-solving, writing)
│   ├── technical/                # Programming (web-dev, APIs, databases)
│   ├── business/                 # Business (analysis, strategy)
│   ├── domain/                   # Your expertise (payments, compliance)
│   └── personal/                 # Productivity (health, finance, learning)
│
├── context/                       # Your knowledge brain
│   ├── CLAUDE.md                 # Master PAI documentation (READ THIS!)
│   ├── identity/
│   │   ├── profile.md           # Who you are, expertise
│   │   ├── preferences.md       # How you like to work
│   │   └── values.md            # Your principles
│   ├── knowledge/
│   │   ├── languages/           # Programming languages
│   │   ├── frameworks/          # Tech frameworks
│   │   ├── domains/             # Domain expertise
│   │   ├── patterns/            # Design patterns
│   │   └── apis/                # API docs
│   ├── projects/
│   │   ├── current/             # Active projects
│   │   └── archive/             # Past projects
│   └── resources/
│       ├── tools/               # Tool docs
│       └── templates/           # Reusable templates
│
├── commands/                      # Custom workflows (empty for now)
├── hooks/                         # Context loader
└── agents/                        # (existing - don't touch)
```

---

## 🚀 Getting Started

### Step 1: Fill in Your Identity (15-30 minutes)

These files teach AI who you are and how you work:

```bash
# Edit your profile
open ~/.claude/context/identity/profile.md

# Edit your preferences
open ~/.claude/context/identity/preferences.md

# Edit your values (optional but recommended)
open ~/.claude/context/identity/values.md
```

**Priority sections to fill in:**
- Name and professional background
- Technical skills (languages, frameworks)
- Current focus and active projects
- Communication preferences
- Code preferences
- Working style

**Tip:** Use [TODO: Fill in] markers to come back to sections later.

### Step 2: Read the Master Documentation

Understand how PAI works:

```bash
open ~/.claude/context/CLAUDE.md
```

**Key sections:**
- Mandatory Startup Protocol
- PAI Architecture Explained
- Usage Patterns
- How Projects Use PAI

### Step 3: Set Environment Variables

Add to `~/.zshrc` (or `~/.bashrc` if you use bash):

```bash
# Add these lines
export CLAUDE_HOME="$HOME/.claude"
export PAI_DIR="$HOME/.claude"

# Reload shell
source ~/.zshrc
```

### Step 4: Test It Out

Start a conversation with AI and verify PAI loads:

```
You: "Load my PAI and tell me what you know about me"
AI: "PAI loaded: [Your Name]'s infrastructure ready..."
```

---

## 📝 Adding Skills

### When to Create a Skill

Create a skill when you have a **reusable capability** that applies across projects:

✅ **Good skill examples:**
- API design patterns
- TypeScript error handling
- Code review checklist
- Business analysis framework
- Payment processing flow

❌ **Not a skill:**
- Project-specific configurations
- One-off solutions
- Temporary workarounds

### Skill File Structure

```markdown
# Skill Name

**Category:** [core/technical/business/domain/personal]

**Brief Description:** [1-2 sentence summary - this is the metadata]

---

## When to Use This Skill

[Trigger conditions - when should AI load this skill?]
- Trigger 1
- Trigger 2
- Trigger 3

---

## How It Works

[Detailed implementation, patterns, examples]

### Approach

[Your methodology]

### Examples

[Concrete examples]

### Common Patterns

[Patterns you use]

---

## Dependencies

**Other skills:**
- [Related skill 1]
- [Related skill 2]

**Context files:**
- [Context file 1]
- [Context file 2]

---

## Notes

[Any additional information]
```

### Creating a New Skill

```bash
# Choose appropriate category
cd ~/.claude/skills/technical

# Create skill file
touch api-design.md

# Edit with your preferred editor
open api-design.md
```

**Remember:** Keep the header brief (metadata) and put details in the body (loaded on demand).

---

## 📚 Adding Knowledge

### When to Add Knowledge

Add to `context/knowledge/` when you have **reference information** AI should know:

✅ **Good knowledge examples:**
- Next.js 15 server actions patterns
- Your company's API authentication flow
- Payment processing compliance requirements
- Design system component guidelines

### Knowledge Organization

```bash
# Programming language knowledge
~/.claude/context/knowledge/languages/typescript/async-patterns.md

# Framework knowledge
~/.claude/context/knowledge/frameworks/nextjs/server-actions.md

# Domain expertise
~/.claude/context/knowledge/domains/payment-processing/compliance.md

# Patterns
~/.claude/context/knowledge/patterns/api-design/rest-patterns.md

# API docs
~/.claude/context/knowledge/apis/stripe-integration.md
```

---

## 🔗 Using PAI in Projects

### Project CLAUDE.md Template

Keep project files lightweight - they should mostly **reference** PAI:

```markdown
# Project: [Project Name]

## Load PAI Skills
- Read: ~/.claude/skills/technical/web-dev-nextjs.md
- Read: ~/.claude/skills/technical/typescript-patterns.md
- Read: ~/.claude/skills/domain/[your-domain].md

## Load Context
- Read: ~/.claude/context/knowledge/frameworks/nextjs/
- Read: ~/.claude/context/knowledge/domains/[your-domain]/

## Project-Specific Details

**Stack:**
- Frontend: [Tech stack]
- Backend: [Tech stack]
- Database: [Database]
- Auth: [Auth solution]
- Deployment: [Platform]

**Current Focus:**
- [What you're actively working on]

**Project Quirks:**
- [Specific constraints or patterns for THIS project only]
```

**Key Principle:** Don't duplicate knowledge. Reference PAI files instead.

---

## 🔄 Common Workflows

### Starting a New Project

1. Create project directory
2. Add lightweight `CLAUDE.md` with PAI references
3. Add project-specific details only
4. AI loads PAI + project context automatically

### Learning a New Technology

1. Research the technology
2. Add knowledge file: `~/.claude/context/knowledge/frameworks/[tech]/overview.md`
3. Create skill if there's a reusable pattern
4. Knowledge now available for all future projects

### Capturing a Pattern

1. Identify reusable pattern
2. Determine category (skill vs. knowledge)
3. Create file in appropriate location
4. Pattern automatically available everywhere

### Refining Your Identity

1. Edit `~/.claude/context/identity/profile.md` as you gain new skills
2. Update `preferences.md` as you discover better workflows
3. AI assistance improves automatically

---

## 🧭 Progressive Disclosure in Action

### How AI Uses PAI

**Every request:**
1. Load identity (profile + preferences) - ~500 tokens
2. Scan skill metadata - ~300 tokens
3. **Total so far: ~800 tokens**

**When task requires specific skills:**
4. Load relevant skill content - ~4,000 tokens
5. Load related context - ~2,000 tokens
6. **Total for complex task: ~6,800 tokens**

**Before PAI:** 50,000 tokens per request
**After PAI:** 6,800 tokens per request
**Savings:** 86% reduction

---

## 🛠️ Maintenance

### Regular Reviews

**Weekly:**
- Review active projects in `context/projects/current/`
- Add new skills discovered during the week

**Monthly:**
- Update `identity/profile.md` with new expertise
- Refactor skills that have grown too large
- Archive completed projects to `projects/archive/`

**Quarterly:**
- Review and update `identity/preferences.md`
- Clean up outdated knowledge
- Consolidate overlapping skills

### Quality Checks

```bash
# List all skills
find ~/.claude/skills -name "*.md"

# Search for specific knowledge
grep -r "search term" ~/.claude/context/knowledge/

# Check identity completeness
cat ~/.claude/context/identity/profile.md | grep TODO

# Verify structure
tree -L 3 ~/.claude/
```

---

## 💡 Pro Tips

### Tip 1: Start Small
Don't try to fill everything at once. Start with:
1. Basic profile (name, current role, tech stack)
2. One or two key skills
3. Add more as you go

### Tip 2: Capture as You Work
When AI suggests a great pattern:
- Immediately save it as a skill or knowledge file
- Your PAI gets smarter with every project

### Tip 3: Keep Projects Lightweight
If your project CLAUDE.md is > 100 lines, move content to PAI:
- Reusable patterns → `skills/`
- Reference knowledge → `context/knowledge/`
- Project file should mostly be references + project-specific details

### Tip 4: Use Consistent Naming
- Skills: `kebab-case.md` (e.g., `api-design.md`)
- Knowledge: Organize by category, use descriptive names
- Projects: Match project name

### Tip 5: Link Files Together
Use relative links in markdown:
```markdown
See also: [API Patterns](../../knowledge/patterns/api-design/rest-patterns.md)
```

---

## 🐛 Troubleshooting

### AI Isn't Loading PAI Context

**Check:**
```bash
# Verify core files exist
ls ~/.claude/context/CLAUDE.md
ls ~/.claude/context/identity/profile.md

# Verify hook exists
ls ~/.claude/hooks/context-loader.ts
```

**Solution:** Fill in at least basic profile information.

### Too Many Tokens Being Used

**Check:** Are you duplicating knowledge in project files?

**Solution:** Move shared knowledge to PAI, reference it from projects.

### Can't Find a Skill

**Search:**
```bash
find ~/.claude/skills -name "*keyword*"
grep -r "keyword" ~/.claude/skills/
```

### Skill Growing Too Large

**Solution:** Split into multiple focused skills or move details to `context/knowledge/`.

---

## 📖 Further Reading

**Essential:**
- `~/.claude/context/CLAUDE.md` - Complete PAI documentation

**References:**
- [Daniel Miessler's Blog Post](https://danielmiessler.com/blog/personal-ai-infrastructure)
- [Daniel Miessler's GitHub Repo](https://github.com/danielmiessler/Personal_AI_Infrastructure)

---

## 🎓 Next Steps

1. ✅ Fill in `identity/profile.md` (at least basic info)
2. ✅ Fill in `identity/preferences.md` (communication & code preferences)
3. ✅ Add environment variables to `~/.zshrc`
4. ✅ Read `context/CLAUDE.md` to understand the system
5. ✅ Create your first skill
6. ✅ Add your first knowledge file
7. ✅ Use PAI in a project

**Remember:** PAI is a living system. It grows with you.

---

**Questions?** Refer to `~/.claude/context/CLAUDE.md` for complete documentation.
