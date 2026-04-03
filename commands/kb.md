---
description: "Manage LLM Knowledge Bases — ingest, compile, query, lint, repo. Usage: /kb <command> [args]"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent, WebFetch, WebSearch, AskUserQuestion
---

# Knowledge Base Manager

Manage LLM-compiled knowledge bases in `/Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases/`.

**Hub root:** `/Users/coreyyoung/Desktop/The_Hub`
**Clippings inbox:** `/Users/coreyyoung/Desktop/The_Hub/Clippings/`
**KB root:** `/Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases/`

## Commands

Parse the user's argument to determine which command to run. **If no argument is given, run the full loop automatically.**

### `/kb` (no args) — Full loop

Run the entire pipeline in sequence:

1. **Status** — show pending clippings count and KB stats
2. **Ingest** — sort all clippings into KBs (auto-create new KBs as needed, ask user to confirm new topic names)
3. **Compile** — compile all KBs that received new raw/ files
4. **Lint** — run health check on all compiled KBs, report gaps and suggestions

Report a summary at the end: what was ingested, what was compiled, any gaps found.

### `/kb ingest` — Sort clippings into KBs

1. Read all `.md` files in `Clippings/`
2. For each clipping, read its content and determine the best topic KB
3. If no matching KB exists, suggest creating one (ask user)
4. Move the file to `Knowledge-Bases/{topic}/raw/` using `mv`
5. Download any remote images referenced in the article to `Knowledge-Bases/{topic}/images/` and update image links to local paths
6. Report what was sorted where

**Auto-create KB structure when needed:**
```
{topic}/
├── raw/
├── wiki/
│   ├── concepts/
│   └── references/
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

### `/kb query "question" [topic]` — Research questions against the wiki

1. If topic specified, scope to that KB. Otherwise search all KBs.
2. Read `_index.md` and `_summaries.md` to understand what's available
3. Read relevant concept and reference articles
4. Synthesize an answer with citations (`[[backlinks]]` to sources)
5. Save the Q&A output to `{topic}/outputs/query-{timestamp}.md`
6. Ask user if they want to file the output back into the wiki

### `/kb lint [topic]` — Health check the wiki

1. Read all raw/ sources and all wiki/ articles
2. Check for:
   - Sources in raw/ not yet summarized in references/
   - Broken `[[wikilinks]]`
   - Concepts mentioned but without their own article
   - Inconsistent claims across articles
   - Stale or thin articles that need expansion
3. Suggest new concept articles based on patterns across sources
4. Suggest questions worth investigating (connections, gaps)
5. Output report to `{topic}/outputs/lint-{timestamp}.md`

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
2. For each KB, show: raw count, wiki article count, last compile date

## Formatting Rules

- All generated wiki files use Obsidian-compatible markdown
- Use `[[wikilinks]]` for internal cross-references
- Use YAML frontmatter on all generated files
- Use `> [!note]` callouts for key insights
- Use `> [!source]` callouts for citations
- Keep concept articles focused — one concept per file
- Keep reference articles as faithful summaries — don't editorialize
