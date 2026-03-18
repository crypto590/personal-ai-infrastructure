#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["psycopg[binary]"]
# ///
"""
Obsidian Export — Exports memory episodes to markdown for human browsing.
Output: ~/Desktop/The_Hub/AI-Memory/{product}.md per product.
Source of truth remains Neon. This is a read-only export layer.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

OBSIDIAN_DIR = Path.home() / "Desktop" / "The_Hub" / "AI-Memory"

TYPE_HEADERS = {
    "decision": "Decisions",
    "preference": "Preferences",
    "fact": "Facts",
    "insight": "Insights",
    "failure": "Failures & Lessons",
    "relationship": "Relationships",
}


def export_product(product: str, episodes: list[dict]) -> Path:
    """Export a single product's episodes to markdown."""
    OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in product)
    output_file = OBSIDIAN_DIR / f"{safe_name}.md"

    # Group by type
    by_type: dict[str, list[dict]] = {}
    for ep in episodes:
        t = ep.get("episode_type", "fact")
        by_type.setdefault(t, []).append(ep)

    lines = [
        f"# {product.title()} — Memory",
        "",
        f"*Auto-exported from Neon memory DB — {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*{len(episodes)} active episodes*",
        "",
        "---",
        "",
    ]

    for etype in ["decision", "preference", "insight", "fact", "failure", "relationship"]:
        eps = by_type.get(etype, [])
        if not eps:
            continue

        header = TYPE_HEADERS.get(etype, etype.title())
        lines.append(f"## {header}")
        lines.append("")

        for ep in eps:
            salience = ep.get("salience", 5)
            subject = ep.get("subject", "")
            content = ep.get("content", "")
            reasoning = ep.get("reasoning", "")
            tags = ep.get("tags", [])
            created = ep.get("created_at", "")

            # Salience indicator
            indicator = "!!!" if salience >= 8 else "!" if salience >= 5 else ""

            lines.append(f"### {indicator} {subject}")
            lines.append("")
            lines.append(content)
            if reasoning:
                lines.append(f"")
                lines.append(f"> **Why:** {reasoning}")
            lines.append("")

            meta_parts = [f"Salience: {salience}/10"]
            if tags:
                # Filter out migration tags for cleaner display
                display_tags = [t for t in tags if t not in ("migrated", "json", "memory-md")]
                if display_tags:
                    meta_parts.append(f"Tags: {', '.join(display_tags)}")
            if created:
                ts = created if isinstance(created, str) else created.isoformat()
                meta_parts.append(f"Created: {ts[:10]}")
            lines.append(f"*{' | '.join(meta_parts)}*")
            lines.append("")

    output_file.write_text("\n".join(lines))
    return output_file


def export_all():
    """Export all products to Obsidian."""
    from memory_db import get_all_grouped

    grouped = get_all_grouped(limit_per_product=100)

    for product, episodes in grouped.items():
        path = export_product(product, episodes)
        print(f"Exported {len(episodes)} episodes → {path}")

    if not grouped:
        print("No episodes to export.")


def export_single(product: str):
    """Export a single product."""
    from memory_db import get_by_product

    episodes = get_by_product(product, limit=100)
    if episodes:
        path = export_product(product, episodes)
        print(f"Exported {len(episodes)} episodes → {path}")
    else:
        print(f"No episodes found for product: {product}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--product", help="Export single product")
    args = parser.parse_args()

    if args.product:
        export_single(args.product)
    else:
        export_all()


if __name__ == "__main__":
    main()
