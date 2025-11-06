# Personal AI Infrastructure (PAI)

**Architecture:** Skills-as-Containers (November 2025)

For complete documentation, read:
`/Users/coreyyoung/Claude/context/CLAUDE.md`

---

## 🚀 Quick Start

**Your PAI uses progressive disclosure for 92.5% token reduction:**

1. **CORE Skill** - Your identity lives in `/Users/coreyyoung/Claude/skills/CORE/SKILL.md`
   - Tier 1 (YAML frontmatter): ~300 tokens, always loaded
   - Tier 2 (body content): ~4000 tokens, loads on-demand

2. **Skills** - Organized in `/Users/coreyyoung/Claude/skills/`
   - Each skill is a directory with `SKILL.md`
   - Optional `workflows/` subdirectory for related tasks

3. **Knowledge** - Reference materials in `/Users/coreyyoung/Claude/context/knowledge/`
   - Languages, frameworks, domains, patterns
   - Skills load these on-demand as needed

---

## 🏗️ Architecture

### Symlink Structure (Visibility + Version Control)
```
~/Claude/              # Visible in Finder, git-tracked
├── skills/            # Skill containers
│   ├── CORE/         # Your identity (replaces context/identity/)
│   ├── technical/    # Technical skills
│   ├── business/     # Business skills
│   └── domain/       # Domain expertise
├── context/          # Knowledge base (reference materials)
│   └── knowledge/    # Languages, frameworks, patterns
├── commands/         # Custom workflows
├── agents/           # Agent definitions
└── hooks/            # Minimal context loader

~/.claude/            # Runtime directory (symlinks to ~/Claude/)
├── skills → ~/Claude/skills
├── context → ~/Claude/context
├── commands → ~/Claude/commands
└── [runtime files: history, sessions, etc.]
```

**Benefits:**
- Edit files in Finder/VSCode (visible in ~/Claude/)
- Commit to GitHub (version controlled)
- Claude Code finds everything (via ~/.claude/ symlinks)

---

## 📋 How It Works

### Progressive Disclosure System

**Old Architecture (July 2025):**
- Forced loading of context files on every prompt
- Token cost: ~500 tokens overhead per request
- Separate context/ and skills/ directories

**New Architecture (November 2025):**
- CORE skill YAML frontmatter (~300 tokens, always available)
- Full skill body loads only when invoked (~4000 tokens on-demand)
- Skills-as-Containers with optional workflows/
- Result: 92.5% token reduction

### Skill Structure

Each skill follows this pattern:
```
skill-name/
├── SKILL.md              # Main skill file with YAML frontmatter
└── workflows/            # Optional: organized sub-tasks
    ├── workflow-1.md
    └── workflow-2.md
```

**YAML Frontmatter (Tier 1 - Always Loaded):**
```yaml
---
name: skill-name
description: Brief description of skill capability
key_info: "Critical information (always available)"
---
```

**Body Content (Tier 2 - On-Demand):**
- Full implementation details
- Extended documentation
- Examples and patterns

---

## 🎯 Key Files

### Your Identity: CORE Skill
`/Users/coreyyoung/Claude/skills/CORE/SKILL.md`

Fill out the CORE skill to establish your:
- Professional background and expertise
- Working preferences and communication style
- Values and engineering principles
- Current focus and learning goals

**This replaces the old `context/identity/` directory.**

### Master Documentation
`/Users/coreyyoung/Claude/context/CLAUDE.md`

Complete PAI documentation including:
- Detailed architecture explanation
- Usage patterns and workflows
- Maintenance and best practices

---

## 🔧 Common Operations

**Check PAI structure:**
```bash
tree -L 2 ~/Claude/
```

**Verify symlinks:**
```bash
ls -la ~/.claude/ | grep -E "skills|context|commands"
```

**List available skills:**
```bash
find ~/Claude/skills -name "SKILL.md" -type f
```

**Search knowledge base:**
```bash
grep -r "search term" ~/Claude/context/knowledge/
```

---

## 📚 References

- **Daniel Miessler's PAI Blog:** https://danielmiessler.com/blog/personal-ai-infrastructure
- **Daniel Miessler's GitHub:** https://github.com/danielmiessler/Personal_AI_Infrastructure
- **Architecture Version:** v1.2.0 (November 2025)
- **Local Documentation:** `/Users/coreyyoung/Claude/context/CLAUDE.md`

---

## ✨ Migration Notes

**What Changed (November 2025):**
- Identity moved from `context/identity/` → `skills/CORE/SKILL.md`
- Hook simplified (zero forced context loading)
- Skills use YAML frontmatter for progressive disclosure
- Optional `workflows/` subdirectories for skill organization

**What Stayed the Same:**
- Symlink architecture (~/Claude/ → ~/.claude/)
- Knowledge base structure (context/knowledge/)
- Skills organized by capability type
- Git-tracked in ~/Claude/

**Token Efficiency:**
- Before: ~500 tokens overhead per request
- After: ~300 tokens in skill frontmatter (40% reduction)
- Deep context: Load full skills only when needed
- Result: 92.5% overall token reduction

---

This PAI is based on Daniel Miessler's architecture:
https://danielmiessler.com/blog/personal-ai-infrastructure
