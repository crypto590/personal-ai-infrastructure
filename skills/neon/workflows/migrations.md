# Safe Schema Migrations with Neon

## The Safe Migration Pattern

Neon's MCP server provides a two-step migration flow that uses temporary branches so production is never at risk.

### Step 1: Prepare
```
prepare_database_migration
```
- Creates a temporary branch from the target
- Applies your migration SQL on the temp branch
- You can inspect the result, run queries, verify

### Step 2: Complete
```
complete_database_migration
```
- **Apply:** Merges migration to the target branch, deletes temp branch
- **Discard:** Deletes temp branch, target is untouched

---

## Manual Migration Flow (Without MCP)

When the MCP migration tools aren't available:

### 1. Create a branch
```bash
neonctl branches create --project <id> --branch migration-test
# or via API with expires_at for safety
```

### 2. Apply migration on branch
```sql
-- Run on the branch, not main
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
CREATE INDEX idx_users_email_verified ON users(email_verified);
```

### 3. Verify
```bash
# Schema diff between branch and parent
neonctl branches schema-diff
# or MCP: compare_database_schema
```

### 4. Apply to main
If the diff looks correct, run the same SQL against main.

### 5. Cleanup
```bash
neonctl branches delete --project <id> --branch <branch_id>
```

---

## Query Optimization Flow

Similar two-step pattern for query tuning:

### Step 1: Prepare
```
prepare_query_tuning
```
- Creates temp branch
- Runs EXPLAIN ANALYZE
- Suggests index or query changes

### Step 2: Complete
```
complete_query_tuning
```
- Apply optimizations to target, or discard

### Finding Slow Queries
```
list_slow_queries
```
Requires `pg_stat_statements` extension enabled. Returns queries sorted by total execution time.

```
explain_sql_statement
```
Returns the execution plan for a specific query.

---

## Drizzle ORM Integration

When using Drizzle for migrations:

```bash
# Always use --name for descriptive migration names
bunx drizzle-kit generate --name add_email_verified

# Push to Neon branch for testing
bunx drizzle-kit push

# After verifying on branch, push to main
```

---

## Rollback

- **Branch-based:** If migration was applied only on a branch, just delete the branch
- **Reset:** `reset_from_parent` reverts a branch to its parent's state
- **Snapshots:** Create a snapshot before migration for point-in-time recovery (billing: $0.09/GB-month)
