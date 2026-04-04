# Neon Setup for AI Agents

## One-Command Setup

```bash
# Authenticates via OAuth, creates API key, configures MCP + agent skills
bunx neonctl@latest init
```

Supports: VS Code, Claude Code, Cursor, Claude Desktop, Codex, OpenCode, Cline, GitHub Copilot CLI, Gemini CLI, Goose, MCPorter, Zed.

After restart, prompt: "Get started with Neon".

---

## Manual MCP Configuration

### Remote MCP — OAuth (recommended)
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

### Remote MCP — API Key
```bash
bunx add-mcp https://mcp.neon.tech/mcp --header "Authorization: Bearer <$NEON_API_KEY>"
```

### Read-Only Mode
Add header `X-Neon-Read-Only: true` to restrict to read-only tools only. Useful for agents that should observe but not mutate.

---

## OAuth Scopes

| Scope | Access |
|---|---|
| `read` | List, describe, query (no mutations) |
| `write` | Create, delete, migrate |
| `*` | Both read and write |

Scope changes require re-authentication.

---

## API Key Setup

1. Neon Console → Settings → API Keys
2. Generate key, store as `NEON_API_KEY` env var
3. Use in API calls: `Authorization: Bearer $NEON_API_KEY`

### Auth Priority (CLI)
1. `--api-key` flag
2. `NEON_API_KEY` env var
3. `credentials.json` from `neonctl auth`
4. Browser OAuth fallback

---

## Verify Setup

```bash
# CLI
neonctl me --output json
neonctl projects list

# MCP — ask your AI assistant:
# "List my Neon projects"
# "Describe my Neon project <name>"
```
