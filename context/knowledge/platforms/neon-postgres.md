# Neon Serverless Postgres — Agent Knowledge Base

> Last updated: 2026-04-03
> Sources: neon.com/docs, github.com/neondatabase/mcp-server-neon, github.com/neondatabase/toolkit

---

## 1. Quick Setup for AI Agents

```bash
# One-command setup — authenticates, creates API key, configures MCP + skills
npx neonctl@latest init

# Or with bun
bunx neonctl@latest init
```

Supports 12+ AI assistants: VS Code, Claude Code, Cursor, Claude Desktop, Codex, OpenCode, Cline, GitHub Copilot CLI, Gemini CLI, Goose, MCPorter, Zed.

After restart, prompt your AI: "Get started with Neon".

---

## 2. Authentication

### API Key
- Generate at: Neon Console > Settings > API Keys
- Header: `Authorization: Bearer $NEON_API_KEY`
- Env var: `NEON_API_KEY`

### CLI Auth Priority
1. `--api-key` flag (highest)
2. `NEON_API_KEY` env var
3. `credentials.json` from `neon auth`
4. Browser-based OAuth (fallback)

---

## 3. Neon MCP Server

### Configuration Options

**Remote MCP (OAuth — recommended):**
```json
{
  "mcpServers": {
    "Neon": {
      "type": "http",
      "url": "https://mcp.neon.tech/mcp"
    }
  }
}
```

**Remote MCP (API Key):**
```bash
npx add-mcp https://mcp.neon.tech/mcp --header "Authorization: Bearer <$NEON_API_KEY>"
```

**OAuth Scopes:** `read`, `write`, or `*` (both)
**Read-only mode:** Add header `X-Neon-Read-Only: true`

### All MCP Tools

#### Project Management
| Tool | Description | Scope |
|------|-------------|-------|
| `list_projects` | List first 10 projects (supports `limit` param) | projects |
| `list_shared_projects` | List projects shared with current user | projects |
| `describe_project` | Get project details including branches and databases | projects |
| `create_project` | Create new project container | projects |
| `delete_project` | Remove project and all resources | projects |
| `list_organizations` | List accessible orgs (supports search) | projects |

#### Branch Management
| Tool | Description | Scope |
|------|-------------|-------|
| `create_branch` | Create branch for dev/testing | branches |
| `delete_branch` | Remove branch | branches |
| `describe_branch` | Get branch details (name, ID, parent) | branches |
| `list_branch_computes` | List compute endpoints with autoscaling info | branches |
| `compare_database_schema` | Schema diff between child and parent branches | schema |
| `reset_from_parent` | Reset branch to parent state (auto-preserves if children exist) | branches |

#### SQL Execution
| Tool | Description | Scope |
|------|-------------|-------|
| `get_connection_string` | Get database connection string | querying |
| `run_sql` | Execute single query (read/write) | querying |
| `run_sql_transaction` | Execute multiple queries in a transaction | querying |
| `get_database_tables` | List all tables in database | schema |
| `describe_table_schema` | Column details, data types, constraints | schema |

#### Database Migrations (Safe via Temp Branches)
| Tool | Description | Scope |
|------|-------------|-------|
| `prepare_database_migration` | Start migration on temporary branch for testing | schema |
| `complete_database_migration` | Finalize migration — merge changes, cleanup | schema |

#### Query Optimization
| Tool | Description | Scope |
|------|-------------|-------|
| `list_slow_queries` | Identify bottlenecks (requires pg_stat_statements) | querying |
| `explain_sql_statement` | Get execution plans | querying |
| `prepare_query_tuning` | Analyze and suggest optimizations on temp branch | querying |
| `complete_query_tuning` | Apply or discard optimizations, cleanup | querying |

#### Infrastructure
| Tool | Description | Scope |
|------|-------------|-------|
| `provision_neon_auth` | Set up auth infrastructure | neon_auth |
| `provision_neon_data_api` | Provision HTTP database access with optional JWT | data_api |

#### Search & Discovery
| Tool | Description | Scope |
|------|-------------|-------|
| `search` | Search orgs, projects, branches by query | null |
| `fetch` | Get detailed info by ID (from search results) | null |

#### Documentation
| Tool | Description | Scope |
|------|-------------|-------|
| `list_docs_resources` | Fetch Neon docs index | docs |
| `get_doc_resource` | Get specific doc page as markdown | docs |

### Read-Only Available Tools
`list_projects`, `list_shared_projects`, `describe_project`, `describe_branch`, `list_branch_computes`, `compare_database_schema`, `run_sql`, `run_sql_transaction`, `get_database_tables`, `describe_table_schema`, `list_slow_queries`, `explain_sql_statement`, `get_connection_string`, `search`, `fetch`, `list_docs_resources`, `get_doc_resource`

---

## 4. @neondatabase/toolkit (JavaScript SDK for Agents)

```bash
npm install @neondatabase/toolkit
# or: bun add @neondatabase/toolkit
```

Bundles Neon API Client + Serverless Driver. Designed for ephemeral databases in tests and AI agents.

```typescript
import { NeonToolkit } from '@neondatabase/toolkit';

const toolkit = new NeonToolkit(process.env.NEON_API_KEY!);

// Create ephemeral project
const project = await toolkit.createProject();

// Run SQL
await toolkit.sql(project, 'CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT)');
await toolkit.sql(project, "INSERT INTO users (name) VALUES ('Alice')");
const result = await toolkit.sql(project, 'SELECT * FROM users');

// Access underlying API client for advanced operations
const apiClient = toolkit.apiClient;

// Cleanup
await toolkit.deleteProject(project);
```

