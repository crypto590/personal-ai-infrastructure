# SPM Build Analysis

Analyze Swift Package Manager dependencies, package plugins, module variants, and CI-oriented build overhead that slow Xcode builds.

*Based on [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill)*

## Core Rules

- Treat package analysis as evidence gathering first, not a mandate to replace dependencies
- Separate package-graph issues from project-setting issues
- Do not rewrite package manifests or dependency sources without explicit approval

## What To Inspect

- `Package.swift` and `Package.resolved`
- Local packages vs remote packages
- Package plugin and build-tool usage
- Binary target footprint
- Dependency layering, repeated imports, and potential cycles
- Build logs or timing summaries showing package-related work

## Verification Before Recommending

Before including any local package in a recommendation, verify it is actually part of the project's dependency graph:

- Check `project.pbxproj` for `XCLocalSwiftPackageReference` entries
- Check `XCSwiftPackageProductDependency` entries to confirm the package's product is linked to at least one target
- If a local package exists on disk but is not referenced in the project, do not include it in recommendations

## Focus Areas

- **Package graph shape** -- how much work changes trigger downstream
- **Plugin overhead** -- during local development and CI
- **Checkout/fetch cost** -- signals in clean environments
- **Configuration drift** -- forcing duplicate module builds
- **Dependency direction violations** -- features depending on each other instead of shared lower layers
- **Circular dependencies** -- extract shared contracts into a protocol module
- **Oversized modules** (200+ files) -- widen incremental rebuild scope
- **Umbrella modules** using `@_exported import` -- create hidden dependency chains
- **Missing interface/implementation separation** -- blocks build parallelism
- **Test targets depending on app target** -- instead of the module under test
- **Swift macro rebuild cascading** -- heavy use of Swift macros (TCA, swift-syntax) can cause trivial changes to cascade into near-full rebuilds
- **`swift-syntax` building universally** -- all architectures when no prebuilt binary is available
- **Multi-platform build multiplication** -- adding a secondary platform (e.g., watchOS) causes shared SPM packages to build multiple times

## Modular SDK Migration Caveat

Migrating from a monolithic target to a modular multi-target SDK does not automatically reduce build time. Modular targets increase `SwiftCompile`, `SwiftEmitModule`, and `ScanDependencies` task counts. Only recommend modular SDK migration for build speed when the project compiles large unused portions of a monolithic SDK.

## Reporting Format

For each finding, include:

- Evidence
- Affected package or plugin
- Likely clean-build vs incremental-build impact
- CI impact if relevant
- Estimated impact
- Approval requirement
