# Neon Branching for Agent Isolation

## Concept

Neon branches are copy-on-write forks of your database. They're instant, cheap, and perfect for isolating agent work from production.

```
main (production)
├── agent-migration-001   (schema refactoring)
├── agent-query-opt-002   (query tuning)
└── agent-feature-003     (feature development)
```

---

## Create a Branch

### Via MCP
Use `create_branch` tool with project ID and optional parent branch.

### Via API
```bash
POST https://console.neon.tech/api/v2/projects/{project_id}/branches
Authorization: Bearer $NEON_API_KEY
Content-Type: application/json

{
  "endpoints": [{"type": "read_write"}],
  "branch": {
    "parent_id": "br-parent-branch-id"
  }
}
```

### Options

| Option | Purpose |
|---|---|
| `"init_source": "schema-only"` | Copy schema without data (faster, no data exposure) |
| `"expires_at": "2026-04-10T00:00:00Z"` | Auto-delete after date (max 30 days, RFC 3339) |

### Via CLI
```bash
neonctl branches create --project <project_id> --branch <name>
```

---

## Agent Isolation Pattern

### Per-Agent Branches
Each agent gets its own branch. Agents work in parallel without interference.

**Workflow:**
1. Create branch from main (with `expires_at` for auto-cleanup)
2. Agent performs work on its branch (`run_sql`, migrations, etc.)
3. Review changes via `compare_database_schema` (schema diff against parent)
4. If approved: apply migration SQL to main, then delete branch
5. If rejected: just delete the branch — main is untouched

### Parallel Subagents (Claude Code Pattern)
```
Main agent spawns 3 subagents:
├── Subagent A → branch-a (schema refactoring)
├── Subagent B → branch-b (query optimization)
└── Subagent C → branch-c (data backfill)
```

Each subagent receives its branch's connection string. Work proceeds in parallel. Main agent reviews diffs and merges approved changes sequentially.

---

## Branch Operations

| Operation | MCP Tool | CLI |
|---|---|---|
| Create | `create_branch` | `neonctl branches create` |
| Delete | `delete_branch` | `neonctl branches delete` |
| Inspect | `describe_branch` | `neonctl branches get` |
| Schema diff | `compare_database_schema` | `neonctl branches schema-diff` |
| Reset to parent | `reset_from_parent` | `neonctl branches reset` |
| Get connection | `get_connection_string` | `neonctl connection-string` |

---

## Cleanup

- **Auto-expire:** Set `expires_at` at creation time
- **Manual:** `delete_branch` or `neonctl branches delete`
- **Reset:** `reset_from_parent` wipes branch changes, keeps the branch (auto-preserves if branch has children)

---

## ID Formats
- Project: `autumn-disk-484331` (adjective-noun-number)
- Branch: `br-dawn-scene-747675` (br- prefix)
