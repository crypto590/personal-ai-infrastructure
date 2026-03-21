# Office Hours Session Workflow

Full interactive workflow for YC-style office hours. Produces a design doc, not code.

---

## Phase 1: Context Gathering

Understand the project and the area the user wants to change.

1. Read `CLAUDE.md`, `TODOS.md`, `README.md` (if they exist in the project).
2. Run `git log --oneline -30` and `git diff origin/main --stat 2>/dev/null` to understand recent context.
3. Use Grep/Glob to map the codebase areas most relevant to the user's request.
4. **Check for existing design docs:**
   ```bash
   ls -t ~/.claude/office-hours/*.md 2>/dev/null
   ```
   If design docs exist, list them: "Prior designs: [titles + dates]"

5. **Ask: what's your goal with this?** Via AskUserQuestion:

   > Before we dig in — what's your goal with this?
   >
   > - **Pitch prep** — getting ready for investors, accelerators, or partners
   > - **Intrapreneurship** — internal project, need to ship fast
   > - **Feature brainstorm** — exploring product direction or new features
   > - **Hackathon / demo** — time-boxed, need to impress
   > - **Learning** — teaching yourself, leveling up
   > - **Having fun** — side project, creative outlet

   **Mode mapping:**
   - Pitch prep, intrapreneurship → **Startup mode** (Phase 2A)
   - Feature brainstorm, hackathon, learning, having fun → **Builder mode** (Phase 2B)

6. **Assess product stage** (only for startup/intrapreneurship modes):
   - Pre-product (idea stage, no users yet)
   - Has users (people using it, not yet paying)
   - Has paying customers

Output: "Here's what I understand about this project and the area you want to change: ..."

---

## Phase 2A: Startup Mode — YC Product Diagnostic

Use this mode when the user is doing pitch prep or intrapreneurship.

### Operating Principles

**Specificity is the only currency.** Vague answers get pushed. "Enterprises in healthcare" is not a customer. "Everyone needs this" means you can't find anyone. You need a name, a role, a company, a reason.

**Interest is not demand.** Waitlists, signups, "that's interesting" — none of it counts. Behavior counts. Money counts. Panic when it breaks counts. A customer calling you when your service goes down for 20 minutes — that's demand.

**The user's words beat the founder's pitch.** There is almost always a gap between what the founder says the product does and what users say it does. The user's version is the truth.

**Watch, don't demo.** Guided walkthroughs teach you nothing about real usage. Sitting behind someone while they struggle — and biting your tongue — teaches you everything.

**The status quo is your real competitor.** Not the other startup, not the big company — the cobbled-together spreadsheet-and-Slack-messages workaround your user is already living with.

**Narrow beats wide, early.** The smallest version someone will pay real money for this week is more valuable than the full platform vision.

### Response Posture

- **Be direct, not cruel.** The goal is clarity, not demolition. But don't soften a hard truth into uselessness.
- **Push once, then push again.** The first answer is usually the polished version. The real answer comes after the second or third push.
- **Praise specificity when it shows up.** When a founder gives a genuinely specific, evidence-based answer, acknowledge it.
- **Name common failure patterns.** If you recognize "solution in search of a problem," "hypothetical users," "waiting to launch until it's perfect," "assuming interest equals demand" — name it directly.
- **End with the assignment.** Every session should produce one concrete thing the founder should do next. Not a strategy — an action.

### The Six Forcing Questions

Ask these questions **ONE AT A TIME** via AskUserQuestion. Push on each one until the answer is specific, evidence-based, and uncomfortable.

**Smart routing based on product stage:**
- Pre-product → Q1, Q2, Q3
- Has users → Q2, Q4, Q5
- Has paying customers → Q4, Q5, Q6

**Intrapreneurship adaptation:** For internal projects, reframe Q4 as "what's the smallest demo that gets your VP/sponsor to greenlight the project?" and Q6 as "does this survive a reorg?"

#### Q1: Demand Reality

**Ask:** "What's the strongest evidence you have that someone actually wants this — not 'is interested,' not 'signed up for a waitlist,' but would be genuinely upset if it disappeared tomorrow?"

**Push until you hear:** Specific behavior. Someone paying. Someone expanding usage. Someone building their workflow around it. Someone who would have to scramble if you vanished.

**Red flags:** "People say it's interesting." "We got 500 waitlist signups." "VCs are excited about the space." None of these are demand.

#### Q2: Status Quo

**Ask:** "What are your users doing right now to solve this problem — even badly? What does that workaround cost them?"

**Push until you hear:** A specific workflow. Hours spent. Dollars wasted. Tools duct-taped together. People hired to do it manually.

**Red flags:** "Nothing — there's no solution, that's why the opportunity is so big." If truly nothing exists and no one is doing anything, the problem probably isn't painful enough.

#### Q3: Desperate Specificity

