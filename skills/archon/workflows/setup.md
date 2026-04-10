# Archon Setup

## Quick Install (30 seconds)

```bash
curl -fsSL https://archon.diy/install | bash
```

Or via Homebrew:
```bash
brew install coleam00/archon/archon
```

---

## Prerequisites

- **Bun** — JavaScript runtime (Archon is TypeScript/Bun)
- **Claude Code** — AI assistant backend
- **GitHub CLI** (`gh`) — For PR creation and GitHub integration

---

## Full Setup (5 minutes)

```bash
# 1. Clone Archon
git clone https://github.com/coleam00/Archon.git
cd Archon

# 2. Install dependencies
bun install

# 3. Run guided setup wizard
claude
# Then say: "Set up Archon"
```

The wizard configures:
- API credentials
- Platform integrations (Slack, Telegram, etc.)
- Database (SQLite default, PostgreSQL optional)
- Model selection

---

## Project-Level Setup

From any project repo:

```bash
cd /path/to/your/project

# Initialize Archon in this repo
mkdir -p .archon/workflows

# Copy default workflows you want to customize
cp ~/.archon/workflows/defaults/*.yaml .archon/workflows/
```

Archon discovers workflows in this order:
1. `.archon/workflows/` in the current repo (overrides)
2. `~/.archon/workflows/defaults/` (bundled defaults)

---

## Platform Adapters

### GitHub Webhooks (15 min)
Triggers workflows on issues, PRs, and comments.

### Slack (15 min)
Send natural language messages to a Slack bot — Archon routes to workflows.

### Telegram (5 min)
Lightweight chat interface for triggering workflows on the go.

### Discord (community-supported)
Community-maintained adapter.

### Web UI
```bash
archon serve
# Opens dashboard at http://localhost:3000
```

Real-time monitoring, visual workflow builder, execution tracking.

---

## Verify Installation

```bash
# Check Archon is available
archon --version

# List available workflows
archon workflow list

# From a project dir, test a simple workflow
cd /path/to/project
claude
# Say: "Use archon to list workflows"
```

---

## Configuration File

`.archon/config.yaml` controls:

```yaml
# AI model selection
model: claude-opus-4-6

# Database
database:
  type: sqlite  # or postgresql
  path: .archon/data.db

# Platform adapters
platforms:
  slack:
    enabled: false
    token: $SLACK_BOT_TOKEN
  telegram:
    enabled: false
    token: $TELEGRAM_BOT_TOKEN
  github:
    enabled: true
    webhook_secret: $GITHUB_WEBHOOK_SECRET
```
