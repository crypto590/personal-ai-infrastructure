#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Memory Migration — Import existing JSON/MD memory into Neon Postgres.

Sources:
  1. ~/.claude/memory/projects/*.json  (97 files, auto-captured)
  2. ~/.claude/projects/*/memory/       (MEMORY.md files, manual)
  3. ~/.claude/agent-memory/*/          (agent-specific research)

Run once: uv run ~/.claude/hooks/memory_migrate.py
"""

import json
import re
import sys
from pathlib import Path

# Import from sibling module
sys.path.insert(0, str(Path(__file__).parent))
from memory_db import connect, detect_product, add_episode, register_product, init_db

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_JSON_DIR = CLAUDE_DIR / "memory" / "projects"
PROJECTS_MD_DIR = CLAUDE_DIR / "projects"
AGENT_MEMORY_DIR = CLAUDE_DIR / "agent-memory"

# Known product seeds
PRODUCT_SEEDS = {
    "/Users/coreyyoung/Desktop/Projects/athlead": ("athlead", "Athlead"),
    "/Users/coreyyoung/Desktop/Projects/athlead-android": ("athlead", "Athlead Android"),
    "/Users/coreyyoung/Desktop/Projects/crewos": ("crewos", "CrewOS"),
    "/Users/coreyyoung/.claude": ("pai", "Personal AI Infrastructure"),
}


def migrate_json_files() -> int:
    """Import ~/.claude/memory/projects/*.json → episodes."""
    count = 0
    if not PROJECTS_JSON_DIR.exists():
        return 0

    for jf in sorted(PROJECTS_JSON_DIR.glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        project = data.get("project", {})
        project_path = project.get("path", "")
        project_name = project.get("name", jf.stem)

        if not project_path:
            continue

        product = detect_product(project_path)

        # Import key decisions
        for decision in data.get("keyDecisions", []):
            if decision.strip():
                add_episode(
                    episode_type="decision",
                    subject=decision[:120],
                    content=decision,
                    salience=6,
                    tags=["migrated", "json"],
                    product=product,
                    project_path=project_path,
                )
                count += 1

        # Import open items as facts
        for item in data.get("openItems", []):
            if item.strip():
                add_episode(
                    episode_type="fact",
                    subject=item[:120],
                    content=item,
                    salience=4,
                    tags=["migrated", "json", "todo"],
                    product=product,
                    project_path=project_path,
                )
                count += 1

        # Import current focus
        focus = data.get("currentFocus", "").strip()
        if focus:
            add_episode(
                episode_type="fact",
                subject=f"Focus: {focus[:110]}",
                content=focus,
                salience=5,
                tags=["migrated", "json", "focus"],
                product=product,
                project_path=project_path,
            )
            count += 1

    return count


def _parse_memory_md(text: str) -> list[dict]:
    """Parse a MEMORY.md file into episode dicts."""
    episodes = []
    current_section = ""
    current_items: list[str] = []

    for line in text.splitlines():
        line = line.strip()

        # Section headers
        if line.startswith("## "):
            # Flush previous section
            if current_section and current_items:
                for item in current_items:
                    episodes.append({
                        "section": current_section,
                        "content": item,
                    })
            current_section = line[3:].strip()
            current_items = []
        elif line.startswith("- "):
            # List item
            item = line[2:].strip()
            # Strip markdown link syntax: [text](file) → text
            item = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', item)
            if item:
                current_items.append(item)
        elif line and not line.startswith("#") and current_section:
            # Continuation text
            if current_items:
                current_items[-1] += " " + line
            elif line:
                current_items.append(line)

    # Flush last section
    if current_section and current_items:
        for item in current_items:
            episodes.append({
                "section": current_section,
                "content": item,
            })

    return episodes


def _section_to_episode_type(section: str) -> tuple[str, int]:
    """Map MEMORY.md section name to episode type and salience."""
    s = section.lower()
    if "decision" in s or "architecture" in s:
        return "decision", 7
    if "feedback" in s or "preference" in s or "style" in s:
        return "preference", 8
    if "workflow" in s or "process" in s or "git" in s:
        return "preference", 7
    if "todo" in s or "open" in s or "task" in s:
        return "fact", 4
    if "stack" in s or "version" in s or "dep" in s:
        return "fact", 5
    if "insight" in s or "learning" in s:
        return "insight", 6
    return "fact", 5


def migrate_memory_md_files() -> int:
    """Import ~/.claude/projects/*/memory/MEMORY.md → episodes."""
    count = 0
    if not PROJECTS_MD_DIR.exists():
        return 0

    for memory_dir in sorted(PROJECTS_MD_DIR.glob("*/memory")):
        memory_file = memory_dir / "MEMORY.md"
        if not memory_file.exists():
            continue

        # Decode project path from directory name
        # e.g. -Users-coreyyoung-Desktop-Projects-crewos → /Users/coreyyoung/Desktop/Projects/crewos
        encoded_name = memory_dir.parent.name
        project_path = encoded_name.replace("-", "/")
        if not project_path.startswith("/"):
            project_path = "/" + project_path

        product = detect_product(project_path)
        text = memory_file.read_text()
        parsed = _parse_memory_md(text)

        for item in parsed:
            episode_type, salience = _section_to_episode_type(item["section"])
            content = item["content"]
            subject = content[:120]

            add_episode(
                episode_type=episode_type,
                subject=subject,
                content=content,
                salience=salience,
                tags=["migrated", "memory-md", item["section"].lower().replace(" ", "-")],
                product=product,
                project_path=project_path,
            )
            count += 1

    return count


def migrate_agent_memory() -> int:
    """Import ~/.claude/agent-memory/*/MEMORY.md → episodes."""
    count = 0
    if not AGENT_MEMORY_DIR.exists():
        return 0

    for agent_dir in sorted(AGENT_MEMORY_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name

        # Import MEMORY.md index
        memory_file = agent_dir / "MEMORY.md"
        if memory_file.exists():
            parsed = _parse_memory_md(memory_file.read_text())
            for item in parsed:
                episode_type, salience = _section_to_episode_type(item["section"])
                add_episode(
                    episode_type=episode_type,
                    subject=item["content"][:120],
                    content=item["content"],
                    salience=salience,
                    tags=["migrated", "agent-memory", agent_name],
                    product="pai",
                    agent_type=agent_name,
                )
                count += 1

        # Import individual research files
        for md_file in sorted(agent_dir.glob("*.md")):
            if md_file.name == "MEMORY.md":
                continue

            text = md_file.read_text().strip()
            if not text:
                continue

            # Use filename as subject, full content as body
            subject = md_file.stem.replace("-", " ").title()[:120]

            # Extract first paragraph or heading as summary
            first_lines = []
            for line in text.splitlines()[:5]:
                if line.strip():
                    first_lines.append(line.strip().lstrip("# "))
                else:
                    break
            summary = " ".join(first_lines)[:500] if first_lines else text[:500]

            add_episode(
                episode_type="insight",
                subject=subject,
                content=summary,
                reasoning=f"Research by {agent_name} agent",
                salience=5,
                tags=["migrated", "agent-research", agent_name, md_file.stem],
                product="pai",
                agent_type=agent_name,
            )
            count += 1

    return count


def seed_products():
    """Seed known product mappings."""
    for prefix, (prod, display) in PRODUCT_SEEDS.items():
        register_product(prefix, prod, display)


def main():
    print("=== Memory Migration ===\n")

    # Ensure schema exists
    print("Ensuring schema...")
    init_db()

    # Seed products
    print("Seeding product mappings...")
    seed_products()

    # Run migrations
    print("\n1. Migrating JSON project files...")
    json_count = migrate_json_files()
    print(f"   Imported {json_count} episodes from JSON files")

    print("\n2. Migrating MEMORY.md files...")
    md_count = migrate_memory_md_files()
    print(f"   Imported {md_count} episodes from MEMORY.md files")

    print("\n3. Migrating agent memory...")
    agent_count = migrate_agent_memory()
    print(f"   Imported {agent_count} episodes from agent memory")

    total = json_count + md_count + agent_count
    print(f"\n=== Migration Complete: {total} total episodes imported ===")

    # Print stats
    from memory_db import get_stats
    stats = get_stats()
    print(f"\nBy product: {json.dumps(stats['by_product'], indent=2)}")
    print(f"By type: {json.dumps(stats['by_type'], indent=2)}")


if __name__ == "__main__":
    main()
