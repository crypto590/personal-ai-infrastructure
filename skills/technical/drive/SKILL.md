---
name: drive
description: Terminal automation CLI for AI agents via tmux. Orchestrate multiple terminal sessions, run commands with reliable completion detection, and execute in parallel.
key_info: "Location: ~/.claude/apps/drive/ | Run: cd ~/.claude/apps/drive && uv run drive <command> | Requires: tmux (brew install tmux)"
---

# Drive CLI — Terminal Automation for AI Agents

Drive provides programmatic tmux control, enabling Claude Code agents to orchestrate multiple terminal sessions. It is adapted from [mac-mini-agent](https://github.com/disler/mac-mini-agent) for local Mac use.

## Installation & Location

```
~/.claude/apps/drive/
```

Run commands with:
```bash
cd ~/.claude/apps/drive && uv run drive <command>
```

Or equivalently:
```bash
cd ~/.claude/apps/drive && uv run python main.py <command>
```

## Commands Reference

### Session Management

```bash
# Create a detached (headless) session — preferred for agent use
drive session create <name> --detach [--window <name>] [--dir <path>]

# Create a session with Terminal.app window (for visual monitoring)
drive session create <name> [--window <name>] [--dir <path>]

# List all sessions
drive session list [--json]

# Kill a session
drive session kill <name>
```

### Run — Execute with Completion Detection

The core command. Runs a shell command in a tmux session and **waits** for it to finish using the sentinel protocol. Returns the exit code and captured output.

```bash
# Basic usage
drive run <session> "<command>" [--timeout 30] [--pane <index>] [--json]

# Examples
drive run worker "npm test" --timeout 60
drive run builder "make build" --json
drive run dev "python script.py" --timeout 0   # 0 = wait forever
```

### Send — Raw Keystrokes (Non-blocking)

For interactive tools where sentinel detection would interfere (vim, ipython, etc.). Does NOT wait for completion.

```bash
drive send <session> "<text>" [--pane <index>] [--enter/--no-enter]

# Examples
drive send editor ":wq" --enter          # Quit vim
drive send repl "print('hello')" --enter  # Send to ipython
drive send app "q" --no-enter             # Send 'q' without Enter
```

### Logs — Capture Pane Output

```bash
drive logs <session> [--lines <n>] [--pane <index>] [--json]

# Examples
drive logs worker --lines 50    # Last 50 lines
drive logs builder --json       # Full pane as JSON
```

### Poll — Wait for Pattern Match

Repeatedly captures pane output and searches for a regex pattern. Useful for waiting on specific output without the sentinel protocol.

```bash
drive poll <session> --until "<regex>" [--timeout 30] [--interval 0.5] [--json]

# Examples
drive poll server --until "Listening on port" --timeout 60
drive poll builder --until "BUILD (SUCCESS|FAILED)" --timeout 120
drive poll runner --until "Tests: \\d+ passed" --interval 1.0
```

### Fanout — Parallel Execution

Run the same command across multiple sessions simultaneously. Uses ThreadPoolExecutor with sentinel detection per session.

```bash
drive fanout "<command>" --targets "session1,session2,session3" [--timeout 30] [--json]

# Examples
drive fanout "git pull" --targets "repo1,repo2,repo3" --timeout 20
drive fanout "npm test" --targets "frontend,backend,shared" --timeout 120 --json
```

### Process Management

```bash
# List processes (filter by name, session, parent PID, or cwd)
drive proc list [--name <substring>] [--session <name>] [--parent <pid>] [--cwd <path>]

# Kill process by PID or name
drive proc kill <pid> [--signal 15] [--force] [--tree]
drive proc kill --name "<pattern>" [--tree]

# Show process tree
drive proc tree <pid>
drive proc tree --session <name>

# Resource snapshot
drive proc top --pid "1234,5678"
drive proc top --session <name>
```

## The Sentinel Protocol

The key innovation of Drive is reliable command completion detection via sentinels.

**How it works:**

1. Generate a unique 8-char hex token
2. Wrap the command: `echo "__START_<token>" ; <cmd> ; echo "__DONE_<token>:$?"`
3. Send the wrapped command to the tmux pane
4. Poll `capture-pane` output every 0.2s looking for the `__DONE_` marker
5. Extract the exit code from `__DONE_<token>:<exit_code>`
6. Extract clean output between `__START_` and `__DONE_` markers

This means:
- Deterministic completion detection (no guessing based on prompt patterns)
- Accurate exit code capture
- Clean output extraction (strips sentinel lines)
- Works regardless of terminal width or line wrapping

## JSON Output Mode

All commands support `--json` for structured output. This is ideal for agent consumption:

```bash
drive run worker "npm test" --json
# {"ok":true,"session":"worker","command":"npm test","exit_code":0,"output":"..."}

drive session list --json
# {"ok":true,"sessions":[{"name":"worker","windows":1,"created":"...","attached":false}]}
```

## Common Workflows

### Spin Up Multiple Agent Workers

```bash
# Create sessions
drive session create agent-1 --detach --dir ~/project
drive session create agent-2 --detach --dir ~/project
drive session create agent-3 --detach --dir ~/project

# Fan out a command
drive fanout "npm test" --targets "agent-1,agent-2,agent-3" --timeout 120
```

### Long-Running Server + Test Pattern

```bash
# Start server in background session
drive session create server --detach --dir ~/api
drive send server "npm start"

# Wait for server to be ready
drive poll server --until "Listening on port 3000" --timeout 30

# Run tests in another session
drive session create tests --detach --dir ~/api
drive run tests "npm test" --timeout 60

# Cleanup
drive session kill server
drive session kill tests
```

### Monitor and Collect Results

```bash
# Check what's happening in a session
drive logs worker --lines 20

# Check resource usage
drive proc top --session worker

# See process tree
drive proc tree --session worker
```

### Interactive Tool Control

```bash
# Open vim and edit
drive session create editor --detach
drive send editor "vim config.yaml"
drive poll editor --until "config.yaml" --timeout 5
drive send editor "isome new content"
drive send editor "ESC" --no-enter
drive send editor ":wq"
```

## Error Handling

Drive uses structured errors with codes:

| Error Code | Meaning |
|---|---|
| `tmux_not_found` | tmux not in PATH |
| `session_not_found` | Named session does not exist |
| `session_exists` | Session already exists (on create) |
| `timeout` | Command exceeded timeout |
| `pattern_not_found` | Poll pattern not matched in time |
| `tmux_error` | Underlying tmux command failed |
| `process_not_found` | PID or name not found |
| `kill_permission_denied` | Insufficient permissions |

All errors include `{"ok": false, "error": "<code>", "message": "..."}` in JSON mode.

## Best Practices

1. **Always use `--detach`** when creating sessions for agent use. The non-detach mode opens Terminal.app windows which is only useful for human monitoring.

2. **Use `run` over `send`** whenever possible. `run` gives you completion detection and exit codes. Only use `send` for interactive tools.

3. **Set appropriate timeouts.** Default is 30s. Use `--timeout 0` for commands that may run indefinitely (but then use `poll` or `logs` to check progress).

4. **Use `--json` for programmatic consumption.** Human mode is for debugging; JSON mode is for agents.

5. **Clean up sessions.** Always `session kill` when done to avoid orphaned tmux sessions.

6. **Use fanout for parallel work.** It handles thread pooling and result collection automatically.
