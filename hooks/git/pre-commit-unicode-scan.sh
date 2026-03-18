#!/bin/bash
# pre-commit-unicode-scan.sh
# Scans staged files for invisible Unicode characters used in supply chain attacks.
# Compatible with git, graphite (gt create/modify), and any tool that runs git commit.
#
# Install options:
#   1. Symlink:    ln -s ~/.claude/hooks/git/pre-commit-unicode-scan.sh .git/hooks/pre-commit
#   2. Source:     Add to existing pre-commit: source ~/.claude/hooks/git/pre-commit-unicode-scan.sh
#   3. Global:     git config --global core.hooksPath ~/.claude/hooks/git/
#                  (caution: overrides project-level hooks)
#
# Covers: Glassworm attack (Tags block + Variation Selectors), plus zero-width
# chars, invisible operators, BOM, and line/paragraph separators.

set -euo pipefail

# File extensions to scan
EXTENSIONS="js|ts|jsx|tsx|mjs|cjs|py|sh|swift|kt|rb|go|rs"

# Get staged files matching extensions (ACM = Added, Copied, Modified)
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.($EXTENSIONS)$" || true)

if [ -z "$staged_files" ]; then
    exit 0
fi

found_issues=false

while IFS= read -r file; do
    [ -f "$file" ] || continue

    # Use perl for reliable Unicode detection (works on macOS without GNU grep)
    matches=$(perl -CSD -ne '
        while (/[\x{200B}-\x{200F}\x{2028}-\x{202F}\x{2060}-\x{206F}\x{FE00}-\x{FE0F}\x{FEFF}\x{E0000}-\x{E01EF}]/g) {
            my $cp = ord($&);
            my $label =
                $cp >= 0xE0100 && $cp <= 0xE01EF ? "Tag Character" :
                $cp >= 0xE0000 && $cp <= 0xE007F ? "Tag Character" :
                $cp >= 0xFE00  && $cp <= 0xFE0F  ? "Variation Selector" :
                $cp >= 0x200B  && $cp <= 0x200F  ? "Zero-Width" :
                $cp >= 0x2060  && $cp <= 0x206F  ? "Invisible Operator" :
                $cp == 0xFEFF                    ? "BOM" :
                "Invisible Unicode";
            printf "    Line %d: U+%04X (%s)\n", $., $cp, $label;
        }
    ' "$file" 2>/dev/null)

    if [ -n "$matches" ]; then
        if [ "$found_issues" = false ]; then
            echo ""
            echo "  Invisible Unicode characters detected in staged files"
            echo "  This matches the Glassworm supply chain attack pattern."
            echo ""
            found_issues=true
        fi
        echo "  $file:"
        echo "$matches"
        echo ""
    fi
done <<< "$staged_files"

if [ "$found_issues" = true ]; then
    echo "  Commit blocked. Review these files for hidden malicious payloads."
    echo "  Use 'git commit --no-verify' to bypass (not recommended)."
    echo ""
    exit 1
fi

exit 0
