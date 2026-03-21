---
name: pitch-deck
effort: medium
description: |
  Generate investor-grade pitch decks using Slidev from design docs or from scratch.
  Combines YC, a16z, and Sequoia pitch frameworks into a proven slide structure.
  Outputs markdown slides, exports to PDF for investor sharing.
  Use after /office-hours to turn a design doc into a deck, or standalone for
  any pitch deck need.
  Triggers: "pitch deck", "make a deck", "create slides", "investor deck",
  "demo day", "generate pitch", "slidev".
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - AskUserQuestion
  - WebSearch
  - WebFetch
metadata:
  last_reviewed: 2026-03-19
  review_cycle: 90
---

# Pitch Deck Generator

Generate polished, investor-grade pitch decks using Slidev. Synthesizes frameworks from YC (Michael Seibel's 7 questions), a16z (product-market fit thesis), Sequoia (narrative arc), and Peter Thiel (contrarian truth) into a single proven structure.

**HARD GATE:** This skill generates presentation content. It does NOT make investment decisions, validate business models, or replace `/office-hours` for strategic thinking.

## When to Use

- After `/office-hours` — turn the design doc into slides
- After `/alex-hormozi-pitch` — turn the offer into a deck
- Standalone — create a pitch deck from scratch for any project
- Before demo day, investor meetings, or accelerator applications

## How to Execute

Run `/pitch-deck` to start, or read the full workflow:

`read ~/.claude/skills/pitch-deck/workflows/generate-deck.md`

## Quick Reference

### The Slide Structure (12 slides max)

Based on synthesis of YC, a16z, Sequoia, and top VC frameworks:

| # | Slide | Purpose | Framework Source |
|---|-------|---------|-----------------|
| 1 | Title + One-Liner | What you do in one sentence | YC (Seibel) |
| 2 | Problem | Pain that exists today | Sequoia |
| 3 | Status Quo | How people solve it now (badly) | YC Office Hours Q2 |
| 4 | Solution | Your product, shown simply | a16z |
| 5 | Why Now? | What changed to make this possible | Sequoia |
| 6 | Traction | Evidence of demand (metrics, users, revenue) | YC Office Hours Q1 |
| 7 | How It Works | Product demo or 3-step flow | a16z |
| 8 | Market | TAM/SAM/SOM — bottom-up, not top-down | Sequoia |
| 9 | Business Model | How you make money (one model, committed) | YC (Seibel) |
| 10 | Team | Why this team wins | YC |
| 11 | The Ask | What you want, what you'll do with it | YC (Seibel) |
| 12 | Closing | Contact info, memorable closing line | — |

### Presentation Tool

**Slidev** — Markdown-based slides with Vue components.
- Write slides in markdown, get polished output
- Export to PDF for investor sharing
- Themes for professional look
- Code-friendly for live demos if needed

### Output

- `slides.md` — Slidev presentation file
- `slides.pdf` — Exported PDF for sharing
- Speaker notes included for each slide

## Upstream Skills

- `/office-hours` → produces design docs that feed into this skill
- `/alex-hormozi-pitch` → produces offer frameworks that inform the pitch

## Downstream

- The generated deck can be reviewed with `/plan-product` for strategic feedback
- PDF can be shared directly with investors
