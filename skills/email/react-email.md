# React Email Templates

Guide for building email templates with React Email in the Athlead turborepo.

---

## Installation

```bash
bun add @react-email/components react-email
```

Add to `package.json` scripts:

```json
{
  "scripts": {
    "email:dev": "email dev",
    "email:export": "email export"
  }
}
```

---

## Basic Template Structure

```tsx
import {
  Html,
  Head,
  Preview,
  Body,
  Container,
  Section,
  Text,
  Button,
  Hr,
  Img,
  Link,
  Tailwind,
} from "@react-email/components";
import { pixelBasedPreset } from "@react-email/components";

interface WelcomeEmailProps {
  userName: string;
  confirmUrl: string;
}

export const WelcomeEmail = ({ userName, confirmUrl }: WelcomeEmailProps) => (
  <Html>
    <Head />
    <Preview>Welcome to Athlead, {userName}!</Preview>
    <Tailwind config={{ presets: [pixelBasedPreset] }}>
      <Body className="bg-white font-sans">
        <Container className="mx-auto max-w-[600px] px-[20px] py-[40px]">
          <Img
            src={`${baseUrl}/static/logo.png`}
            width="120"
            height="40"
            alt="Athlead"
          />
          <Section>
            <Text className="text-[16px] leading-[24px] text-black">
              Hi {userName},
            </Text>
            <Text className="text-[16px] leading-[24px] text-black">
              Welcome to Athlead. Confirm your email to get started.
            </Text>
            <Button
              className="box-border rounded-[8px] bg-black px-[20px] py-[12px] text-[14px] font-semibold text-white"
              href={confirmUrl}
            >
              Confirm Email
            </Button>
          </Section>
          <Hr className="border-solid border-[#eaeaea]" />
          <Text className="text-[12px] text-[#666666]">
            Athlead, Inc. | 123 Main St, City, ST 12345
          </Text>
        </Container>
      </Body>
    </Tailwind>
  </Html>
);

export default WelcomeEmail;
```

---

## Critical Requirements

### pixelBasedPreset (REQUIRED)

Always import and use `pixelBasedPreset` in the Tailwind config. Without it, Tailwind utility classes use `rem` units which break in email clients that ignore `<html>` font-size.

```tsx
import { pixelBasedPreset } from "@react-email/components";

<Tailwind config={{ presets: [pixelBasedPreset] }}>
  {/* template content */}
</Tailwind>
```

### Button Must Use `box-border`

The `<Button>` component requires `box-border` class to render padding correctly across email clients.

```tsx
<Button className="box-border px-[20px] py-[12px] ...">Click</Button>
```

### Hr Must Use `border-solid`

The `<Hr>` component requires explicit `border-solid` to render consistently.

```tsx
<Hr className="border-solid border-[#eaeaea]" />
```

---

## Email Client Limitations

These DO NOT work in email and must be avoided:

| Feature              | Why it fails                        | Alternative                         |
| -------------------- | ----------------------------------- | ----------------------------------- |
| SVG images           | Gmail, Outlook strip SVGs           | Use PNG/JPG                         |
| WEBP images          | Outlook doesn't support WEBP        | Use PNG/JPG                         |
| Flexbox              | Outlook uses Word rendering engine  | Use tables (React Email handles)    |
| CSS Grid             | No email client support             | Use tables                          |
| Media queries        | Gmail strips `<style>` tags         | Use inline styles (Tailwind does)   |
| Dark mode selectors  | Inconsistent support                | Design for both light/dark manually |
| CSS variables        | No support                          | Use literal values                  |
| `position: absolute` | No support in Outlook               | Use table-based layout              |
| Web fonts            | Inconsistent loading                | Use system font stacks              |
| `max-width` on img   | Outlook ignores                     | Use `width` attribute               |

### Safe Design Patterns

- Use `<Container>` with `max-w-[600px]` for layout width
- Use `<Section>` for grouping content blocks
- Use `<Row>` and `<Column>` for multi-column layouts (table-based)
- Stick to system fonts: Arial, Helvetica, Georgia, Times New Roman
- All images must have `width` and `height` attributes
- Use PNG for logos, JPG for photos
- Keep total email size under 100KB for fast loading

---

## Static Files

Place static assets (images, logos) in the `emails/static/` directory.

### URL Pattern

```tsx
// Development
const baseUrl = "http://localhost:3000";

// Production
const baseUrl = "https://athlead.com";

// Pattern used in templates
const baseUrl = process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : "http://localhost:3000";
```

### Image Usage

```tsx
<Img
  src={`${baseUrl}/static/logo.png`}
  width="120"
  height="40"
  alt="Athlead"
/>
```

---

## Rendering to HTML and Plain Text

```tsx
import { render } from "@react-email/components";
import { WelcomeEmail } from "./emails/welcome";

// Render to HTML
const html = await render(<WelcomeEmail userName="Alice" confirmUrl="..." />);

// Render to plain text
const text = await render(
  <WelcomeEmail userName="Alice" confirmUrl="..." />,
  { plainText: true }
);
```

### Sending via Resend

```tsx
import { Resend } from "resend";
import { WelcomeEmail } from "./emails/welcome";

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: "Athlead <noreply@athlead.com>",
  to: user.email,
  subject: "Welcome to Athlead!",
  react: <WelcomeEmail userName={user.name} confirmUrl={confirmUrl} />,
});
```

Note: When using `react` prop, Resend renders the component server-side. You can also pass pre-rendered `html` and `text` props instead.

---

## PreviewProps Pattern

Use `PreviewProps` to provide default data for the React Email dev server preview.

```tsx
import type { PreviewProps } from "@react-email/components";

// ... component definition ...

WelcomeEmail.PreviewProps = {
  userName: "Jane Doe",
  confirmUrl: "https://athlead.com/confirm?token=abc123",
} satisfies PreviewProps<typeof WelcomeEmail>;

export default WelcomeEmail;
```

This lets you run `bun email:dev` and see the template with realistic data without needing a database or API connection.

---

## Template Organization

```
packages/email/
├── emails/
│   ├── static/           # Images, logos (PNG/JPG only)
│   │   ├── logo.png
│   │   └── hero.jpg
│   ├── welcome.tsx       # Welcome / confirm email
│   ├── password-reset.tsx
│   ├── order-confirmation.tsx
│   ├── newsletter.tsx
│   └── components/       # Shared email components
│       ├── footer.tsx
│       ├── header.tsx
│       └── button.tsx
├── package.json
└── tsconfig.json
```

### Shared Components

Extract repeated patterns into shared components:

```tsx
// emails/components/footer.tsx
export const EmailFooter = () => (
  <>
    <Hr className="border-solid border-[#eaeaea]" />
    <Text className="text-[12px] text-[#666666]">
      Athlead, Inc. | 123 Main St, City, ST 12345
    </Text>
    <Link href="{{unsubscribe}}" className="text-[12px] text-[#666666]">
      Unsubscribe
    </Link>
  </>
);
```

---

## Testing Emails

1. **Visual preview:** `bun email:dev` opens browser preview
2. **Send test:** Use Resend dashboard "Send Test" or a test script
3. **Cross-client testing:** Use Litmus or Email on Acid
4. **Key clients to test:** Gmail (web + mobile), Apple Mail, Outlook (desktop + web)
5. **Check plain text version:** Ensure it reads well without formatting
