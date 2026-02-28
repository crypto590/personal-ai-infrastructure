---
name: react-best-practices
description: Vercel's 45 React/Next.js performance optimization rules across 8 categories. USE WHEN writing React components, reviewing code for performance, optimizing bundle size, fixing async waterfalls, or building Chrome extensions with React. NOT for Swift/iOS, Kotlin/Android, or backend-only Node.js projects.
source: https://github.com/vercel-labs/agent-skills
version: 1.0.0
metadata:
  author: vercel-labs
  version: 1.0.0
  category: technical
  tags: [react, nextjs, performance, frontend, optimization, vercel]
---

# React Best Practices (Vercel Engineering)

## When to Activate This Skill

- Writing new React components
- Reviewing React code for performance issues
- Optimizing bundle size (especially for Chrome extensions)
- Fixing async/await waterfalls
- Client-side data fetching patterns
- Re-render optimization
- Code review for React projects

## Priority Categories (by Impact)

| Priority | Category | Rules | Key Focus |
|----------|----------|-------|-----------|
| CRITICAL | Eliminating Waterfalls | 5 | `Promise.all()`, defer await |
| CRITICAL | Bundle Size | 5 | Direct imports, dynamic loading |
| HIGH | Server-Side Performance | 7 | Auth, caching, RSC boundaries |
| MEDIUM-HIGH | Client-Side Data Fetching | 4 | SWR, deduplication |
| MEDIUM | Re-render Optimization | 7 | State, memoization |
| MEDIUM | Rendering Performance | 7 | CSS, Suspense, hydration |
| LOW-MEDIUM | JavaScript Performance | 12 | Loops, caching, Maps |
| LOW | Advanced Patterns | 2 | Refs, stable callbacks |

## Critical Rules Summary

### 1. Waterfalls (CRITICAL)

**Always parallelize independent operations:**
```typescript
// BAD: Sequential (3 round trips)
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()

// GOOD: Parallel (1 round trip)
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments()
])
```

**Defer await until needed:**
```typescript
// BAD: Blocks both branches
async function handle(skip: boolean) {
  const data = await fetchData()
  if (skip) return { skipped: true }
  return processData(data)
}

// GOOD: Only await when needed
async function handle(skip: boolean) {
  if (skip) return { skipped: true }
  const data = await fetchData()
  return processData(data)
}
```

### 2. Bundle Size (CRITICAL)

**Direct imports over barrel files:**
```typescript
// BAD: Imports entire library (200-800ms cost)
import { Check, X } from 'lucide-react'

// GOOD: Direct imports only
import Check from 'lucide-react/dist/esm/icons/check'
import X from 'lucide-react/dist/esm/icons/x'
```

**Dynamic imports for heavy components:**
```typescript
import dynamic from 'next/dynamic'

const HeavyEditor = dynamic(
  () => import('./monaco-editor'),
  { ssr: false }
)
```

### 3. Re-render Optimization (MEDIUM)

**Functional setState updates:**
```typescript
// BAD: Requires state as dependency
const addItem = useCallback((item) => {
  setItems([...items, item])
}, [items])

// GOOD: Stable callback, no dependencies
const addItem = useCallback((item) => {
  setItems(curr => [...curr, item])
}, [])
```

**Lazy state initialization:**
```typescript
// BAD: Runs every render
const [data] = useState(expensiveComputation())

// GOOD: Runs only once
const [data] = useState(() => expensiveComputation())
```

### 4. JavaScript Performance (LOW-MEDIUM)

**Use Set/Map for O(1) lookups:**
```typescript
// BAD: O(n) per check
items.filter(item => allowedIds.includes(item.id))

// GOOD: O(1) per check
const allowedSet = new Set(allowedIds)
items.filter(item => allowedSet.has(item.id))
```

**Use toSorted() for immutability:**
```typescript
// BAD: Mutates original
const sorted = users.sort((a, b) => a.name.localeCompare(b.name))

// GOOD: Creates new array
const sorted = users.toSorted((a, b) => a.name.localeCompare(b.name))
```

## Chrome Extension Relevance

For StreakFlow and similar Chrome extensions:
- **Bundle size is critical** - affects load time in extension popup
- **Client-side focus** - Server-side rules less relevant
- **Re-render optimization** - Important for responsive UI
- **Event listener deduplication** - Content scripts need this

## Full Reference

For complete 45 rules with detailed examples:
```
read /Users/coreyyoung/.claude/skills/technical/react-best-practices/AGENTS.md
```

## Source

Vercel Engineering, January 2026
https://github.com/vercel-labs/agent-skills
