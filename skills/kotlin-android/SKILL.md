---
name: kotlin-android
effort: high
description: "Unified Kotlin/Android/Compose development. MVVM architecture, code review, ktlint, Detekt, accessibility, and Play Store distribution."
metadata:
  last_reviewed: 2026-03-17
  review_cycle: 90
---

# Kotlin/Android Development

Comprehensive skill covering architecture, code review, quality assurance, and best practices for Kotlin/Android/Jetpack Compose development.

---

## Capabilities

### Architecture (MVVM + UDF)

Modern MVVM architecture with Unidirectional Data Flow for Kotlin/Compose. ViewModels manage state and coordinate Repositories, Repositories handle data operations, Models are pure immutable data, Composables delegate all actions to ViewModels.

| Topic | File | Summary |
|---|---|---|
| ViewModels | [architecture/viewmodels.md](architecture/viewmodels.md) | StateFlow patterns, viewModelScope, sealed UI states, SavedStateHandle |
| Repositories | [architecture/repositories.md](architecture/repositories.md) | Interface-based design, Result<T>, Hilt binding, Room + Retrofit |
| Models | [architecture/models.md](architecture/models.md) | Immutable data classes, @Immutable, domain/entity/DTO separation |
| Composables | [architecture/composables.md](architecture/composables.md) | hiltViewModel, collectAsStateWithLifecycle, state hoisting |
| Navigation | [architecture/navigation.md](architecture/navigation.md) | Type-safe @Serializable routes, NavHost, feature graphs |
| Error Handling | [architecture/error-handling.md](architecture/error-handling.md) | Sealed UI states, Result<T>, SnackbarHost, error propagation |
| Advanced Patterns | [architecture/advanced-patterns.md](architecture/advanced-patterns.md) | Shared ViewModels, UseCase layer, pagination, optimistic UI |
| Material Design | [architecture/material-design.md](architecture/material-design.md) | MaterialTheme, color roles, typography scale, dynamic color |
| Testing | [architecture/testing.md](architecture/testing.md) | Interface-based mocks, TestDispatcher, Compose testing |
| Examples | [architecture/examples.md](architecture/examples.md) | Complete real-world feature implementations |
| Quick Reference | [architecture/quick-reference.md](architecture/quick-reference.md) | Code templates, decision trees, anti-patterns |

**Core Principle:** Unidirectional data flow with strict layer separation.

```
Composable -> ViewModel -> (UseCase) -> Repository -> Model
```

**Production Requirements:**
- ViewModels: `@HiltViewModel`, `@Inject constructor`, private `MutableStateFlow`, public `StateFlow`, `viewModelScope`
- Repositories: interface + `@Inject` impl, `@Binds` module, returns `Result<T>`, no UI state
- Models: `data class`, all `val`, no async code, no `StateFlow`/`LiveData`, `@Immutable` for Compose
- Composables: `hiltViewModel()`, `collectAsStateWithLifecycle()`, never call repositories directly

---

### Code Review

Specialized review agents for Android code quality and compliance.

| Topic | File | Summary |
|---|---|---|
| Accessibility | [review/accessibility.md](review/accessibility.md) | TalkBack, touch targets, semantics, RTL, font scaling |
| Concurrency | [review/concurrency.md](review/concurrency.md) | viewModelScope, dispatchers, Flow lifecycle, thread safety |
| Pattern Validation | [review/pattern-validation.md](review/pattern-validation.md) | MVVM compliance, ViewModel/Repository/Composable/Model validation |
| API Research | [review/api-research.md](review/api-research.md) | Android API investigation, deprecated API watchlist, Jetpack BOM |
| Material Design 3 | [review/material-design-review.md](review/material-design-review.md) | Color roles, typography, dynamic color, dark mode, components |

**Severity Levels:**
- Critical: Block PR (GlobalScope, Composable calls Repository, missing TalkBack labels, hardcoded colors breaking dark mode)
- Warning: Address before shipping (collectAsState not lifecycle-aware, LiveData instead of StateFlow, string navigation routes)
- Info: Optional improvements (Compose stability annotations, spacing grid alignment)

---

### Quality Checks

Automated code quality tools for Android projects.

| Topic | File | Summary |
|---|---|---|
| Android Checks | [quality/checks.md](quality/checks.md) | ktlint, Detekt, Android Lint, JaCoCo coverage, Compose metrics |

**Quick Commands:**
- `/android-check` - Lint + build
- `/android-check --test` - Lint + build + tests
- `/android-check --fix` - Auto-fix ktlint violations
- `/android-check --coverage` - Tests with JaCoCo coverage report
- `/android-check --compose` - Compose compiler stability metrics

---

### Workflows

| Topic | File | Summary |
|---|---|---|
| Swift Migration | [workflows/swift-migration.md](workflows/swift-migration.md) | iOS to Android migration patterns (Swift/SwiftUI → Kotlin/Compose) |
| Play Store Distribution | [workflows/play-store-distribution.md](workflows/play-store-distribution.md) | End-to-end Play Store checklist — signing, AAB build, upload, staged rollout |

---

## Decision Tree

```
What are you building?

Data structure with business logic
  -> Create Model (data class, val properties, no async)
  -> See: architecture/models.md

Async operation (API, database, SDK)
  -> Create Repository (interface + @Inject impl)
  -> See: architecture/repositories.md

Shared business logic across ViewModels
  -> Create UseCase (@Inject class with operator invoke)
  -> See: architecture/advanced-patterns.md

UI state management or repository coordination
  -> Create ViewModel (@HiltViewModel)
  -> See: architecture/viewmodels.md

Display UI or handle user input
  -> Create Composable (delegates to ViewModel)
  -> See: architecture/composables.md

Reviewing Android code for PR
  -> Run review checklists
  -> See: review/*.md

Running quality checks before commit
  -> Run android-check
  -> See: quality/checks.md
```

---

## Dependencies

**Related skills:**
- `ios-swift` - iOS/Swift development (see workflows/swift-migration.md for cross-platform)

**Recommended context files:**
- Project-specific `docs/android-conventions.md`
- Project-specific `docs/architecture-decisions.md`

---

## Key Principles

1. **Unidirectional data flow**: Composables observe state, never mutate ViewModel properties
2. **Single Source of Truth (SSOT)**: Each piece of data has one authoritative source
3. **Interface-based everything**: All components testable in isolation via Hilt `@Binds`
4. **Structured concurrency**: `viewModelScope`, never `GlobalScope`, lifecycle-aware Flow collection
5. **Clear separation**: Each layer has single responsibility — no cross-layer violations
6. **Material 3 first**: `MaterialTheme.colorScheme`, `MaterialTheme.typography`, dynamic color
