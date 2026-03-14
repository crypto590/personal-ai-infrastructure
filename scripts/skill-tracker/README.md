# Skill Tracker — Self-Improving Skills Loop

Observe → Inspect → Amend → Evaluate

Turns static SKILL.md files into living components that improve based on execution evidence.

## Setup

1. **Create a Neon database** at [neon.tech](https://neon.tech) (free tier works)
2. **Enable pgvector** in the Neon console (SQL tab: `CREATE EXTENSION vector;`)
3. **Set the connection string**:
   ```bash
   # In ~/.claude/.env
   NEON_DATABASE_URL=postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Run schema migration**:
   ```bash
   uv run ~/.claude/scripts/skill-tracker/setup_db.py
   ```

## How It Works

### Observe (Automatic)

The `SubagentStop` hook automatically records an observation every time an agent completes:
- What skill/agent ran
- Whether it succeeded or failed
- Error classification (tool_call, instruction, timeout, output_quality)
- Task summary extracted from the transcript
- Cross-project tracking via `cwd`

No manual intervention needed — observations accumulate automatically.

### Inspect (On-Demand)

```bash
# Inspect a specific skill
uv run ~/.claude/scripts/skill-tracker/inspect.py code-review

# Dashboard of all skills
uv run ~/.claude/scripts/skill-tracker/inspect.py --all

# Or use the command:
# /inspect-skill code-review
```

### Amend (Human-in-the-Loop)

```bash
# Propose an amendment based on evidence
uv run ~/.claude/scripts/skill-tracker/amend.py \
  --skill "code-review" \
  --type "fix_tool_call" \
  --rationale "SwiftLint path fails in Mint-managed projects" \
  --evidence "[101, 103]" \
  --original-file "~/.claude/skills/technical/code-review/SKILL.md"

# Apply after review
uv run ~/.claude/scripts/skill-tracker/amend.py --apply 1

# Or use the amendify skill which handles the full flow
```

### Evaluate (After ~5 Runs)

```bash
# Check if amendment improved things
uv run ~/.claude/scripts/skill-tracker/evaluate.py 1

# Roll back if it made things worse
uv run ~/.claude/scripts/skill-tracker/evaluate.py 1 --rollback
```

## Database Schema

| Table | Purpose |
|---|---|
| `skills` | Registry of all skills with embeddings |
| `observations` | One record per skill execution |
| `amendments` | Proposed/applied skill changes with version tracking |
| `evaluations` | Before/after amendment comparisons |

Views:
- `skill_health` — Dashboard with success rates and error patterns
- `recent_failures` — Last 50 failures for quick inspection

## Cross-Project

All hooks write to the same Neon database regardless of which project directory you're in. The `project` column in observations tracks which project each execution came from, so you can:
- See if a skill fails only in certain projects
- Track skill usage across your entire workflow
- Identify project-specific vs. universal issues

## Files

```
scripts/skill-tracker/
├── README.md          # This file
├── __init__.py        # Package init
├── db.py              # Database connection module
├── schema.sql         # Full database schema
├── setup_db.py        # One-time migration script
├── observe.py         # Observation recording (used by hook)
├── inspect.py         # Skill inspection and pattern analysis
├── amend.py           # Amendment proposal and application
└── evaluate.py        # Before/after comparison

skills/meta-skills/amendify/
├── SKILL.md           # Amendify skill definition
└── workflows/
    └── propose-amendment.md  # Step-by-step amendment workflow

commands/
├── inspect-skill.md   # /inspect-skill command
└── evaluate-skill.md  # /evaluate-skill command
```
