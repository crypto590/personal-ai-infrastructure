# Agent Output Context

Automated transcript collection from SubagentStop hooks.

## Purpose

This directory stores complete agent transcripts for:
- **Agent Evaluation**: Review agent performance and decision-making
- **Prompt Refinement**: Identify patterns in agent failures/successes
- **Context Handoff Debugging**: Trace how information flows between agents
- **Learning & Documentation**: Real examples of agent reasoning

## Structure

```
agent-output-context/
├── 2025-11-20/
│   ├── a1b2c3d4/          # Session ID (first 8 chars of agent_id)
│   │   ├── 001-solution-architect.jsonl
│   │   ├── 002-ui-ux-designer.jsonl
│   │   ├── 003-react-developer.jsonl
│   │   └── 004-performance-engineer.jsonl
│   └── e5f6g7h8/          # Different session
│       ├── 001-database-engineer.jsonl
│       └── 002-python-web-scraper.jsonl
└── 2025-11-21/
    └── ...
```

**Organization:**
- **Date**: `YYYY-MM-DD` format
- **Session ID**: First 8 characters of agent_id (groups related agents)
- **Sequential Number**: `001`, `002`, `003` (order agents ran)
- **Agent Name**: Identifies which agent produced the transcript

## Transcript Format

Each `.jsonl` file is JSON Lines format containing the complete agent conversation:

```jsonl
{"role": "user", "content": "Design architecture for..."}
{"role": "assistant", "content": "I'll design a microservices architecture..."}
{"role": "user", "content": "..."}
```

Parse with:
```python
import json

with open('001-solution-architect.jsonl') as f:
    for line in f:
        msg = json.loads(line)
        print(f"{msg['role']}: {msg['content'][:100]}...")
```

## How It Works

**SubagentStop Hook** (`hooks/subagent_stop.py`):
1. Receives SubagentStop event with `agent_id` and `agent_transcript_path`
2. Copies transcript to organized directory structure
3. Numbers sequentially within session
4. Logs save location

**Automatic Collection** (Claude Code 2.0.42+):
- No manual intervention needed
- Transcripts saved automatically when agents complete
- Grouped by session for easy pipeline analysis

## Use Cases

### 1. Agent Performance Review
```bash
# Find all react-developer transcripts
find . -name "*react-developer.jsonl"

# Review recent failures
grep -l "error\|failed" **/*.jsonl
```

### 2. Prompt Iteration
```bash
# Check if agents are following PAI format
grep -c "📋 SUMMARY" **/*.jsonl

# Find agents using npm instead of bun
grep -l "npm install" **/*.jsonl
```

### 3. Session Flow Analysis
```bash
# View complete agent pipeline for a session
ls -lh 2025-11-20/a1b2c3d4/

# See what architect decided before implementer ran
cat 2025-11-20/a1b2c3d4/001-solution-architect.jsonl
```

### 4. Context Handoff Debugging
```bash
# "Why did react-developer make this choice?"
# → Check what solution-architect said before it
cat 2025-11-20/a1b2c3d4/001-solution-architect.jsonl | grep "architecture\|design"
cat 2025-11-20/a1b2c3d4/002-react-developer.jsonl | head -n 20
```

## Cleanup

Transcripts can grow large. Periodically clean old sessions:

```bash
# Remove transcripts older than 30 days
find ~/.claude/agent-output-context -type d -name "2025-*" -mtime +30 -exec rm -rf {} \;

# Or keep only last 7 days
find ~/.claude/agent-output-context -type d -name "2025-*" -mtime +7 -exec rm -rf {} \;
```

## Analysis Tools (Future)

See `/Users/coreyyoung/.claude/tools/` for analysis scripts (to be created):
- `eval-agents.py` - Performance metrics across sessions
- `compare-prompts.py` - Before/after prompt changes
- `trace-pipeline.py` - Visualize agent handoff flow

## Configuration

Controlled by `hooks/subagent_voice.py`:
- `OUTPUT_DIR`: Storage location (default: `~/.claude/agent-output-context`)
- Session ID format: First 8 chars of `agent_id`
- Sequential numbering per session

## Requirements

- Claude Code 2.0.42+ (for `agent_id` and `agent_transcript_path` metadata)
- SubagentStop hook configured in `settings.json`

## Privacy Note

**Transcripts contain complete agent conversations including:**
- User prompts and questions
- Agent responses and reasoning
- Code snippets and file paths
- Project-specific context

**Security:**
- This directory is in `~/.claude/` (private, not committed to git)
- Should be included in `.gitignore` if you version control PAI system
- Contains potentially sensitive project information
- Review before sharing transcripts externally
