# Personal AI Infrastructure (PAI) - Master Context System

## Overview

This is a **Personal AI Infrastructure** based on Daniel Miessler's architecture - a "build once, use everywhere" system where all knowledge, skills, and preferences live in a central location that's available to all projects.

**Architecture Source:** https://danielmiessler.com/blog/personal-ai-infrastructure

---

## 🚀 Mandatory Startup Protocol

**EVERY TIME you begin working, you MUST:**

1. **Read these core files IN THIS ORDER:**
   - `~/.claude/context/CLAUDE.md` (this file)
   - `~/.claude/context/identity/profile.md`
   - `~/.claude/context/identity/preferences.md`

2. **Acknowledge context loading by stating:**
   - "PAI loaded: [Your Name]'s infrastructure ready"
   - Note any skills or knowledge areas you've loaded

3. **Progressive skill loading:**
   - Scan `~/.claude/skills/` directory structure
   - Load skill metadata (descriptions only) for awareness
   - Load full skill content ONLY when triggered by task requirements

---

## 🏗️ PAI Architecture Explained

### Skills-Based with Progressive Disclosure

The PAI uses a **three-level progressive disclosure** system that achieved 92.5% token reduction:

#### **Level 1: Skill Metadata (Always Loaded, ~300 tokens)**
- Skill names and brief descriptions
- Located in each skill's README.md or header
- Provides awareness of available capabilities
- Always in system prompt

#### **Level 2: Full Skill Content (Load on Demand, ~4000 tokens)**
- Complete skill implementation
- Loaded ONLY when task explicitly requires it
- Located in individual skill files

#### **Level 3: Deep Context (Load as Needed)**
- Domain-specific knowledge files
- API documentation
- Framework details
- Loaded progressively based on conversation needs

### How Skills Discovery Works

```
User request → Scan skill metadata → Identify relevant skills → Load full content → Execute task
```

**Example:**
- User: "Build a Next.js API endpoint"
- You scan: `~/.claude/skills/technical/` metadata
- You identify: `web-dev-nextjs.md` skill
- You load: Full Next.js skill + relevant context from `~/.claude/context/knowledge/frameworks/nextjs/`
- You execute: Using loaded knowledge

---

## 📁 Directory Structure Guide

### `~/.claude/skills/` - Capability-Based Skills Library

Skills are organized by **capability type**, NOT by project:

```
skills/
├── core/           # Universal capabilities (problem-solving, writing, research, analysis)
├── technical/      # Programming skills (web-dev, databases, APIs, DevOps)
├── business/       # Business capabilities (analysis, marketing, strategy, finance)
├── domain/         # Domain expertise (payments, underwriting, compliance, industry-specific)
└── personal/       # Personal productivity (health, finance, learning, habits)
```

**Each skill file should contain:**
- **Header:** Brief description (metadata)
- **When to use:** Trigger conditions
- **How it works:** Implementation details
- **Examples:** Usage patterns
- **Dependencies:** Other skills or context required

### `~/.claude/context/` - The Knowledge Brain

Central repository of all knowledge, identity, and preferences:

```
context/
├── CLAUDE.md                    # This master file
├── identity/
│   ├── profile.md              # Who you are, background, expertise
│   ├── preferences.md          # How you like to work
│   └── values.md               # Your principles and decision-making framework
├── knowledge/
│   ├── languages/              # Programming languages (typescript/, swift/, python/)
│   ├── frameworks/             # Tech frameworks (nextjs/, react/, django/)
│   ├── domains/                # Domain expertise (payment-processing/, underwriting/)
│   ├── patterns/               # Design patterns and architectural approaches
│   └── apis/                   # API documentation and integration guides
├── projects/
│   ├── current/                # Active projects for reference
│   └── archive/                # Past projects (lessons learned, patterns)
└── resources/
    ├── tools/                  # Tool documentation and configurations
    └── templates/              # Reusable code templates, boilerplates
```

**Knowledge Organization:**
- Each subdirectory contains markdown files
- Files are modular and reference each other
- Use relative links for cross-references
- Keep files focused on single topics

### `~/.claude/commands/` - Custom Workflows

**Purpose:** Store custom command workflows and automations

**Status:** Empty initially - populate as patterns emerge

**Example future use:**
- `deploy-app.md` - Standard deployment checklist
- `code-review.md` - Code review workflow
- `research-task.md` - Research methodology

### `~/.claude/hooks/` - Context Management

**Purpose:** Ensure PAI context loads properly and validate usage

**Key file:** `context-loader.ts` - Runs on user prompt submit to verify context is loaded

---

## 🎯 Usage Patterns

### Example 1: Programming Task

**Request:** "Build a TypeScript API endpoint with authentication"

**Your workflow:**
1. Load identity/profile.md (understand preferences)
2. Scan skills/technical/ metadata
3. Identify relevant skills:
   - `api-development.md`
   - `typescript-patterns.md`
   - `authentication.md`
4. Load full content of identified skills
5. Load context/knowledge/languages/typescript/
6. Load context/knowledge/patterns/api-design/
7. Execute task using loaded knowledge

### Example 2: Business Task

**Request:** "Analyze payment processing flow for compliance"

