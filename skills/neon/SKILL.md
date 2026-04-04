---
name: neon
effort: medium
description: "Neon serverless Postgres: branching, MCP tools, @neondatabase/toolkit, migrations, agent isolation patterns, and CLI operations."
metadata:
  last_reviewed: 2026-04-03
  review_cycle: 90
---

# Neon Serverless Postgres

Operational skill for working with Neon — branching, SQL, migrations, agent isolation, and the MCP server. Reference knowledge lives at `context/knowledge/platforms/neon-postgres.md`.

---

## Quick Routing Table

| Need to... | Read this |
|---|---|
| Set up Neon MCP or AI integration | `workflows/setup.md` |
| Create/manage branches for agent isolation | `workflows/branching.md` |
| Run safe schema migrations | `workflows/migrations.md` |
| Use @neondatabase/toolkit in code | `workflows/toolkit.md` |

---

## Core Principles

1. **Never mutate production directly.** Always use a branch for schema changes, query tuning, or destructive operations. The MCP server's `prepare_database_migration` and `prepare_query_tuning` tools enforce this automatically via temp branches.

2. **Branch-per-agent for parallel work.** When running multiple agents (e.g., parallel Claude Code subagents), each gets its own Neon branch. This prevents interference and enables independent rollback.

3. **Auto-expire branches.** Use `expires_at` (max 30 days) on agent branches so forgotten branches don't accumulate. The API accepts RFC 3339 timestamps.

4. **Prefer MCP tools over raw API.** When the Neon MCP server is available, use its tools (`run_sql`, `create_branch`, `prepare_database_migration`, etc.) rather than calling the REST API directly. The MCP tools handle connection management and cleanup.

5. **Schema-only branches for testing.** Use `"init_source": "schema-only"` when you need the structure but not the data — faster creation, no data exposure.

---

## MCP Tools Quick Reference

### Most-Used Tools
| Tool | What it does |
|---|---|
| `run_sql` | Execute a single query |
| `run_sql_transaction` | Execute multiple queries atomically |
| `create_branch` | Create a branch for dev/testing |
| `delete_branch` | Remove a branch |
| `compare_database_schema` | Diff schemas between parent and child branch |
| `prepare_database_migration` | Start migration on temp branch (safe) |
| `complete_database_migration` | Finalize or discard migration |
| `get_connection_string` | Get connection string for a branch |
| `describe_table_schema` | Inspect columns, types, constraints |

### Read-Only Safe Tools
`list_projects`, `describe_project`, `describe_branch`, `get_database_tables`, `describe_table_schema`, `list_slow_queries`, `explain_sql_statement`, `get_connection_string`, `search`, `fetch`

---

## Authentication

```bash
# Environment variable (preferred)
export NEON_API_KEY="your-key"

# CLI auth (interactive)
neonctl auth

# API header
Authorization: Bearer $NEON_API_KEY
```

---

## CLI Quick Commands

```bash
neonctl init                          # Set up AI assistants (MCP + skills)
neonctl projects list                 # List projects
neonctl branches create --project <id> --branch <name>
neonctl branches schema-diff          # Compare schemas
neonctl connection-string <branch>    # Get connection string
neonctl set-context --project <id>    # Set default project context
```

---

## Decision Guide

- **Starting fresh?** Run `neonctl init` → read `workflows/setup.md`
- **Need a branch for agent work?** → `workflows/branching.md`
- **Running a migration?** → `workflows/migrations.md`
- **Writing agent code with ephemeral databases?** → `workflows/toolkit.md`
- **Need full API/tool reference?** → `context/knowledge/platforms/neon-postgres.md`
