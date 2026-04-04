---
description: "Manage LLM Knowledge Bases — ingest, compile, query, lint, repo. Usage: /kb <command> [args]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent, WebFetch, WebSearch, AskUserQuestion
---

# Knowledge Base Manager

Manage LLM-compiled knowledge bases in `/Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases/`.

**Hub root:** `/Users/coreyyoung/Desktop/The_Hub`
**Clippings inbox:** `/Users/coreyyoung/Desktop/The_Hub/Clippings/`
**KB root:** `/Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases/`

## Logging

Every KB has a `wiki/log.md` — an append-only chronological record of all operations. The LLM appends to it automatically on every ingest, compile, query, and lint. **Never delete or rewrite entries.**

**Entry format:**
```markdown
## [YYYY-MM-DD] operation | Subject
Brief description of what happened.
- Files touched, sources processed, queries answered, issues found
```

**Example entries:**
```markdown
## [2026-04-04] ingest | AutoAgent article
Ingested 1 source from Clippings/. Created reference article, updated 3 concept pages.
- New: references/autoagent-self-optimizing-agents.md
- Updated: concepts/self-optimizing-agents.md, concepts/harness-engineering.md, concepts/meta-agent-task-agent-split.md

## [2026-04-04] compile | Full recompile
Recompiled wiki from 5 raw sources. 7 concept articles, 5 reference articles.

## [2026-04-04] query | "What distinguishes harness engineering from prompt engineering?"
Synthesized answer from 3 concept articles. Filed to outputs/query-2026-04-04-harness-vs-prompt.md.
- User filed output back into wiki as concepts/harness-vs-prompt-engineering.md

## [2026-04-04] lint | Health check
Found 2 orphan pages, 1 missing concept, 0 contradictions.
- Suggested questions: "How does model empathy relate to agent overfitting?"
- Suggested sources: search for papers on LLM self-correction benchmarks
```

The log is parseable: `grep "^## \[" wiki/log.md | tail -5` gives the last 5 entries.

## Commands

Parse the user's argument to determine which command to run. **If no argument is given, run the full loop automatically.**

### `/kb` (no args) — Full loop

Run the entire pipeline in sequence:

1. **Status** — show pending clippings count and KB stats
2. **Ingest** — sort all clippings into KBs (auto-create new KBs as needed, ask user to confirm new topic names)
3. **Compile** — compile all KBs that received new raw/ files
4. **Lint** — run health check on all compiled KBs, report gaps and suggestions

Report a summary at the end: what was ingested, what was compiled, any gaps found. Append log entries for each operation.

### `/kb ingest` — Sort clippings into KBs

1. Read all `.md` files in `Clippings/`
2. For each clipping, read its content and determine the best topic KB
3. If no matching KB exists, suggest creating one (ask user)
4. Move the file to `Knowledge-Bases/{topic}/raw/` using `mv`
5. Download any remote images referenced in the article to `Knowledge-Bases/{topic}/images/` and update image links to local paths
6. Append a log entry to each KB's `wiki/log.md` listing what was ingested
7. Report what was sorted where

**Auto-create KB structure when needed:**
```
{topic}/
├── raw/
├── wiki/
│   ├── concepts/
│   ├── references/
│   ├── log.md
│   └── _schema.md
├── outputs/
└── images/
```

### `/kb compile [topic]` — Build/update wiki from raw sources

Spawn a `kb-builder` agent to compile the wiki. If no topic specified, compile all KBs that have new raw/ files since last compile.

The agent will:
1. Read all files in `{topic}/raw/`
2. Generate/update `wiki/_index.md` — master index of all concepts and references
3. Generate/update `wiki/_summaries.md` — one-paragraph summary of each source
4. For each source, create/update `wiki/references/{source-name}.md` with:
   - Title, author, date, source URL (from frontmatter)
   - Key points and takeaways
   - Backlinks to concept articles
5. Identify concepts across sources, create/update `wiki/concepts/{concept}.md` with:
   - Definition and explanation
   - Cross-references to sources that discuss it
   - Connections to other concepts
   - Backlinks using `[[wikilinks]]`
