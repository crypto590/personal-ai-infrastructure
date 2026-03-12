# Knowledge Retrieval Workflow

## Purpose

Search Obsidian vault for prior research, notes, decisions, and context before starting work. Prevents rework, surfaces past decisions, and ensures continuity across sessions.

## When to Use

- Before starting any non-trivial task
- When the user asks about something that may already be documented
- Before making architectural decisions (check for prior decisions)
- When onboarding to an unfamiliar area of the project

## Search Strategies

### 1. Keyword Search

Broadest approach. Start here when you have a general topic.

```bash
# Search for relevant terms
obsidian vault=The_Hub search query="authentication"

# Try multiple related terms
obsidian vault=The_Hub search query="JWT tokens"
obsidian vault=The_Hub search query="auth middleware"
```

### 2. Tag-Based Discovery

Find notes organized by category. Good when you know the domain.

```bash
# List all tags to see what's available
obsidian vault=The_Hub tags

# Search for tagged content
obsidian vault=The_Hub search query="#architecture"
obsidian vault=The_Hub search query="#decision"
obsidian vault=The_Hub search query="#project/backend"
```

### 3. Backlink Exploration

Find notes that reference a known topic. Good for discovering related context you didn't know existed.

```bash
# What links TO this note?
obsidian vault=The_Hub backlinks file="Auth Architecture"

# What does this note link OUT to?
obsidian vault=The_Hub links file="Auth Architecture"
```

### 4. Property-Based Filtering

Search by metadata when notes use structured frontmatter.

```bash
# Find notes with specific properties
obsidian vault=The_Hub search query="status: active"
obsidian vault=The_Hub search query="priority: high"
```

### 5. Link Graph Traversal

Follow the knowledge graph from a starting note. Best for deep exploration.

```bash
# Start from a known note
obsidian vault=The_Hub read file="Project Alpha"

# Follow outgoing links discovered in the note
obsidian vault=The_Hub read file="Auth Architecture"
obsidian vault=The_Hub read file="API Design Decisions"

# Check what else links to those notes
obsidian vault=The_Hub backlinks file="Auth Architecture"
```

## Full Retrieval Workflow

Follow this sequence before starting work on a topic:

### Step 1: Broad Search

```bash
obsidian vault=The_Hub search query="payments"
obsidian vault=The_Hub search query="stripe"
obsidian vault=The_Hub search query="billing"
```

### Step 2: Read Relevant Notes

Based on search results, read the most relevant notes:

```bash
obsidian vault=The_Hub read file="Payments Architecture"
obsidian vault=The_Hub read file="Stripe Integration Notes"
```

### Step 3: Explore Connections

```bash
obsidian vault=The_Hub backlinks file="Payments Architecture"
obsidian vault=The_Hub links file="Payments Architecture"
```

### Step 4: Check for Past Decisions

```bash
obsidian vault=The_Hub search query="decision payment"
obsidian vault=The_Hub search query="#decision #payments"
```

### Step 5: Summarize and Proceed

After gathering context, summarize what you found before starting work. Mention:
- Relevant prior decisions and their rationale
- Existing patterns or conventions discovered
- Open questions noted in previous sessions
- Related notes the user may want to review

## Example: Before Implementing a Payment System

```bash
# 1. Search broadly
obsidian vault=The_Hub search query="payments"
obsidian vault=The_Hub search query="stripe"
obsidian vault=The_Hub search query="checkout"

# 2. Read what comes up
obsidian vault=The_Hub read file="Payment Flow Design"

# 3. Check for decisions
obsidian vault=The_Hub search query="#decision #payments"

# 4. Explore the graph
obsidian vault=The_Hub backlinks file="Payment Flow Design"

# 5. Check for unresolved items
obsidian vault=The_Hub search query="TODO payment"
obsidian vault=The_Hub tasks file="Payment Flow Design"
```

Then report findings to the user:

> Found 3 related notes. `Payment Flow Design` documents a prior decision to use Stripe Checkout Sessions (DEC-038). `Webhook Handler Patterns` has the retry logic conventions. There's an open task to handle subscription renewals. Proceeding with these conventions in mind.

## Tips

- Search multiple synonyms (e.g., "auth", "authentication", "login", "credentials")
- Check `obsidian vault=The_Hub orphans` periodically to find isolated notes that may be relevant but unlinked
- Use `obsidian vault=The_Hub unresolved` to find broken links that may indicate missing documentation
- When you find useful context, mention the note names so the user knows where the information came from
