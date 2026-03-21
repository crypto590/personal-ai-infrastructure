---
name: graphite
effort: medium
description: |
  Graphite stacked PRs workflow for monorepo and Git worktree projects.
  Use when performing Git branching, committing, PR operations, or stack management
  in projects using Graphite (gt). Covers gt commands, worktree rules, conflict
  resolution, commit messages, PR sizing, and stack design patterns.
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Graphite Stacked PRs — Monorepo + Worktree Workflow

This skill governs all Git branching, committing, and PR operations in projects using Graphite (`gt`) with Git worktrees.

## Core Principles

1. **Always use `gt` over `git`** for branch and commit operations. Raw `git commit`, `git checkout -b`, and `git commit --amend` break Graphite's internal stack metadata and cause silent desync.
2. **Orient before acting.** Run `gt ls` before any branch operation to understand the current stack state.
3. **One logical change per stack entry.** Each stacked branch should represent a single reviewable unit — a feature, a refactor, a fix — not a grab bag of changes.
4. **Keep PRs ≤ 400 lines of meaningful diff.** Beyond this threshold, review quality degrades. If a change exceeds 400 lines, split it into multiple stack entries.
5. **Worktrees are independent.** Each Git worktree maintains its own Graphite stack. Never assume stack state carries across worktrees.

## Environment Awareness

Before performing any Graphite operations, determine the current context:

```bash
# Where are we?
pwd
# What does the stack look like?
gt ls
# What branch are we on?
gt branch
# Are there uncommitted changes?
git status
```

### Worktree Detection

This project uses Git worktrees. The main repo and each worktree have independent checked-out branches and independent Graphite stacks.

```
project-root/              # main repo — trunk (main/develop), merges, shared code
project-root-android/      # worktree — Android app stack
project-root-web/          # worktree — React web app stack
```

Key rules:
- Run `gt init` once in each new worktree before using Graphite commands.
- Shared code changes (packages, schemas, API types) go through the main repo as standalone PRs, then sync into worktrees via `gt sync`.
- Never cross-edit files between worktrees. If both apps need the same shared change, commit it to trunk first.

## Command Reference

### Navigation

| Command | Action |
|---------|--------|
| `gt ls` | Show all tracked branches and stack relationships. **Run this first.** |
| `gt log short` | Show the current stack with abbreviated info. |
| `gt up` | Move to the child branch above current in the stack. |
| `gt down` | Move to the parent branch below current. |
| `gt top` | Jump to the tip (newest) of the current stack. |
| `gt bottom` | Jump to the base (oldest) of the current stack. |
| `gt branch` | Show current branch name. |

### Creating Stack Entries

| Command | Action |
|---------|--------|
| `gt create <branch-name>` | Create a new branch stacked on current. Stage and commit changes first. |
| `gt modify -c -m "message"` | Create a new commit on the current branch (preferred for adding changes). |
| `gt modify --amend` | Amend the head commit of the current branch. |
| `gt modify -cam "message"` | Stage all + create new commit in one shot. |

**Never use:**
- `git commit` — use `gt modify -c` instead
- `git checkout -b` — use `gt create` instead
- `git commit --amend` — use `gt modify --amend` instead

### Stack Maintenance

| Command | Action |
|---------|--------|
| `gt restack` | Rebase all branches in the stack to maintain parent-child consistency. Local only, no network. |
| `gt sync` | Pull trunk from remote, rebase stacks, prompt to delete merged branches. |
| `gt get` | Sync the current branch/stack from remote. Surgical — only touches this stack, not global. Safe in worktrees. |

### Submitting PRs

| Command | Action |
|---------|--------|
| `gt submit` | Push all stacked branches as linked PRs to GitHub. Creates/updates PRs with dependency annotations. |
| `gt submit --stack` | Submit only the current stack (useful in worktrees with multiple stacks). |

### Branch Management

| Command | Action |
|---------|--------|
| `gt move --onto <target>` | Rebase current branch onto a different parent. Use `--onto` flag to avoid interactive mode. |
| `gt split` | Split current branch into multiple branches. Interactive — notify user and let them drive. |

## Conflict Resolution

When `gt restack`, `gt sync`, or `gt move` hits a merge conflict:

1. Run `git status` to identify conflicting files.
2. Edit conflicting files — resolve all `<<<<<<<`, `=======`, `>>>>>>>` markers.
3. Stage resolved files: `git add <file>` or `gt add -A`.
4. Resume: `gt continue`.
5. **Never** use `git rebase --continue` — Graphite tracks its own rebase state separately.
6. After resolution, verify the stack: `gt ls` and run tests if applicable.

If conflicts are complex or span multiple files, **stop and notify the user** rather than guessing at resolution intent.

## Commit Messages

Write commit messages that make sense in a stack context. The reviewer sees them in sequence, so each should be self-explanatory:

```
# Good — clear what this stack entry does
gt create -m "add clerk auth provider and route guards"
gt create -m "implement athlete profile page with stats grid"
gt create -m "add video upload component with progress indicator"

# Bad — vague, doesn't help reviewer understand the stack
gt create -m "auth stuff"
gt create -m "more changes"
gt create -m "fix"
```

## PR Sizing and Stack Design

### Target: ≤ 400 lines per stack entry

Break work into logical, reviewable units:

