# @neondatabase/toolkit — Agent SDK

A minimal JavaScript SDK for spinning up ephemeral Postgres databases and running SQL. Designed for test environments and AI agent loops.

## Install

```bash
bun add @neondatabase/toolkit
```

## API Surface

```typescript
import { NeonToolkit } from '@neondatabase/toolkit';

const toolkit = new NeonToolkit(process.env.NEON_API_KEY!);
```

| Method | Signature | Description |
|---|---|---|
| `createProject()` | `() => Promise<Project>` | Create a new Neon project (includes database + branch) |
| `sql()` | `(project: Project, query: string) => Promise<any>` | Execute SQL on the project |
| `deleteProject()` | `(project: Project) => Promise<void>` | Delete project and all resources |
| `apiClient` | Property | Direct access to underlying Neon API client |

## Usage Pattern

```typescript
const toolkit = new NeonToolkit(process.env.NEON_API_KEY!);

// Create ephemeral database
const project = await toolkit.createProject();

try {
  // Schema
  await toolkit.sql(project, `
    CREATE TABLE conversations (
      id SERIAL PRIMARY KEY,
      agent_id TEXT NOT NULL,
      message TEXT NOT NULL,
      created_at TIMESTAMPTZ DEFAULT NOW()
    )
  `);

  // Write
  await toolkit.sql(project, `
    INSERT INTO conversations (agent_id, message)
    VALUES ('agent-1', 'Task completed successfully')
  `);

  // Read
  const result = await toolkit.sql(project, 'SELECT * FROM conversations');
  console.log(result);
} finally {
  // Always cleanup
  await toolkit.deleteProject(project);
}
```

## Advanced: Direct API Client

For operations beyond create/sql/delete, use the underlying API client:

```typescript
const api = toolkit.apiClient;

// Create a branch on an existing project
// List projects, manage roles, etc.
```

## Agent Loop Pattern

```typescript
async function agentTask(taskId: string) {
  const toolkit = new NeonToolkit(process.env.NEON_API_KEY!);
  const project = await toolkit.createProject();

  try {
    // Agent sets up its schema
    await toolkit.sql(project, 'CREATE TABLE ...');

    // Agent loop: read/write as needed
    while (!done) {
      const data = await toolkit.sql(project, 'SELECT ...');
      // ... process ...
      await toolkit.sql(project, 'INSERT ...');
    }

    return results;
  } finally {
    await toolkit.deleteProject(project);
  }
}
```

## When to Use Toolkit vs MCP

| Scenario | Use |
|---|---|
| Agent needs ephemeral database for a task | Toolkit |
| Agent managing existing Neon project | MCP tools |
| Programmatic database provisioning in code | Toolkit |
| Interactive database operations via AI assistant | MCP tools |
| Test fixtures / CI pipelines | Toolkit |
| Schema migrations on existing databases | MCP tools |

## Caveats

- Early development — API may change
- Each `createProject()` creates a full Neon project (not just a branch)
- For branch-level isolation on an existing project, use the API client directly or MCP tools
- Always wrap in try/finally to ensure cleanup
