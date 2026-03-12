# Spec: Research Authentication Best Practices for Next.js App Router

> Created: 2026-03-10
> Priority: medium
> Time Limit: 5 minutes

---

## Instructions

**Context:**
We are building a Next.js 15 App Router application and need to implement authentication. The app uses Server Components, Server Actions, and has both public and protected routes. We need to understand the current best practices before writing code.

**Constraints:**
- Focus on Next.js App Router specifically (not Pages Router)
- Prefer library-based solutions over hand-rolled auth
- Must support OAuth providers (Google, GitHub at minimum)
- Must work with server components and middleware

**Approach:**
Start with the official Next.js auth documentation, then evaluate the top 3 auth libraries. Compare trade-offs and provide a recommendation.

---

## Tasks

1. Research Next.js official auth patterns for App Router (middleware, server components, route protection)
2. Evaluate NextAuth.js v5 (Auth.js) — setup complexity, features, limitations
3. Evaluate Clerk and Lucia as alternatives — compare DX, pricing, flexibility
4. Identify the recommended session strategy (JWT vs database sessions) for our use case

---

## Deliverables

**Success looks like:**
- Clear comparison of 3 auth approaches with pros/cons
- A specific recommendation with rationale
- Example code snippets for the recommended approach

**Artifacts to produce:**
- [ ] Comparison table (library, setup effort, features, cost, maintenance)
- [ ] Recommended approach with 2-3 sentence rationale
- [ ] Skeleton middleware.ts showing route protection pattern
- [ ] List of required packages and env vars

---

## Time Limit

**Default: 5 minutes.**

If you are approaching the time limit:
1. Stop working on new tasks
2. Document what you completed and what remains
3. Deliver partial results with a clear status summary
4. List any blockers or decisions that need human input

Do NOT spend time polishing — deliver what you have.
