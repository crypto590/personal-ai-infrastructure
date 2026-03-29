# Xcode Build Benchmark

Produce a repeatable Xcode build baseline before attempting any optimization.

*Based on [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill)*

## Core Rules

- Measure before recommending changes
- Capture clean and incremental builds separately
- Keep command, destination, configuration, scheme, and warm-up rules consistent across runs
- Write a timestamped JSON artifact to `.build-benchmark/`
- Do not change project files as part of benchmarking

## Inputs To Collect

Confirm or infer:

- Workspace or project path
- Scheme
- Configuration (Debug/Release)
- Destination (simulator or device)
- Whether a custom `DerivedData` path is needed

## Worktree Considerations

When benchmarking inside a git worktree, SPM packages with `exclude:` paths that reference gitignored directories (e.g., `__Snapshots__`) will cause `xcodebuild -resolvePackageDependencies` to crash. Create those missing directories before running any builds.

## Default Workflow

1. Normalize the build command and note every flag that affects caching or module reuse
2. Run one warm-up build to validate that the command succeeds
3. Run 3 clean builds
4. If `COMPILATION_CACHING = YES` is detected, run 3 cached clean builds (build once to warm the cache, then delete DerivedData but not the compilation cache before each measured run)
5. Run 3 zero-change builds (build immediately after a successful build with no edits) to measure fixed overhead floor: dependency computation, project description transfer, build description creation, script phases, codesigning, and validation
6. Optionally run 3 incremental builds with a file touch to measure a real edit-rebuild loop
7. Save the raw results and summary into `.build-benchmark/`
8. Report medians and spread, not just the single fastest run

## Preferred Command

```bash
xcodebuild -workspace App.xcworkspace \
  -scheme MyApp \
  -configuration Debug \
  -destination "platform=iOS Simulator,name=iPhone 16" \
  -showBuildTimingSummary \
  clean build
```

## Required Output

- Clean build median, min, max
- Cached clean build median, min, max (when COMPILATION_CACHING is enabled)
- Zero-change build median, min, max (fixed overhead floor)
- Incremental build median, min, max (if touch-file was used)
- Biggest timing-summary categories
- Environment details that could affect comparisons
- Path to the saved artifact

If results are noisy, say so and recommend rerunning under calmer conditions.
