---
name: email
effort: high
description: "Unified email: deliverability (SPF/DKIM/DMARC), React Email templates, Resend API, compliance (CAN-SPAM/GDPR/CASL), and list management."
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Email Skill — Routing Hub

This skill covers everything email-related for the Athlead platform. Use the routing table below to find the right sub-file for your task.

---

## Quick Routing Table

| Need to...                                      | Read this file         |
| ------------------------------------------------ | ---------------------- |
| Set up SPF/DKIM/DMARC records                   | `best-practices.md`   |
| Fix deliverability / spam issues                 | `best-practices.md`   |
| Understand transactional vs marketing email      | `best-practices.md`   |
| Handle CAN-SPAM / GDPR / CASL compliance        | `best-practices.md`   |
| Implement double opt-in flow                     | `best-practices.md`   |
| Set up webhook handling and retry logic          | `best-practices.md`   |
| Manage suppression lists                         | `best-practices.md`   |
| Build an email template with React Email         | `react-email.md`      |
| Understand email client rendering limitations    | `react-email.md`      |
| Use Tailwind in email templates                  | `react-email.md`      |
| Render email to HTML / plain text                | `react-email.md`      |
| Use PreviewProps for template development        | `react-email.md`      |
| Send email via Resend SDK                        | `resend.md`           |
| Set up Resend API keys                           | `resend.md`           |
| Configure inbound email processing               | `resend.md`           |
| Manage Resend domains and audiences              | `resend.md`           |

---

## Architecture Context (Athlead)

- **Stack:** Turborepo + Next.js 16 + Fastify 5 + Drizzle/PostgreSQL
- **Package manager:** bun (preferred)
- **Email templates:** React Email (shared package in turborepo)
- **Email provider:** Resend
- **Mobile clients:** Swift/SwiftUI + Kotlin/Compose (trigger emails via API)

### Email Flow Overview

```
Client (Web/iOS/Android)
  → API (Fastify route handler)
    → Validation (Zod schema)
      → Email service (Resend SDK)
        → Delivery → Webhooks → Status update (Drizzle/PG)
```

---

## Sub-File Summaries

### best-practices.md
Architecture patterns, authentication (SPF/DKIM/DMARC), deliverability optimization, compliance requirements, webhook handling, list management, and double opt-in flows.

### react-email.md
Building email templates with React Email components, Tailwind integration, email client limitations, static assets, rendering pipeline, and PreviewProps development workflow.

### resend.md
Resend platform integration including SDK setup, API key management, sending transactional and marketing email, inbound email processing, domain configuration, and audience management.

---

## Decision Guide

- **Starting a new email feature?** Read `best-practices.md` first for architecture, then `react-email.md` for templates, then `resend.md` for sending.
- **Debugging delivery issues?** Start with `best-practices.md` (deliverability section).
- **Just need to send an email?** Go straight to `resend.md`.
- **Building a template?** Go straight to `react-email.md`.
