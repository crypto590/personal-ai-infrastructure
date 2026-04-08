---
name: Never log per-tool-call to persistent storage
description: Past incident — logging every agent tool call to the memory system spiraled to 100% Mac memory use. Avoid unbounded per-call writes.
type: feedback
---

Never design observability/logging that writes one persistent record per tool call.

**Why:** A previous memory-system implementation logged every agent tool call and spiraled to 100% Mac memory use. The failure mode is: agent subtasks fan out into many tool calls, each call triggers a write (DB insert, file append, in-memory buffer), and the write path either shares memory with Claude or accumulates faster than it drains. The specific trigger is **Agent/Task subagents** because one user prompt can generate hundreds of nested tool calls across multiple sub-Claudes.

**How to apply:**
- **Aggregate at session-end**, not per-call. One hook-triggered summary write per session (total calls, error count, top failing tools, p95 latency, error samples).
- **Keep raw per-call data only in bounded files** that rotate (like the OTel events.jsonl with file exporter rotation). Never tail these into a persistent DB in real time.
- **For drill-down, query the raw files on demand** (grep/jq/duckdb), don't pre-ingest everything.
- **Never put ingestion inside a hook that runs per tool call** (e.g., PostToolUse). Only Stop/SubagentStop/SessionEnd hooks are safe.
- **If a tailer process is necessary**, it must be standalone (not a Claude Code hook), bounded buffer, backpressure-drop-oldest, and target a cloud DB (not local).
- **Red flag phrases in designs**: "log every tool call", "per-call record", "real-time ingest of tool events", "tail events.jsonl to DB", "live event timeline", "WebSocket event stream", "per-event batching" (batching is just polling with extra steps).
- **Specifically: do not propose installing disler/claude-code-hooks-multi-agent-observability or any tool with the same shape (PreToolUse + PostToolUse hooks calling send_event per tool).** Even with the LLM summarizer stripped, even with batched DB writes, the architecture is wrong for analytical observability. The right shape is session-end aggregation reading the session JSONL post-hoc.
- **First-question check before proposing observability:** "Can this question be answered from the session JSONL file *after* the session ends?" If yes — and it almost always is — that is the answer. No hooks per tool call needed.

When in doubt, prefer coarse-grained periodic/session-end writes over fine-grained per-event writes.
