# Skills Directory

This directory contains **reusable capabilities** organized by skill category. Skills are domain-agnostic and work across all projects.

---

## 📂 Directory Structure

```
skills/
├── core/           # Universal capabilities
├── technical/      # Programming & engineering skills
├── business/       # Business-focused capabilities
├── domain/         # Domain-specific expertise
└── personal/       # Personal productivity skills
```

---

## 🎯 What Goes Here

### ✅ DO Add Skills For:
- Reusable patterns that apply across projects
- Methodologies and frameworks you use consistently
- Problem-solving approaches
- Technical capabilities (programming, tools, platforms)
- Business capabilities (analysis, strategy, communication)
- Domain expertise (industry-specific knowledge applications)

### ❌ DON'T Add:
- Project-specific configurations (those go in project CLAUDE.md files)
- One-off solutions
- Temporary workarounds
- Knowledge/reference material (those go in `context/knowledge/`)

---

## 📝 Skill File Format

Each skill file should follow this structure:

```markdown
# Skill Name

**Category:** [core/technical/business/domain/personal]

**Brief Description:** [1-2 sentence summary - metadata loaded always]

---

## When to Use This Skill

[Trigger conditions - when should this skill be loaded?]

---

## How It Works

[Detailed implementation - loaded on demand only]

### Methodology
### Examples
### Common Patterns

---

## Dependencies

**Related skills:** [Other skills this uses]
**Required context:** [Context files needed]
```

---

## 📚 Category Descriptions

### `/core/` - Universal Capabilities

**What goes here:** Skills applicable to any domain or project

**Examples:**
- `problem-solving.md` - Systematic problem-solving framework
- `research.md` - Research methodology
- `writing.md` - Technical writing patterns
- `analysis.md` - Analytical thinking frameworks
- `communication.md` - Communication strategies

**When to use:** Fundamental capabilities used everywhere

---

### `/technical/` - Programming & Engineering

**What goes here:** Technical and programming skills

**Examples:**
- `api-design.md` - REST/GraphQL API patterns
- `typescript-patterns.md` - TypeScript best practices
- `database-design.md` - Database schema design
- `testing-strategy.md` - Testing approaches
- `deployment.md` - Deployment workflows
- `performance-optimization.md` - Performance tuning
- `error-handling.md` - Error handling patterns

**When to use:** Technical implementation tasks

---

### `/business/` - Business Capabilities

**What goes here:** Business-focused skills

**Examples:**
- `business-analysis.md` - Requirements gathering and analysis
- `stakeholder-management.md` - Working with stakeholders
- `project-planning.md` - Project planning approaches
- `product-strategy.md` - Product thinking
- `data-analysis.md` - Business data analysis
- `financial-modeling.md` - Financial analysis

**When to use:** Business-oriented tasks

---

### `/domain/` - Domain Expertise

**What goes here:** Industry or domain-specific skills

**Examples:**
- `payment-processing.md` - Payment flow implementations
- `underwriting.md` - Underwriting workflows
- `compliance-review.md` - Compliance checking
- `healthcare-integration.md` - Healthcare system integration
- `fintech-security.md` - Financial services security

**When to use:** Domain-specific implementations

**Note:** This is where YOUR unique expertise lives

---

### `/personal/` - Personal Productivity

**What goes here:** Personal productivity and growth skills

**Examples:**
- `learning-strategy.md` - How you learn new things
- `time-management.md` - Time management approach
- `note-taking.md` - Note-taking system
- `habit-tracking.md` - Habit formation
- `health-tracking.md` - Health and wellness
- `finance-management.md` - Personal finance

**When to use:** Personal tasks and self-improvement

---

## 🚀 Creating Your First Skill

### Step 1: Identify the Pattern

Ask yourself:
- Is this something I do repeatedly?
- Would this apply to multiple projects?
- Is this a capability or approach (not just knowledge)?

If yes → It's a skill!

### Step 2: Choose the Category

- **Universal approach?** → `core/`
- **Technical pattern?** → `technical/`
- **Business capability?** → `business/`
- **Industry-specific?** → `domain/`
- **Personal productivity?** → `personal/`

### Step 3: Create the File

```bash
cd /Users/coreyyoung/Claude/skills/[category]
touch skill-name.md
```

### Step 4: Fill in the Template

Use the skill file format above. Keep the header brief (metadata) and put details in the body.

### Step 5: Test It

Use the skill in a project and verify AI loads it when needed.

---

## 🎓 Progressive Disclosure

Skills use **three-level loading**:

### Level 1: Metadata (Always Loaded)
- Brief description in the header
- ~10-20 tokens per skill
- Gives AI awareness of available capabilities

### Level 2: Full Skill (On Demand)
- Complete implementation details
- Loaded when task explicitly requires it
- ~200-500 tokens per skill

### Level 3: Deep Context (As Needed)
- Related knowledge files from `context/knowledge/`
- Loaded progressively based on conversation

**This achieves 92.5% token reduction while maintaining full capability.**

---

## 🔗 Linking Skills Together

Skills can reference each other:

```markdown
## Dependencies

**Related skills:**
- `/Users/coreyyoung/Claude/skills/technical/api-design.md`
- `/Users/coreyyoung/Claude/skills/technical/error-handling.md`

**Required context:**
- `/Users/coreyyoung/Claude/context/knowledge/frameworks/nextjs/`
```

---

## 🛠️ Maintenance

### When to Refactor

**Split a skill when:**
- File grows beyond ~500 lines
- Covers multiple distinct capabilities
- Has independent, reusable components

**Merge skills when:**
- Multiple small skills always used together
- Overlap in implementation
- Can be combined without losing clarity

### Updating Skills

Skills should evolve as you:
- Learn better approaches
- Discover new patterns
- Gain experience

**Update immediately when:**
- You find a better way
- Standards change
- You identify missing patterns

---

## 📊 Example Skill

See `core/problem-solving.md` template:

```markdown
# Problem Solving Framework

**Category:** core

**Brief Description:** Systematic approach to breaking down and solving complex problems

---

## When to Use This Skill

Load this skill when:
- Facing a complex problem without obvious solution
- Need to break down a large challenge
- Multiple possible approaches exist
- Requirements are unclear

---

## How It Works

### 1. Define the Problem
- What exactly are we trying to solve?
- What are the constraints?
- What does success look like?

### 2. Break It Down
- Decompose into smaller sub-problems
- Identify dependencies
- Find the simplest piece to start with

### 3. Explore Solutions
- Brainstorm multiple approaches
- Consider trade-offs
- Prototype if needed

### 4. Implement & Iterate
- Start with minimal viable solution
- Test and validate
- Refine based on feedback

---

## Dependencies

**Related skills:**
- `research.md` - For investigating unknowns
- `analysis.md` - For evaluating options
```

---

## 💡 Tips

1. **Start Simple:** Create basic skills first, add details as you use them
2. **Be Specific:** Focus each skill on one capability
3. **Add Examples:** Real examples make skills more useful
4. **Link Generously:** Connect related skills and context
5. **Update Often:** Skills should reflect your current best practices

---

**Questions?** See `/Users/coreyyoung/Claude/context/CLAUDE.md` for complete PAI documentation.
