# Personal AI Infrastructure (PAI)

**Architecture:** Skills-as-Containers (November 2025)

For complete documentation, read:
`/Users/coreyyoung/.claude/context/CLAUDE.md`

---

## 🚀 Quick Start

**Your PAI uses progressive disclosure for 92.5% token reduction:**

1. **CORE Skill** - Your identity lives in `/Users/coreyyoung/.claude/skills/CORE/SKILL.md`
   - Tier 1 (YAML frontmatter): ~300 tokens, always loaded
   - Tier 2 (body content): ~4000 tokens, loads on-demand

2. **Skills** - Organized in `/Users/coreyyoung/.claude/skills/`
   - Each skill is a directory with `SKILL.md`
   - Optional `workflows/` subdirectory for related tasks

3. **Knowledge** - Reference materials in `/Users/coreyyoung/.claude/context/knowledge/`
   - Languages, frameworks, domains, patterns
   - Skills load these on-demand as needed

---

## 🏗️ Architecture

### Unified Structure (.gitignore-based Version Control)
```
~/.claude/             # All files in one location
├── .git/              # Git repository
├── .gitignore         # Separates tracked PAI from system files
├── skills/            # Skill containers (tracked)
│   ├── CORE/         # Your identity
│   ├── technical/    # Technical skills
│   ├── business/     # Business skills
│   └── domain/       # Domain expertise
├── context/           # Knowledge base (tracked)
│   └── knowledge/    # Languages, frameworks, patterns
├── commands/          # Custom workflows (tracked)
├── agents/            # Agent definitions (tracked)
├── hooks/             # Minimal context loader (tracked)
├── CLAUDE.md          # Documentation (tracked)
├── QUICKSTART.md      # Quick reference (tracked)
├── PLUGINS.md         # Plugin docs (tracked)
└── [system files]     # Runtime files (ignored by .gitignore)
    ├── history.jsonl
    ├── settings.json
    ├── debug/
    ├── file-history/
    ├── session-env/
    ├── shell-snapshots/
    ├── statsig/
    ├── todos/
    ├── ide/
    ├── projects/
    └── plugins/
```

**Benefits:**
- Single source of truth - no symlinks
- Smart .gitignore separates PAI from system files
- Claude Code finds everything reliably
- Simpler mental model and maintenance

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
`/Users/coreyyoung/.claude/skills/CORE/SKILL.md`

Fill out the CORE skill to establish your:
- Professional background and expertise
- Working preferences and communication style
- Values and engineering principles
- Current focus and learning goals

**This replaces the old `context/identity/` directory.**

### Master Documentation
`/Users/coreyyoung/.claude/context/CLAUDE.md`

Complete PAI documentation including:
- Detailed architecture explanation
- Usage patterns and workflows
- Maintenance and best practices

---

## 🔧 Common Operations

**Check PAI structure:**
```bash
tree -L 2 ~/.claude/
```

**Verify git tracking:**
```bash
cd ~/.claude && git status
```

**List available skills:**
```bash
find ~/.claude/skills -name "SKILL.md" -type f
```

**Search knowledge base:**
```bash
grep -r "search term" ~/.claude/context/knowledge/
```

---

## 📚 References

- **Daniel Miessler's PAI Blog:** https://danielmiessler.com/blog/personal-ai-infrastructure
- **Daniel Miessler's GitHub:** https://github.com/danielmiessler/Personal_AI_Infrastructure
- **Architecture Version:** v1.3.0 (November 2025)
- **Local Documentation:** `/Users/coreyyoung/.claude/context/CLAUDE.md`

---

## ✨ Migration Notes

### v1.3.0 (November 2025) - Unified Structure
**What Changed:**
- **Removed symlink architecture** - Everything now lives in `~/.claude/`
- **Smart .gitignore** - Separates tracked PAI files from system files
- **Simpler path resolution** - No more symlink issues with agents/skills
- **Single source of truth** - Edit and commit from one location

**Why This Change:**
- Symlinks caused agent discovery issues in some projects
- Simpler mental model - everything in one place
- .gitignore is more reliable than symlink management
- Easier maintenance and troubleshooting

### v1.2.0 (November 2025) - Skills-as-Containers
**What Changed:**
- Identity moved from `context/identity/` → `skills/CORE/SKILL.md`
- Hook simplified (zero forced context loading)
- Skills use YAML frontmatter for progressive disclosure
- Optional `workflows/` subdirectories for skill organization

**What Stayed the Same:**
- Knowledge base structure (context/knowledge/)
- Skills organized by capability type
- Git version control

**Token Efficiency:**
- Before: ~500 tokens overhead per request
- After: ~300 tokens in skill frontmatter (40% reduction)
- Deep context: Load full skills only when needed
- Result: 92.5% overall token reduction

---

This PAI is based on Daniel Miessler's architecture:
https://danielmiessler.com/blog/personal-ai-infrastructure