6. Update `_index.md` with the full concept map and source list
7. Append a log entry to `wiki/log.md` summarizing what was compiled/updated

### `/kb query "question" [topic]` — Research questions against the wiki

1. If topic specified, scope to that KB. Otherwise search all KBs.
2. Read `_index.md` and `_summaries.md` to understand what's available
3. If the KB has a `_schema.md`, read it for domain-specific conventions
4. Read relevant concept and reference articles
5. Synthesize an answer with citations (`[[backlinks]]` to sources)
6. Save the Q&A output to `{topic}/outputs/query-{timestamp}.md`
7. **Default: file the output back into the wiki** — ask user to confirm. Good answers are wiki pages. A comparison, analysis, or synthesis is valuable and shouldn't disappear into chat history. If confirmed, create/update a concept or reference article from the output.
8. Append a log entry to `wiki/log.md`

### `/kb lint [topic]` — Health check the wiki

1. Read all raw/ sources and all wiki/ articles
2. Read `wiki/log.md` to understand recency — prioritize checking recently-touched pages
3. **Structural checks:**
   - Sources in raw/ not yet summarized in references/
   - Broken `[[wikilinks]]`
   - Orphan pages with no inbound links
   - Concepts mentioned but without their own article
   - Missing cross-references between related concepts
4. **Content checks:**
   - Inconsistent or contradictory claims across articles
   - Stale claims that newer sources have superseded
   - Thin articles that need expansion
5. **Research driver — this is the key upgrade:**
   - Suggest new concept articles based on patterns across sources
   - **Suggested questions:** connections worth exploring, contradictions to resolve, synthesis opportunities (e.g., "How does X relate to Y across these 3 sources?")
   - **Suggested sources:** specific searches, papers, articles, or topics that would fill identified gaps (e.g., "Search for benchmarks on LLM self-correction to strengthen the agent-overfitting concept")
   - **Suggested queries:** `/kb query` commands the user could run to generate valuable new wiki pages
6. Append a log entry to `wiki/log.md`
7. Output report to `{topic}/outputs/lint-{timestamp}.md`

### `/kb list` — List all knowledge bases

List all KBs with article counts and last modified dates.

### `/kb create <topic>` — Create a new empty KB

Create the directory structure for a new topic KB.

### `/kb repo <path> [name]` — Create KB from a codebase

Build a knowledge base from a git repository. The agent scans the repo, extracts key artifacts into `raw/`, and compiles a wiki that any agent (or human) can use to understand the codebase.

**If no name is given**, derive it from the repo directory name (e.g., `/path/to/athlead` → `athlead`).

#### Step 1: Scaffold

Create the KB at `Knowledge-Bases/{name}/` with the standard structure, plus a `repo.md` metadata file:

```markdown
---
title: "{name} Codebase KB"
type: repo
repo_path: "{absolute path}"
last_synced: {ISO date}
---
```

#### Step 2: Extract raw artifacts

Scan the repo and copy key files into `raw/`. Do NOT copy the entire repo. Extract:

**Always extract (if they exist):**
- `README.md`, `CLAUDE.md`, any root-level docs
- Package manifests: `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Gemfile`, etc.
- Config files: `tsconfig.json`, `docker-compose.yml`, `.env.example`, etc.
- CI/CD: `.github/workflows/*.yml`, `Dockerfile`
- API schemas: `openapi.yaml`, `schema.graphql`, `*.proto`
- Database schemas: migration files, `schema.prisma`, `drizzle/` schemas

**Generate and extract:**
- `_tree.md` — output of `tree -L 3 -I 'node_modules|.git|dist|build|target|__pycache__'` as a markdown file
- `_git-summary.md` — recent git log (`git log --oneline -30`), branch list, contributors
- `_entry-points.md` — identify and concatenate key entry point files (main.ts, index.ts, app.py, main.rs, etc.) with file path headers
- `_architecture.md` — any docs/architecture files, ADRs (Architecture Decision Records), or design docs found in `docs/`, `doc/`, `adr/`, or similar

