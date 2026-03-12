---
name: kotlin-android
description: Expert Kotlin and Jetpack Compose development using MVVM + UDF architecture, Material Design 3, and modern Android patterns. Enforces strict architectural conventions, unidirectional data flow, and interface-based testing. USE WHEN building Android apps, refactoring to Kotlin/Compose, implementing MVVM, dependency injection with Hilt, or migrating from other platforms (Swift, React Native).
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
- Implementing dependency injection with Hilt

## Core Architecture: MVVM + UDF + Compose

Google recommends a layered architecture with Unidirectional Data Flow (UDF), which aligns naturally with MVVM. State flows down, events flow up.

**Unidirectional Flow:**
```
Composable → ViewModel → (UseCase) → Repository → Model
```

### Core Layers

**1. Models** (Data Classes)
- Always `data class`, immutable (`val`)
- Computed properties for business logic
- No async operations, no mutable state

**2. Repositories** (Interfaces + Implementations)
- `class` for async operations, `object` for pure functions
- Always interface-based for testing
- Stateless, return `Result<T>` for error handling
- No UI state management

**2.5. Domain Layer** (Optional - Use Cases/Interactors)
- Optional layer for complex apps with shared business logic
- Use when multiple ViewModels need the same business rules
- Keeps ViewModels thin by extracting reusable logic
```kotlin
class GetNewsUseCase @Inject constructor(
    private val repository: NewsRepository
) {
    operator fun invoke(): Flow<List<Article>> = repository.getNews()
}
```

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

### MVI as Advanced Alternative

MVI (Model-View-Intent) adds explicit Intent/Event handling for stricter state management. Consider MVI for complex apps (banking, e-commerce, multi-step flows) where you need exhaustive event handling and state reproducibility. MVVM + UDF handles most scenarios well and is the recommended default.

## Key Conventions

### Required Patterns

