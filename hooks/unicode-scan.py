#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Invisible Unicode scanner for Claude Code PreToolUse hook.
Detects the Glassworm supply chain attack pattern: malicious payloads encoded
as invisible Unicode characters (Tags block, Variation Selectors, zero-width chars)
that render as whitespace but decode to executable bytes via eval().

Exit 0 = allow, Exit 2 = block
"""

import json
import re
import sys

# Invisible Unicode ranges used in supply chain attacks
# - Zero-width chars: U+200B-U+200F
# - Line/paragraph separators: U+2028-U+202F
# - Invisible operators: U+2060-U+206F
# - Variation Selectors: U+FE00-U+FE0F (Glassworm: maps to bytes 0-15)
# - BOM: U+FEFF
# - Tags block: U+E0000-U+E01EF (Glassworm: maps to bytes 16-255+)
INVISIBLE_UNICODE_RE = re.compile(
    r'[\u200B-\u200F\u2028-\u202F\u2060-\u206F\uFE00-\uFE0F\uFEFF'
    r'\U000E0000-\U000E01EF]'
)

# File extensions worth scanning (skip config, markdown, images, etc.)
SCAN_EXTENSIONS = frozenset((
    '.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs',
    '.py', '.sh', '.swift', '.kt', '.rb', '.go', '.rs',
))


def should_scan(file_path: str) -> bool:
    if not file_path:
        return True  # No path = bash command, always scan
    return any(file_path.endswith(ext) for ext in SCAN_EXTENSIONS)


def label(cp: int) -> str:
    if 0xFE00 <= cp <= 0xFE0F:
        return f"Variation Selector (U+{cp:04X})"
    if 0xE0100 <= cp <= 0xE01EF:
        return f"Tag Character (U+{cp:05X})"
    if 0xE0000 <= cp <= 0xE007F:
        return f"Tag Character (U+{cp:05X})"
    if 0x200B <= cp <= 0x200F:
        return f"Zero-Width (U+{cp:04X})"
    if 0x2028 <= cp <= 0x202F:
        return f"Separator (U+{cp:04X})"
    if 0x2060 <= cp <= 0x206F:
        return f"Invisible Operator (U+{cp:04X})"
    if cp == 0xFEFF:
        return "BOM (U+FEFF)"
    return f"Invisible (U+{cp:04X})"


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool = data.get('tool_name', '')
    inp = data.get('tool_input', {})

    # Extract content to scan based on tool type
    file_path = ''
    if tool == 'Write':
        file_path = inp.get('file_path', '')
        text = inp.get('content', '')
    elif tool == 'Edit':
        file_path = inp.get('file_path', '')
        text = inp.get('new_string', '')
    elif tool == 'Bash':
        text = inp.get('command', '')
    else:
        sys.exit(0)

    if not should_scan(file_path):
        sys.exit(0)

    hits = INVISIBLE_UNICODE_RE.findall(text)
    if not hits:
        sys.exit(0)

    # Build report
    types = sorted({label(ord(c)) for c in hits})
    lines = [
        f"BLOCKED: {len(hits)} invisible Unicode character(s) detected",
        f"Target: {file_path or 'bash command'}",
        "Types:",
    ]
    for t in types:
        lines.append(f"  - {t}")
    lines.append("")
    lines.append("This matches the Glassworm supply chain attack pattern.")
    lines.append("Invisible chars can encode arbitrary payloads executed via eval().")
    lines.append("Inspect the source manually before allowing this write.")

    print('\n'.join(lines), file=sys.stderr)
    sys.exit(2)


if __name__ == '__main__':
    main()
