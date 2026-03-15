# Android MVVM Pattern Validation

**Part of:** [kotlin-android](../SKILL.md) > Review

**Trigger:** After writing new Android features, before PR review for Kotlin/Compose code, asking "is my architecture correct?", reviewing ViewModels/Repositories/Composables, checking for proper layer separation, validating Hilt injection patterns, implementing new features.

---

## Validation Checklist

### 1. ViewModel Structure

**Required pattern with strict ordering:**

```kotlin
@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val repository: FeatureRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // REGION: UI State
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // REGION: Internal State
    private var currentPage = 0
    private var searchJob: Job? = null

    // REGION: Initialization
    init {
        val id: String? = savedStateHandle["id"]
        id?.let { loadFeature(it) }
    }

    // REGION: Public Actions
    fun loadFeature(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getFeature(id)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Unknown error") }
        }
    }

    fun onSearchQueryChanged(query: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300)
            if (isActive) loadSearch(query)
        }
    }

    // REGION: Private Helpers
    private suspend fun loadSearch(query: String) {
        repository.search(query)
            .onSuccess { _uiState.value = UiState.Success(it) }
    }
}
```

**Required ordering within ViewModels:**

1. UI state (`MutableStateFlow` / `StateFlow` pairs)
2. Internal state (`private var` tracking fields)
3. `init` block (if needed)
4. Public action functions
5. Private helper functions

**Validation points:**

| Check | Required | Status |
|---|---|---|
| `@HiltViewModel` | Yes | ? |
| `@Inject constructor` | Yes | ? |
| Extends `ViewModel()` | Yes | ? |
| Private `MutableStateFlow` | Yes | ? |
| Public `StateFlow` via `asStateFlow()` | Yes | ? |
| Interface-based repository dependency | Yes | ? |
| `viewModelScope.launch` for coroutines | Yes | ? |
| No Compose imports | Yes | ? |
| Sealed UI state class | Yes | ? |
| No `GlobalScope` usage | Yes | ? |

**Report format:**
```
VIEWMODEL: [ClassName]
- @HiltViewModel: [present/missing]
- @Inject constructor: [present/missing]
- MutableStateFlow private: [yes/no]
- StateFlow public: [yes/no]
- Repository interface (not impl): [yes/no]
- viewModelScope usage: [yes/no]
- Compose imports: [none/present - violation]
- Sealed UI state: [present/missing]
- Overall: [PASS/FAIL]
```

### 2. Repository Structure

**Required pattern:**

```kotlin
// Interface for testability
interface FeatureRepository {
    suspend fun getFeature(id: String): Result<Feature>
    suspend fun search(query: String): Result<List<Feature>>
    fun observeFeatures(): Flow<List<Feature>>
}

// Implementation with Hilt binding
class FeatureRepositoryImpl @Inject constructor(
    private val api: FeatureApi,
    private val dao: FeatureDao
) : FeatureRepository {

    override suspend fun getFeature(id: String): Result<Feature> =
        runCatching {
            val cached = dao.getFeature(id)
            if (cached != null) {
                cached.toDomain()
            } else {
                val remote = api.getFeature(id)
                dao.insert(remote.toEntity())
                remote.toDomain()
            }
        }

    override fun observeFeatures(): Flow<List<Feature>> =
        dao.observeAll().map { entities -> entities.map { it.toDomain() } }
}

// Hilt module binding
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindFeatureRepository(
        impl: FeatureRepositoryImpl
    ): FeatureRepository
}
```

**Validation points:**

| Check | Required | Status |
|---|---|---|
| Interface defined | Yes | ? |
| `@Inject constructor` on implementation | Yes | ? |
| No UI state stored | Yes | ? |
| Returns `Result<T>` or data classes | Yes | ? |
| `@Binds` in Hilt module | Yes | ? |
| Stateless (no `MutableStateFlow`) | Yes | ? |

**Report format:**
```
REPOSITORY: [RepositoryName]
- Interface: [defined/missing]
- Impl annotation: [@Inject/missing]
- Hilt binding: [@Binds present/missing]
- UI state in repository: [none/present - violation]
- Returns Result<T>: [yes/no]
- Overall: [PASS/FAIL]
```

### 3. Composable Delegation Pattern

**Required pattern:**

```kotlin
@Composable
fun FeatureScreen(
    viewModel: FeatureViewModel = hiltViewModel(),
    onNavigateToDetail: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Collect one-time events
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.NavigateToDetail -> onNavigateToDetail(event.id)
                is UiEvent.ShowError -> { /* show snackbar */ }
            }
        }
    }

    when (val state = uiState) {
        is UiState.Loading -> LoadingContent()
        is UiState.Success -> FeatureContent(
            data = state.data,
            onAction = viewModel::performAction  // Delegates to ViewModel
        )
        is UiState.Error -> ErrorContent(
            message = state.message,
            onRetry = viewModel::retry
        )
    }
}
```

