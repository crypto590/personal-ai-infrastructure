---
name: qa
effort: high
argument-hint: "[fix | report]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
description: "Multi-platform QA with health scoring. Two modes: fix (atomic commits) and report. Covers build, types, tests, lint, security, performance, accessibility."
metadata:
  last_reviewed: 2026-03-20
  review_cycle: 90
---

# QA — Multi-Platform Quality Assurance

Multi-platform quality assurance with weighted health scoring across 8 categories.
Produces a scored health report and optionally fixes issues with atomic commits.

---

## Modes

### `/qa fix` (default)

Find issues and fix them with atomic commits. Each fix gets its own commit for easy revert.

### `/qa report`

Report only. No files are modified, no commits are created. Produces a scored health report.

If the user does not specify a mode, default to **fix**.

---

## Prerequisites

Before starting any QA run:

1. **Verify clean working tree:**
   ```bash
   git status --porcelain
   ```
   - If output is non-empty, **STOP** and ask the user to commit or stash changes first.
   - A clean working tree is required so that QA fixes are isolated and revertable.

2. **Detect project platforms:**
   - Check for `apps/web` or Next.js config → Web platform
   - Check for `*.xcodeproj` or `Package.swift` → iOS platform
   - Check for `build.gradle.kts` or Android manifest → Android platform
   - Run checks only for detected platforms.

---

## 8-Category Health Scoring

Each category is scored 0–100. The overall score is a weighted sum.

### Category 1: Build Health (Weight: 15%)

**Checks:**
- Run `turbo run build` across all workspace packages.
- Verify all packages compile without errors.
- Check for build warnings (deduct 2 points per warning, up to 20 points).

**Scoring:**
- 100: Clean build, zero errors, zero warnings.
- Deduct 50 points per build error.
- Deduct 2 points per build warning.
- Minimum score: 0.

**Fix mode:** Build errors cannot be auto-fixed safely. Report them and ask the user.

---

### Category 2: Type Safety (Weight: 15%)

**Checks:**
- Run `turbo run check-types` (TypeScript strict mode).
- Scan for `any` type usage — each explicit `any` deducts 1 point (up to 30 points).
- Verify Zod schemas cover all external data inputs (API responses, form data, env vars).
- **Brand type audit:** Scan for domain IDs passed as bare `string` or `number` where branded/nominal types would prevent cross-domain bugs (e.g., `userId: string` vs `userId: UserId`). Deduct 1 point per unbranded domain ID in function signatures (up to 10 points).
- **Model coherence:** Flag models with 3+ optional fields only set in specific contexts — signal to split into distinct types. Flag models where field names don't cohere around the model name (e.g., `phone_number` on `BillingAddress`). Deduct 2 points per incoherent model (up to 10 points).

**Scoring:**
- 100: Zero TypeScript errors, minimal `any` usage, Zod coverage on external inputs, branded domain IDs, coherent models.
- Deduct 10 points per type error.
- Deduct 1 point per `any` usage.
- Deduct 5 points per unvalidated external input.
- Deduct 1 point per unbranded domain ID in function signatures (up to 10).
- Deduct 2 points per incoherent model (up to 10).

