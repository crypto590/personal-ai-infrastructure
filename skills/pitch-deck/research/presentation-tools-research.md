# Presentation Tools Research

## Recommendation: Slidev + `seriph` theme

### Why Slidev

1. Official AI skill (`npx skills add slidevjs/slidev`) — Claude gets full syntax knowledge
2. `seriph` theme has investor-appropriate visual weight — professional, readable, not developer-y
3. Standard pitch sections map cleanly to built-in layouts
4. PDF export is one command, no manual steps
5. Charts/data (market size, growth) via Vue components or static images
6. AI-native workflow explicitly supported by the Slidev team

### Fallback Options

- **Marp** + Marpstyle `Jobs` theme — when deck is text-heavy and speed matters most
- **md2pptx** (Python) — when investor explicitly needs editable `.pptx`

## Slidev Quick Reference

### Installation
```bash
npm init slidev@latest  # or: bun create slidev
npx playwright install chromium  # required for PDF export
```

### slides.md Format
```markdown
---
theme: seriph
title: Company Name — Seed Round
---

# Company Name
Tagline · Round Size

---
layout: section
---
# The Problem

---

# 80% of X still do Y manually

---
layout: two-cols
---
# Our Solution
::left::
- Feature 1
- Feature 2
::right::
![Product screenshot](/product.png)
```

### Per-Slide Frontmatter Options
- `layout:` — default, center, two-cols, section, image-right, image-left, cover, end
- `background:` — image URL or color
- `class:` — UnoCSS utility classes
- `transition:` — slide transition animation
- `clicks:` — number of click steps

### Export Commands
```bash
slidev export                           # PDF (default)
slidev export --output investor-deck.pdf  # named PDF
slidev export --format pptx             # PPTX (slides as images)
slidev export --format png              # PNG per slide (for review)
slidev export --with-clicks             # expand click animations
slidev export --dark                    # dark mode export
slidev export --with-toc                # PDF bookmarks
slidev export --timeout 60000           # longer timeout for complex slides
```

### Best Themes for Pitch Decks

| Theme | Package | Best For |
|---|---|---|
| **seriph** | `@slidev/theme-seriph` | Investor decks (elegant, serif, muted) |
| **apple-basic** | `@slidev/theme-apple-basic` | Product pitches (Keynote-inspired) |
| **geist** | `slidev-theme-geist` | Technical/SaaS pitches (Vercel dark) |
| default | `@slidev/theme-default` | Clean baseline |

### Gotchas

- PPTX export renders slides as images, not editable text
- Playwright/Chromium required for export — add to setup
- Interactive features (Monaco, click animations) disappear in PDF — use `--with-clicks`
- Missing content in PDF: add `--timeout 60000`
- Keep a reusable template project — Vite setup takes ~1-2 min

## Marp (Fallback)

```bash
npx @marp-team/marp-cli slide-deck.md --pdf
npx @marp-team/marp-cli slide-deck.md --pptx
```

3 built-in themes. Community: Marpstyle `Jobs` for pitch decks. Simpler than Slidev but fewer layouts.

## md2pptx (Editable PPTX)

```bash
pip install md2pptx
md2pptx presentation.md
```

Outputs true editable PPTX. Quality depends on template. Use when investor needs to edit.

## Sources

- [Slidev Getting Started](https://sli.dev/guide/)
- [Slidev Syntax Guide](https://sli.dev/guide/syntax)
- [Slidev Exporting](https://sli.dev/guide/exporting.html)
- [Slidev Work with AI](https://sli.dev/guide/work-with-ai)
- [Slidev Theme Gallery](https://sli.dev/resources/theme-gallery)
- [Marp Official](https://marp.app/)
- [Marpstyle Themes](https://github.com/cunhapaulo/marpstyle)
- [md2pptx](https://github.com/MartinPacker/md2pptx)
