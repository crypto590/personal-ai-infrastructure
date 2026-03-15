---
name: ios-swift
description: >
  Unified iOS/Swift development skill. Covers MVC architecture (Controllers, Services, Models, Views),
  SwiftUI patterns, code review (accessibility, Liquid Glass, concurrency, pattern validation, API research),
  quality checks (SwiftLint, build, tests), cross-platform migration, and iOS distribution (TestFlight,
  App Store Connect, code signing, xcodebuild CLI).
  Trigger words: iOS, Swift, SwiftUI, Xcode, Apple, accessibility, concurrency, Liquid Glass, MVC architecture,
  code review, pattern validation, VoiceOver, actor, async/await, task cancellation, Sendable, SwiftLint, build,
  TestFlight, distribution, App Store Connect, code signing, archive, provisioning profile.
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
| Pattern Validation | [review/pattern-validation.md](review/pattern-validation.md) | MVC compliance, controller/service/view/model validation, layer separation |
| API Research | [review/api-research.md](review/api-research.md) | Apple API investigation, documentation sources, availability checks |

**Severity Levels:**
- Critical: Block PR (data races, missing MainActor, missing VoiceOver labels, glass on content)
- Warning: Address before shipping (missing task cancellation, performance concerns)
- Info: Optional improvements (optimization suggestions)

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

### Workflows

| Topic | File | Summary |
|-------|------|---------|
| Swift Migration | [workflows/swift-migration.md](workflows/swift-migration.md) | iOS to Android migration patterns (Swift/SwiftUI -> Kotlin/Compose) |
| TestFlight Deployment | [workflows/testflight-deployment.md](workflows/testflight-deployment.md) | End-to-end TestFlight checklist — signing, archiving, upload, tester distribution |

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

Reviewing iOS code for PR
  -> Run review checklists
  -> See: review/*.md

Running quality checks before commit
  -> Run ios-check
  -> See: quality/checks.md
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
