# Generate Pitch Deck Workflow

Full workflow for generating an investor-grade pitch deck using Slidev.

---

## Phase 1: Content Gathering

Determine what content we're working with.

### Option A: From a Design Doc (post /office-hours)

```bash
ls -t ~/.claude/office-hours/*.md 2>/dev/null
```

If design docs exist, read the most recent APPROVED one and extract:
- Problem statement
- Demand evidence
- Status quo
- Target user & narrowest wedge
- Recommended approach
- Success criteria

Ask via AskUserQuestion: "Found design doc: '{title}'. Use this as the basis for the pitch deck?"
- A) Yes, use this design doc
- B) No, start from scratch (go to Option B)

### Option B: From Scratch

Ask these questions **ONE AT A TIME** via AskUserQuestion. These map directly to Michael Seibel's 7 questions:

**Q1: "What does your product do? Explain it like you're telling a smart friend over coffee — no jargon."**
- Apply the email test: if you'd need to add clarification, it's too complex
- Push for the user path method: walk through how a customer actually uses it

**Q2: "Who specifically needs this? Not a category — a person. What's their name, title, and what keeps them up at night?"**
- Red flag: category-level answers ("athletes", "coaches", "SMBs")
- Push until you hear a specific human with a specific pain

**Q3: "What are they doing right now to solve this problem? What does that workaround cost them?"**
- Must be a concrete workflow, not "nothing exists"
- Quantify: hours, dollars, frustration

**Q4: "What's your strongest evidence of demand? Not interest — demand. Who would be upset if this disappeared?"**
- Revenue > active users > signups > "people say it's interesting"
- Include timeframes: "500 users" means nothing without "in 3 weeks"

**Q5: "What's your business model? Pick one and commit."**
- Red flag: listing 5 monetization ideas
- Push for: pricing, unit economics, LTV/CAC if known

**Q6: "What's your unique insight — what do you know about this problem that others don't?"**
- Must be specific and sourced from experience/data
- NOT: "the market is growing" or "AI makes everything better"

**Q7: "How much are you raising, and what will you do with it? What milestones will you hit?"**
- Must be specific milestones, not "hire engineers"
- 18-month runway is the standard

### For Sports-Tech / Athlead Specifically

Also ask:
- "What's the institutional adoption lever? Which organization mandates or recommends your product?"
- "How do you overcome the 'vitamin vs painkiller' objection?" (reference research)
- "Who are your target investors? Generalist or sports-tech specific?" (recommend: Courtside Ventures, Elysian Park, Arctos, Comcast SportsTech for sports-tech)

---

## Phase 2: Slide Architecture

Based on gathered content, map to the 12-slide structure. This structure synthesizes YC, a16z, Sequoia, and Thiel frameworks.

Present the outline via AskUserQuestion before generating:

```
PITCH DECK OUTLINE:

1. TITLE + ONE-LINER
   "{Company} — {one sentence}"

2. PROBLEM
   "{Pain statement — specific, quantified}"

3. STATUS QUO
   "{How people solve it now, badly}"

4. SOLUTION
   "{Your product, simply explained}"

5. WHY NOW?
   "{What changed — technology, behavior, regulation}"

6. TRACTION
   "{Metrics: revenue, users, growth rate, engagement}"

7. HOW IT WORKS
   "{3-step flow or product demo}"

8. MARKET
   "{Bottom-up TAM/SAM/SOM}"

9. BUSINESS MODEL
   "{How you make money — one model}"

10. TEAM
    "{Why this team wins}"

11. THE ASK
    "{Amount, use of funds, milestones}"

12. CLOSING
    "{Contact + memorable line}"

A) Approve outline — generate slides
B) Revise — tell me what to change
C) Reorder — different slide order for this pitch
```

### Slide Selection by Stage

Not every pitch needs all 12. Smart-skip based on stage:

| Stage | Include | Skip/Minimize |
|-------|---------|---------------|
| Pre-product | 1,2,3,4,5,8,10,11 | 6 (no traction), 7 (no product to demo) |
| Has users | 1,2,4,5,6,7,8,9,10,11 | 3 (shorter) |
| Revenue | All 12 — lead with 6 (traction) | — |
| Demo day (~2 min) | 1,2,4,6,11 | Everything else — 5 slides max |

### Anti-Pattern Checklist

Before generating, verify the outline avoids these:

