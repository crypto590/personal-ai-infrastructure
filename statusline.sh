#!/bin/bash

# Claude Code Status Line Script
# Receives JSON input via stdin with session context

# Read JSON input from stdin
input=$(cat)

# Extract key information
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir // ""')
project_dir=$(echo "$input" | jq -r '.workspace.project_dir // ""')
context_used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Get git branch if in a git repo
git_branch=""
check_dir="${project_dir:-$current_dir}"
if [ -n "$check_dir" ] && [ -d "$check_dir/.git" ]; then
    git_branch=$(cd "$check_dir" 2>/dev/null && git branch --show-current 2>/dev/null || echo "")
fi

# Get project name (last component of project_dir)
project_name=""
if [ -n "$project_dir" ]; then
    project_name=$(basename "$project_dir")
fi

# Build progress bar (10 chars wide)
progress_bar=""
if [ -n "$context_used" ]; then
    filled=$(printf "%.0f" $(echo "$context_used / 10" | bc -l 2>/dev/null || echo "0"))
    [ "$filled" -gt 10 ] && filled=10
    [ "$filled" -lt 0 ] && filled=0
    empty=$((10 - filled))
    progress_bar=$(printf "%${filled}s" | tr ' ' '█')$(printf "%${empty}s" | tr ' ' '░')
fi

# Build status line
# 1. Model Name (cyan)
printf "\033[36m%s\033[0m" "$model"

# 2. Progress bar (color based on usage)
if [ -n "$progress_bar" ]; then
    if [ "$(printf '%.0f' "$context_used")" -ge 80 ]; then
        printf " \033[31m%s\033[0m" "$progress_bar"  # Red if >= 80%
    elif [ "$(printf '%.0f' "$context_used")" -ge 50 ]; then
        printf " \033[33m%s\033[0m" "$progress_bar"  # Yellow if >= 50%
    else
        printf " \033[32m%s\033[0m" "$progress_bar"  # Green otherwise
    fi
fi

# 3. Percentage context used (yellow)
if [ -n "$context_used" ]; then
    printf " \033[33m%.0f%%\033[0m" "$context_used"
fi

# 4. Git Branch (red)
if [ -n "$git_branch" ]; then
    printf " \033[31m(%s)\033[0m" "$git_branch"
fi

# 6. Project name (green)
if [ -n "$project_name" ]; then
    printf " \033[32m%s\033[0m" "$project_name"
fi
