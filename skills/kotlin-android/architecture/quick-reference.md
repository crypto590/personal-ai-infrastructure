# Quick Reference

**Part of:** [kotlin-android](../SKILL.md) > Architecture

---

## Decision Trees

### What Layer Do I Need?

```
What are you building?

Immutable data structure with business logic
→ Create Model (data class with computed properties)

Async operation (API call, database access)
→ Create Repository (interface + implementation class)

UI state management or coordinating data
→ Create ViewModel (@HiltViewModel extending ViewModel)

Render UI or handle user input
→ Create Composable (@Composable function)

Business logic shared by 2+ ViewModels
→ Consider UseCase in domain layer

Background task that survives process death
→ CoroutineWorker with WorkManager
```

### StateFlow vs SharedFlow vs Channel?

```
Emitting current UI state (screens, forms)?
→ StateFlow (MutableStateFlow with asStateFlow())

One-shot events (navigation, snackbars, dialogs)?
→ Channel<Event>(Channel.BUFFERED) exposed as receiveAsFlow()

Broadcasting to multiple collectors?
→ SharedFlow with replay = 0

Lifecycle-aware collection in Composable?
→ collectAsStateWithLifecycle() (always use over collectAsState())
```

### LazyColumn vs Column?

```
Unknown or large number of items?
→ LazyColumn (only composes visible items)

Small, fixed number of items (< ~10)?
→ Column with items directly

Need sections/headers/footers?
→ LazyColumn with LazyListScope items/item functions
```

### ViewModel Scope?

```
State for one screen?
→ Default: hiltViewModel() scoped to BackStackEntry

State shared across sibling screens in a flow (checkout, onboarding)?
→ hiltViewModel(navBackStackEntry) scoped to nav graph

State for entire session (auth user, cart)?
→ hiltViewModel(LocalContext.current as ComponentActivity)
```

---

## Code Templates

### ViewModel Template

```kotlin
@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val repository: FeatureRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<FeatureUiState>(FeatureUiState.Loading)
    val uiState: StateFlow<FeatureUiState> = _uiState.asStateFlow()

    private val _events = Channel<FeatureEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    init {
        loadData()
    }

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = FeatureUiState.Loading
            repository.fetchData()
                .onSuccess { _uiState.value = FeatureUiState.Success(it) }
                .onFailure { _uiState.value = FeatureUiState.Error(it.message ?: "Error") }
        }
    }

    fun clearError() {
        if (_uiState.value is FeatureUiState.Error) {
            _uiState.value = FeatureUiState.Loading
        }
    }
}

sealed interface FeatureUiState {
    data object Loading : FeatureUiState
    data class Success(val data: FeatureData) : FeatureUiState
    data class Error(val message: String) : FeatureUiState
}

sealed interface FeatureEvent {
    data object NavigateBack : FeatureEvent
    data class ShowSnackbar(val message: String) : FeatureEvent
}
```

### Repository Template

```kotlin
// Interface
interface FeatureRepository {
    suspend fun fetchData(): Result<FeatureData>
    suspend fun saveData(data: FeatureData): Result<Unit>
}

// Implementation
class FeatureRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : FeatureRepository {

    override suspend fun fetchData(): Result<FeatureData> {
        return try {
            val response = apiService.getData()
            Result.success(response.toDomain())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun saveData(data: FeatureData): Result<Unit> {
        return try {
            apiService.putData(data.toRequest())
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Composable Screen Template

```kotlin
@Composable
fun FeatureScreen(
    onNavigateBack: () -> Unit = {},
    viewModel: FeatureViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is FeatureEvent.NavigateBack -> onNavigateBack()
                is FeatureEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) },
        topBar = {
            TopAppBar(
                title = { Text("Feature") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentAlignment = Alignment.Center
        ) {
            when (val state = uiState) {
                is FeatureUiState.Loading -> CircularProgressIndicator()
                is FeatureUiState.Success -> FeatureContent(data = state.data)
                is FeatureUiState.Error -> {
                    AlertDialog(
                        onDismissRequest = viewModel::clearError,
                        confirmButton = {
                            TextButton(onClick = viewModel::clearError) { Text("OK") }
                        },
                        title = { Text("Error") },
                        text = { Text(state.message) }
                    )
                }
            }
        }
    }
}
```

### Hilt Module Template

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class FeatureModule {

    @Binds
    @Singleton
    abstract fun bindFeatureRepository(impl: FeatureRepositoryImpl): FeatureRepository
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

### Fake Repository Template (for testing)

```kotlin
class FakeFeatureRepository : FeatureRepository {
    var data: FeatureData? = null
    var shouldFail: Boolean = false
    var fetchCallCount = 0

