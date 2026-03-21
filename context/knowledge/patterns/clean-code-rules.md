# Clean Code Rules

Six rules adapted from NASA JPL's "Power of Ten" (Gerard Holzmann, 2006) for TypeScript, Swift, Kotlin, and Python. These rules are **always active** — every agent must follow them when writing or reviewing code.

Source: Holzmann's original rules target safety-critical C. These adaptations preserve the analytical philosophy (can I prove this code does what I think it does?) while fitting modern managed-language stacks.

---

## Rule 1: Bounded Iteration

**Every loop, retry, poll, and paginated fetch must have an explicit maximum.**

No unbounded iteration. If code can loop, it must have a visible upper bound.

**Applies to:**
- `while` loops — must have a max iteration count or break condition that is provably reachable
- Retry logic — must have `maxRetries` (typically 3-5)
- Polling — must have `maxAttempts` or a timeout
- Pagination — must have `maxPages` or a total limit
- Recursive calls — must have a depth limit or provably terminate
- `for await` streams — must have a consumer-side limit

**Examples:**

Bad:
```typescript
while (!ready) { await check(); }
```

Good:
```typescript
const MAX_ATTEMPTS = 10;
for (let i = 0; i < MAX_ATTEMPTS; i++) {
  if (await check()) break;
  await delay(1000 * Math.pow(2, i));
}
```

Bad:
```swift
func fetchAll(cursor: String?) async throws -> [Item] {
  var items: [Item] = []
  var next = cursor
  while next != nil {
    let page = try await api.fetch(cursor: next)
    items.append(contentsOf: page.items)
    next = page.nextCursor
  }
  return items
}
```

Good:
```swift
func fetchAll(cursor: String?, maxPages: Int = 50) async throws -> [Item] {
  var items: [Item] = []
  var next = cursor
  for _ in 0..<maxPages {
    guard let current = next else { break }
    let page = try await api.fetch(cursor: current)
    items.append(contentsOf: page.items)
    next = page.nextCursor
  }
  return items
}
```

---

## Rule 2: Small Functions

**No function, method, or composable body exceeds 40 lines.**

Long functions cannot be held in working memory during review. They almost certainly do multiple things and should be split.

**How to count:** Lines of logic inside the function body, excluding blank lines and closing braces/brackets. The signature and documentation don't count.

**What to do when a function exceeds 40 lines:**
1. Identify distinct responsibilities within the function
2. Extract each into a named semantic function
3. The original becomes a pragmatic function that composes them

**Platform-specific guidance:**
- **SwiftUI/Compose:** A View/Composable body over 40 lines should extract sub-views
- **React:** A component over 40 lines of JSX should extract sub-components
- **API handlers:** Split validation, business logic, and response formatting

---

## Rule 3: Minimal Scope

**Declare all variables and state at the smallest possible scope.**

The wider the scope, the harder it is to reason about what can read or modify a value.

**Hierarchy (most preferred → least preferred):**
1. Block-scoped (`let`/`const` inside `if`/`for`, local `val`/`var`)
2. Function-scoped (parameters, local variables)
3. Component/class-scoped (`@State`, `StateFlow`, `useState`)
4. Module-scoped (file-level constants)
5. Global/app-scoped (avoid — use dependency injection instead)

**Rules:**
- Never use `var` (JS/TS) — use `const` by default, `let` only when reassignment is needed
- Never use global mutable state — pass values through parameters or dependency injection
- In Swift, prefer `let` over `var`; in Kotlin, prefer `val` over `var`
- State that only one component needs should live in that component, not a parent or store

---

## Rule 4: Validate All Boundaries

**Check every return value at system boundaries. Validate every input from external sources.**

Internal code can trust the type system. But at every boundary where data enters or leaves, validate explicitly.

**System boundaries (must validate):**
- API responses (from external services)
- User input (forms, URL parameters, deep links)
- Database query results (especially nullable joins)
- File system reads
- Environment variables
- Inter-process communication (webhooks, message queues)

**Internal boundaries (trust the type system):**
- Function-to-function calls within the same module
- Component prop passing within the same feature
- Service-to-service within the same process

**How to validate:**
- TypeScript: Zod schemas at API boundaries, strict types internally
- Swift: `guard let` / `Result` types, validate `Codable` decoding
- Kotlin: `sealed class` / `Result<T>`, validate `@Serializable` parsing
- Python: Pydantic models at API boundaries

**Never silently swallow errors:**
```typescript
// Bad — swallows the error
try { await save(data); } catch (e) { /* ignore */ }

// Good — handle or propagate
try {
  await save(data);
} catch (e) {
  logger.error("Failed to save", { error: e, data });
  throw new SaveError("Save failed", { cause: e });
}
```

---

## Rule 5: Simple Control Flow

**Maximum 3 levels of nesting. Use early returns. No unnecessary complexity.**

Code should be readable top-to-bottom without mental stack management.

**Rules:**
- Maximum 3 levels of indentation from the function body
- Use early returns / guard clauses to flatten `if/else` chains
- Prefer `switch`/`when` with exhaustive cases over `if/else if/else if/else`
- Avoid ternary chains (`a ? b : c ? d : e`)
- If a conditional block exceeds 10 lines, extract it into a named function

**Examples:**

Bad (4 levels deep):
```typescript
function process(items: Item[]) {
  for (const item of items) {
    if (item.isActive) {
      if (item.hasPermission) {
        if (item.type === "premium") {
          // deep logic here
        }
      }
    }
  }
}
```

Good (early returns flatten it):
```typescript
function processItem(item: Item) {
  if (!item.isActive) return;
  if (!item.hasPermission) return;
  if (item.type !== "premium") return;
  // logic here, at one level
}

function process(items: Item[]) {
  for (const item of items) {
    processItem(item);
  }
}
```

---

## Rule 6: Zero Warnings

**All linters, type checkers, and static analyzers must pass with zero warnings before code is committed.**

Warnings are future bugs. A zero-warning policy prevents warning blindness where real issues hide in a sea of noise.

**Required tooling by platform:**
- **TypeScript:** `tsc --strict` + ESLint (zero errors, zero warnings)
- **Swift:** SwiftLint (zero violations)
- **Kotlin:** ktlint + Detekt (zero issues)
- **Python:** mypy + ruff (zero errors)

**Rules:**
- Never suppress a warning without a comment explaining why
- Never use `// @ts-ignore`, `// eslint-disable`, `@SuppressWarnings`, `# type: ignore` without justification
- If a warning is a false positive, suppress it with documentation — don't disable the rule globally
- New code must not introduce new warnings in existing files

---

## Quick Reference

| # | Rule | Check |
|---|------|-------|
| 1 | Bounded iteration | Does every loop/retry/poll have a max? |
| 2 | Small functions | Is every function ≤40 lines? |
| 3 | Minimal scope | Is every variable at its smallest possible scope? |
| 4 | Validate boundaries | Are all system boundary inputs validated? |
| 5 | Simple control flow | Is nesting ≤3 levels? Are there early returns? |
| 6 | Zero warnings | Do all linters/analyzers pass clean? |
