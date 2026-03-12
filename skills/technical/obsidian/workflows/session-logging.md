# Session Logging Workflow

## Purpose

Capture decisions, outcomes, and learnings from Claude Code sessions into Obsidian. Creates a persistent record of what was done, why, and what comes next.

## When to Use

- After completing a task or subtask
- After making a significant architectural or design decision
- At the end of a work session
- When a decision has important rationale worth preserving

## Patterns

### 1. Daily Note Append

Add a session summary to today's daily note. Best for general session tracking.

```bash
obsidian vault=The_Hub daily:append content="\n## Session: Auth Refactor (14:30)\n\n> [!summary] Outcome\n> Migrated authentication from session-based to JWT tokens.\n\n- **Decision:** JWT with refresh tokens over session cookies\n- **Rationale:** Better mobile support, stateless backend\n- **Files changed:** `auth.ts`, `middleware.ts`, `login.tsx`\n- **Tests:** All passing (47/47)\n- **Next:** Implement token refresh endpoint\n\n#session/dev #project/backend"
```

### 2. Project Note Append

Add outcomes to a specific project page. Best for project-scoped tracking.

```bash
# First, verify the project note exists
obsidian vault=The_Hub read file="Project Alpha"

# Append the update
obsidian vault=The_Hub append file="Project Alpha" content="\n## Update: 2025-11-15\n\n> [!done] Completed\n> JWT authentication implementation.\n\n- Replaced session middleware with JWT validation\n- Added [[Token Refresh]] endpoint design\n- Unblocked: [[API Gateway]] integration\n\n### Open Questions\n- Token expiry duration (currently 15min)\n- Refresh token rotation policy"
```

### 3. Decision Log

Create or append to a dedicated decisions file. Best for decisions that need to be findable later.

```bash
# Append a structured decision entry
obsidian vault=The_Hub append file="Decision Log" content="\n---\n\n### DEC-042: JWT Over Session Cookies\n\n| Field | Value |\n|-------|-------|\n| Date | 2025-11-15 |\n| Status | Accepted |\n| Context | [[Project Alpha]] auth system |\n| Decider | Team consensus |\n\n**Context:** Mobile clients need stateless auth. Session cookies require sticky sessions on the load balancer.\n\n**Decision:** Use JWT access tokens (15min) with rotating refresh tokens (7d).\n\n**Consequences:**\n- (+) Stateless backend, horizontal scaling\n- (+) Works natively on mobile\n- (-) Token revocation requires deny-list\n- (-) Larger request headers\n\n**Related:** [[Auth Architecture]], [[API Security]]\n\n#decision #architecture #auth"
```

## Combined Example

After implementing a feature, log to both daily note and project note:

```bash
# 1. Append summary to daily note
obsidian vault=The_Hub daily:append content="\n## Session: Payment Integration (16:00)\n- Implemented Stripe checkout flow\n- See [[Payments Project]] for details\n#session/dev"

# 2. Append details to project note
obsidian vault=The_Hub append file="Payments Project" content="\n## 2025-11-15: Stripe Checkout\n\n> [!success] Milestone Complete\n> Checkout flow working end-to-end in staging.\n\n- Integrated Stripe Checkout Sessions API\n- Added webhook handler for `checkout.session.completed`\n- Error handling with retry logic (3 attempts, exponential backoff)\n- [[Stripe Webhook Secrets]] stored in env vars\n\n### Remaining\n- [ ] Add subscription support\n- [ ] Handle failed payments\n- [ ] Add invoice generation"
```

## Formatting Tips

- Use `> [!summary]`, `> [!done]`, `> [!warning]` callouts for visual structure
- Add `#session/dev`, `#decision`, `#project/name` tags for discoverability
- Use `[[wikilinks]]` to connect to related notes
- Include timestamps in headings for chronological scanning
- Keep entries scannable: bold key terms, use lists over paragraphs
