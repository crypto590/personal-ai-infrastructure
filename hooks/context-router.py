#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
ContextRouter -- Smart context injection based on prompt classification.

Tiers:
  0 (Greeting):  Nothing                          ~0 tokens
  1 (Skill):     Nothing (skills self-load)        ~0 tokens
  2 (Standard):  Lean identity reminder          ~100 tokens
  3 (Project):   Identity + project memory       ~250 tokens
  4 (Memory):    Identity + search results       ~400 tokens

Also detects explicit positive/negative feedback signals and records them.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# ---------------------------------------------------------------------------
# Prompt Classification
# ---------------------------------------------------------------------------

GREETINGS = {
    "hey", "hello", "hi", "sup", "yo", "heya", "hiya", "howdy",
    "good morning", "good afternoon", "good evening", "what's up",
    "whats up", "hey alex", "hello alex", "hi alex",
}

MEMORY_KEYWORDS = {
    "/memory", "/remember", "/forget",
    "remember when", "do you remember", "recall",
    "what do you know about", "check your memory",
}

# Lean identity -- injected on standard/project prompts (~200 tokens)
LEAN_IDENTITY = """You are Alex — Personal AI Orchestrator. Orchestrator first, IC second.

AGENT ROUTING (mandatory):
- ALL coding → `code` agent (has clean code rules + platform conventions)
- Codebase search → `Explore` agent
- Web research → `research-specialist` agent
- Architecture → `Plan` agent
- PR review → `code-reviewer` agent
- NEVER use swift-specialist, kotlin-specialist, react-developer, nextjs-app-developer, fastify-specialist.

WHEN TO DELEGATE vs WORK DIRECTLY:
- Delegate: 2+ files, research, parallel tasks, substantial coding
- Direct: single-file edits, sequential diagnostics, trivial lookups, answering from context

Code quality: 6 rules always active — see context/knowledge/patterns/clean-code-rules.md
Stack: TypeScript, React, Python, Swift, Kotlin. Packages: bun (JS/TS), uv (Python).
Security: ~/.claude/ is private — never commit to public repos."""

# ---------------------------------------------------------------------------
# Signal Detection
# ---------------------------------------------------------------------------

POSITIVE_SIGNALS = {
    "perfect", "great", "exactly", "nailed it", "love it",
    "awesome", "excellent", "nice work", "good job", "well done",
    "yes exactly", "that's right",
}

NEGATIVE_SIGNALS = {
    "wrong", "no not that", "that's broken", "incorrect",
    "that's wrong", "fix this", "broken", "no that's not",
}


def detect_signal(prompt: str):
    """Detect positive/negative feedback signals. Returns (sentiment, trigger) or (None, '')."""
    p = prompt.strip().lower()
    for signal in POSITIVE_SIGNALS:
        if signal in p:
            return "positive", signal
    for signal in NEGATIVE_SIGNALS:
        if signal in p:
            return "negative", signal
    return None, ""


def classify_prompt(prompt: str, cwd: str) -> str:
    """Classify prompt into a routing tier."""
    p = prompt.strip().lower()
    words = p.split()

    if not words:
        return "greeting"

    # Tier 0: Greeting
    first_word = words[0]
    if p in GREETINGS or first_word in {"hey", "hello", "hi", "sup", "yo", "heya", "howdy"}:
        if len(words) <= 5:
            return "greeting"

    # Tier 1: Skill invocation (starts with /)
    if p.startswith("/"):
        return "skill"

    # Tier 4: Memory query
    if any(kw in p for kw in MEMORY_KEYWORDS):
        return "memory"

    # Tier 3: Project-specific (working in known project dir)
    try:
        from memory_db import detect_product, connect
        with connect() as conn:
            product = detect_product(cwd, conn)
        if product in ("athlead", "crewos"):
            return "project"
    except Exception:
        pass

    # Tier 2: Standard
    return "standard"


def get_project_memory(cwd: str, budget_chars: int = 600) -> str:
    """Load project-specific episodes from Neon."""
    try:
        from memory_db import (
            detect_product, get_by_product, format_for_injection, connect,
        )
        with connect() as conn:
            product = detect_product(cwd, conn)

        if product not in ("athlead", "crewos", "pai"):
            return ""

        episodes = get_by_product(product, limit=15)
        if not episodes:
            return ""

        text = format_for_injection(episodes, budget_chars=budget_chars)
        if not text:
            return ""
        return f"\n<project-memory product=\"{product}\">\n{text}\n</project-memory>"
    except Exception:
        return ""


def search_memory(query: str, cwd: str, budget_chars: int = 800) -> str:
    """Search memory for episodes matching the query."""
    try:
        from memory_db import (
            find_matching, detect_product, format_for_injection, connect,
        )
        with connect() as conn:
            product = detect_product(cwd, conn)

        # Try product-scoped search first, then global
        results = find_matching(query, product=product, limit=10)
        if not results:
            results = find_matching(query, limit=10)

        if not results:
            return "\n<memory-results>No matching memories found.</memory-results>"

        text = format_for_injection(results, budget_chars=budget_chars)
        return f"\n<memory-results>\n{text}\n</memory-results>"
    except Exception as e:
        return f"\n<memory-results>Memory search error: {e}</memory-results>"


def main():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({"continue": True}))
        return

    prompt = hook_input.get("prompt", "")
    cwd = hook_input.get("cwd", os.getcwd())

    # --- Signal detection ---
    sentiment, trigger = detect_signal(prompt)
    if sentiment:
        try:
            from memory_db import record_signal, detect_product, connect
            with connect() as conn:
                product = detect_product(cwd, conn)
            # Use session_id=0 as placeholder (actual session is tracked elsewhere)
            record_signal(
                session_id=0,
                sentiment=sentiment,
                prompt_snippet=prompt[:200],
                product=product,
                project_path=cwd,
            )
        except Exception:
            pass

    # --- Tier-based context injection ---
    tier = classify_prompt(prompt, cwd)
    output_parts = []

    if tier == "greeting":
        pass

    elif tier == "skill":
        pass

    elif tier == "memory":
        output_parts.append(LEAN_IDENTITY)
        search_terms = prompt.strip()
        for kw in sorted(MEMORY_KEYWORDS, key=len, reverse=True):
            search_terms = search_terms.replace(kw, "").strip()
        if search_terms:
            output_parts.append(search_memory(search_terms, cwd))

    elif tier == "project":
        output_parts.append(LEAN_IDENTITY)
        output_parts.append(get_project_memory(cwd, budget_chars=400))

    else:  # standard
        output_parts.append(LEAN_IDENTITY)

    output = "\n".join(p for p in output_parts if p)
    if output:
        print(json.dumps({"continue": True, "output": output}))
    else:
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
