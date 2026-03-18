# Resend Platform

Integration guide for Resend email platform in the Athlead stack.

---

## API Key Setup

1. Create an API key in the [Resend Dashboard](https://resend.com/api-keys)
2. Store in environment: `RESEND_API_KEY`
3. Use separate keys for development and production
4. Restrict production keys to specific domains

```bash
# .env.local (never commit)
RESEND_API_KEY=re_xxxxxxxxxxxx
```

---

## SDK Installation

```bash
bun add resend
```

---

## Quick Routing Guide

| Task                              | Sub-skill / Section     |
| --------------------------------- | ----------------------- |
| Send a transactional email        | send-email              |
| Send a marketing/batch email      | send-email (batch)      |
| Process inbound email             | resend-inbound          |
| Build an AI-powered email inbox   | agent-email-inbox       |
| Create/manage email templates     | templates               |
| Manage domains                    | domain-management       |
| Manage audiences/contacts         | audience-management     |

---

## send-email

### Single Email

```tsx
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

const { data, error } = await resend.emails.send({
  from: "Athlead <noreply@athlead.com>",
  to: ["user@example.com"],
  subject: "Welcome to Athlead",
  react: <WelcomeEmail userName="Alice" />,
  // OR use pre-rendered:
  // html: "<html>...</html>",
  // text: "Plain text version",
});

if (error) {
  console.error("Email send failed:", error);
  // Handle error — log, retry, or alert
}
```

### Batch Emails

```tsx
const { data, error } = await resend.batch.send([
  {
    from: "Athlead <team@mail.athlead.com>",
    to: ["user1@example.com"],
    subject: "Weekly Update",
    react: <NewsletterEmail />,
  },
  {
    from: "Athlead <team@mail.athlead.com>",
    to: ["user2@example.com"],
    subject: "Weekly Update",
    react: <NewsletterEmail />,
  },
]);
```

### Send Options

| Option        | Description                           |
| ------------- | ------------------------------------- |
| `from`        | Sender address (must be verified domain) |
| `to`          | Recipient(s) — string or array        |
| `cc`          | CC recipients                         |
| `bcc`         | BCC recipients                        |
| `reply_to`    | Reply-to address                      |
| `subject`     | Email subject line                    |
| `react`       | React Email component                 |
| `html`        | Raw HTML string                       |
| `text`        | Plain text version                    |
| `headers`     | Custom email headers                  |
| `attachments` | File attachments                      |
| `tags`        | Key-value tags for tracking           |
| `scheduled_at`| Schedule send (ISO 8601 datetime)     |

---

## resend-inbound

Process incoming emails with Resend's inbound feature.

### Setup

1. Add MX record pointing to Resend: `inbound.resend.com` (priority 10)
2. Configure inbound webhook in Resend dashboard
3. Set webhook URL: `POST /api/webhooks/resend/inbound`

### Webhook Payload

```tsx
// Fastify route handler
app.post("/api/webhooks/resend/inbound", async (request, reply) => {
  const { from, to, subject, html, text, attachments } = request.body;

  // Process inbound email
  // - Parse content
  // - Store in database
  // - Trigger automations

  return reply.status(200).send({ received: true });
});
```

---

## agent-email-inbox

Pattern for AI-powered email processing.

### Architecture

```
Inbound Email → Resend Webhook
  → Parse & classify (AI)
    → Route to handler
      → Auto-reply / Escalate / Archive
        → Log action (Drizzle → PG)
```

### Use Cases

- Support ticket creation from inbound email
- Auto-classification (support, billing, spam)
- AI-drafted responses for review
- Escalation rules based on content/sender

---

## templates

### Managing Templates via Code

Keep templates in the codebase as React Email components (see `react-email.md`). This gives you:

- Version control for all templates
- Type safety with TypeScript
- Preview with `bun email:dev`
- Shared components across templates

### Template Variables

Use component props for dynamic content:

```tsx
interface OrderEmailProps {
  orderNumber: string;
  items: Array<{ name: string; price: number }>;
  total: number;
}
```

---

## domain-management

### Adding a Domain

1. Go to Resend Dashboard > Domains
2. Add your domain (e.g., `athlead.com`)
3. Add the DNS records Resend provides (SPF, DKIM, DMARC)
4. Wait for verification (24-72 hours)

### Recommended Domain Strategy

| Domain              | Purpose              |
| ------------------- | -------------------- |
| `athlead.com`       | Transactional email  |
| `mail.athlead.com`  | Marketing email      |

Separate domains protect transactional deliverability from marketing reputation.

---

## audience-management

### Creating Audiences

```tsx
const { data } = await resend.audiences.create({
  name: "Newsletter Subscribers",
});
```

### Managing Contacts

```tsx
// Add contact
await resend.contacts.create({
  audience_id: "aud_xxxx",
  email: "user@example.com",
  first_name: "Alice",
  unsubscribed: false,
});

// Remove contact
await resend.contacts.remove({
  audience_id: "aud_xxxx",
  email: "user@example.com",
});
```

---

## Error Handling

### Common Errors

| Error Code           | Meaning                    | Action                    |
| -------------------- | -------------------------- | ------------------------- |
| `validation_error`   | Invalid request payload    | Fix request data          |
| `missing_required_field` | Required field missing | Add missing field         |
| `rate_limit_exceeded`| Too many requests          | Implement backoff         |
| `not_found`          | Resource doesn't exist     | Check ID/domain           |

### Retry Strategy

```tsx
async function sendWithRetry(emailData: SendEmailParams, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const { data, error } = await resend.emails.send(emailData);
    if (data) return data;
    if (error && attempt < maxRetries) {
      await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
      continue;
    }
    throw new Error(`Email send failed after ${maxRetries} attempts: ${error}`);
  }
}
```

---

## Useful Links

- [Resend Documentation](https://resend.com/docs)
- [Resend API Reference](https://resend.com/docs/api-reference)
- [Resend SDK (npm)](https://www.npmjs.com/package/resend)
- [React Email Docs](https://react.email/docs)
- [Resend Dashboard](https://resend.com/overview)
