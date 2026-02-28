# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Validate a SKILL.md file against Anthropic skill standards and PAI conventions."""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run with: uv run scripts/validate_skill.py <path>")
    sys.exit(1)


def validate_skill(skill_path: str) -> list[str]:
    """Validate a SKILL.md file. Returns list of issues found."""
    path = Path(skill_path)
    issues: list[str] = []
    warnings: list[str] = []

    # File existence
    if not path.exists():
        return [f"SKILL.md not found at {path}"]

    if path.name != "SKILL.md":
        issues.append(f"File must be named exactly 'SKILL.md', got '{path.name}'")

    content = path.read_text()
    lines = content.split("\n")

    # Check frontmatter exists
    if not content.startswith("---"):
        issues.append("Missing YAML frontmatter (must start with ---)")
        return issues

    # Extract frontmatter
    fm_end = content.index("---", 3)
    fm_raw = content[3:fm_end].strip()

    try:
        frontmatter = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        issues.append(f"Invalid YAML frontmatter: {e}")
        return issues

    if not isinstance(frontmatter, dict):
        issues.append("Frontmatter must be a YAML mapping")
        return issues

    # Required fields
    if "name" not in frontmatter:
        issues.append("Missing required field: name")
    else:
        name = frontmatter["name"]
        if not re.match(r"^[a-z][a-z0-9-]*$", str(name)) and name != "Alex":
            warnings.append(f"Name '{name}' should be kebab-case (e.g., 'my-skill-name')")

        # Check folder name matches
        folder_name = path.parent.name
        if str(name) != folder_name and folder_name != "CORE" and name != "Alex":
            warnings.append(f"Folder name '{folder_name}' doesn't match skill name '{name}'")

    if "description" not in frontmatter:
        issues.append("Missing required field: description")
    else:
        desc = str(frontmatter["description"]).strip()
        if len(desc) > 1024:
            issues.append(f"Description too long ({len(desc)} chars, max 1024)")
        if len(desc) < 20:
            warnings.append("Description is very short - include trigger phrases for better discoverability")
        if "<" in desc or ">" in desc:
            issues.append("Description must not contain XML angle brackets (< or >)")

    # Recommended fields
    if "metadata" not in frontmatter:
        warnings.append("Missing recommended field: metadata (author, version, category, tags)")
    else:
        meta = frontmatter.get("metadata", {})
        if isinstance(meta, dict):
            for field in ["author", "version", "category", "tags"]:
                if field not in meta:
                    warnings.append(f"Missing metadata.{field}")

    # Body content checks
    body = content[fm_end + 3:].strip()
    word_count = len(body.split())

    if word_count > 5000:
        warnings.append(f"SKILL.md body is {word_count} words (recommended: <5000). Consider using references/")

    if word_count < 10:
        warnings.append("SKILL.md body has very little content")

    # Check for references directory mention if file is large
    if word_count > 3000 and "references/" not in content:
        warnings.append("Large skill file - consider extracting detailed docs to references/ directory")

    # Print results
    print(f"\nValidating: {path}")
    print(f"{'=' * 60}")

    if not issues and not warnings:
        print("PASS - No issues found")
    else:
        for issue in issues:
            print(f"  ERROR: {issue}")
        for warning in warnings:
            print(f"  WARN:  {warning}")

    print(f"\nStats: {word_count} words, {len(lines)} lines")
    print(f"Result: {len(issues)} errors, {len(warnings)} warnings")

    return issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate_skill.py <path-to-SKILL.md>")
        print("       uv run scripts/validate_skill.py --all <skills-dir>")
        sys.exit(1)

    if sys.argv[1] == "--all":
        skills_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / ".claude" / "skills"
        all_issues = []
        for skill_file in sorted(skills_dir.rglob("SKILL.md")):
            result = validate_skill(str(skill_file))
            all_issues.extend(result)
        print(f"\n{'=' * 60}")
        print(f"Total: {len(all_issues)} errors across all skills")
        sys.exit(1 if all_issues else 0)
    else:
        result = validate_skill(sys.argv[1])
        sys.exit(1 if result else 0)
