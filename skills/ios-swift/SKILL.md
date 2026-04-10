---
name: ios-swift
effort: high
description: "Unified iOS/Swift/SwiftUI development. MVC architecture, code review, SwiftLint, accessibility, concurrency, SwiftData, security, build optimization, TestFlight, App Store ASO, and Figma-to-SwiftUI workflows."
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# iOS & Swift Development

Comprehensive skill covering architecture, code review, quality assurance, and best practices for iOS/Swift/SwiftUI development.

---

## Capabilities

### Architecture (MVC)

Modern MVC architecture for Swift/SwiftUI with strict unidirectional data flow. Observable Controllers coordinate Services and manage UI state, Services handle async operations, Models contain business logic, Views delegate to Controllers.

| Topic | File | Summary |
|-------|------|---------|
| Controllers | [architecture/controllers.md](architecture/controllers.md) | Observable patterns, task cancellation, state management, production checklist |
| Services | [architecture/services.md](architecture/services.md) | Actor vs struct decisions, protocol-based design, async patterns |
| Models | [architecture/models.md](architecture/models.md) | Immutable structs, computed properties, Codable compliance |
| Views | [architecture/views.md](architecture/views.md) | SwiftUI delegation, Controller integration, composition |
| Error Handling | [architecture/error-handling.md](architecture/error-handling.md) | Controller error patterns, custom error types, user-facing messages |
| Navigation | [architecture/navigation.md](architecture/navigation.md) | Controller-owned intent, NavigationStack, modals, deep linking |
| Advanced Patterns | [architecture/advanced-patterns.md](architecture/advanced-patterns.md) | Controller composition, shared controllers, state machines |
| Testing | [architecture/testing.md](architecture/testing.md) | Protocol-based testing, mock services, async testing |
| Liquid Glass | [architecture/liquid-glass.md](architecture/liquid-glass.md) | iOS 26+ design system, glass effect patterns, performance |
| Examples | [architecture/examples.md](architecture/examples.md) | Complete real-world feature implementations |
| Quick Reference | [architecture/quick-reference.md](architecture/quick-reference.md) | Code templates, decision trees, anti-patterns |

**Core Principle:** Unidirectional data flow with strict layer separation.

```
View -> Controller -> Service -> Model
```

**Production Requirements:**
- Controllers: `@Observable @MainActor final class`, `private(set)` properties, protocol-based services, task tracking + cancellation, deinit cleanup
- Services: `actor` for async (never `class`), protocol for testing, no UI state
- Models: `struct`, `Codable`, `Equatable`, no async code, no `@Published`
- Views: `@State private var controller`, delegate to Controller, never call Services directly

---

### Code Review

Specialized review agents for iOS code quality and compliance.

| Topic | File | Summary |
|-------|------|---------|
| Accessibility | [review/accessibility.md](review/accessibility.md) | VoiceOver, Assistive Access, contrast, tap targets, system preferences |
| Liquid Glass | [review/liquid-glass.md](review/liquid-glass.md) | Surface appropriateness, single layer rule, performance, API usage |
| Concurrency | [review/concurrency.md](review/concurrency.md) | Actor isolation, @concurrent, data races, Sendable, Swift 6.2 |
| Concurrency Patterns | [review/concurrency-patterns.md](review/concurrency-patterns.md) | Grep hotspots, bug patterns, async streams, Swift 6.2 features |
| SwiftUI Tips | [review/swiftui-tips.md](review/swiftui-tips.md) | Deprecated APIs, view optimization, HIG design, modern Swift idioms |
| Performance Audit | [review/swiftui-performance-audit.md](review/swiftui-performance-audit.md) | 6-step profiling workflow, code smells, Instruments diagnosis |
| Pattern Validation | [review/pattern-validation.md](review/pattern-validation.md) | MVC compliance, controller/service/view/model validation, layer separation |
| API Research | [review/api-research.md](review/api-research.md) | Apple API investigation, documentation sources, availability checks |

**Severity Levels:**
- Critical: Block PR (data races, missing MainActor, missing VoiceOver labels, glass on content)
- Warning: Address before shipping (missing task cancellation, performance concerns)
- Info: Optional improvements (optimization suggestions)

---

### SwiftData

Comprehensive SwiftData reference covering model rules, predicate gotchas, CloudKit constraints, and iOS 18+/26+ features. Adapted from [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) (Paul Hudson, MIT).

| Topic | File | Summary |
|-------|------|---------|
| Core Rules | [swiftdata/core-rules.md](swiftdata/core-rules.md) | Autosaving, ModelContext, relationships, @Transient, @Query, migrations |
| Predicates | [swiftdata/predicates.md](swiftdata/predicates.md) | String matching, unsupported operations, runtime crash gotchas |
| CloudKit | [swiftdata/cloudkit.md](swiftdata/cloudkit.md) | Unique constraints, optional requirements, eventual consistency |
| Indexing | [swiftdata/indexing.md](swiftdata/indexing.md) | iOS 18+ #Index, single and compound indexes |
| Class Inheritance | [swiftdata/class-inheritance.md](swiftdata/class-inheritance.md) | iOS 26+ @Model subclassing, querying, typecasting in predicates |

---

### Quality Checks

Automated code quality tools for iOS projects.