    override suspend fun fetchData(): Result<FeatureData> {
        fetchCallCount++
        if (shouldFail) return Result.failure(Exception("Fake error"))
        return data?.let { Result.success(it) }
            ?: Result.failure(Exception("No data"))
    }

    override suspend fun saveData(data: FeatureData): Result<Unit> {
        if (shouldFail) return Result.failure(Exception("Save failed"))
        this.data = data
        return Result.success(Unit)
    }

    fun reset() {
        data = null
        shouldFail = false
        fetchCallCount = 0
    }
}
```

---

## Common Patterns Cheat Sheet

### Loading State

```kotlin
// ViewModel
private val _uiState = MutableStateFlow<UiState>(UiState.Loading)

fun load() {
    viewModelScope.launch {
        _uiState.value = UiState.Loading
        repository.fetch()
            .onSuccess { _uiState.value = UiState.Success(it) }
            .onFailure { _uiState.value = UiState.Error(it.message ?: "") }
    }
}

// Composable
when (val state = uiState) {
    is UiState.Loading -> CircularProgressIndicator()
    is UiState.Success -> Content(state.data)
    is UiState.Error -> ErrorView(state.message)
}
```

### Debounced Search

```kotlin
private var searchJob: Job? = null

fun onQueryChanged(query: String) {
    searchJob?.cancel()
    if (query.isBlank()) {
        _uiState.value = SearchUiState.Idle
        return
    }
    searchJob = viewModelScope.launch {
        delay(300)
        repository.search(query)
            .onSuccess { _uiState.value = SearchUiState.Results(it) }
    }
}
```

### One-Shot Navigation Event

```kotlin
// ViewModel
private val _events = Channel<Event>(Channel.BUFFERED)
val events = _events.receiveAsFlow()

fun onSuccess() {
    viewModelScope.launch { _events.send(Event.NavigateToHome) }
}

// Composable
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is Event.NavigateToHome -> navController.navigate(HomeRoute)
        }
    }
}
```

### Pagination (Cursor-based)

```kotlin
private var nextCursor: String? = null

fun loadMore() {
    val state = _uiState.value as? UiState.Success ?: return
    if (!state.hasMore) return
    viewModelScope.launch {
        repository.fetchPage(cursor = nextCursor)
            .onSuccess { page ->
                nextCursor = page.nextCursor
                _uiState.update { current ->
                    (current as UiState.Success).copy(
                        items = current.items + page.items,
                        hasMore = page.hasMore
                    )
                }
            }
    }
}
```

### Optimistic UI

```kotlin
fun onToggleLike(item: Item) {
    val previous = _uiState.value
    _uiState.update { optimisticUpdate(it, item) }
    viewModelScope.launch {
        repository.toggleLike(item.id)
            .onFailure { _uiState.value = previous } // rollback
    }
}
```

### stateIn for Flows

```kotlin
// Convert cold Flow to hot StateFlow
val items: StateFlow<List<Item>> = repository.observeItems()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList()
    )
