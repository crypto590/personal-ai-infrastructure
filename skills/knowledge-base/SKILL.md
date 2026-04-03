---
name: knowledge-base
effort: medium
context: fork
agent: kb-builder
argument-hint: "[ingest|compile|query|lint|list|create|status] [topic] [args]"
description: "LLM-compiled knowledge bases from clipped articles. Ingest from Clippings/, compile wikis, query, lint. Karpathy-style KB workflow."
metadata:
  last_reviewed: 2026-04-02
  review_cycle: 90
  hub_path: /Users/coreyyoung/Desktop/The_Hub
  kb_path: /Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases
  clippings_path: /Users/coreyyoung/Desktop/The_Hub/Clippings
---

# Knowledge Base — LLM-Compiled Wiki System

## Overview

Based on Andrej Karpathy's LLM Knowledge Base workflow. Raw source material (clipped articles, papers, images) is collected in `raw/`, then compiled by an LLM into a structured, interlinked markdown wiki viewable in Obsidian. The LLM maintains all indexes, summaries, concept articles, and cross-references. You rarely edit the wiki manually.

## Workflow

```
Clip article → Clippings/ → /kb ingest → {topic}/raw/
                                              ↓
                                    /kb compile → wiki/
                                              ↓
                              _index.md + concepts/ + references/
                                              ↓
                                    /kb query → outputs/
                                              ↓
                                    /kb lint → health report
```

## Key Paths

| Path | Purpose |
|------|---------|
| `/Users/coreyyoung/Desktop/The_Hub/Clippings/` | Web Clipper inbox |
| `/Users/coreyyoung/Desktop/The_Hub/Knowledge-Bases/` | All KBs |
| `{kb}/raw/` | Source documents (never modified by LLM) |
| `{kb}/wiki/` | LLM-compiled wiki (LLM's domain) |
| `{kb}/wiki/_index.md` | Master index (auto-maintained) |
| `{kb}/wiki/_summaries.md` | Source summaries (auto-maintained) |
| `{kb}/wiki/concepts/` | Concept articles with backlinks |
| `{kb}/wiki/references/` | Per-source summaries |
| `{kb}/outputs/` | Query results, slides, reports |
| `{kb}/images/` | Local images |

## Commands

- `/kb ingest` — Sort clippings into KBs by topic
- `/kb compile [topic]` — Build/update wiki from raw sources
- `/kb query "question" [topic]` — Research questions against wiki
- `/kb lint [topic]` — Health check (gaps, broken links, inconsistencies)
- `/kb list` — List all KBs with stats
- `/kb create <topic>` — Scaffold a new KB
- `/kb status` — Pending clippings + KB stats

## Design Principles

1. **Clippings are the inbox** — clip freely, sort later
2. **Raw is sacred** — LLM never modifies source documents
3. **Wiki is the LLM's domain** — user reads, LLM writes
4. **Indexes replace RAG** — auto-maintained `_index.md` and `_summaries.md` let the LLM find what it needs without vector search
5. **Outputs feed back** — Q&A results can be filed back into the wiki
6. **Obsidian-native** — `[[wikilinks]]`, YAML frontmatter, callouts, Marp slides
