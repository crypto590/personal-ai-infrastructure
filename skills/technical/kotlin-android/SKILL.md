---
name: kotlin-android
description: Expert Kotlin and Jetpack Compose development using MVVM architecture, Material Design 3, and modern Android patterns. Enforces strict architectural conventions, unidirectional data flow, and interface-based testing. USE WHEN building Android apps, refactoring to Kotlin/Compose, implementing MVVM, or migrating from other platforms (Swift, React Native).
---

# Kotlin/Android Development

## When to Activate This Skill

- Building new Android applications with Kotlin
- Implementing Jetpack Compose UI
- Refactoring to MVVM architecture
- Migrating from React Native/Swift to native Android
- Enforcing architectural patterns and conventions
- Material Design 3 implementation
- Android app modernization

## Core Architecture: MVVM + Compose

**Unidirectional Flow:**
```
Composable → ViewModel → Repository → Model
```

### Four Layers (Always Use)

**1. Models** (Data Classes)
- Always `data class`, immutable (`val`)
- Computed properties for business logic
- No async operations, no mutable state

**2. Repositories** (Interfaces + Implementations)
- `class` for async operations, `object` for pure functions
- Always interface-based for testing
- Stateless, return `Result<T>` for error handling
- No UI state management

**3. ViewModels** (Lifecycle-Aware)
- Extend `ViewModel`, use `StateFlow` for state
- Private `MutableStateFlow`, public `StateFlow` exposure
- Coroutines in `viewModelScope` for auto-cancellation
- Sealed UI state classes (Loading, Success, Error)
- No Compose dependencies

**4. Composables** (Jetpack Compose UI)
- Obtain ViewModel via `viewModel()` function
- Collect state with `collectAsStateWithLifecycle()`
- Delegate all actions to ViewModel
- Never call Repositories directly
- Never mutate ViewModel state

## Key Conventions

### Required Patterns

**ViewModel Structure:**
```kotlin
class FeatureViewModel(
    private val repository: FeatureRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun performAction() {
        viewModelScope.launch {
            repository.doWork()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message) }
        }
    }
}
```

**Composable Structure:**
```kotlin
@Composable
fun FeatureScreen(viewModel: FeatureViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> LoadingView()
        is UiState.Success -> ContentView(state.data)
        is UiState.Error -> ErrorView(state.message)
    }
}
```

### Material Design 3

- Use `androidx.compose.material3` components only
- Apply `MaterialTheme` for theming
- Dynamic color on Android 12+ via `dynamicColorScheme()`
- Follow semantic color roles (`onSurface`, `primaryContainer`)
- Never hardcode colors

### Error Handling

- Sealed UI state for all possible states
- ViewModel handles Repository errors
- `Result<T>` pattern in Repositories
- User-friendly error messages in Composables

### Navigation

- ViewModel owns navigation intent (sealed class)
- Composable owns `NavController` mechanism
- Use `Channel` and `Flow` for one-time events
- Modal state represented as nullable `StateFlow`

## Production Requirements Checklist

**ViewModel:**
- ✅ Extends `ViewModel`
- ✅ Private `MutableStateFlow` with public `StateFlow`
- ✅ Interface-based repository dependency
- ✅ Coroutines in `viewModelScope`
- ✅ Sealed UI state classes

**Repository:**
- ✅ Interface for testing
- ✅ No stored UI/business state
- ✅ Returns `Result<T>` or data classes
- ✅ Proper error handling

**Critical Rules:**
- ❌ Models: No async code, no mutable state
- ❌ Repositories: No UI state, stateless only
- ❌ ViewModels: No Compose dependencies
- ❌ Composables: Never call Repositories directly

## Available Workflows

### Swift Migration
For migrating iOS apps to Android: `read /Users/coreyyoung/Claude/skills/technical/kotlin-android/workflows/swift-migration.md`

## Comprehensive Reference

**Full conventions and patterns:**
`read /Users/coreyyoung/Claude/context/knowledge/languages/kotlin-conventions.md`

This includes:
- Detailed MVVM layer usage
- Advanced patterns (ViewModel composition, shared ViewModels)
- Navigation patterns
- Material 3 migration guide
- Testing with interface-based repositories
- Complete code examples

## Key Principles

1. **Unidirectional data flow**: UI observes state, never mutates
2. **Interface-based everything**: All components testable in isolation
3. **Structured concurrency**: Memory-safe async with lifecycle awareness
4. **Clear separation**: Each layer has single responsibility
5. **Material 3 first**: Modern design system from the start
