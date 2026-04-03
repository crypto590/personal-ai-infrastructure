---
description: "Manage LLM Knowledge Bases — ingest clippings, compile wiki, query, lint. Usage: /kb <command> [args]"
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
