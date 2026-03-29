# Xcode Build Optimization Orchestrator

Coordinates the full build optimization workflow: benchmarking, analysis, prioritization, approval, implementation, and verification.

*Based on [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill)*

## Core Rules

- The success metric is **wall-clock build time** (developer wait duration)
- Always benchmark before changes, obtain explicit approval, and re-benchmark afterward
- Do not conflate parallelized task time with actual wait time

## Two-Phase Workflow

### Phase 1 -- Analyze (Non-Destructive)

1. **Benchmark** -- Establish baselines using the [benchmark workflow](benchmark.md)
2. **Analyze** -- Run specialist analyses:
   - [Compilation Analyzer](compilation-analyzer.md) -- Swift compile hotspots
   - [Project Analyzer](project-analyzer.md) -- Build settings, schemes, script phases
   - [SPM Analysis](spm-analysis.md) -- Package graph, plugins, module variants
3. **Prioritize** -- Generate an optimization plan at `.build-benchmark/optimization-plan.md`

### Phase 2 -- Execute (Requires Approval)

1. Review recommendations and mark approvals
2. Implement approved changes one at a time
3. Verify compilation succeeds after each change
4. Re-benchmark to measure wall-clock deltas
5. Report results with absolute and percentage improvements

## Prioritization Logic

When cumulative task time exceeds wall-clock median by 2x or more, most work runs in parallel. In this case:

- Compile hotspot fixes are unlikely to reduce wait time
- Serial bottlenecks (script phases, asset compilation) take priority
- Label parallel-only improvements honestly

## Impact Language

Every recommendation must state expected wait-time savings:

- "Expected to reduce your [clean/incremental] build by approximately X seconds"
- "Impact on wait time is uncertain -- re-benchmark after applying to confirm"
- "Reduces parallel compile work but unlikely to reduce build wait time"

Task-time savings alone are never presented as the headline.

## Approval Gate

Before execution, present a checklist with:

- Recommendation name
- Expected impact
- Evidence summary
- Affected files
- Risk level (low/medium/high)

## Regression Evaluation

Distinguish true regressions from acceptable trade-offs. For example, enabling `COMPILATION_CACHING = YES` may slow cold builds but significantly accelerates cached builds reflecting realistic workflows.

Best-practice settings that should persist regardless of immediate benchmark results:
- `COMPILATION_CACHING = YES`
- `EAGER_LINKING = YES`
- `SWIFT_USE_INTEGRATED_DRIVER = YES`
- `DEBUG_INFORMATION_FORMAT = dwarf` (Debug)
