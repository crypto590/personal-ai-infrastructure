---
name: plan-design
effort: high
context: fork
model: sonnet
description: "Multi-platform design audit: web (React/Tailwind), iOS (Liquid Glass), Android (Material 3). 80-item checklist with AI slop detection. Report-only."
metadata:
  last_reviewed: 2026-03-20
  review_cycle: 90
---

# Multi-Platform Design Audit

## Mode

**Report-only — NEVER modify code.** Screenshot evidence required where possible. Use `mcp__chrome-devtools__take_screenshot` for web, request simulator screenshots for mobile.

---

## Platform Tracks

### Web: React / Tailwind 4
- `@theme` directive for design tokens
- New color system (oklch-based)
- Container queries (`@container`)
- `@starting-style` for entry animations
- Verify Tailwind 4 patterns, not v3 legacy

### iOS: Liquid Glass / SwiftUI
- Single-layer glass rule (never stack glass on glass)
- Appropriate glass surfaces (navigation bars, tab bars, toolbars)
- Content readability through glass (contrast, vibrancy)
- Dynamic Type support
- Safe area compliance

### Android: Material Design 3
- Dynamic color (Material You)
- Color roles (primary, secondary, tertiary, error, surface)
- Typography scale (display, headline, title, body, label)
- Shape system (extra-small to extra-large)
- Motion tokens

---

## 80-Item Checklist (10 Categories x 8 Items)

### 1. Hierarchy

| # | Item | Platform |
|---|------|----------|
| 1.1 | Visual weight matches content importance | All |
| 1.2 | Primary action is immediately identifiable | All |
| 1.3 | Secondary actions are clearly subordinate | All |
| 1.4 | Scanning order matches reading pattern (F-pattern or Z-pattern) | All |
| 1.5 | Empty states have clear visual hierarchy | All |
| 1.6 | Error states maintain hierarchy | All |
| 1.7 | Loading states preserve layout (no layout shift) | All |
| 1.8 | Modal/overlay hierarchy is clear | All |

### 2. Typography

| # | Item | Platform |
|---|------|----------|
| 2.1 | Consistent type scale (no arbitrary sizes) | All |
| 2.2 | Font weights create clear hierarchy (2-3 weights max) | All |
| 2.3 | Line-height appropriate for body (1.5-1.75) and headings (1.1-1.3) | All |
| 2.4 | Measure (line length) between 45-75 characters | All |
| 2.5 | No orphaned headings (heading at bottom of container) | All |
| 2.6 | Consistent text alignment | All |
| 2.7 | Platform type system: Tailwind prose or custom scale (web), Dynamic Type (iOS), Material type scale (Android) | Per-platform |
| 2.8 | Monospace for code, system font for UI | All |

### 3. Color & Contrast

| # | Item | Platform |
|---|------|----------|
| 3.1 | WCAG AA minimum (4.5:1 text, 3:1 large text/UI) | All |
| 3.2 | WCAG AAA for critical content (7:1) | All |
| 3.3 | Color palette coherent (not random) | All |
| 3.4 | Color conveys meaning consistently (red=error, green=success) | All |
| 3.5 | Not relying on color alone for information | All |
| 3.6 | Dark mode support (if applicable) | All |
| 3.7 | Platform color system: Tailwind 4 color system (web), system colors (iOS), dynamic color (Android) | Per-platform |
| 3.8 | Focus indicators visible and consistent | All |

### 4. Spacing

| # | Item | Platform |
|---|------|----------|
| 4.1 | Consistent spacing scale (4px/8px base) | All |
| 4.2 | Related items grouped (proximity principle) | All |
| 4.3 | Sufficient whitespace between sections | All |
| 4.4 | Padding consistent within component types | All |
| 4.5 | Margin consistent between component types | All |
| 4.6 | Vertical rhythm maintained | All |
| 4.7 | Touch targets: 44pt (iOS), 48dp (Android), 44px (web) | Per-platform |
| 4.8 | No cramped layouts | All |

### 5. Interaction States

| # | Item | Platform |
|---|------|----------|
| 5.1 | Hover state (web) | Web |
| 5.2 | Focus state (all platforms) | All |
| 5.3 | Active/pressed state | All |
| 5.4 | Disabled state (visually distinct, not just opacity) | All |
| 5.5 | Loading state | All |
| 5.6 | Error state | All |
| 5.7 | Success/completion state | All |
| 5.8 | Empty state | All |

### 6. Responsive Design