**Smart extraction for large repos:**
- For monorepos, extract each package/app's manifest and entry point
- Skip generated files, lock files, vendored deps
- Cap individual files at 500 lines — truncate with a note if longer
- Total raw/ should stay under ~50 files to keep compilation manageable

#### Step 3: Compile

Spawn the `kb-builder` agent to compile the wiki, but with **codebase-specific article types**:

**Reference articles** (`wiki/references/`):
- One per major module, service, or package
- Summarizes purpose, key exports, dependencies, entry points

**Concept articles** (`wiki/concepts/`):
- Domain concepts the code implements (e.g., auth flow, payment processing, data pipeline)
- Architecture patterns used (e.g., monorepo structure, API gateway, event sourcing)
- Key technical decisions and trade-offs

**Index** (`wiki/_index.md`):
- Module map: what each part of the codebase does
- Dependency graph: how modules relate
- Tech stack summary
- "Start here" guide: where to look first for common tasks

**Summaries** (`wiki/_summaries.md`):
- One-line summary per raw artifact

#### Step 4: Report

Show what was extracted, what was compiled, and suggest next steps (e.g., "run `/kb repo <path>` again after major changes to re-sync").

### `/kb sync [name]` — Re-sync a repo KB

Re-run extraction on an existing repo KB to pick up changes. Reads `repo.md` for the path, re-extracts artifacts, and recompiles only what changed.

### `/kb status` — Show pending clippings + KB stats

1. Count files in Clippings/
2. For each KB, show: raw count, wiki article count, last compile date, last log entry

## Per-KB Schema (`_schema.md`)

Each KB can have an optional `wiki/_schema.md` that tells the LLM how to compile and maintain that specific wiki. This is the key configuration file — it's what makes the LLM a disciplined wiki maintainer for a specific domain rather than a generic one.

**Auto-generated on `/kb create`** with sensible defaults. Co-evolved during compilation as the LLM and user discover what works for the domain.

**Default template:**
```markdown
---
title: "{topic} KB Schema"
created: {ISO date}
last_updated: {ISO date}
---

# {topic} — Wiki Schema

## Compilation Conventions
- **Concept granularity:** One concept per file. Split when a concept has >3 distinct sub-topics.
- **Reference style:** Faithful summaries with key takeaways. Don't editorialize.
- **Cross-referencing:** Use [[wikilinks]] liberally. Every concept should link to related concepts and source references.
- **Frontmatter tags:** Each wiki page gets `tags`, `sources` (count), `last_updated` in YAML frontmatter.

## Domain-Specific Notes
<!-- The LLM updates this section as it learns the domain -->
<!-- e.g., "This KB is research-heavy — prioritize citing methodology and sample sizes" -->
<!-- e.g., "This KB tracks a codebase — emphasize architecture decisions and dependency relationships" -->

## Output Formats
- Default: markdown wiki pages
- Queries: markdown with citations
<!-- Add domain-specific formats as needed, e.g., Marp slides, comparison tables -->
```

The schema is **not required** — KBs work fine without one. But for domains where you want specific compilation behavior (e.g., a research KB that tracks methodology rigor, or a codebase KB that emphasizes architecture), it's the right lever.

## Search at Scale

At small scale (~5 KBs, <100 wiki pages), reading `_index.md` to navigate is sufficient. As KBs grow past ~50 wiki pages, consider adding a proper search tool:

- **[qmd](https://github.com/tobi/qmd)** — Local search engine for markdown files. Hybrid BM25/vector search with LLM re-ranking. Has both CLI and MCP server modes.
- **Simple grep fallback** — The LLM can always shell out to `grep -r` across wiki files as a baseline.
- **Future:** When a KB exceeds 50 wiki pages, `/kb lint` should flag this and suggest setting up qmd.

## Formatting Rules

- All generated wiki files use Obsidian-compatible markdown
- Use `[[wikilinks]]` for internal cross-references
- Use YAML frontmatter on all generated files
- Use `> [!note]` callouts for key insights
- Use `> [!source]` callouts for citations
- Keep concept articles focused — one concept per file
- Keep reference articles as faithful summaries — don't editorialize
