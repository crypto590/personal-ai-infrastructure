# Personal AI Infrastructure (PAI)

**For complete PAI documentation, read:**
`/Users/coreyyoung/Claude/context/CLAUDE.md`

## Directory Setup

This PAI uses **symlinks** to make content accessible to Claude Code:
- **Files live here:** `~/Claude/` (visible, git-tracked)
- **Claude Code accesses via:** `~/.claude/` (symlinked)
- **Benefit:** Edit in Finder/VSCode, commit to GitHub, Claude finds everything

**Quick Reference:**
- Skills: `~/Claude/skills/` (also accessible at `~/.claude/skills/`)
- Context: `~/Claude/context/` (also accessible at `~/.claude/context/`)
- Commands: `~/Claude/commands/` (also accessible at `~/.claude/commands/`)
- Identity: `~/Claude/context/identity/profile.md`

This PAI is based on Daniel Miessler's architecture:
https://danielmiessler.com/blog/personal-ai-infrastructure