| # | Item | Platform |
|---|------|----------|
| 6.1 | Breakpoint strategy defined (mobile-first) | Web |
| 6.2 | Content reflows gracefully (no horizontal scroll) | All |
| 6.3 | Images scale appropriately | All |
| 6.4 | Touch-friendly on mobile (no hover-dependent interactions) | Web/iOS/Android |
| 6.5 | Navigation adapts to screen size | All |
| 6.6 | Tables have mobile alternative (cards or horizontal scroll) | Web |
| 6.7 | Modals/dialogs fit mobile screens | All |
| 6.8 | No fixed widths that break on small screens | All |

### 7. Motion & Animation

| # | Item | Platform |
|---|------|----------|
| 7.1 | Transitions are purposeful (not decorative) | All |
| 7.2 | Duration appropriate (150-300ms for micro, 300-500ms for page) | All |
| 7.3 | Easing curves natural (ease-out for enter, ease-in for exit) | All |
| 7.4 | `prefers-reduced-motion` respected | All |
| 7.5 | No layout thrashing during animation | All |
| 7.6 | Loading indicators present for >500ms waits | All |
| 7.7 | Skeleton screens for content loading | All |
| 7.8 | No janky/stuttering animations | All |

### 8. Content & Microcopy

| # | Item | Platform |
|---|------|----------|
| 8.1 | Button labels are action verbs ("Save" not "OK") | All |
| 8.2 | Error messages are helpful (what went wrong + how to fix) | All |
| 8.3 | Empty states guide user to action | All |
| 8.4 | Labels are clear and concise | All |
| 8.5 | Placeholder text is helpful, not instructional | All |
| 8.6 | Confirmation dialogs explain consequences | All |
| 8.7 | Success messages confirm what happened | All |
| 8.8 | Consistent tone and voice | All |

### 9. AI Slop Detection (anti-patterns to flag)

| # | Item | Platform |
|---|------|----------|
| 9.1 | Gratuitous gradients (purple-to-blue hero sections) | All |
| 9.2 | Generic 3-column feature grids with icons | Web |
| 9.3 | Centered everything (no visual hierarchy) | All |
| 9.4 | Stock illustration style (isometric, blob-people) | All |
| 9.5 | Excessive rounded corners on everything | All |
| 9.6 | Rainbow/neon color schemes with no brand coherence | All |
| 9.7 | "Hero section -> features -> testimonials -> CTA" cookie-cutter layout | Web |
| 9.8 | Generic placeholder copy ("Lorem ipsum" or "Your amazing feature") | All |

### 10. Performance Feel

| # | Item | Platform |
|---|------|----------|
| 10.1 | Perceived load time < 1s (skeleton/placeholder) | All |
| 10.2 | No layout shift (CLS score) | Web |
| 10.3 | Images lazy-loaded below fold | Web |
| 10.4 | Fonts don't cause FOUT/FOIT | Web |
| 10.5 | Scroll performance smooth (60fps) | All |
| 10.6 | No blocking modals on page load | All |
| 10.7 | Progressive disclosure of complex forms | All |
| 10.8 | Instant feedback on user actions | All |

---

## Audit Procedure

1. **Determine scope:** Which platform(s)? Which screen(s)/flow(s)?
2. **Capture evidence:** Take screenshots of current state before auditing.
3. **Run checklist:** Go through all 80 items, marking Pass/Fail/N/A.
4. **Score:** Calculate pass rate per category and overall.
5. **Classify issues:**
   - **Critical (must fix):** Accessibility violations, broken interactions, layout shift
   - **Improvement (should fix):** Inconsistencies, suboptimal patterns, minor polish
6. **Generate report** in the output format below.

---

## Output Format

```
## Design Audit: [scope]

### Platform: [Web/iOS/Android/All]

### Score: XX/80 items passing

| Category | Pass | Fail | N/A |
|----------|------|------|-----|
| Hierarchy | X | X | X |
| Typography | X | X | X |
| Color & Contrast | X | X | X |
| Spacing | X | X | X |
| Interaction States | X | X | X |
| Responsive Design | X | X | X |
| Motion & Animation | X | X | X |
| Content & Microcopy | X | X | X |
| AI Slop Detection | X | X | X |
| Performance Feel | X | X | X |

### Critical Issues (must fix)
1. [issue + location + why it matters]
2. ...

### Improvements (should fix)
1. [issue + location + suggested fix]
2. ...

### Notes
[platform-specific observations, patterns noticed, positive callouts]
```

---

## References

- `vercel-react-best-practices` for React performance patterns
- `ios-swift/review/liquid-glass.md` and `ios-swift/review/accessibility.md`
- `kotlin-android/review/material-design-review.md` and `kotlin-android/review/accessibility.md`