```

---

## File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Model | `PascalCase.kt` | `User.kt`, `Post.kt` |
| Repository interface | `{Name}Repository.kt` | `UserRepository.kt` |
| Repository impl | `{Name}RepositoryImpl.kt` | `UserRepositoryImpl.kt` |
| ViewModel | `{Feature}ViewModel.kt` | `UserViewModel.kt` |
| Composable screen | `{Feature}Screen.kt` | `UserScreen.kt` |
| Composable component | `{Name}.kt` | `UserCard.kt`, `PostItem.kt` |
| Hilt module | `{Scope}Module.kt` | `RepositoryModule.kt`, `NetworkModule.kt` |
| Room DAO | `{Entity}Dao.kt` | `UserDao.kt` |
| Room entity | `{Name}Entity.kt` | `UserEntity.kt` |
| Route | `{Feature}Route.kt` | Defined in a routes file or feature module |
| UseCase | `{Action}{Entity}UseCase.kt` | `GetUserFeedUseCase.kt` |

---

## Package Structure

```
com.myapp/
├── core/
│   ├── data/
│   │   ├── network/          # Retrofit, ApiService
│   │   └── local/            # Room database, DAOs
│   ├── di/                   # Hilt modules
│   └── ui/
│       ├── theme/            # MaterialTheme, colors, typography, shapes
│       └── components/       # Reusable Composables
├── features/
│   ├── auth/
│   │   ├── data/             # AuthRepository, AuthRepositoryImpl
│   │   ├── model/            # Credentials, AuthResponse
│   │   ├── SignInViewModel.kt
│   │   └── SignInScreen.kt
│   ├── feed/
│   │   ├── data/
│   │   ├── model/
│   │   ├── FeedViewModel.kt
│   │   └── FeedScreen.kt
│   └── profile/
└── navigation/
    ├── Routes.kt             # @Serializable route definitions
    └── AppNavHost.kt
```

---

## Gradle Dependency Checklist

```kotlin
dependencies {
    // Core
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.5")
    implementation("androidx.activity:activity-compose:1.9.2")

    // Compose BOM (manages all Compose versions)
    implementation(platform("androidx.compose:compose-bom:2024.09.02"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")

    // Lifecycle & ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.5")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.5")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.8.1")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.51.1")
    kapt("com.google.dagger:hilt-android-compiler:2.51.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Retrofit + Kotlin Serialization
    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.jakewharton.retrofit:retrofit2-kotlinx-serialization-converter:1.0.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Image loading
    implementation("io.coil-kt:coil-compose:2.7.0")

    // Adaptive layouts
    implementation("androidx.compose.material3.adaptive:adaptive:1.0.0")
    implementation("androidx.compose.material3.adaptive:adaptive-layout:1.0.0")
    implementation("androidx.compose.material3.adaptive:adaptive-navigation:1.0.0")

    // Paging (if needed)
    implementation("androidx.paging:paging-compose:3.3.2")

    // WorkManager (if needed)
    implementation("androidx.work:work-runtime-ktx:2.9.1")

    // Testing
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
    testImplementation("app.cash.turbine:turbine:1.1.0")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")
}
```

---

## Frequently Used Imports

```kotlin
// ViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.launch

// Composable
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.hilt.navigation.compose.hiltViewModel

// Material 3
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState

// Compose Layout
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

// Navigation
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.toRoute
import kotlinx.serialization.Serializable
```

---

## Layer Summary

| Layer | Type | Role | Rules |
|-------|------|------|-------|
| **Model** | `data class` | Immutable data + computed properties | No async, no mutable state |
| **Repository** | `interface` + `class` impl | Async data access | Returns `Result<T>`, no UI state |
| **ViewModel** | `@HiltViewModel class` | UI state + coordination | No Compose imports, `viewModelScope` only |
| **Composable** | `@Composable fun` | Render UI, delegate actions | Never call repos directly, never mutate VM |

---

## Common Scenarios Quick Lookup

| Scenario | Pattern |
|----------|---------|
| Fetch data on screen open | `init { loadData() }` in ViewModel |
| Navigate on event | `Channel` events, `LaunchedEffect` collector in Composable |
| Show loading spinner | `UiState.Loading` → `CircularProgressIndicator()` |
| Handle API error | `Result.failure` → `UiState.Error` → `AlertDialog` |
| Search with debounce | `delay(300)` + `Job.cancel()` in ViewModel |
| Infinite scroll | Load more when last item appears, append to list |
| Pull to refresh | `PullToRefreshBox`, call `refresh()` on ViewModel |
| Form validation | Computed `isFormValid` property on UI state data class |
| Password toggle | `isPasswordVisible` in UI state, `PasswordVisualTransformation` |
| Share content | `Channel` event → Intent in Composable |
| Offline first | Room as SSOT, `Flow` from DAO, sync in background |
