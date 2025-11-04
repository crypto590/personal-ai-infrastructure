# Token Efficiency Guide

Strategies for optimizing token usage in your PAI while maintaining full capability.

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [best-practices.md](best-practices.md) - General best practices
- [structure.md](structure.md) - PAI organization
- [skill-template.md](skill-template.md) - Skill structure

---

## Table of Contents

- [Understanding Token Usage](#understanding-token-usage)
- [Progressive Disclosure Strategy](#progressive-disclosure-strategy)
- [File Size Guidelines](#file-size-guidelines)
- [Optimization Techniques](#optimization-techniques)
- [Measuring Efficiency](#measuring-efficiency)

---

## Understanding Token Usage

### What Are Tokens?

Tokens are chunks of text that Claude processes. Roughly:
- 1 token ≈ 4 characters
- 1 token ≈ 0.75 words
- 100 tokens ≈ 75 words
- 1,000 tokens ≈ 750 words

**Example:**
```
"The quick brown fox" = 4 words = ~5 tokens
"import { FastifyInstance } from 'fastify'" = ~10 tokens
```

### Why Token Efficiency Matters

**Context window limits:**
- Each Claude model has a context window (e.g., 200k tokens)
- Your PAI, conversation history, and response all share this window
- Efficient loading = more room for conversation and responses

**Cost considerations:**
- API usage charged per token
- Efficient PAI = lower costs

**Response quality:**
- Less clutter = more focused responses
- Claude can "see" relevant information better
- Reduces need to re-explain context

### Token Usage Without PAI

**Traditional approach (loading everything):**
```
Identity: ~2,000 tokens
All skills: ~50,000 tokens
All context: ~100,000 tokens
Conversation: ~5,000 tokens
Response budget: ~43,000 tokens
Total: ~157,000 tokens
```

**Problems:**
- Little room for complex conversations
- Expensive per request
- Most information unused
- Claude must sift through noise

### Token Usage With PAI

**PAI approach (progressive loading):**
```
Identity: ~500 tokens (profile + preferences)
Skill metadata: ~300 tokens (all skill descriptions)
Skill content (on demand): ~1,500 tokens (one SKILL.md)
Context (on demand): ~3,000 tokens (one context file)
Conversation: ~5,000 tokens
Response budget: ~190,000 tokens
Total typical usage: ~10,300 tokens
```

**Benefits:**
- 93% reduction in baseline usage
- Room for complex conversations
- Much lower cost
- Focused, relevant information

---

## Progressive Disclosure Strategy

### Three-Level Loading

**Level 1: Metadata (Always Loaded)**
- Identity (profile + preferences): ~500 tokens
- Skill descriptions: ~300 tokens
- Total: ~800 tokens

**Purpose:** Give Claude awareness of capabilities without loading full content

**What it includes:**
- Who you are
- What skills exist
- Brief description of each skill
- When to trigger each skill

**Level 2: Full Skill (On Trigger)**
- SKILL.md main file: ~1,500 tokens
- Loaded when: User question matches trigger conditions
- Total so far: ~2,300 tokens

**Purpose:** Provide enough detail to answer basic questions, reference deeper content

**What it includes:**
- Core principle
- Brief overview
- Decision framework
- References to detailed files

**Level 3: Deep Dive (As Needed)**
- Detail files: ~3,000-5,000 tokens each
- Context files: ~1,500-5,000 tokens each
- Loaded when: Specific topics needed
- Total typical: ~6,000-10,000 tokens

**Purpose:** Comprehensive information on specific topics

**What it includes:**
- Detailed patterns
- Complete examples
- API reference
- Advanced topics

### Example Progressive Loading

**Query:** "How should I structure my Swift app?"

**Level 1 (Always loaded):**
```
✓ Identity (~500 tokens)
✓ Skill metadata (~300 tokens)
  - Sees swift-architecture exists
  - Sees it covers architecture decisions
```

**Level 2 (Triggered):**
```
✓ swift-architecture/SKILL.md (~1,500 tokens)
  - Reads overview
  - Sees Level 1, 2, 3 architecture
  - Sees references to detail files
Total: ~2,300 tokens
```

**Response:** Can answer with progressive architecture overview

---

**Query:** "Show me SOLID principles in Swift ViewModels"

**Level 1 & 2 (Same as above):**
```
✓ Identity (~500 tokens)
✓ Skill metadata (~300 tokens)
✓ swift-architecture/SKILL.md (~1,500 tokens)
```

**Level 3 (Needed for this query):**
```
✓ VIEWMODEL_PATTERNS.md (~3,500 tokens)
✓ SOLID_PRINCIPLES.md (~5,000 tokens)
Total: ~10,800 tokens
```

**Response:** Can provide detailed SOLID examples in ViewModels

---

## File Size Guidelines

### Token Estimates

**Lines to tokens (rough conversion):**
- 50 lines ≈ 1,000 tokens
- 100 lines ≈ 2,000 tokens
- 150 lines ≈ 3,000 tokens
- 300 lines ≈ 6,000 tokens
- 500 lines ≈ 10,000 tokens

**Actual tokens depend on:**
- Code examples (more tokens per line)
- Markdown formatting (links, headers add tokens)
- Language (some words are multiple tokens)

### Skill File Targets

**SKILL.md (main file):**
- Target: 50-150 lines
- Tokens: 1,000-1,500 tokens
- Maximum: 200 lines / 2,000 tokens

**Detail files:**
- Target: 200-500 lines per file
- Tokens: 3,000-5,000 tokens per file
- Maximum: 500 lines / 10,000 tokens

**Total skill (all files):**
- Maximum: 15,000 tokens if all loaded
- Typical: 4,500 tokens (SKILL + one detail)

### Context File Targets

**Simple reference:**
- Target: 100-300 lines
- Tokens: 1,500-3,000 tokens

**Comprehensive reference:**
- Target: 200-500 lines
- Tokens: 3,000-5,000 tokens
- Use table of contents

### When to Split Files

**Split when:**
- Main file exceeds 150 lines
- Total content exceeds 500 lines
- Multiple distinct sub-topics
- Some content is rarely needed

**Keep together when:**
- Tightly coupled topics
- Frequently used together
- Total under 500 lines
- Splitting would hurt usability

---

## Optimization Techniques

### Technique 1: Front-Load Important Content

**Why:** Claude often previews files with `head -100` to decide what to load

**How:**
- Put critical information in first 100 lines
- Use clear headings early
- Include table of contents at top
- Summary before details

**Example structure:**
```markdown
# Topic

[Brief description]

**Referenced from**: [links]

## Table of Contents
[...]

## Overview
[Critical information here - first 100 lines]

## Detailed Section 1
[Details can come later]
```

### Technique 2: Use Table of Contents

**Why:** Shows structure even in partial reads

**When:** Files >100 lines

**Example:**
```markdown
## Table of Contents

- [Overview](#overview)
- [Section 1](#section-1)
  - [Subsection 1.1](#subsection-11)
- [Section 2](#section-2)
```

### Technique 3: Extract Rarely-Needed Content

**Identify content that:**
- Advanced users need but beginners don't
- Edge cases and gotchas
- Historical context (old versions)
- Exhaustive reference (when summary suffices)

**Extract to:**
- Separate detail file
- Collapsible `<details>` section
- "Advanced Topics" appendix

**Example:**
```markdown
## Basic Usage

[Common patterns most users need]

## Advanced Patterns

[Less common patterns]

<details>
<summary>Legacy v1.x patterns (deprecated)</summary>

[Historical patterns for reference]
</details>
```

### Technique 4: Avoid Duplication

**Problem:** Same information in multiple files wastes tokens

**Solution:**
- Single source of truth
- Reference, don't repeat
- Use links to detailed coverage

**Bad:**
```markdown
# File 1
[Complete explanation of SOLID principles]

# File 2
[Complete explanation of SOLID principles again]
```

**Good:**
```markdown
# File 1
[Complete explanation of SOLID principles]

# File 2
For SOLID principles, see [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md).
```

### Technique 5: Compress Examples

**Don't sacrifice clarity, but:**
- Remove unnecessary comments
- Use concise variable names in examples
- Show key parts, link to full code
- Use "..." to indicate omitted code

**Verbose example (unnecessary tokens):**
```typescript
// This is a function that handles user login
// It takes an email and password as parameters
// It returns a promise that resolves to a user object
async function handleUserLogin(
  userEmailAddress: string, 
  userPassword: string
): Promise<UserObject> {
  // First we validate the input
  if (!userEmailAddress || !userPassword) {
    throw new Error('Missing required fields');
  }
  
  // Then we call the authentication service
  const authenticatedUser = await authService.login(
    userEmailAddress, 
    userPassword
  );
  
  // Finally we return the authenticated user
  return authenticatedUser;
}
```

**Concise example (same information, fewer tokens):**
```typescript
async function login(email: string, password: string): Promise<User> {
  if (!email || !password) throw new Error('Missing fields');
  return await authService.login(email, password);
}
```

### Technique 6: Use Links Strategically

**Internal links (no token cost):**
- Link to other PAI files freely
- Use anchor links to specific sections
- Reference instead of repeating

**External links:**
- Link to official docs instead of copying
- Use sparingly (describe what's at link)
- Reference version-specific docs

### Technique 7: Efficient Code Examples

**Show complete examples, but:**
- One example is often enough
- Don't show every variation
- Use comments to explain variations
- Link to more examples in detail file

**Pattern:**
```markdown
## Basic Pattern

[One complete example]

## Variations

This pattern can be adapted for:
- Variation 1: [Brief description]
- Variation 2: [Brief description]

See [EXAMPLES.md](EXAMPLES.md) for complete variations.
```

---

## Measuring Efficiency

### How to Measure Token Usage

**Method 1: Ask Claude**
```
You: "How many tokens did you load for that question?"
Claude: [Will tell you approximate token counts]
```

**Method 2: Calculate from files**
```
Lines × 2 ≈ tokens (rough estimate)
```

**Method 3: Token counter tools**
- Use online token calculators
- Anthropic API returns token counts
- Some editors have token count plugins

### Target Metrics

**Baseline (always loaded):**
- Target: <1,000 tokens
- Actual: Identity (~500) + metadata (~300) ≈ 800 tokens

**Simple query:**
- Target: <3,000 tokens total
- Actual: Baseline + SKILL.md ≈ 2,300 tokens

**Complex query:**
- Target: <10,000 tokens total
- Actual: Baseline + SKILL + 2 detail files ≈ 8,800 tokens

**Maximum (comprehensive answer):**
- Target: <20,000 tokens total
- Actual: Baseline + SKILL + 4-5 detail files ≈ 18,000 tokens

### Efficiency Ratios

**Good progressive disclosure:**
```
Simple:Complex:Maximum = 1:4:8

Example:
2,300 (simple) : 8,800 (complex) : 18,000 (max)
```

**Poor progressive disclosure:**
```
Simple:Complex:Maximum = 1:1:1

Example:
18,000 (simple) : 18,000 (complex) : 18,000 (max)
[Loading everything every time]
```

### Monitoring Over Time

**Track quarterly:**
- Total PAI token count
- Average tokens per query
- Most frequently loaded files
- Rarely loaded files (candidates for archiving)

**Signs of token bloat:**
- Simple queries using >5,000 tokens
- Baseline growing over 1,500 tokens
- Every query loading 10+ files
- Skills growing past 20,000 tokens total

**When to optimize:**
- Baseline exceeds 1,500 tokens → Trim identity/metadata
- Skills exceed 20,000 tokens → Split into more detail files
- Simple queries exceed 5,000 tokens → Improve progressive disclosure
- Noticed slow responses → Might be token overhead

---

## Optimization Case Study

### Before Optimization

**swift-architecture skill (original):**
```
SKILL.md: 400 lines = ~8,000 tokens
Total: 8,000 tokens
```

**Problem:**
- Every basic Swift question loads full 8,000 tokens
- No progressive disclosure
- Much content rarely needed for simple questions

### After Optimization

**swift-architecture skill (optimized):**
```
SKILL.md: 150 lines = ~1,500 tokens
ARCHITECTURE_LEVELS.md: 300 lines = ~6,000 tokens
VIEWMODEL_PATTERNS.md: 250 lines = ~5,000 tokens
SERVICE_LAYER.md: 250 lines = ~5,000 tokens
SOLID_PRINCIPLES.md: 300 lines = ~6,000 tokens
EXAMPLES.md: 200 lines = ~4,000 tokens
QUICK_REFERENCE.md: 150 lines = ~3,000 tokens

Total if all loaded: ~30,500 tokens
Typical usage: ~4,500 tokens (SKILL + one detail)
```

**Improvement:**
- Simple questions: 8,000 → 1,500 tokens (81% reduction)
- Complex questions: 8,000 → 6,500 tokens (19% reduction)
- Very complex: 8,000 → 10,500 tokens (but much more comprehensive)

**Result:**
- Better progressive disclosure
- More detailed content available
- Lower token usage for common cases
- Scalable to add more content

---

## Quick Reference

| File Type | Target Size | Token Count | When to Split |
|-----------|------------|-------------|---------------|
| SKILL.md | 50-150 lines | 1,000-1,500 | >200 lines |
| Detail file | 200-500 lines | 3,000-5,000 | >500 lines |
| Context | 100-300 lines | 1,500-3,000 | >500 lines |
| Reference | 200-500 lines | 3,000-5,000 | >500 lines |

**Efficiency targets:**
- Baseline: <1,000 tokens
- Simple query: <3,000 tokens
- Complex query: <10,000 tokens
- Maximum: <20,000 tokens

---

## Related Resources

**Organizational:**
- [structure.md](structure.md) - PAI structure
- [best-practices.md](best-practices.md) - General best practices

**Templates:**
- [skill-template.md](skill-template.md) - Includes size guidelines
- [context-template.md](context-template.md) - Includes size guidelines

**Examples:**
- `/Users/coreyyoung/Claude/skills/technical/swift-architecture/` - Optimized example