| Topic | File | Summary |
|-------|------|---------|
| iOS Checks | [quality/checks.md](quality/checks.md) | SwiftLint, build verification, unit tests, coverage |

**Quick Commands:**
- `/ios-check` - Lint + build
- `/ios-check --test` - Lint + build + tests
- `/ios-check --fix` - Auto-fix lint violations
- `/ios-check --coverage` - Tests with coverage report

---

### Build Optimization

Xcode build performance analysis and optimization. Adapted from [AvdLee/Xcode-Build-Optimization-Agent-Skill](https://github.com/AvdLee/Xcode-Build-Optimization-Agent-Skill).

| Topic | File | Summary |
|-------|------|---------|
| Orchestrator | [build-optimization/orchestrator.md](build-optimization/orchestrator.md) | Full workflow: benchmark, analyze, prioritize, approve, implement, verify |
| Benchmark | [build-optimization/benchmark.md](build-optimization/benchmark.md) | Repeatable clean/incremental build measurements with timestamped artifacts |
| Compilation Analyzer | [build-optimization/compilation-analyzer.md](build-optimization/compilation-analyzer.md) | Swift compile hotspots, type-checking diagnostics, source-level fixes |
| Project Analyzer | [build-optimization/project-analyzer.md](build-optimization/project-analyzer.md) | Build settings, schemes, script phases, target dependencies audit |
| SPM Analysis | [build-optimization/spm-analysis.md](build-optimization/spm-analysis.md) | Package graph, plugin overhead, module variants, macro cascading |

**Quick Start:** Use the orchestrator for a full optimization pass, or pick a specific analyzer for targeted investigation.

---

### Security

iOS/macOS security covering Keychain, biometrics, CryptoKit, Secure Enclave, and credential management. Adapted from [ivan-magda/swift-security-skill](https://github.com/ivan-magda/swift-security-skill) (Ivan Magda, MIT).

| Topic | File | Summary |
|-------|------|---------|
| Guidelines | [security/guidelines.md](security/guidelines.md) | 7 non-negotiable rules, anti-pattern scan, CryptoKit algorithms, review checklist |

**Non-Negotiable Rules:**
1. Never ignore `OSStatus`
2. Never use `LAContext.evaluatePolicy()` as standalone auth
3. Never store secrets in UserDefaults/plist
4. Never call `SecItem*` on `@MainActor`
5. Always set `kSecAttrAccessible` explicitly
6. Always use add-or-update pattern
7. Always target data protection keychain on macOS

---

### Workflows

| Topic | File | Summary |
|-------|------|---------|
| Swift Migration | [workflows/swift-migration.md](workflows/swift-migration.md) | iOS to Android migration patterns (Swift/SwiftUI -> Kotlin/Compose) |
| TestFlight Deployment | [workflows/testflight-deployment.md](workflows/testflight-deployment.md) | End-to-end TestFlight checklist — signing, archiving, upload, tester distribution |
| App Store ASO | [workflows/app-store-aso.md](workflows/app-store-aso.md) | Metadata optimization, keyword strategy, character limits, screenshot planning |
| Figma to SwiftUI | [workflows/figma-to-swiftui.md](workflows/figma-to-swiftui.md) | 8-step Figma MCP workflow, layout/typography/color translation, component mapping |

---

## Decision Tree

```
What are you building?

Data structure with business logic
  -> Create Model (struct with computed properties)
  -> See: architecture/models.md

Async operation (API, database, SDK)
  -> Create Service (actor or struct + protocol)
  -> See: architecture/services.md

UI state management or service coordination
  -> Create Controller (@Observable class)
  -> See: architecture/controllers.md

Display UI or handle user input
  -> Create View (SwiftUI, delegates to Controller)
  -> See: architecture/views.md

Using SwiftData for persistence
  -> Follow SwiftData rules and predicate gotchas
  -> See: swiftdata/*.md

Reviewing iOS code for PR
  -> Run review checklists (includes SwiftUI tips, concurrency patterns)
  -> See: review/*.md

Running quality checks before commit
  -> Run ios-check
  -> See: quality/checks.md

Slow Xcode builds or build optimization
  -> Run build optimization orchestrator
  -> See: build-optimization/orchestrator.md

Storing credentials, tokens, or sensitive data
  -> Follow security guidelines (Keychain, biometrics, CryptoKit)
  -> See: security/guidelines.md

SwiftUI performance issues (janky scrolling, high CPU, excessive rebuilds)
  -> Run performance audit workflow
  -> See: review/swiftui-performance-audit.md

Implementing design from Figma
  -> Follow Figma-to-SwiftUI workflow (requires Figma MCP)
  -> See: workflows/figma-to-swiftui.md

Optimizing App Store listing
  -> Follow ASO workflow for metadata and keywords
  -> See: workflows/app-store-aso.md
```

---

## Full Reference

For the complete compiled reference document with all content from every section, see [AGENTS.md](AGENTS.md).

---

## Dependencies

**Related skills:**
- `kotlin-android` - Android/Kotlin development (see workflows/swift-migration.md for cross-platform)

**Recommended context files:**
- Project-specific `docs/swift-conventions.md`
- Project-specific `docs/swift-best-practices.md`
- Project-specific `docs/liquid-glass-conventions.md`
- Project-specific `docs/design-conventions.md`