**Validation points:**

| Check | Required | Status |
|---|---|---|
| `hiltViewModel()` for injection | Yes | ? |
| `collectAsStateWithLifecycle()` (not `collectAsState`) | Yes | ? |
| No direct repository calls | Yes | ? |
| No `MutableStateFlow` mutation | Yes | ? |
| Actions delegate to ViewModel | Yes | ? |
| Navigation callback as parameter | Yes | ? |

**Report format:**
```
COMPOSABLE: [ScreenName]
- hiltViewModel() usage: [yes/no]
- collectAsStateWithLifecycle: [yes/no]
- Direct repository calls: [none/count - violations]
- ViewModel state mutation: [none/count - violations]
- Action delegation: [yes/no]
- Overall: [PASS/FAIL]
```

### 4. Model Compliance

**Required pattern:**

```kotlin
// Domain model: pure data, immutable
data class Feature(
    val id: String,
    val name: String,
    val description: String,
    val createdAt: Long,
    val tags: List<String> = emptyList()
) {
    // Computed properties only
    val displayName: String get() = name.ifBlank { "Unnamed Feature" }
    val isTagged: Boolean get() = tags.isNotEmpty()
}

// Entity model: maps to database
@Entity(tableName = "features")
data class FeatureEntity(
    @PrimaryKey val id: String,
    val name: String,
    val description: String,
    val createdAt: Long
) {
    fun toDomain() = Feature(id = id, name = name, description = description, createdAt = createdAt)
}

// DTO model: maps to API response
@Serializable
data class FeatureDto(
    val id: String,
    val name: String,
    val description: String,
    @SerialName("created_at") val createdAt: Long
) {
    fun toDomain() = Feature(id = id, name = name, description = description, createdAt = createdAt)
}
```

**Validation points:**

| Check | Required | Status |
|---|---|---|
| `data class` (not regular class) | Yes | ? |
| All properties `val` (immutable) | Yes | ? |
| No suspend functions | Yes | ? |
| No `MutableStateFlow` or `LiveData` | Yes | ? |
| No ViewModel/Repository dependencies | Yes | ? |
| `@Immutable` annotation (for Compose stability) | Recommended | ? |

**Report format:**
```
MODEL: [ModelName]
- data class: [yes/class - violation]
- All val properties: [yes/count with var - violations]
- Suspend functions: [none/present - violation]
- StateFlow/LiveData: [none/present - violation]
- @Immutable annotation: [present/missing]
- Overall: [PASS/FAIL]
```

### 5. Navigation Patterns (Type-Safe)

**Required pattern (Navigation 2.8+):**

```kotlin
// Route definitions — serializable, not strings
@Serializable data object HomeRoute
@Serializable data class FeatureDetailRoute(val id: String)
@Serializable data class FeatureEditRoute(val id: String, val isNew: Boolean = false)

// NavHost setup
NavHost(navController = navController, startDestination = HomeRoute) {
    composable<HomeRoute> {
        HomeScreen(
            onNavigateToDetail = { id ->
                navController.navigate(FeatureDetailRoute(id))
            }
        )
    }
    composable<FeatureDetailRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<FeatureDetailRoute>()
        FeatureDetailScreen(featureId = route.id)
    }
}
```

**Validation points:**

| Check | Required | Status |
|---|---|---|
| `@Serializable` route data classes/objects | Yes | ? |
| No string-based routes | Yes | ? |
| `toRoute<T>()` for argument extraction | Yes | ? |
| `composable<T>` with type parameter | Yes | ? |
| Navigation actions passed as lambdas | Yes | ? |

**Report format:**
```
NAVIGATION: [NavGraph or Screen]
- Serializable routes: [yes/no]
- String routes: [none/count - violations]
- toRoute<T>() usage: [yes/no]
- Navigation lambdas (not NavController in ViewModel): [yes/no]
- Overall: [PASS/FAIL]
```

### 6. State Management (StateFlow, not LiveData)

**Check:** Modern StateFlow patterns, not deprecated LiveData.

```kotlin
// GOOD - StateFlow
private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()

// VIOLATION - LiveData is deprecated in favor of StateFlow
private val _uiState = MutableLiveData<UiState>()  // VIOLATION
val uiState: LiveData<UiState> = _uiState

// GOOD - stateIn for converting cold Flow to hot StateFlow
val users: StateFlow<List<User>> = repository.observeUsers()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList()
    )
```

