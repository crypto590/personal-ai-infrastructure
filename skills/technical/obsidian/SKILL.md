---
name: obsidian
description: Unified Obsidian vault interaction via CLI and content creation. Read/write/search notes, manage tasks, create daily entries, work with Bases databases and JSON Canvas. Default vault "The_Hub". USE WHEN interacting with Obsidian vault, writing notes, searching knowledge base, managing tasks, creating canvas files, working with Bases, or logging session outcomes.
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Obsidian Vault Interaction

## When to Activate This Skill

- Writing or reading notes in the vault
- Searching for prior knowledge, research, or context
- Managing tasks in Obsidian
- Creating Bases (`.base`) database files
- Creating Canvas (`.canvas`) visual files
- Logging session decisions or outcomes
- Working with daily notes

## Setup & Requirements

- **Obsidian 1.12+** with Catalyst license
- CLI enabled: Settings > General > Enable CLI
- **App must be running** (first CLI command launches it if needed)
- Default vault: `The_Hub` (always pass `vault=The_Hub` as first parameter)

## CLI Core Reference

### Vault Targeting

Every command starts with vault targeting. Use `file=` for wikilink-style name resolution, `path=` for exact paths from vault root.

```bash
# Target vault (always first parameter)
obsidian vault=The_Hub <command>

# Reference by note name (wikilink resolution)
obsidian vault=The_Hub read file="Project Alpha"

# Reference by exact path
obsidian vault=The_Hub read path="Projects/2025/Project Alpha.md"

# Copy output to clipboard
obsidian vault=The_Hub read file="note" --copy
```

### Daily Notes

```bash
# Open today's daily note
obsidian vault=The_Hub daily

# Read today's daily note contents
obsidian vault=The_Hub daily:read

# Append to end of daily note
obsidian vault=The_Hub daily:append content="## Session Log\n- Completed auth refactor"

# Prepend to beginning of daily note
obsidian vault=The_Hub daily:prepend content="## Morning Priorities\n- [ ] Review PRs"
```

### File Operations

```bash
# Create a new file
obsidian vault=The_Hub create path="Projects/new-project.md" content="---\nstatus: active\n---\n# New Project"

# Read file contents
obsidian vault=The_Hub read file="Project Alpha"

# Append to existing file
obsidian vault=The_Hub append file="Project Alpha" content="\n## Update\nNew findings added."

# Prepend to existing file
obsidian vault=The_Hub prepend file="Project Alpha" content="> [!important] Priority Change\n> Deadline moved up.\n\n"

# Move or rename a file
obsidian vault=The_Hub move file="Old Name" path="Archive/Old Name.md"

# Delete a file
obsidian vault=The_Hub delete file="Scratch Notes"
```

### Search & Discovery

```bash
# Full-text search
obsidian vault=The_Hub search query="authentication flow"

# Find notes linking TO a specific note
obsidian vault=The_Hub backlinks file="Project Alpha"

# List outgoing links FROM a note
obsidian vault=The_Hub links file="Project Alpha"

# Find broken/unresolved links
obsidian vault=The_Hub unresolved

# Find orphaned notes (no links in or out)
obsidian vault=The_Hub orphans

# List all tags in the vault
obsidian vault=The_Hub tags
```

### Task Management

```bash
# List all tasks
obsidian vault=The_Hub tasks

# Filter by status
obsidian vault=The_Hub tasks status=todo

# Tasks from a specific file
obsidian vault=The_Hub tasks file="Project Alpha"

# View or modify an individual task
obsidian vault=The_Hub task
```

### Properties & Metadata

```bash
# View all properties on a note
obsidian vault=The_Hub properties file="Project Alpha"

# Set a property
obsidian vault=The_Hub property:set file="Project Alpha" property="status" value="complete"

# Remove a property
obsidian vault=The_Hub property:remove file="Project Alpha" property="priority"

# List and analyze all tags
obsidian vault=The_Hub tags
```

### Templates

```bash
# List available templates
obsidian vault=The_Hub templates

# Read a template's contents
obsidian vault=The_Hub template:read file="Daily Note Template"

# Insert/apply a template
obsidian vault=The_Hub template:insert file="Daily Note Template"
```

### Content Formatting

- Use `\n` for newlines in content parameters
- Use `\t` for tabs
- For complex multi-line content, prefer writing to a temp file and using file operations

## Integration Patterns

**Before starting work** -- search vault for relevant context:
```bash
obsidian vault=The_Hub search query="topic keywords"
obsidian vault=The_Hub tags
```

**After completing work** -- log outcomes to daily note:
```bash
obsidian vault=The_Hub daily:append content="\n## Session Summary\n- Decision: migrated auth to JWT\n- Outcome: all tests passing\n- Next: implement refresh tokens"
```

**Task sync** -- check tasks before and after work:
```bash
obsidian vault=The_Hub tasks status=todo
```

## Available Workflows

| Workflow | When to Use | Load Command |
|----------|-------------|--------------|
| Session Logging | Appending decisions/outcomes to vault | `read /Users/coreyyoung/.claude/skills/technical/obsidian/workflows/session-logging.md` |
| Knowledge Retrieval | Searching vault before starting work | `read /Users/coreyyoung/.claude/skills/technical/obsidian/workflows/knowledge-retrieval.md` |
| Task Management | Managing Obsidian tasks from sessions | `read /Users/coreyyoung/.claude/skills/technical/obsidian/workflows/task-management.md` |
| Obsidian Markdown | Writing Obsidian-flavored markdown | `read /Users/coreyyoung/.claude/skills/technical/obsidian/obsidian-markdown/SKILL.md` |
| Obsidian Bases | Creating .base database files | `read /Users/coreyyoung/.claude/skills/technical/obsidian/obsidian-bases/SKILL.md` |
| JSON Canvas | Creating .canvas visual files | `read /Users/coreyyoung/.claude/skills/technical/obsidian/json-canvas/SKILL.md` |

## Key Principles

1. **Always specify `vault=The_Hub`** as the first parameter
2. **Search before creating** to avoid duplicate notes
3. **Use `file=` for note names**, `path=` for exact paths from vault root
4. **Append to daily notes** for session logging (never overwrite)
5. **Combine CLI commands with format knowledge** from the Obsidian Markdown, Bases, and Canvas workflows
6. **Obsidian must be running** for the CLI to work