**API Surface:**
- `new NeonToolkit(apiKey: string)` — constructor
- `.createProject()` — create new Neon project
- `.sql(project, query)` — execute SQL on project
- `.deleteProject(project)` — remove project
- `.apiClient` — direct access to Neon API client

> Status: Early development, API may change.

---

## 5. Neon API — Branch Operations

Base URL: `https://console.neon.tech/api/v2`

### Create Branch
```bash
POST /projects/{project_id}/branches
Authorization: Bearer $NEON_API_KEY
Content-Type: application/json

{
  "endpoints": [{"type": "read_write"}],
  "branch": {
    "parent_id": "br-wispy-dew-591433"
  }
}
```

**Options:**
- `"init_source": "schema-only"` — copy schema without data
- `"expires_at": "2024-12-15T18:02:16Z"` — auto-delete (max 30 days, RFC 3339)

### List Branches
```bash
GET /projects/{project_id}/branches
```

### Delete Branch
```bash
DELETE /projects/{project_id}/branches/{branch_id}
```

### Restore Branch
```bash
POST /projects/{project_id}/branches/{branch_id}/restore
```

### ID Formats
- Project IDs: `autumn-disk-484331` (adjective-noun-number)
- Branch IDs: `br-` prefix (e.g., `br-dawn-scene-747675`)

---

## 6. neonctl CLI Reference

### Installation
```bash
brew install neonctl          # macOS
npm i -g neonctl              # Node.js 18+
bun install -g neonctl        # Bun
bunx neonctl <command>        # Without install
```

### Key Commands
```bash
neon auth                          # Authenticate via browser
neon projects list                 # List all projects
neon projects create               # Create project
neon branches list                 # List branches
neon branches create --project <id> --branch <name>
neon branches reset --project <id> --branch <id>
neon branches restore --project <id> --branch <id>
neon branches schema-diff          # Compare schemas
neon databases list                # List databases
neon databases create              # Create database
neon roles list                    # List roles
neon connection-string <branch>    # Get connection string
neon set-context --project <id>    # Set default project
neon init                          # Configure AI assistants (MCP + skills)
```

### Output Formats
`-o json|yaml|table` (default: table)

---

## 7. Agent Patterns with Neon

### Branch-Per-Agent Isolation
Each AI agent gets its own branch, enabling parallel execution without interference:

```
main (production)
├── agent-migration-001  (schema refactoring)
├── agent-query-opt-002  (query tuning)
└── agent-feature-003    (feature development)
```

**Workflow:**
1. Create branch from main: `POST /projects/{id}/branches` with parent_id
2. Agent works on its branch (run_sql, migrations, etc.)
3. Review changes via `compare_database_schema` (schema diff)
4. Merge by applying migration to main, then delete branch
5. Cleanup: delete branch or use `expires_at` for auto-cleanup

### Safe Schema Migrations (MCP Pattern)
1. `prepare_database_migration` — creates temp branch, applies migration
2. Review the diff via `compare_database_schema`
3. `complete_database_migration` — applies to target branch, cleans up temp

### Query Optimization (MCP Pattern)
1. `prepare_query_tuning` — creates temp branch, runs EXPLAIN ANALYZE
2. Review suggestions
3. `complete_query_tuning` — apply or discard, cleanup

### Database Versioning with Snapshots
- Snapshot API enables point-in-time captures of database state
- AI agents can create snapshots before destructive operations
- Restore to any snapshot if agent makes mistakes
- Billing: $0.09/GB-month (as of May 2026)

---

## 8. Neon Auth

- Passwordless authentication infrastructure
- Webhook support for custom OTP delivery and signup validation
- Provisioned via MCP tool: `provision_neon_auth`
- Row-Level Security (RLS) support for data protection

---

## 9. Vector Search (pgvector)

Neon supports `pgvector` for AI embeddings:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  embedding vector(1536),
  content TEXT
);
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 10. Key Changelog Items (2026)

| Date | Item | Impact |
|------|------|--------|
| Apr 2026 | AI-assisted doc shortcuts (Copy as MD, open in Claude) | DX |
| Apr 2026 | Azure region deprecation for new projects | Migration needed |
| Apr 2026 | `pg_search` deprecated for new projects | Use alternatives |
| Mar 2026 | Neon in Stripe Projects (`stripe projects add neon/postgres`) | Provisioning |
| Mar 2026 | Automatic cache prewarming on compute restart | Performance |
| Mar 2026 | Snapshots billing starts May 2026 ($0.09/GB-month) | Cost |
| Mar 2026 | `npx neonctl@latest init` supports 12+ AI assistants | Agent setup |
| Mar 2026 | Isolated subagents guide (parallel Claude Code + branches) | Agent architecture |
| Mar 2026 | Safe AI schema refactoring with OpenAI Codex | Migration safety |

### API Deprecation
- `GET /consumption_history/account` sunset: June 1, 2026
- Use project-level consumption metrics instead

---

## 11. Integrations

- **Vercel**: Preview deployment branches, AI SDK read replica protection
- **Stripe**: `stripe projects add neon/postgres` for agentic provisioning
- **GitHub Actions**: `neondatabase/create-branch-action@v6.3.1`
- **Drizzle ORM**: Agent skills for Drizzle integration
- **Frameworks**: AgentStack, AutoGen, Azure AI Agent Service, Composio + CrewAI, LangGraph, Mastra
