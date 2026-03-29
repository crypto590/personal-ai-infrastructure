# Xcode Project Analyzer

Audit Xcode project configuration, build settings, scheme behavior, and script phases to find build-time improvements.

*Based on [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill)*

## Core Rules

- Recommendation-first by default
- Require explicit approval before changing project files, schemes, or build settings
- Prefer measured findings tied to timing summaries, build logs, or project configuration evidence
- Distinguish debug-only pain from release-only pain

## What To Review

- Scheme build order and target dependencies
- Debug vs release build settings
- Run script phases and dependency-analysis settings
- Derived-data churn or invalidating custom steps
- Opportunities for parallelization
- Explicit module dependency settings and module-map readiness
- `Planning Swift module` time in Build Timing Summary
- Asset catalog compilation time (especially with large or numerous catalogs)
- `ExtractAppIntentsMetadata` time
- Zero-change build overhead (if a no-op rebuild exceeds a few seconds)
- CocoaPods usage (deprecated -- recommend migrating to SPM)
- Task Backtraces (Xcode 16.4+) to diagnose why tasks re-run unexpectedly

## Build Settings Checklist

Audit Debug and Release configurations for these key settings:

| Setting | Debug | Release |
|---------|-------|---------|
| `SWIFT_COMPILATION_MODE` | `singlefile` (incremental) | `wholemodule` |
| `SWIFT_OPTIMIZATION_LEVEL` | `-Onone` | `-O` or `-Osize` |
| `DEBUG_INFORMATION_FORMAT` | `dwarf` | `dwarf-with-dsym` |
| `COMPILATION_CACHING` | `YES` | `YES` |
| `EAGER_LINKING` | `YES` | `YES` |
| `SWIFT_USE_INTEGRATED_DRIVER` | `YES` | `YES` |
| `GCC_OPTIMIZATION_LEVEL` | `-O0` | `-Os` |
| `DEAD_CODE_STRIPPING` | `YES` | `YES` |

## Apple-Derived Checks

- Target dependencies are accurate and not missing or inflated
- Schemes build in `Dependency Order`
- Run scripts declare inputs and outputs
- `.xcfilelist` files are used when scripts have many inputs or outputs
- `DEFINES_MODULE` is enabled where custom frameworks should expose module maps
- Headers are self-contained enough for module-map use

## Typical Wins

- Skip debug-time scripts that only matter in release
- Add missing script guards or dependency-analysis metadata
- Remove accidental serial bottlenecks in schemes
- Align build settings that cause unnecessary module variants
- Fix stale project structure that forces broader rebuilds
- Identify linters/formatters that touch file timestamps without changing content
- Split large asset catalogs into separate resource bundles across targets
- Use Task Backtraces to pinpoint exact input changes triggering unnecessary work

## Reporting Format

For each issue, include:

- Evidence
- Likely scope
- Why it affects clean builds, incremental builds, or both
- Estimated impact
- Approval requirement
