---
name: Neon Postgres Knowledge Base
description: Comprehensive Neon reference for AI agents — MCP server tools, branching API, @neondatabase/toolkit, CLI, agent isolation patterns, and 2026 changelog
type: reference
---

Full knowledge base compiled at `~/.claude/context/knowledge/platforms/neon-postgres.md`

Covers:
- **MCP Server**: 25+ tools across projects, branches, SQL, migrations, query optimization, auth, search, docs
- **@neondatabase/toolkit**: Ephemeral project creation + SQL execution for agents (JS SDK)
- **Branching API**: `POST/GET/DELETE /projects/{id}/branches` — branch-per-agent isolation, schema-only branches, auto-expiry
- **neonctl CLI**: `init` for AI setup, `branches create/reset/restore/schema-diff`, `connection-string`
- **Agent Patterns**: Branch-per-agent isolation, safe migrations via temp branches, query tuning workflow, database versioning with snapshots
- **Auth**: OAuth + API key, read-only mode via `X-Neon-Read-Only: true`
- **Changelog 2026**: Azure deprecation, Stripe integration, cache prewarming, snapshots billing ($0.09/GB-month May 2026), `consumption_history/account` sunset June 2026