**ViewModel Structure:**
```kotlin
@HiltViewModel
class FeatureViewModel @Inject constructor(
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

**StateFlow best practice:** Convert cold Flows to hot StateFlows using `stateIn()` with `SharingStarted.WhileSubscribed(5_000)` to survive configuration changes while cleaning up when the UI is gone.

**Process Death Handling:** Use `SavedStateHandle` to preserve critical ViewModel state across process death:
```kotlin
@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle,
    private val repository: FeatureRepository
) : ViewModel() {
    // Survives process death
    private val selectedId: String? = savedStateHandle["selectedId"]
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

### Dependency Injection (Hilt)

- Constructor injection preferred over field injection
- Use `@HiltViewModel` for ViewModels, `@Inject constructor` for repositories
- `@AndroidEntryPoint` on Activities/Fragments that use injection
- Provide interfaces via `@Binds` in Hilt modules

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

### Navigation (Type-Safe, Navigation 2.8+)

- Use `@Serializable` data classes/objects as route definitions (no string-based routes)
- ViewModel owns navigation intent via sealed class events
- Composable owns `NavController` mechanism
- Use `Channel` and `Flow` for one-time navigation events
- Modal state represented as nullable `StateFlow`

```kotlin
// Route definitions
@Serializable data object Home : Route
@Serializable data class AthleteDetail(val id: String) : Route

// NavHost setup
NavHost(navController, startDestination = Home) {
    composable<Home> { HomeScreen(onNavigate = { navController.navigate(it) }) }
    composable<AthleteDetail> { backStackEntry ->
        val route = backStackEntry.toRoute<AthleteDetail>()
        AthleteDetailScreen(athleteId = route.id)
    }
}
```

**Sealed interface for grouped routes:**
```kotlin
@Serializable sealed interface TopLevelRoute {
    @Serializable data object Home : TopLevelRoute
    @Serializable data object Search : TopLevelRoute
    @Serializable data object Profile : TopLevelRoute
}

// Feature-scoped navigation graph extension
fun NavGraphBuilder.athleteGraph(navController: NavController) {
    composable<AthleteList> { AthleteListScreen(navController) }
    composable<AthleteDetail> { backStackEntry ->
        val route = backStackEntry.toRoute<AthleteDetail>()
        AthleteDetailScreen(athleteId = route.id)
    }
}
```

**Nested navigation graphs per feature:**
```kotlin
// Main NavHost composes feature graphs
NavHost(navController, startDestination = TopLevelRoute.Home) {
    athleteGraph(navController)
    recruitingGraph(navController)
    feedGraph(navController)
    settingsGraph(navController)
}
```

Each feature module defines its own `NavGraphBuilder` extension, keeping navigation decoupled.

### Coroutine Patterns

**Debounce with Job cancellation (search, filtering):**
```kotlin
private var searchJob: Job? = null

fun onSearchQueryChanged(query: String) {
    searchJob?.cancel()
    searchJob = viewModelScope.launch {
        delay(300) // debounce
        repository.search(query)
            .onSuccess { _uiState.value = UiState.Success(it) }
            .onFailure { _uiState.value = UiState.Error(it.message) }
    }
}
```

**Parallel loading with coroutineScope/async:**
```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        _uiState.value = UiState.Loading
        coroutineScope {
            val profile = async { repository.getProfile() }
            val stats = async { repository.getStats() }
            val feed = async { repository.getFeed() }

            _uiState.value = UiState.Success(
                profile = profile.await().getOrThrow(),
                stats = stats.await().getOrThrow(),
                feed = feed.await().getOrThrow()
            )
        }
    }
}
```

### Pagination Patterns

**Cursor-based (preferred for feeds, timelines):**
```kotlin
private var cursor: String? = null
private val _items = MutableStateFlow<List<Item>>(emptyList())

fun loadMore() {
    if (isLoading) return
    viewModelScope.launch {
        repository.getItems(cursor = cursor, limit = 20)
            .onSuccess { page ->
                _items.value = _items.value + page.items
                cursor = page.nextCursor
            }
    }
}
```

**Offset-based (for search results, admin lists):**
```kotlin
fun loadPage(page: Int) {
    viewModelScope.launch {
        repository.getItems(offset = page * PAGE_SIZE, limit = PAGE_SIZE)
            .onSuccess { _uiState.value = UiState.Success(it) }
    }
}
```

### Optimistic UI

Update UI immediately, rollback on failure:
```kotlin
fun toggleFavorite(item: Item) {
    val previous = _uiState.value
    // Optimistic update
    _uiState.value = updateItemInState(item.copy(isFavorite = !item.isFavorite))

    viewModelScope.launch {
        repository.toggleFavorite(item.id)
            .onFailure {
                _uiState.value = previous // Rollback
                _events.send(UiEvent.ShowSnackbar("Failed to update"))
            }
    }
}
```

### ViewModel Scoping

- Default: ViewModel scoped to nearest `NavBackStackEntry` or `ViewModelStoreOwner`
- **Shared across screens**: Use `@ActivityRetainedScoped` for state that survives navigation
- **App-wide singletons**: Use `@Singleton` in Hilt modules

```kotlin
// Shared ViewModel scoped to Activity (survives navigation)
@HiltViewModel
class SharedSessionViewModel @Inject constructor(
    private val authManager: AuthManager
) : ViewModel() {
    val currentUser: StateFlow<User?> = authManager.currentUser
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
}

// Access from any Composable in the Activity
@Composable
fun SomeScreen(
    sharedVm: SharedSessionViewModel = hiltViewModel(
        viewModelStoreOwner = LocalContext.current as ComponentActivity
    )
)
```

### Compose Performance & Stability

- Annotate immutable data classes with `@Immutable` to skip unnecessary recompositions
- Use `@Stable` for classes with stable public API but mutable internals
- Prefer `ImmutableList` (from kotlinx.collections.immutable) over `List` in state
- Audit recompositions with Layout Inspector's "Show recomposition counts"

```kotlin
@Immutable
data class AthleteUiModel(
    val id: String,
    val name: String,
    val stats: ImmutableList<Stat>
)

@Stable
class ThemeState(
    val isDark: Boolean,
    val colorScheme: ColorScheme
)
```

## Production Requirements Checklist

**ViewModel:**
- ✅ `@HiltViewModel` with `@Inject constructor`
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

**Release Build:**
- ✅ ProGuard/R8 keep rules for `@Serializable` classes
- ✅ Keep rules for Ktor, Hilt, and Room
- ✅ Baseline Profiles generated in CI

## Available Workflows

### Swift Migration
For migrating iOS apps to Android: `read /Users/coreyyoung/.claude/skills/technical/kotlin-android/workflows/swift-migration.md`

## Comprehensive Reference

**Full conventions and patterns:**
`read /Users/coreyyoung/.claude/context/knowledge/languages/kotlin-conventions.md`

This includes:
- Detailed MVVM layer usage
- Advanced patterns (ViewModel composition, shared ViewModels)
- Navigation patterns
- Material 3 migration guide
- Testing with interface-based repositories
- Complete code examples

## Key Principles

1. **Unidirectional data flow**: UI observes state, never mutates
2. **Single Source of Truth (SSOT)**: Each piece of data has one authoritative source
3. **Interface-based everything**: All components testable in isolation
4. **Structured concurrency**: Memory-safe async with lifecycle awareness
5. **Clear separation**: Each layer has single responsibility
6. **Material 3 first**: Modern design system from the start