- [ ] No "$X trillion TAM" without bottom-up math
- [ ] No magic quadrant competitive slide
- [ ] No "we have no competition"
- [ ] No hockey stick without the mechanism causing it
- [ ] No 5-year precision projections (18 months max)
- [ ] No "first mover advantage" as a moat
- [ ] No long advisor lists
- [ ] No "better UX" as the differentiator
- [ ] No AI-washing ("AI-powered" without specifics)
- [ ] No missing ask at the end
- [ ] Traction has timeframes attached
- [ ] Business model is singular, not "5 possible approaches"

---

## Phase 3: Slidev Project Setup

### Check for Existing Template

```bash
ls ~/.claude/pitch-decks/ 2>/dev/null
```

### First-Time Setup

```bash
mkdir -p ~/.claude/pitch-decks
cd ~/.claude/pitch-decks
npm init slidev@latest -- --template default
npx playwright install chromium
```

### Theme Selection

Ask via AskUserQuestion:

> Which visual style fits this pitch?
>
> A) **Seriph** — Elegant serif font, muted colors. Best for investor meetings. (recommended)
> B) **Apple Basic** — Keynote-inspired, black & white. Best for product demos.
> C) **Geist** — Vercel-style dark theme. Best for technical/SaaS pitches.
> D) **Default** — Clean minimal. Safe baseline.

---

## Phase 4: Generate Slides

Write `slides.md` using the approved outline. Follow these rules:

### Content Rules (from research)

1. **One idea per slide.** If you need a second paragraph, you need a second slide.
2. **30pt minimum font equivalent.** In Slidev, this means short bullet points, not paragraphs.
3. **Numbers over words.** "$500K MRR, 3x YoY" beats "We're growing fast."
4. **Show, don't tell.** Screenshots, diagrams, charts over text descriptions.
5. **Speaker notes for everything.** The slide is the visual; the note is what you say.
6. **Email-readable.** VCs read decks async. Every slide must stand alone without narration.

### Slide-by-Slide Generation Guide

```markdown
---
theme: seriph
title: {Company Name} — {Round}
info: |
  Pitch deck generated by /pitch-deck
  Based on YC, a16z, and Sequoia frameworks
---

# {Company Name}
{One-liner: what you do in one sentence}

{Tagline or round info}

<!-- Speaker note: Introduce yourself. Name, role, one sentence of credibility. Then read the one-liner. -->

---
layout: section
---

# The Problem

<!-- Speaker note: Tell the story of the specific person who has this problem. Use their name if you can. -->

---

# {Quantified pain statement}

{2-3 bullet points with specific evidence}

<!-- Speaker note: This is where you ground the problem in reality. Cite specific numbers, quotes, or observations. -->

---
layout: two-cols
---

# The Status Quo

::left::

**What people do today:**
- {Workaround 1}
- {Workaround 2}
- {Workaround 3}

::right::

**What it costs them:**
- {Time cost}
- {Dollar cost}
- {Opportunity cost}

<!-- Speaker note: Paint the picture of the painful workaround. Make the investor feel the friction. -->

---
layout: image-right
image: /product-screenshot.png
---

# Our Solution

{2-3 sentences: what it does, how it works}

<!-- Speaker note: Demo if possible. Otherwise, walk through the user path: "You open the app, you see X, you do Y, you get Z." -->

---

# Why Now?

{What changed to make this possible/necessary}

- **Technology:** {shift}
- **Market:** {behavior change}
- **Timing:** {why this moment}

<!-- Speaker note: This is the Sequoia question. Could this have worked 5 years ago? What's different now? -->

---

# Traction

{Lead metric — biggest number first}

| Metric | Value | Timeframe |
|--------|-------|-----------|
| {metric} | {value} | {period} |
| {metric} | {value} | {period} |
| {metric} | {value} | {period} |

<!-- Speaker note: Context matters. "500 users in 3 weeks since launch with zero marketing spend" is a story. "500 users" is not. -->

---
layout: two-cols
---

# How It Works

::left::

**1. {Step 1}**
{One sentence}

**2. {Step 2}**
{One sentence}

**3. {Step 3}**
{One sentence}

::right::

![Product flow](/flow-diagram.png)

<!-- Speaker note: Walk through the 3-step flow. Keep it concrete. -->

---

# Market

**TAM:** ${X}B — {definition}
**SAM:** ${X}M — {your segment}
**SOM:** ${X}M — {3-year realistic capture}

{Bottom-up math: X customers × $Y/year = $Z}

<!-- Speaker note: ALWAYS explain your bottom-up math. "There are X thousand {target customers} in {geography}. At ${price}/year, that's a ${SAM} addressable market." -->

---

# Business Model

**{Model type}:** {one sentence}

| | Price | LTV | CAC |
|---|---|---|---|
| {tier/segment} | ${X}/mo | ${Y} | ${Z} |

<!-- Speaker note: Own one model. If asked about others, say "We've considered X but we're focused on Y because Z." -->

---
layout: two-cols
---

# Team

::left::

**{Name}** — {Role}
{One line of relevant credibility}

**{Name}** — {Role}
{One line of relevant credibility}

::right::

{Why this team wins in this specific market. Domain expertise, prior exits, unique access.}

<!-- Speaker note: Don't list your GPA. Say what you've built and why you understand this problem better than anyone. -->

---
layout: center
class: text-center
---

# The Ask

## ${Amount} {Round Type}

**Use of funds:**
- {X%} — {Category} → {Milestone}
- {X%} — {Category} → {Milestone}
- {X%} — {Category} → {Milestone}

**18-month milestones:** {specific targets}

<!-- Speaker note: Be direct. "We're raising $X at $Y valuation. Here's exactly what we'll do with it and what we'll achieve." -->

---
layout: end
class: text-center
---

# {Company Name}

{Memorable closing line}

{email} · {website}

<!-- Speaker note: End strong. Restate the one-liner. Thank them. Ask for questions. -->
```

