# Email Best Practices

Comprehensive guide covering architecture, deliverability, authentication, compliance, and operational patterns for the Athlead email system.

---

## Architecture Overview

### End-to-End Email Flow

```
User → Form → Client Validation (Zod)
  → API (Fastify) → Server Validation (Zod)
    → Double Opt-In Check
      → Email Service (Resend SDK)
        → Delivery Attempt
          → Webhook (delivered/bounced/complained)
            → Status Update (Drizzle → PostgreSQL)
              → Suppression List Update (if bounce/complaint)
```

### Key Principles

- **Never send without validation** — Zod schemas on both client and server
- **Double opt-in for marketing** — Required by GDPR, best practice everywhere
- **Transactional emails skip opt-in** — Password resets, order confirmations, etc.
- **Webhook-driven status** — Never assume delivery; track via webhooks
- **Suppression is permanent** — Once bounced/complained, never send again without explicit re-opt-in

---

## SPF / DKIM / DMARC Setup

### SPF (Sender Policy Framework)

- Add a TXT record to your DNS: `v=spf1 include:resend.com ~all`
- Only one SPF record per domain (merge if needed)
- Use `~all` (soft fail) during testing, move to `-all` (hard fail) in production
- Check with: `dig TXT yourdomain.com`

### DKIM (DomainKeys Identified Mail)

- Resend provides DKIM keys during domain verification
- Add the CNAME records Resend provides to your DNS
- Typically 3 CNAME records for key rotation
- Verification takes 24-72 hours

### DMARC (Domain-based Message Authentication)

- Add TXT record: `v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com`
- Start with `p=none` (monitor only), then `p=quarantine`, then `p=reject`
- Monitor DMARC reports before tightening policy
- Recommended production policy: `v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@yourdomain.com`

### Verification Checklist

1. SPF record exists and includes Resend
2. DKIM CNAME records added and verified in Resend dashboard
3. DMARC record exists with at least `p=none`
4. Test with mail-tester.com (aim for 9+/10)
5. Check headers on received emails for `pass` on SPF, DKIM, DMARC

---

## Deliverability Best Practices

### Sender Reputation

- Use a subdomain for marketing email (e.g., `mail.athlead.com`)
- Keep transactional on the primary domain or a separate subdomain
- Warm up new domains: start with 50/day, double weekly
- Monitor bounce rate (keep under 2%) and complaint rate (keep under 0.1%)

### Content Guidelines

- Avoid spam trigger words in subject lines
- Maintain a healthy text-to-image ratio (at least 60% text)
- Always include a plain text version
- Personalize where possible (improves engagement)
- Keep subject lines under 50 characters for mobile

### List Hygiene

- Remove hard bounces immediately (automated via webhooks)
- Remove soft bounces after 3 consecutive failures
- Re-engagement campaign for inactive subscribers (90+ days)
- Sunset policy: remove unengaged after 180 days
- Never purchase email lists

---

## Transactional vs Marketing Email

### Transactional Email

- Triggered by user action (signup, purchase, password reset)
- Does NOT require opt-in or unsubscribe link
- Must be timely (send within seconds)
- Examples: welcome email, password reset, order confirmation, receipt
- Send from: `noreply@athlead.com` or `support@athlead.com`

### Marketing Email

- Sent to promote products, features, or content
- REQUIRES opt-in consent and unsubscribe link
- Can be batched/scheduled
- Examples: newsletter, product updates, promotions, re-engagement
- Send from: `team@mail.athlead.com` (subdomain)
- Must include physical mailing address

### Hybrid Emails

- Some emails blur the line (e.g., "Your trial is ending" with an upsell)
- Rule of thumb: if the primary purpose is promotional, treat as marketing
- When in doubt, include unsubscribe link

---

## Compliance

### CAN-SPAM (United States)

- Accurate "From" and "Reply-To" headers
- Non-deceptive subject lines
- Identify message as advertisement (marketing only)
- Include physical mailing address
- Honor opt-out within 10 business days
- No purchased lists

### GDPR (European Union)

- Explicit consent required (no pre-checked boxes)
- Double opt-in recommended (required in some EU countries)
- Right to erasure — delete all data on request
- Data processing agreement with Resend
- Record consent: timestamp, IP, method, exact language shown
- Privacy policy must describe email data usage

### CASL (Canada)

- Express consent required for marketing
- Implied consent expires after 2 years (existing business relationship)
- Include sender identification and contact info
- Unsubscribe mechanism must work for 60 days after sending

### Implementation Checklist

- [ ] Consent recorded in database (timestamp, IP, method)
- [ ] Unsubscribe link in every marketing email
- [ ] Unsubscribe works within 1 click (no login required)
- [ ] Physical address in marketing email footer
- [ ] Privacy policy covers email data usage
- [ ] Data deletion endpoint handles email records

---

## Webhook Handling

### Setup

- Register webhook endpoint in Resend dashboard
- Endpoint: `POST /api/webhooks/resend`
- Verify webhook signature using Resend's signing secret

### Event Types to Handle

| Event                | Action                                    |
| -------------------- | ----------------------------------------- |
| `email.sent`         | Log send timestamp                        |
| `email.delivered`    | Update status to delivered                |
| `email.opened`       | Track engagement (marketing only)         |
| `email.clicked`      | Track engagement (marketing only)         |
| `email.bounced`      | Add to suppression list, log reason       |
| `email.complained`   | Add to suppression list immediately       |
| `email.unsubscribed` | Update preferences, stop marketing emails |

### Retry Logic

- Resend retries failed webhooks automatically
- Your endpoint must be idempotent (use event ID for dedup)
- Return 200 quickly — process asynchronously if needed
- Store raw webhook payload for debugging
- Implement dead letter queue for processing failures

### Idempotency Pattern

```
1. Receive webhook
2. Check event ID in processed_events table
3. If exists → return 200 (already processed)
4. If not → process event, insert event ID, return 200
5. Wrap in transaction
```

---

## List Management and Suppression

### Suppression List

- Maintained in PostgreSQL via Drizzle schema
- Check suppression list BEFORE every send
- Sources: hard bounces, complaints, manual unsubscribes
- Fields: email, reason, source_event_id, created_at
- Never delete from suppression — only add

### Audience Segmentation

- Use Resend Audiences for marketing lists
- Sync segments from your database to Resend
- Tags: user type, signup source, engagement level, preferences

### Double Opt-In Flow

```
1. User submits email → store with status "pending"
2. Send confirmation email with unique token (expires 24h)
3. User clicks confirm link → status "confirmed"
4. Only send marketing to "confirmed" contacts
5. Log confirmation: timestamp, IP, user agent
```

---

## Email Capture Patterns

### Form Best Practices

- Single email field + submit button for maximum conversion
- Client-side format validation (Zod)
- Server-side validation + duplicate check
- Rate limit submissions (5 per IP per hour)
- Honeypot field for bot prevention (hidden field that should remain empty)

### Confirmation Page

- Show "Check your inbox" message
- Include spam folder reminder
- Offer resend option (rate limited)
- No auto-redirect — let user read the message
