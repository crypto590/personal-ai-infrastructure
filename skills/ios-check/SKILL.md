---
name: ios-check
description: Run iOS code quality checks (SwiftLint, build, tests, coverage). NOT for code review, architecture validation, or accessibility audits - use ios-review skills for those.
argument-hint: "[--test] [--coverage] [--fix] [path]"
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Glob, mcp__xcodebuildmcp__test_sim, mcp__xcodebuildmcp__build_sim
compatibility: "Requires macOS with Xcode, SwiftLint, and xcodebuild MCP server"
metadata:
  author: coreyyoung
  version: 1.0.0
  category: technical
  tags: [ios, swiftlint, code-quality, testing, coverage, xcode]
---

# iOS Code Quality Check

Run code quality checks for iOS projects before commits or PRs.

## Arguments

- `--test` - Run unit tests after lint/build
- `--coverage` - Run tests with code coverage report
- `--fix` - Auto-fix SwiftLint violations where possible
- `[path]` - iOS project path (defaults to detecting `athlead-ios` in current repo)

## Workflow

### 1. Detect iOS Project

Look for iOS project in this order:
1. Explicit path argument
2. `apps/athlead-ios/` relative to git root
3. Current directory if it contains `.xcodeproj`

### 2. Check SwiftLint Config

If `.swiftlint.yml` doesn't exist in the iOS project:
1. Show the user the template from `templates/.swiftlint.yml`
2. Ask if they want to create it
3. Create if confirmed

### 3. Run Checks (in order)

| Check | Command | When |
|-------|---------|------|
| **SwiftLint** | `swiftlint` or `swiftlint --fix` | Always |
| **Build** | Use `mcp__xcodebuildmcp__build_sim` | Always |
| **Tests** | Use `mcp__xcodebuildmcp__test_sim` | `--test` or `--coverage` |
| **Coverage** | Parse xcresult for coverage % | `--coverage` |

### 4. Report Results

```
## iOS Check Results

| Check     | Status | Details |
|-----------|--------|---------|
| SwiftLint | ✅/❌  | X warnings, Y errors |
| Build     | ✅/❌  | [errors if any] |
| Tests     | ✅/❌/⏭️ | X passed, Y failed / skipped |
| Coverage  | ✅/⏭️  | XX.X% / skipped |

**Ready for commit**: Yes/No
```

### 5. If Issues Found

- List SwiftLint errors with `file:line` references
- Offer to fix with `--fix` if not already used
- For build errors, show the relevant error output

## SwiftLint Config Notes

The template config:
- Excludes `.build/`, `DerivedData/`, generated files
- Allows short names (`i`, `j`, `x`, `y`) in loops
- Sets line length to 120 (warning) / 200 (error)
- Disables rules that conflict with SwiftUI patterns

## Examples

```bash
# Quick lint + build check
/ios-check

# Full check with tests
/ios-check --test

# Fix lint issues automatically
/ios-check --fix

# Specific project path
/ios-check ~/Projects/other-ios-app
```