**Report format:**
```
STATE MANAGEMENT: [PASS/WARN]
- StateFlow usage: [count]
- LiveData usage: [list - violations, should migrate]
- stateIn with WhileSubscribed: [count]
- Correct initial values: [yes/no]
```

### 7. DI Compliance (Hilt)

**Check:** All injection uses Hilt, no manual construction.

```kotlin
// GOOD - Hilt provides everything
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {
    // Hilt injects into activities with @AndroidEntryPoint
}

@AndroidEntryPoint
class FeatureFragment : Fragment() {
    private val viewModel: FeatureViewModel by viewModels()  // Hilt-provided
}

// VIOLATION - Manual construction bypasses DI
class BadActivity : AppCompatActivity() {
    private val viewModel = FeatureViewModel(  // VIOLATION: manual construction
        repository = FeatureRepositoryImpl(api, dao)
    )
}

// GOOD - Hilt module for third-party dependencies
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()
}
```

**Validation points:**

| Check | Required | Status |
|---|---|---|
| `@AndroidEntryPoint` on Activities/Fragments | Yes | ? |
| `@HiltViewModel` on ViewModels | Yes | ? |
| `@Inject constructor` on repositories/services | Yes | ? |
| `@Binds` for interface-to-impl binding | Yes | ? |
| `@Provides` for third-party types | Yes | ? |
| No `new` / constructor calls in activities | Yes | ? |

**Report format:**
```
DI COMPLIANCE: [PASS/FAIL]
- @AndroidEntryPoint on entry points: [count/total]
- Manual ViewModel construction: [list - violations]
- Manual repository construction: [list - violations]
- Hilt modules for bindings: [count]
- Overall: [PASS/FAIL]
```

### 8. Layer Separation

**Check:** No cross-layer violations.

| From | To | Allowed |
|---|---|---|
| Composable | ViewModel | Yes |
| Composable | Repository | No |
| Composable | Model | Read only |
| ViewModel | Repository | Yes |
| ViewModel | Model | Yes |
| ViewModel | Composable API | No |
| Repository | ViewModel | No |
| Repository | Model | Yes |
| Model | Any | No (pure data) |

**Report format:**
```
LAYER SEPARATION: [PASS/FAIL]
- Composable -> Repository calls: [none/count - violations]
- ViewModel -> Compose imports: [none/count - violations]
- Repository with StateFlow/UI state: [none/count - violations]
- Model with suspend functions: [none/count - violations]
```

---

## Validation Matrix

For each feature, fill in this matrix:

| Requirement | ViewModel | Repository | Composable | Model |
|---|---|---|---|---|
| `@HiltViewModel` / `@Inject` | [ ] | [ ] | N/A | N/A |
| Interface-based | N/A | [ ] | N/A | N/A |
| Sealed state class | [ ] | N/A | N/A | N/A |
| `viewModelScope` / no GlobalScope | [ ] | N/A | N/A | N/A |
| `StateFlow` not `LiveData` | [ ] | N/A | N/A | N/A |
| `collectAsStateWithLifecycle` | N/A | N/A | [ ] | N/A |
| No layer violations | [ ] | [ ] | [ ] | [ ] |
| Immutable data | N/A | N/A | N/A | [ ] |
| Type-safe navigation | N/A | N/A | [ ] | N/A |

---

## Validation Output Format

```markdown
## Android MVVM Pattern Validation: [Feature Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical: [count]

### ViewModels
[details per ViewModel]

### Repositories
[details per repository]

### Composables
[details per screen]

### Models
[details per model]

### Layer Separation
[details]

### Navigation
[details]

### DI Compliance
[details]

### Critical Issues (must fix)
1. [list]

### Warnings (should fix)
1. [list]

### Recommendations
1. [list]
```

---

## Severity Levels

| Level | Criteria | Action |
|---|---|---|
| Critical | Composable calls Repository directly, ViewModel has Compose imports, `GlobalScope` usage, manual ViewModel construction bypassing Hilt | Block PR |
| Warning | `LiveData` instead of `StateFlow`, `collectAsState` instead of `collectAsStateWithLifecycle`, missing `@Immutable` on model, string-based navigation routes | Address before shipping |
| Info | Missing `// REGION:` comments, `stateIn` optimization, missing `@Immutable` annotation | Optional improvement |

---

## Quick Reference: What Goes Where

```
Feature needs...                        -> Create...
-----------------------------------------------------
Data structure with business logic      -> Model (data class, val, no async)
Async operation (API, database)         -> Repository (interface + @Inject impl)
UI state or repository coordination     -> ViewModel (@HiltViewModel)
Display UI or handle user input         -> Composable (delegates to ViewModel)
Shared business logic across ViewModels -> UseCase (@Inject class with operator invoke)
```