```
# Good stack — each entry is one concern
Stack: feature/athlete-profiles
  ├── 1. add profile data model and API types (~150 lines)
  ├── 2. implement profile fetch and caching (~200 lines)
  ├── 3. build profile UI components (~300 lines)
  └── 4. add edit profile form with validation (~250 lines)

# Bad stack — everything in one branch
Stack: feature/athlete-profiles
  └── 1. add athlete profiles (~900 lines) ← reviewer will procrastinate
```

### PR Title Prefixes

When working in a monorepo with multiple apps, prefix PR titles for reviewer context:

- `[shared]` — changes to shared packages, schemas, types
- `[android]` — Android-specific changes
- `[web]` — React web app changes
- `[infra]` — CI, build config, tooling

## Workflow Patterns

### Starting a New Feature Stack

```bash
# Sync trunk first
gt sync

# Create the first branch in the stack
gt create feature/web-auth-provider
# ... make changes ...
gt modify -cam "add clerk auth provider wrapper"

# Stack the next piece
gt create feature/web-auth-routes
# ... make changes ...
gt modify -cam "add protected route components"

# Submit the whole stack as linked PRs
gt submit
```

### Syncing After Trunk Changes

When shared code merges to trunk and you need it in your worktree stack:

```bash
gt sync          # pulls trunk, rebases your stack
gt ls            # verify stack is clean
```

### Fixing a Mistake — Commit on Wrong Branch

1. If changes are uncommitted: `git stash`, navigate to correct branch, `git stash pop`, commit with `gt modify`.
2. If already committed to wrong branch:
   - `gt create <correct-branch>` to preserve the commit in a new branch
   - `gt down` back to the original
   - `git reset --hard HEAD~1` (safe — commit lives on the new branch)
   - `gt restack` to clean up

### Adding Changes to a Mid-Stack Branch

```bash
gt down          # or gt bottom, navigate to the target branch
# ... make changes ...
gt modify --amend   # or gt modify -c for a new commit
gt restack          # propagate changes up through the stack
gt submit           # update all PRs
```

## Interactivity Handling

Some Graphite commands open interactive selectors or editors. When running as an agent:

- **Prefer explicit flags** over interactive mode (e.g., `--onto <branch>` for `gt move`).
- **Never attempt to interact with** `gt split` — it requires complex user decisions. Stop and notify the user.
- **If a command hangs** waiting for input, it's likely in interactive mode. Kill it (`Ctrl+C`) and retry with explicit flags.
- For `gt modify`, always pass `-m "message"` or `--amend` to avoid opening an editor.

## PR Submission from Worktrees

`gt submit` works identically from any worktree. All worktrees share the same `.git` object database, remote origin, and refs. Graphite metadata lives in the shared `.git/` directory, so submitting from any worktree:

- Pushes branches to the same remote
- Creates or updates linked PRs on the same GitHub repo
- Annotates dependency chains correctly across the stack

There is no difference between running `gt submit` in the main repo versus a worktree — the result is the same set of PRs on the same repository.

## Worktree Safety — gt sync Can Nuke Sibling Worktrees

**This is the most dangerous Graphite footgun in a multi-worktree setup.**

`gt sync` rebases trunk and restacks ALL tracked branches globally — including branches checked out in other worktrees. If another worktree has unstaged changes when this happens, those changes are silently erased.

### The Scenario

```bash
# You're in athlead-web/, actively editing files (unstaged)
# Meanwhile in athlead-android/, you run:
gt sync    # ← rebases trunk, restacks ALL branches
           # including the branch checked out in athlead-web/
           # unstaged work in athlead-web/ is GONE
```

### Rules (Always Follow)

1. **Prefer `gt get` over `gt sync` in worktrees.** `gt get` only syncs the current branch/stack from remote — it is surgical, not global. It will not touch branches checked out in other worktrees.
2. **Reserve `gt sync` for the main repo only**, and only after confirming all worktrees are clean.
3. **Before ANY sync operation**, verify all worktrees have clean working directories:

```bash
# Pre-sync safety check — run from any worktree
git worktree list
# Then check each worktree is clean:
git -C /path/to/other-worktree status --short
# If any show changes → commit or stash them first
```

4. **Shell alias for safety.** Add this to `~/.zshrc` so every sync starts with a visual reminder:

```bash
# Add to ~/.zshrc — safety reminder before sync
alias gtsync='echo "⚠️  Check all worktrees are clean first" && git worktree list && gt sync'
```

### Quick Reference

| Operation | In Worktree | In Main Repo |
|-----------|-------------|--------------|
| Sync this stack only | `gt get` | `gt get` |
| Full global sync | **DON'T** — use `gt get` | `gt sync` (after confirming all worktrees clean) |
| After stack merges | `gt get` + `gt restack` | `gt sync` |

## Things to Avoid

| Don't | Do Instead |
|-------|------------|
| `git commit -m "msg"` | `gt modify -c -m "msg"` |
| `git checkout -b new-branch` | `gt create new-branch` |
| `git commit --amend` | `gt modify --amend` |
| `git rebase --continue` | `gt continue` |
| Commit to wrong branch | Check `gt ls` first, fix with the misplaced commit pattern above |
| Stack entries > 400 lines | Split into smaller logical units |
| Edit shared code in a worktree | Make shared changes on trunk in the main repo |