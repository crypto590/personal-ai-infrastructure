# TypeScript Review Checklist

Apply this checklist to all changed `.ts`, `.tsx`, `.js`, `.jsx` files.

## Zod Validation

- [ ] Every external input (API request body, query params, webhook payload) has a Zod schema
- [ ] Zod schemas match OpenAPI spec (contract-first development)
- [ ] Error messages are user-friendly, not raw Zod errors exposed to clients
- [ ] No `.passthrough()` on external input schemas (prevents unexpected fields leaking through)
- [ ] Zod schemas are colocated with their routes or in a shared `schemas/` directory
- [ ] `.transform()` and `.refine()` are used correctly with proper error messages

## Drizzle ORM

- [ ] **N+1 detection:** queries inside loops should use `.with()` or batch queries instead
- [ ] Missing `.returning()` on INSERT/UPDATE when the result is used downstream
- [ ] No raw SQL without parameterized values (SQL injection risk)
- [ ] Missing indexes for frequently queried columns (check WHERE/JOIN/ORDER BY clauses)
- [ ] Transaction usage for multi-table mutations (`.transaction()` wrapping related writes)
- [ ] Proper use of `.onConflict()` for upsert operations
- [ ] Select only needed columns instead of `select *` equivalent

## Fastify

- [ ] Handler type correctness: `protectedHandler` vs `publicHandler` vs `onboardingHandler`
- [ ] Schema validation on route definition (Fastify `schema` option for request/response)
- [ ] Error responses use consistent error format across all handlers
- [ ] No synchronous blocking operations in async handlers
- [ ] Proper use of Fastify lifecycle hooks (preHandler, onSend, etc.)
- [ ] Route prefixing and organization follows service boundaries

## Next.js / React

- [ ] `"use client"` directive placed as deep as possible in the component tree, not at page level
- [ ] Server Component serialization: no functions, classes, or non-serializable values in props passed to client components
- [ ] Server-only imports (`server-only` package) not leaked to client bundles
- [ ] `key` prop on lists uses stable identifiers, not array index for dynamic lists
- [ ] No unnecessary `useEffect` — prefer derived state and event handlers
- [ ] `Suspense` boundaries around async server components and lazy-loaded client components
- [ ] Reference `vercel-react-best-practices` skill for additional performance checks (bundle size, rendering, data fetching)

## Auth (Clerk)

- [ ] `auth()` called on all protected routes and API endpoints
- [ ] Role/permission checks for sensitive operations (admin actions, data deletion, user management)
- [ ] Session token not exposed to client-side JavaScript unnecessarily
- [ ] Middleware configured to protect route groups correctly
- [ ] Webhook signature verification for Clerk webhooks

## BFF Pattern

- [ ] Client components never call microservices directly — all requests go through BFF/API routes
- [ ] Microservices never import from each other — each service is independently deployable
- [ ] API routes aggregate data from multiple services when needed (no client-side orchestration)
- [ ] Service-to-service communication uses internal network, not public endpoints

## Contract Integrity

- [ ] Zod schemas and API response types match (no drift between validation and types)
- [ ] OpenAPI spec updated when routes change (new endpoints, changed parameters, modified responses)
- [ ] Type generation is up to date (`npm run generate` or equivalent has been run)
- [ ] Breaking changes are versioned (new API version, not in-place modification)
- [ ] Shared types between packages are properly exported from the shared package
