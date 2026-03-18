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
session_cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')

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

# Build gradient progress bar (10 chars wide, green→yellow→red)
progress_bar=""
if [ -n "$context_used" ]; then
    filled=$(printf "%.0f" $(echo "$context_used / 10" | bc -l 2>/dev/null || echo "0"))
    [ "$filled" -gt 10 ] && filled=10
    [ "$filled" -lt 0 ] && filled=0
    empty=$((10 - filled))
    # Each filled block colored by its position: 1-5 green, 6-7 yellow, 8-10 red
    bar=""
    for i in $(seq 1 "$filled"); do
        if [ "$i" -le 5 ]; then
            bar="${bar}\033[32m█\033[0m"
        elif [ "$i" -le 7 ]; then
            bar="${bar}\033[33m█\033[0m"
        else
            bar="${bar}\033[31m█\033[0m"
        fi
    done
    for i in $(seq 1 "$empty"); do
        bar="${bar}\033[90m░\033[0m"
    done
    progress_bar="$bar"
fi

# Voice server status indicator
voice_icon=""
if curl -s --max-time 1 http://localhost:8888/health > /dev/null 2>&1; then
    voice_icon="🔊"
else
    voice_icon="🔇"
fi

# === Anthropic Usage API (cached 3 min) ===
CACHE_DIR="$HOME/.cache/claude-statusline"
CACHE_FILE="$CACHE_DIR/usage.json"
CACHE_MAX_AGE=180

get_usage_data() {
    # Return cached data if fresh
    if [ -f "$CACHE_FILE" ]; then
        local now=$(date +%s)
        local mod=$(stat -f %m "$CACHE_FILE" 2>/dev/null || echo "0")
        local age=$(( now - mod ))
        if [ "$age" -lt "$CACHE_MAX_AGE" ]; then
            cat "$CACHE_FILE"
            return 0
        fi
    fi

    # Get OAuth token from macOS Keychain
    local token
    token=$(security find-generic-password -s "Claude Code-credentials" -a "$(whoami)" -w 2>/dev/null | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
    if [ -z "$token" ]; then
        [ -f "$CACHE_FILE" ] && cat "$CACHE_FILE"
        return 1
    fi

    # Fetch usage data
    local response
    response=$(curl -s --max-time 3 \
        -H "Authorization: Bearer $token" \
        -H "anthropic-beta: oauth-2025-04-20" \
        "https://api.anthropic.com/api/oauth/usage" 2>/dev/null)

    if [ $? -eq 0 ] && echo "$response" | jq -e '.five_hour' > /dev/null 2>&1; then
        mkdir -p "$CACHE_DIR"
        echo "$response" > "$CACHE_FILE"
        echo "$response"
        return 0
    fi

    [ -f "$CACHE_FILE" ] && cat "$CACHE_FILE"
    return 1
}

usage_json=$(get_usage_data)
five_hr_pct=""
seven_day_pct=""
reset_time=""
weekly_reset_time=""

if [ -n "$usage_json" ]; then
    five_hr_pct=$(echo "$usage_json" | jq -r '.five_hour.utilization // empty')
    seven_day_pct=$(echo "$usage_json" | jq -r '.seven_day.utilization // empty')
    resets_at=$(echo "$usage_json" | jq -r '.five_hour.resets_at // empty')

    now_epoch=$(date +%s)

    # Calculate time until 5hr block reset
    if [ -n "$resets_at" ]; then
        clean_ts=$(echo "$resets_at" | sed 's/\.[0-9]*+00:00$//' | sed 's/\.[0-9]*Z$//')
        reset_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$clean_ts" +%s 2>/dev/null)
        if [ -n "$reset_epoch" ] && [ "$reset_epoch" -gt "$now_epoch" ]; then
            remaining=$(( reset_epoch - now_epoch ))
            hours=$(( remaining / 3600 ))
            minutes=$(( (remaining % 3600) / 60 ))
            if [ "$hours" -gt 0 ]; then
                reset_time="${hours}h${minutes}m"
            else
                reset_time="${minutes}m"
            fi
        fi
    fi

    # Calculate time until 7-day reset
    weekly_resets_at=$(echo "$usage_json" | jq -r '.seven_day.resets_at // empty')
    if [ -n "$weekly_resets_at" ]; then
        clean_ts=$(echo "$weekly_resets_at" | sed 's/\.[0-9]*+00:00$//' | sed 's/\.[0-9]*Z$//')
        weekly_reset_epoch=$(date -j -u -f "%Y-%m-%dT%H:%M:%S" "$clean_ts" +%s 2>/dev/null)
        if [ -n "$weekly_reset_epoch" ] && [ "$weekly_reset_epoch" -gt "$now_epoch" ]; then
            remaining=$(( weekly_reset_epoch - now_epoch ))
            days=$(( remaining / 86400 ))
            hours=$(( (remaining % 86400) / 3600 ))
            if [ "$days" -gt 0 ]; then
                weekly_reset_time="${days}d${hours}h"
            else
                weekly_reset_time="${hours}h"
            fi
        fi
    fi
fi

# === Build status line ===

# 1. Voice indicator
printf "%s " "$voice_icon"

# 2. Model Name (cyan)
printf "\033[36m%s\033[0m" "$model"

# 3. Session cost (bold green - money)
if [ -n "$session_cost" ] && [ "$session_cost" != "0" ]; then
    printf " \033[1;32m\$%.2f\033[0m" "$session_cost"
fi

# 4. Gradient progress bar (colors baked in per-block)
if [ -n "$progress_bar" ]; then
    printf " "
    printf "$progress_bar"
fi

# 5. Percentage context used (color matches bar zone)
if [ -n "$context_used" ]; then
    ctx_int=$(printf '%.0f' "$context_used")
    if [ "$ctx_int" -ge 70 ]; then
        printf " \033[31m%.0f%%\033[0m" "$context_used"    # Red
    elif [ "$ctx_int" -ge 50 ]; then
        printf " \033[33m%.0f%%\033[0m" "$context_used"    # Yellow
    else
        printf " \033[32m%.0f%%\033[0m" "$context_used"    # Green
    fi
fi

# 6. 5-hour block usage (color-coded) + reset countdown (matched color)
if [ -n "$five_hr_pct" ]; then
    five_int=$(printf '%.0f' "$five_hr_pct")
    if [ "$five_int" -ge 80 ]; then
        color="31"   # Red
    elif [ "$five_int" -ge 50 ]; then
        color="33"   # Yellow
    else
        color="32"   # Green
    fi
    printf " \033[${color}m5h:%s%%\033[0m" "$five_int"
    if [ -n "$reset_time" ]; then
        printf "\033[${color}m↻%s\033[0m" "$reset_time"
    fi
fi

# 7. 7-day usage (blue) + reset countdown
if [ -n "$seven_day_pct" ]; then
    seven_int=$(printf '%.0f' "$seven_day_pct")
    if [ "$seven_int" -ge 80 ]; then
        color="31"   # Red
    elif [ "$seven_int" -ge 50 ]; then
        color="33"   # Yellow
    else
        color="34"   # Blue
    fi
    printf " \033[${color}m7d:%s%%\033[0m" "$seven_int"
    if [ -n "$weekly_reset_time" ]; then
        printf "\033[${color}m↻%s\033[0m" "$weekly_reset_time"
    fi
fi

# 9. Git Branch (red)
if [ -n "$git_branch" ]; then
    printf " \033[31m(%s)\033[0m" "$git_branch"
fi

# 10. Project name (green)
if [ -n "$project_name" ]; then
    printf " \033[32m%s\033[0m" "$project_name"
fi