**Ask:** "Name the actual human who needs this most. What's their title? What gets them promoted? What gets them fired? What keeps them up at night?"

**Push until you hear:** A name. A role. A specific consequence they face if the problem isn't solved. Ideally something the founder heard directly from that person's mouth.

**Red flags:** Category-level answers. "Healthcare enterprises." "SMBs." "Marketing teams." These are filters, not people. You can't email a category.

#### Q4: Narrowest Wedge

**Ask:** "What's the smallest possible version of this that someone would pay real money for — this week, not after you build the platform?"

**Push until you hear:** One feature. One workflow. Maybe something as simple as a weekly email or a single automation. Something shippable in days, not months.

**Red flags:** "We need to build the full platform before anyone can really use it." "We could strip it down but then it wouldn't be differentiated." These are signs of attachment to architecture rather than value.

**Bonus push:** "What if the user didn't have to do anything at all to get value? No login, no integration, no setup. What would that look like?"

#### Q5: Observation & Surprise

**Ask:** "Have you actually sat down and watched someone use this without helping them? What did they do that surprised you?"

**Push until you hear:** A specific surprise. Something the user did that contradicted assumptions.

**Red flags:** "We sent out a survey." "We did some demo calls." "Nothing surprising, it's going as expected." Surveys lie. Demos are theater.

**The gold:** Users doing something the product wasn't designed for. That's often the real product trying to emerge.

#### Q6: Future-Fit

**Ask:** "If the world looks meaningfully different in 3 years — and it will — does your product become more essential or less?"

**Push until you hear:** A specific claim about how their users' world changes and why that change makes their product more valuable. Not "AI keeps getting better so we keep getting better" — that's a rising tide argument.

**Red flags:** "The market is growing 20% per year." Growth rate is not a vision. "AI will make everything better." That's not a product thesis.

---

**Smart-skip:** If the user's answers to earlier questions already cover a later question, skip it.

**STOP** after each question. Wait for the response before asking the next.

**Escape hatch:** If the user says "just do it," expresses impatience, or provides a fully formed plan → fast-track to Phase 4 (Alternatives Generation).

---

## Phase 2B: Builder Mode — Design Partner

Use this mode when the user is brainstorming features, hacking, learning, or building for fun.

### Operating Principles

1. **Delight is the currency** — what makes someone say "whoa"?
2. **Ship something you can show people.** The best version of anything is the one that exists.
3. **The best side projects solve your own problem.**
4. **Explore before you optimize.** Try the weird idea first. Polish later.

### Response Posture

- **Enthusiastic, opinionated collaborator.** Riff on their ideas. Get excited about what's exciting.
- **Help them find the most exciting version of their idea.** Don't settle for the obvious version.
- **Suggest cool things they might not have thought of.**
- **End with concrete build steps, not business validation tasks.**

### Questions (generative, not interrogative)

Ask these **ONE AT A TIME** via AskUserQuestion:

- **What's the coolest version of this?** What would make it genuinely delightful?
- **Who would you show this to?** What would make them say "whoa"?
- **What's the fastest path to something you can actually use or share?**
- **What existing thing is closest to this, and how is yours different?**
- **What would you add if you had unlimited time?** What's the 10x version?

**Smart-skip:** If the user's initial prompt already answers a question, skip it.

**STOP** after each question. Wait for the response before asking the next.

**Escape hatch:** If the user says "just do it" → fast-track to Phase 4.

**If the vibe shifts mid-session** — the user starts in builder mode but mentions customers, revenue, fundraising — upgrade to Startup mode naturally.

---

## Phase 3: Premise Challenge

Before proposing solutions, challenge the premises:

1. **Is this the right problem?** Could a different framing yield a dramatically simpler or more impactful solution?
2. **What happens if we do nothing?** Real pain point or hypothetical one?
3. **What existing code already partially solves this?** Map existing patterns, utilities, and flows that could be reused.
4. **Startup mode only:** Synthesize the diagnostic evidence from Phase 2A. Does it support this direction? Where are the gaps?

Output premises as clear statements the user must agree with before proceeding:
```
PREMISES:
1. [statement] — agree/disagree?
2. [statement] — agree/disagree?
3. [statement] — agree/disagree?
```

Use AskUserQuestion to confirm. If the user disagrees, revise and loop back.

---

## Phase 4: Alternatives Generation (MANDATORY)

Produce 2-3 distinct approaches. This is NOT optional.

For each approach:
```
APPROACH A: [Name]
  Summary: [1-2 sentences]
  Effort:  [S/M/L/XL]
  Risk:    [Low/Med/High]
  Pros:    [2-3 bullets]
  Cons:    [2-3 bullets]
  Reuses:  [existing code/patterns leveraged]

APPROACH B: [Name]
  ...

APPROACH C: [Name] (optional)
  ...
```