### Image Placeholders

For any `![](/image.png)` reference, create a note in speaker notes:
```
<!-- TODO: Replace with actual screenshot/diagram -->
```

The user will add real images. Don't block on this.

---

## Phase 5: Export & Review

### Generate PDF

```bash
cd ~/.claude/pitch-decks
npx slidev export --output {company}-pitch-{date}.pdf --timeout 60000
```

### Generate PNGs for Review

```bash
npx slidev export --format png --output {company}-slides
```

### Review Checklist

Present via AskUserQuestion:

```
DECK REVIEW:

Slide-by-slide check:
✓/✗ 1. Title — One-liner passes the email test?
✓/✗ 2. Problem — Specific and quantified?
✓/✗ 3. Status quo — Concrete workaround described?
✓/✗ 4. Solution — Clear without jargon?
✓/✗ 5. Why now — Timing argument is specific?
✓/✗ 6. Traction — Numbers have timeframes?
✓/✗ 7. How it works — 3 steps, a child could follow?
✓/✗ 8. Market — Bottom-up math shown?
✓/✗ 9. Business model — One model, committed?
✓/✗ 10. Team — Relevant credibility only?
✓/✗ 11. The ask — Amount + milestones + use of funds?
✓/✗ 12. Closing — Memorable?

Anti-pattern check:
✓/✗ No TAM inflation
✓/✗ No magic quadrant
✓/✗ No hedging language
✓/✗ No missing timeframes
✓/✗ Email-readable without narration

A) Approve — deck is ready
B) Revise — specify which slides need changes
C) Regenerate — start over with different approach
```

---

## Phase 6: Handoff

Once approved:

1. **Save the deck:**
   ```bash
   mkdir -p ~/.claude/pitch-decks/exports
   cp {company}-pitch-{date}.pdf ~/.claude/pitch-decks/exports/
   ```

2. **Speaker notes export** (optional):
   Extract all speaker notes into a separate document for practice.

3. **Next steps:**
   - Practice the pitch out loud — 2 minutes for demo day, 10 minutes for meetings
   - Replace image placeholders with real screenshots
   - Get feedback from someone NOT in your industry (clarity test)
   - **If pitching sports-tech:** target Courtside Ventures, Elysian Park, Arctos, Comcast SportsTech first

4. **Suggest related skills:**
   - `/alex-hormozi-pitch` — craft the offer framework behind the pitch
   - `/plan-product` — strategic review of the product direction
   - `/office-hours` — stress-test with another round of forcing questions

---

## Important Rules

- **Never fake traction.** If there's no traction, skip the slide. A bad traction slide is worse than none.
- **One idea per slide.** Split ruthlessly.
- **Numbers need timeframes.** Always.
- **The ask is mandatory.** Every deck ends with a clear ask.
- **Email-readable.** VCs read async. No slide should require narration to understand.
- **Speaker notes are mandatory.** Every slide gets notes — they're the pitch script.

### Completion Status

- **DONE** — deck generated, PDF exported, review passed
- **DONE_WITH_CONCERNS** — deck generated but has flagged issues (missing images, weak traction, etc.)
- **NEEDS_CONTEXT** — insufficient content to generate a credible deck