**Fix mode:**
- Replace `any` with proper types where inference is possible.
- Add Zod schemas for unvalidated external inputs.
- Add branded type definitions for domain IDs where missing (report only — don't auto-fix existing call sites).
- Report incoherent models with split recommendation (report only — structural changes require human decision).
- Commit: `fix(qa): [type-safety] replace any with proper types in <file>`

---

### Category 3: Test Coverage (Weight: 15%)

**Checks:**
- Run `turbo run test` and collect results.
- Check pass/fail ratio.
- Scan for skipped tests (`.skip`, `xit`, `xdescribe`, `@Disabled`).
- Verify critical paths have test coverage (auth flows, payment, data mutations).

**Scoring:**
- 100: All tests pass, no skipped tests without justification.
- Deduct 5 points per failing test.
- Deduct 2 points per unjustified skipped test.
- Deduct 10 points if critical paths lack tests (reported, not auto-fixed).

**Fix mode:**
- Remove `.skip` from tests that should be running (if the test passes when unskipped).
- Do NOT auto-generate new tests — report missing coverage instead.
- Commit: `fix(qa): [test-coverage] unskip passing test in <file>`

---

### Category 4: Lint Compliance (Weight: 10%)

**Checks — per platform:**

**Web (TypeScript):**
- Run `turbo run lint` (ESLint).
- Count errors and warnings separately.

**iOS (Swift):**
- Reference `ios-swift/quality/checks.md` for SwiftLint configuration and rules.
- Run SwiftLint if available.

**Android (Kotlin):**
- Reference `kotlin-android/quality/checks.md` for ktlint and Detekt configuration.
- Run ktlint and Detekt if available.

**Scoring:**
- 100: Zero lint errors across all platforms.
- Deduct 5 points per lint error.
- Deduct 1 point per lint warning (up to 20 points).

**Fix mode:**
- Run auto-fix where available (`eslint --fix`, `swiftlint autocorrect`, `ktlint -F`).
- Commit: `fix(qa): [lint] auto-fix lint issues in <scope>`

---

### Category 5: Security (Weight: 15%)

**Checks:**

1. **Secret scanning:** Scan for hardcoded API keys, tokens, passwords, connection strings.
   - Patterns: `API_KEY=`, `SECRET=`, `PASSWORD=`, `Bearer `, `sk-`, `pk_`, base64-encoded credentials.
   - Check `.env` files are gitignored.

2. **Auth protection:** Verify protected API endpoints have auth middleware.
   - Fastify routes with sensitive data should have `onRequest` or `preHandler` auth hooks.

3. **SQL injection:** Verify all database queries use Drizzle ORM (parameterized).
   - Flag any raw SQL strings with string interpolation.

4. **XSS vectors:** Scan for `dangerouslySetInnerHTML` without sanitization.
   - Flag any usage that doesn't pass through DOMPurify or equivalent.

5. **Dependency vulnerabilities:** Check for known vulnerabilities.
   - Run `npm audit` or `bun audit` if available.

**Scoring:**
- 100: No secrets exposed, auth on all protected routes, no injection vectors.
- Deduct 25 points per exposed secret.
- Deduct 15 points per unprotected sensitive endpoint.
- Deduct 20 points per SQL injection vector.
- Deduct 10 points per unsanitized XSS vector.
- Deduct 5 points per known dependency vulnerability.

**Fix mode:**
- Move hardcoded secrets to environment variables.
- Add auth middleware to unprotected endpoints.
- **Never fix security issues silently** — always report what was found and what was fixed.
- Commit: `fix(qa): [security] move hardcoded secret to env var in <file>`

---

### Category 6: Performance (Weight: 10%)

**Checks:**

1. **Bundle size:** Check for unexpected bundle size growth.
   - Look for large imports that should be tree-shaken or lazy-loaded.
   - Flag barrel file imports (`import { x } from '@/components'`) that pull entire directories.

2. **Drizzle query efficiency:**
   - Detect N+1 query patterns (queries inside loops).
   - Flag missing `.limit()` on unbounded queries.
   - Check for proper use of `.with()` for relations.

3. **Image optimization:**
   - Verify images use `next/image` (not raw `<img>` tags) in Next.js.
   - Check for unoptimized large images in the public directory.

4. **React re-renders:**
   - Flag inline object/array/function creation in JSX props.
   - Flag missing `key` props in lists.
   - Flag state updates that could be batched.

**Scoring:**
- 100: No performance anti-patterns detected.
- Deduct 5 points per barrel import issue.
- Deduct 10 points per N+1 query pattern.
- Deduct 3 points per unoptimized image.
- Deduct 3 points per unnecessary re-render pattern.

**Fix mode:**
- Replace barrel imports with direct imports.
- Replace `<img>` with `next/image`.
- Wrap inline functions with `useCallback` where appropriate.
- Commit: `fix(qa): [performance] replace barrel import in <file>`

---

### Category 7: Accessibility (Weight: 10%)

**Checks — per platform:**

**Web:**
- WCAG AA compliance on changed/new components.
- Check for missing `alt` text on images.
- Check for proper heading hierarchy (h1 → h2 → h3, no skips).
- Check for missing `aria-label` on interactive elements without visible text.
- Check for insufficient color contrast (if detectable statically).
- Check form inputs have associated labels.

**iOS:**
- Reference `ios-swift/review/accessibility.md` for iOS-specific checks.
- VoiceOver labels, traits, and hints.
- Dynamic Type support.

**Android:**
- Reference `kotlin-android/review/accessibility.md` for Android-specific checks.
- TalkBack content descriptions.
- Touch target sizes (minimum 48dp).

**Scoring:**
- 100: All accessibility checks pass.
- Deduct 5 points per missing alt text.
- Deduct 5 points per missing aria-label on interactive elements.
- Deduct 10 points per heading hierarchy violation.
- Deduct 5 points per form input without label.
- Deduct 3 points per platform-specific violation.

**Fix mode:**
- Add missing alt text (use descriptive text based on context, or `alt=""` for decorative images).
- Add missing aria-labels.
- Add missing form labels.
- Commit: `fix(qa): [accessibility] add missing alt text in <file>`

---

### Category 8: Contract Integrity (Weight: 10%)

**Checks:**

1. **Zod ↔ API alignment:**
   - Verify Zod schemas match the TypeScript types used in API responses.
   - Check that request validation schemas match what the handler expects.

2. **OpenAPI spec accuracy:**
   - If an OpenAPI spec exists, verify it matches actual route definitions.
   - Check that all documented endpoints exist and undocumented endpoints are flagged.

3. **Type generation currency:**
   - If using generated types (from Drizzle, OpenAPI, etc.), verify they are up to date.
   - Check that generated files are not manually modified.

**Scoring:**
- 100: All contracts are in sync.
- Deduct 10 points per schema/type mismatch.
- Deduct 5 points per undocumented endpoint.
- Deduct 10 points per stale generated type.

**Fix mode:**
- Regenerate types where possible.
- Update Zod schemas to match actual API responses.
- Commit: `fix(qa): [contract] sync Zod schema with API response in <file>`

---

## Fix Mode Behavior

When running in fix mode:

1. **One atomic commit per fix.** Each fix is a single commit that can be independently reverted.
2. **Commit message format:** `fix(qa): [category] description`
3. **Hard cap: 50 fixes maximum per run.** After 50 fixes, stop fixing and report remaining issues.
4. **Priority order:** Fix issues in category weight order (highest weight first).
5. **Never fix security issues silently** — always report what was found, even after fixing.

---

## Report Output Format

After all checks complete (in either mode), produce this report:

```
## QA Health Report

### Overall Score: XX/100

| Category           | Score | Weight | Issues |
|--------------------|-------|--------|--------|
| Build Health       | XX    | 15%    | N issues |
| Type Safety        | XX    | 15%    | N issues |
| Test Coverage      | XX    | 15%    | N issues |
| Lint Compliance    | XX    | 10%    | N issues |
| Security           | XX    | 15%    | N issues |
| Performance        | XX    | 10%    | N issues |
| Accessibility      | XX    | 10%    | N issues |
| Contract Integrity | XX    | 10%    | N issues |

### Issues by Category

#### 1. Build Health (XX/100)
- [list of issues found]

#### 2. Type Safety (XX/100)
- [list of issues found]

#### 3. Test Coverage (XX/100)
- [list of issues found]

#### 4. Lint Compliance (XX/100)
- [list of issues found]

#### 5. Security (XX/100)
- [list of issues found]

#### 6. Performance (XX/100)
- [list of issues found]

#### 7. Accessibility (XX/100)
- [list of issues found]

#### 8. Contract Integrity (XX/100)
- [list of issues found]

### Recommendations
[Top 3 highest-impact fixes, prioritized by weighted score improvement]
```

---

## Safety Rules

1. **Clean working tree required** — refuse to start if uncommitted changes exist.
2. **One commit per fix** — every fix is atomic and independently revertable.
3. **50-fix hard cap** — stop fixing after 50 commits to avoid runaway changes.
4. **Screenshot evidence** — for visual issues, use chrome-devtools MCP if available to capture evidence.
5. **Never fix security issues silently** — always report what was found, what was fixed, and what remains.
6. **No destructive changes** — never delete files, drop database tables, or remove API endpoints in fix mode.

---

## References

- `context/knowledge/patterns/clean-code-rules.md` — 6 mandatory rules: bounded iteration, small functions, minimal scope, validate boundaries, simple control flow, zero warnings.
- `context/knowledge/patterns/self-documenting-code.md` — Semantic vs pragmatic functions, model design, drift detection.
- `ios-swift/quality/checks.md` — iOS-specific quality checks (SwiftLint rules, build verification).
- `kotlin-android/quality/checks.md` — Android-specific quality checks (ktlint, Detekt, Android Lint).
- `vercel-react-best-practices` — React and Next.js performance optimization patterns.
- chrome-devtools MCP — Use for web visual testing and screenshot capture when available.
