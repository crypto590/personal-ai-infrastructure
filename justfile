# ~/.claude/justfile — PAI Command Runner
# Usage: cd ~/.claude && just <command>
# Install just: brew install just

# Default: show available commands
default:
    @just --list

# ─── PAI Status ───────────────────────────────────────────────

# Show git status of PAI repository
status:
    @echo "── PAI Git Status ──"
    @git -C ~/.claude status --short
    @echo ""
    @echo "── Recent Commits ──"
    @git -C ~/.claude log --oneline -5

# List all available skills
skills:
    @echo "── Available Skills ──"
    @find ~/.claude/skills -name "SKILL.md" -type f | sed 's|.*skills/||; s|/SKILL.md||' | sort

# List all agent definitions
agents:
    @echo "── Available Agents ──"
    @ls ~/.claude/agents/*.md 2>/dev/null | sed 's|.*agents/||; s|\.md||' | sort

# Show current memory files
memory:
    @echo "── Memory Files ──"
    @find ~/.claude/memory -type f 2>/dev/null | sed 's|.*memory/||' | sort || echo "No memory files found"
    @echo ""
    @echo "── Agent Memory ──"
    @find ~/.claude/agent-memory -type f 2>/dev/null | sed 's|.*agent-memory/||' | sort || echo "No agent memory files found"

# Show recent Claude session activity
logs:
    @echo "── Recent Session Logs ──"
    @ls -lt ~/.claude/logs/ 2>/dev/null | head -20 || echo "No logs found"

# ─── Validation ───────────────────────────────────────────────

# Run validation checks on PAI structure
check:
    @echo "── PAI Structure Check ──"
    @echo "Skills:"
    @find ~/.claude/skills -name "SKILL.md" -type f | wc -l | xargs echo "  Count:"
    @echo "Agents:"
    @ls ~/.claude/agents/*.md 2>/dev/null | wc -l | xargs echo "  Count:"
    @echo "Commands:"
    @find ~/.claude/commands -type f 2>/dev/null | wc -l | xargs echo "  Count:"
    @echo ""
    @echo "── YAML Validation ──"
    @find ~/.claude/jobs -name "*.yaml" -type f -exec python3 -c "import yaml, sys; yaml.safe_load(open(sys.argv[1])); print(f'  OK: {sys.argv[1]}')" {} \; 2>/dev/null || echo "  No job files to validate"
    @echo ""
    @echo "── Git Health ──"
    @git -C ~/.claude diff --stat HEAD 2>/dev/null || echo "  No git changes"

# ─── Git Operations ──────────────────────────────────────────

# Sync PAI changes: stage, commit, push
sync message="PAI sync":
    @echo "── Syncing PAI ──"
    git -C ~/.claude add -A
    git -C ~/.claude commit -m "{{message}}"
    git -C ~/.claude push
    @echo "── Sync Complete ──"

# ─── Apps ─────────────────────────────────────────────────────

# Run steer CLI (agent steering interface)
steer *args:
    cd ~/.claude/apps/steer && uv run main.py {{args}}

# Run drive CLI (agent driving interface)
drive *args:
    cd ~/.claude/apps/drive && uv run main.py {{args}}

# ─── Job Management ──────────────────────────────────────────

# Get job status by ID
job id:
    uv run ~/.claude/apps/jobs/tracker.py get {{id}}

# List all jobs
jobs *args:
    uv run ~/.claude/apps/jobs/tracker.py list {{args}}

# Send a prompt to create a new agent job
send +prompt:
    uv run ~/.claude/apps/jobs/tracker.py create "{{prompt}}"

# ─── Spec Templates ──────────────────────────────────────────

# List available spec templates
specs:
    @echo "── Spec Templates ──"
    @ls ~/.claude/specs/*.md 2>/dev/null | sed 's|.*specs/||' | sort

# Create a new spec from template
spec-new name:
    @cp ~/.claude/specs/TEMPLATE.md ~/.claude/specs/{{name}}.md
    @echo "Created spec: ~/.claude/specs/{{name}}.md"
