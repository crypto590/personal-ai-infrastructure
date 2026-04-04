# Memory Index

- [feedback_drizzle_migration_names.md](feedback_drizzle_migration_names.md) — Always use `--name` flag with `drizzle-kit generate` for descriptive migration names
- [project_staging_deployment.md](project_staging_deployment.md) — All APIs merge into single users-api service in staging/production
- [project_transitpay_architecture.md](project_transitpay_architecture.md) — Three-service architecture: Next.js (frontend) + Fastify+Zod (CRM API) + Rust/axum (gateway), Turborepo monorepo
- [reference_fis_mmh.md](reference_fis_mmh.md) — FIS MMH API: UAT sandbox, auth, test harness (21 scenarios), known WireMock issues
- [reference_transit_sandbox.md](reference_transit_sandbox.md) — TransIT API 3.0: sandbox URLs, auth (deviceID+transactionKey), test harness, client rewrite needed
- [reference_circle_sandbox.md](reference_circle_sandbox.md) — Circle Programmable Wallets: RSA-OAEP auth, testnet chains, API path patterns, faucet, test harness
- [reference_anthropic_harness_design.md](reference_anthropic_harness_design.md) — Anthropic harness design: all named patterns (A/B/C), 3-agent roles, sprint contracts, evaluator tuning, anti-patterns, evolution model
- [feedback_use_bun_not_npx.md](feedback_use_bun_not_npx.md) — Always use bun/bunx, never npm/npx in athlead
- [reference_neon_knowledge_base.md](reference_neon_knowledge_base.md) — Neon Postgres agent KB at `context/knowledge/platforms/neon-postgres.md` — MCP tools, branching API, toolkit SDK, CLI, agent patterns
- [feedback_skills_not_nested.md](feedback_skills_not_nested.md) — Skills must be top-level under `~/.claude/skills/`, never nested under category subdirs