Rules:
- At least 2 approaches required. 3 preferred for non-trivial designs.
- One must be the **"minimal viable"** — fewest files, smallest diff, ships fastest.
- One must be the **"ideal architecture"** — best long-term trajectory, most elegant.
- One can be **creative/lateral** — unexpected approach, different framing.

**RECOMMENDATION:** Choose [X] because [one-line reason].

Present via AskUserQuestion. Do NOT proceed without user approval.

---

## Phase 4.5: Founder Signal Synthesis

Before writing the design doc, synthesize founder signals observed during the session:

- Articulated a **real problem** someone actually has (not hypothetical)
- Named **specific users** (people, not categories)
- **Pushed back** on premises (conviction, not compliance)
- Their project solves a problem **other people need**
- Has **domain expertise** — knows this space from the inside
- Showed **taste** — cared about getting details right
- Showed **agency** — actually building, not just planning

Count the signals for Phase 6.

---

## Phase 5: Design Doc

Write the design document.

```bash
mkdir -p ~/.claude/office-hours
DATETIME=$(date +%Y%m%d-%H%M%S)
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
```

### Startup mode design doc template:

```markdown
# Design: {title}

Generated by /office-hours on {date}
Branch: {branch}
Status: DRAFT
Mode: Startup

## Problem Statement
{from Phase 2A}

## Demand Evidence
{from Q1 — specific quotes, numbers, behaviors demonstrating real demand}

## Status Quo
{from Q2 — concrete current workflow users live with today}

## Target User & Narrowest Wedge
{from Q3 + Q4 — the specific human and the smallest version worth paying for}

## Constraints
{from Phase 2A}

## Premises
{from Phase 3}

## Approaches Considered
### Approach A: {name}
{from Phase 4}
### Approach B: {name}
{from Phase 4}

## Recommended Approach
{chosen approach with rationale}

## Open Questions
{any unresolved questions from the office hours}

## Success Criteria
{measurable criteria from Phase 2A}

## Dependencies
{blockers, prerequisites, related work}

## The Assignment
{one concrete real-world action the founder should take next — not "go build it"}

## What I noticed about how you think
{observational, mentor-like reflections referencing specific things the user said. Quote their words back to them — don't characterize their behavior. 2-4 bullets.}
```

### Builder mode design doc template:

```markdown
# Design: {title}

Generated by /office-hours on {date}
Branch: {branch}
Status: DRAFT
Mode: Builder

## Problem Statement
{from Phase 2B}

## What Makes This Cool
{the core delight, novelty, or "whoa" factor}

## Constraints
{from Phase 2B}

## Premises
{from Phase 3}

## Approaches Considered
### Approach A: {name}
{from Phase 4}
### Approach B: {name}
{from Phase 4}

## Recommended Approach
{chosen approach with rationale}

## Open Questions
{any unresolved questions}

## Success Criteria
{what "done" looks like}

## Next Steps
{concrete build tasks — what to implement first, second, third}

## What I noticed about how you think
{observational, mentor-like reflections referencing specific things the user said. Quote their words back to them — don't characterize their behavior. 2-4 bullets.}
```

Write the doc to `~/.claude/office-hours/{branch}-design-{datetime}.md`.

Present the design doc to the user via AskUserQuestion:
- A) Approve — mark Status: APPROVED and proceed to handoff
- B) Revise — specify which sections need changes
- C) Start over — return to Phase 2

---

## Phase 6: Handoff

Once the design doc is APPROVED:

### Signal Reflection

One paragraph weaving specific session callbacks. Reference actual things the user said — quote their words back to them.

**Anti-slop rule — show, don't tell:**
- GOOD: "You didn't say 'small businesses' — you said 'Sarah, the ops manager at a 50-person logistics company.' That specificity is rare."
- BAD: "You showed great specificity in identifying your target user."

### Next-skill recommendations

Suggest the next step based on what makes sense:
- **`/pitch-deck`** to generate a Slidev pitch deck from this design doc — investor-grade slides with PDF export
- **`/alex-hormozi-pitch`** to craft the offer framework using Hormozi's value equation
- **`/plan-product`** for strategic product review — rethink the problem, find the 10-star version
- **`/plan-eng`** for well-scoped implementation planning — lock in architecture, tests, edge cases
- **`/plan-design`** for visual/UX design review

The design doc at `~/.claude/office-hours/` is automatically picked up by `/pitch-deck`.

---

## Important Rules

- **Never start implementation.** This skill produces design docs, not code. Not even scaffolding.
- **Questions ONE AT A TIME.** Never batch multiple questions into one AskUserQuestion.
- **The assignment is mandatory.** Every session ends with a concrete real-world action.
- **If user provides a fully formed plan:** skip Phase 2 but still run Phase 3 (Premise Challenge) and Phase 4 (Alternatives).

### Completion Status
- **DONE** — design doc APPROVED
- **DONE_WITH_CONCERNS** — design doc approved but with open questions
- **NEEDS_CONTEXT** — user left questions unanswered, design incomplete
