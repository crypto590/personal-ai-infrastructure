# Xcode Compilation Analyzer

Analyze Swift and mixed-language compile hotspots using build timing summaries and Swift frontend diagnostics, then produce source-level optimization recommendations.

*Based on [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill)*

## Core Rules

- Start from evidence -- a recent `.build-benchmark/` artifact or raw timing-summary output
- Prefer analysis-only compiler flags over persistent project edits during investigation
- Rank findings by expected **wall-clock** impact, not cumulative compile-time impact
- When compile tasks are heavily parallelized (sum of compile categories >> wall-clock median), label recommendations as "Reduces compiler workload (parallel)" rather than "Reduces build time"
- Do not edit source or build settings without explicit developer approval

## What To Inspect

- `Build Timing Summary` output from clean and incremental builds
- Long-running `CompileSwiftSources` or per-file compilation tasks
- `SwiftEmitModule` time -- can reach 60s+ after a single-line change in large modules
- `Planning Swift module` time -- if disproportionately large in incremental builds, signals unexpected input invalidation or macro-related rebuild cascading
- Ad hoc diagnostic flags:
  - `-Xfrontend -warn-long-expression-type-checking=<ms>`
  - `-Xfrontend -warn-long-function-bodies=<ms>`
  - `-Xfrontend -debug-time-compilation` -- per-file compile times
  - `-Xfrontend -debug-time-function-bodies` -- per-function compile times
  - `-Xswiftc -driver-time-compilation` -- driver-level timing
  - `-Xfrontend -stats-output-dir <path>` -- detailed compiler statistics (JSON)
- Mixed Swift and Objective-C surfaces that increase bridging work

## Analysis Workflow

1. Identify whether the main issue is broad compilation volume or a few extreme hotspots
2. Parse timing-summary categories and rank the biggest compile contributors
3. Run diagnostic flags to surface type-checking hotspots
4. Map evidence to a concrete recommendation list
5. Separate code-level suggestions from project-level or module-level suggestions

## Common Hotspot Patterns

- Missing explicit type information in expensive expressions
- Complex chained or nested expressions that are hard to type-check
- Delegate properties typed as `AnyObject` instead of a concrete protocol
- Oversized Objective-C bridging headers or generated Swift-to-ObjC surfaces
- Header imports that skip framework qualification and miss module-cache reuse
- Classes missing `final` that are never subclassed
- Overly broad access control (`public`/`open`) on internal-only symbols
- Monolithic SwiftUI `body` properties that should be decomposed into subviews
- Long method chains or closures without intermediate type annotations

## Reporting Format

For each recommendation, include:

- Observed evidence
- Likely affected file or module
- Expected wait-time impact (e.g., "Expected to reduce clean build by ~2s" or "Reduces parallel compile work but unlikely to reduce build wait time")
- Confidence level
- Whether approval is required before applying