**Your workflow:**
1. Load identity/profile.md (understand domain expertise)
2. Scan skills/business/ and skills/domain/ metadata
3. Identify relevant skills:
   - `business-analysis.md`
   - `payment-processing.md`
   - `compliance-review.md`
4. Load full content of identified skills
5. Load context/knowledge/domains/payment-processing/
6. Execute analysis using domain expertise

### Example 3: Research Task

**Request:** "Research best practices for Next.js 15 server actions"

**Your workflow:**
1. Scan skills/core/ for `research.md`
2. Load research skill
3. Scan context/knowledge/frameworks/nextjs/
4. If no existing knowledge, use web search
5. Optionally add findings to context/knowledge/frameworks/nextjs/server-actions.md
6. Provide research summary

---

## 🧭 Core Principles

### 1. Single Source of Truth
- Knowledge lives in ONE place only
- Projects REFERENCE PAI, never duplicate
- Updates cascade automatically to all projects

### 2. Progressive Disclosure
- Load only what's needed, when needed
- Start with metadata, drill down as required
- Minimize token usage while maximizing capability

### 3. Domain Agnostic
- Skills are transferable across projects
- Context is organized by topic, not project
- Reusable everywhere

### 4. Modular & Composable
- Skills combine to solve complex problems
- Each skill is independent and focused
- Context files link together naturally

### 5. Always Learning
- Capture new patterns in skills/
- Document new knowledge in context/
- Refine continuously

---

## 🔗 How Projects Use PAI

### Project CLAUDE.md Structure

Projects should have lightweight CLAUDE.md files that **LINK** to PAI:

```markdown
# Project: MyApp

## Load PAI Skills
- Read: ~/.claude/skills/technical/web-dev-nextjs.md
- Read: ~/.claude/skills/technical/typescript-patterns.md
- Read: ~/.claude/skills/domain/payment-processing.md

## Load Context
- Read: ~/.claude/context/knowledge/frameworks/nextjs/
- Read: ~/.claude/context/knowledge/domains/payment-processing/

## Project-Specific Context
- Database: PostgreSQL on Supabase
- Auth: Clerk
- Deployment: Vercel
- Specific quirks or constraints for THIS project only

## Current Focus
[What you're actively working on]
```

**Key Point:** Project files should be < 100 lines and mostly consist of file path references to PAI + project-specific details.

---

## 📊 Token Efficiency

### Before PAI (Per Request)
- Load all skills: ~20,000 tokens
- Load all context: ~30,000 tokens
- **Total: ~50,000 tokens per request**

### After PAI (Per Request)
- Load skill metadata: ~300 tokens
- Load identity: ~500 tokens
- Load specific skills on demand: ~4,000 tokens
- Load specific context on demand: ~2,000 tokens
- **Total: ~6,800 tokens per request (86% reduction)**

**Progressive loading means:**
- Most responses use < 7,000 tokens
- Complex tasks may use 10,000-15,000 tokens
- Still 70%+ reduction even in complex scenarios

---

## 🛠️ Maintenance & Updates

### Adding New Skills
1. Identify capability category (core/technical/business/domain/personal)
2. Create skill file in appropriate skills/ subdirectory
3. Include brief header description (metadata)
4. Add trigger conditions and examples
5. Update relevant skills/ README.md

### Adding New Context
1. Identify knowledge category (languages/frameworks/domains/patterns/apis)
2. Create markdown file in appropriate context/knowledge/ subdirectory
3. Use focused, single-topic approach
4. Link to related context files
5. Keep identity/ files updated as expertise grows

### Refactoring
- If a skill grows too large, split it
- If context files overlap, consolidate
- Remove outdated knowledge
- Archive old project learnings to projects/archive/

---

## 🎓 Learning Loop

After each significant task:

1. **Capture new patterns** → Add/update skills/
2. **Document new knowledge** → Add/update context/knowledge/
3. **Record project lessons** → Add to projects/archive/
4. **Refine preferences** → Update identity/preferences.md

The PAI gets smarter with every interaction.

---

## 🚦 Quick Reference Commands

**Check PAI structure:**
```bash
tree -L 2 ~/.claude/
```

**List available skills:**
```bash
find ~/.claude/skills -name "*.md" -type f
```

**Search knowledge base:**
```bash
grep -r "search term" ~/.claude/context/knowledge/
```

**Validate PAI:**
```bash
# Ensure core files exist
ls ~/.claude/context/identity/profile.md
ls ~/.claude/context/CLAUDE.md
```

---

## 📚 References

- **Daniel Miessler's PAI Blog:** https://danielmiessler.com/blog/personal-ai-infrastructure
- **Daniel Miessler's GitHub Repo:** https://github.com/danielmiessler/Personal_AI_Infrastructure
- **v0.5.0 Architecture Update:** Skills-based progressive disclosure achieving 92.5% token reduction

---

## ✨ Final Notes

This PAI is your **persistent AI brain** that:
- Knows who you are
- Understands how you work
- Contains all your knowledge and skills
- Works across all projects
- Gets smarter over time

Always start by loading context. Always end by capturing new learnings.

**The PAI is not a static system - it's a living, growing extension of your expertise.**
