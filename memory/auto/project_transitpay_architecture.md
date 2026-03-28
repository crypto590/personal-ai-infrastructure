---
name: TransitPay Platform Architecture
description: Three-service architecture decisions for the TransitPay merchant acquiring platform (CRM + Gateway + Frontend)
type: project
---

TransitPay is a three-service architecture decided 2026-03-24:

1. **Next.js** (`apps/web/`) — Portal UI only, no Server Actions for data mutations
2. **Fastify + Zod** (`apps/api/`) — CRM API for web frontend AND external integrations (ISOs, merchants, software)
3. **Rust / axum** (`gateway/`) — Payment gateway (MPP, TransIT, MMH, Circle)

**Why:** Server Actions can't serve external API consumers. Fastify provides proper REST endpoints, OpenAPI generation, and middleware chain for fintech compliance.

**How to apply:** When building new features, backend logic goes in `apps/api/` (Fastify), not in Next.js Server Actions. Next.js only renders UI and calls the Fastify API via TanStack Query.

Key infra decisions:
- Turborepo monorepo with bun workspaces
- `packages/shared/` for Zod schemas + TS types shared between web and api
- Two Neon PostgreSQL databases (CRM DB + Gateway DB) for PCI scope isolation
- Hosting deferred — building portable containers, evaluating startup credit programs (AWS Activate, GCP for Startups)
- Ports: web=3005, gateway=3100, api=3200, pg=5433, redis=6380
