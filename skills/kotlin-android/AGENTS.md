# Kotlin/Android Development - Full Compiled Reference

**This is the compiled reference for agents.** It contains ALL rules, patterns, checklists, and code examples from every section of the kotlin-android skill. For the navigable index, see [SKILL.md](SKILL.md).

---

# Part 1: Architecture (MVVM + UDF)

Modern MVVM architecture with Unidirectional Data Flow for Kotlin/Compose.

```
Composable -> ViewModel -> (UseCase) -> Repository -> Model
```

**Layer Separation Rules:**

| From | To | Allowed |
|------|----|---------|
| Composable | ViewModel | Yes |
| Composable | Repository | NO |
| Composable | Model | Read only |
| ViewModel | Repository | Yes |
| ViewModel | Model | Yes |
| ViewModel | Composable API | NO |
| Repository | ViewModel | NO |
| Repository | Model | Yes |
| Model | Any | NO (pure data) |

**Decision Tree:**

```
What are you building?

Immutable data structure with business logic -> Model (data class)
Async operation (API, database, SDK) -> Repository (interface + impl)
Shared business logic across ViewModels -> UseCase (@Inject class with operator invoke)
UI state management or coordination -> ViewModel (@HiltViewModel)
Display UI or handle user input -> Composable (delegates to ViewModel)
```

---

## 1.1 ViewModels (@HiltViewModel + StateFlow)

ViewModels manage UI state and coordinate repository calls. They bridge Composables (presentation) and Repositories (data layer).

**Key characteristics:**
- Always `@HiltViewModel` with `@Inject constructor`
- Extends `ViewModel`
- Private `MutableStateFlow`, public `StateFlow` via `asStateFlow()`
- Interface-based repository injection
- All coroutines in `viewModelScope`
- No Compose imports

### Basic ViewModel Pattern

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            repository.fetchUser(id)
                .onSuccess { user ->
                    _uiState.value = UserUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(
                        error.message ?: "Unknown error"
                    )
                }
        }
    }
}

sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}
```

### Required Property Order Within ViewModels

1. UI state (`MutableStateFlow` / `StateFlow` pairs)
2. Internal state (`private var` tracking fields)
3. `init` block (if needed)
4. Public action functions
5. Private helper functions

### Production Checklist

| Check | Required |
|-------|----------|
| `@HiltViewModel` | Yes |
| `@Inject constructor` | Yes |
| Extends `ViewModel()` | Yes |
| Private `MutableStateFlow` | Yes |
| Public `StateFlow` via `asStateFlow()` | Yes |
| Interface-based repository dependency | Yes |
| `viewModelScope.launch` for coroutines | Yes |
| No Compose imports | Yes |
| Sealed UI state class | Yes |
| No `GlobalScope` usage | Yes |
| No `LiveData` in new code | Yes |

### Converting Cold Flow to Hot StateFlow

```kotlin
val articles: StateFlow<List<Article>> = repository.getArticles()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = emptyList()
    )
```

### Job Cancellation Pattern (search, debounce)

```kotlin
private var searchJob: Job? = null

fun onSearchQueryChanged(query: String) {
    searchJob?.cancel()
    searchJob = viewModelScope.launch {
        delay(300) // debounce
        repository.searchUsers(query)
            .onSuccess { _uiState.value = UiState.Success(it) }
            .onFailure { _uiState.value = UiState.Error(it.message ?: "Search failed") }
    }
}
```

### SavedStateHandle for Process Death

```kotlin
@HiltViewModel
class DetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val repository: DetailRepository
) : ViewModel() {
    private val itemId: String = checkNotNull(savedStateHandle["itemId"])
    private val searchQuery = savedStateHandle.getStateFlow("searchQuery", "")
}
```

### ViewModel Anti-Patterns

- **Exposing MutableStateFlow**: Always use `asStateFlow()`
- **No Job cancellation**: Cancel previous search before starting new
- **Using LiveData in new code**: Use StateFlow instead
- **God ViewModel**: Split into focused ViewModels (~200 lines max)
- **Concrete repository dependency**: Use interfaces for testability
- **Holding Context reference**: Use `@ApplicationContext` if truly needed

---

## 1.2 Repositories (Interface + Implementation)

Repositories handle async operations. Always interface-based for testability.

**Key characteristics:**
- Always define interface + implementation
- Return `Result<T>` or `Flow<T>` for reactive data
- No UI state -- stateless operations (caching OK)
- Return domain Models, never ViewModels
- Never import Compose classes

### Interface + Implementation Pattern

```kotlin
interface UserRepository {
    suspend fun fetchUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<User>
    fun observeUser(id: String): Flow<User?>
}

class UserRepositoryImpl @Inject constructor(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : UserRepository {

    override suspend fun fetchUser(id: String): Result<User> {
        return try {
            val dto = remoteDataSource.getUser(id)
            val user = dto.toDomain()
            localDataSource.saveUser(user.toEntity())
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override fun observeUser(id: String): Flow<User?> =
        localDataSource.observeUser(id).map { it?.toDomain() }
}
```

### Hilt Binding

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class DataModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

### Error Handling at Repository Boundary

```kotlin
override suspend fun getProduct(id: String): Result<Product> {
    return try {
        val dto = api.getProduct(id)
        Result.success(dto.toDomain())
    } catch (e: HttpException) {
        when (e.code()) {
            401 -> Result.failure(AppError.Unauthorized)
            404 -> Result.failure(AppError.NotFound("Product not found"))
            in 500..599 -> Result.failure(AppError.ServerError(e.code()))
            else -> Result.failure(AppError.Unknown(e.message()))
        }
    } catch (e: IOException) {
        Result.failure(AppError.NetworkUnavailable)
    }
}
```

### Repository Production Checklist

| Check | Required |
|-------|----------|
| Interface defined | Yes |
| `@Inject constructor` on implementation | Yes |
| `@Binds` in Hilt module | Yes |
| Returns `Result<T>` or `Flow<T>` | Yes |
| No UI state stored | Yes |
| No Compose imports | Yes |
| No `MutableStateFlow` | Yes |

---

## 1.3 Models (Immutable Data Classes)

Models are pure data structures with computed properties.

**Key characteristics:**
- Always `data class`, never regular `class`
- Always immutable (`val` properties only)
- No `suspend` functions or coroutines
- No `MutableStateFlow`, `LiveData`, or ViewModel references
- Business logic in computed properties

### Basic Pattern

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val createdAt: Long
) {
    val displayName: String
        get() = name.ifBlank { email }

    val initials: String
        get() = name.split(" ")
            .take(2)
            .mapNotNull { it.firstOrNull()?.uppercaseChar() }
            .joinToString("")
}
```

### Three-Layer Model Separation

```kotlin
// Domain model (app-internal)
data class User(val id: String, val name: String, val email: String)

// Room entity (database)
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "display_name") val name: String,
    val email: String
)

// API DTO (network)
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("avatar_url") val avatarUrl: String? = null
)

// Mapping extensions
fun UserEntity.toDomain(): User = User(id = id, name = name, email = email)
fun UserDto.toDomain(): User = User(id = id, name = name, email = email)
```

### Sealed UI State

```kotlin
sealed interface ProductUiState {
    data object Loading : ProductUiState
    data class Success(val product: Product) : ProductUiState
    data class Error(val message: String) : ProductUiState
}
```

### Model Production Checklist

| Check | Required |
|-------|----------|
| `data class` | Yes |
| All properties `val` | Yes |
| No suspend functions | Yes |
| No `MutableStateFlow`/`LiveData` | Yes |
| No ViewModel/Context references | Yes |
| `@Immutable` for Compose stability | Recommended |

---

## 1.4 Composables (Jetpack Compose)

Composables render UI and delegate actions to ViewModels.

**Key characteristics:**
- Obtain ViewModel with `hiltViewModel()`
- Collect state with `collectAsStateWithLifecycle()` -- NOT `collectAsState()`
- Delegate all actions to ViewModel methods
- No business logic in Composables
- Never call Repositories directly

### Basic Screen Pattern

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UserUiState.Success -> {
            UserContent(user = state.user, onRefresh = viewModel::refresh)
        }
        is UserUiState.Error -> {
            ErrorScreen(message = state.message, onRetry = viewModel::retry)
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser()
    }
}
```

### State Hoisting

```kotlin
// Stateful (owns ViewModel)
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val query by viewModel.query.collectAsStateWithLifecycle()
    val results by viewModel.results.collectAsStateWithLifecycle()
    SearchScreenContent(query = query, results = results, onQueryChange = viewModel::onQueryChanged)
}

// Stateless (receives state and callbacks)
@Composable
fun SearchScreenContent(
    query: String,
    results: SearchUiState,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) { /* pure UI */ }
```

### Naming and Parameter Conventions

```kotlin
// Screen-level: route args first, nav callbacks, ViewModel last with default
@Composable
fun UserProfileScreen(
    userId: String,
    onNavigateToSettings: () -> Unit,
    viewModel: UserProfileViewModel = hiltViewModel()
)

// UI components: data first, callbacks, Modifier always last with default
@Composable
fun UserCard(
    user: User,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
)
```

### Side Effects

```kotlin
// LaunchedEffect -- tied to composition lifecycle
LaunchedEffect(Unit) { viewModel.loadData() }
LaunchedEffect(userId) { viewModel.loadUser(userId) }

// Collect one-time events
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            is UiEvent.NavigateToDetail -> onNavigateToDetail(event.id)
        }
    }
}

// rememberCoroutineScope -- user-triggered coroutines
val scope = rememberCoroutineScope()
Button(onClick = { scope.launch { snackbarHostState.showSnackbar("Saved") } })
```

### Performance: Stability

```kotlin
// @Immutable for data classes passed to Composables
@Immutable
data class UserCardData(val id: String, val name: String, val avatarUrl: String?)

// ImmutableList for stable collections
@Immutable
data class NewsUiState(val articles: ImmutableList<Article>)

// derivedStateOf -- avoid recomposition from rapid state changes
val showScrollToTop by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 2 }
}
```

### Composable Anti-Patterns

- **Side effects in composition**: Use `LaunchedEffect`, not direct calls
- **Calling Repositories directly**: Always through ViewModel
- **`collectAsState`**: Use `collectAsStateWithLifecycle()`
- **Unstable lambda captures**: Use stable function references

---

## 1.5 Navigation (Type-Safe @Serializable Routes)

Use Navigation Compose 2.8+ with `@Serializable` route classes. Never string-based routes.

### Route Definitions

```kotlin
@Serializable data object HomeRoute
@Serializable data object SearchRoute
@Serializable data class ProfileRoute(val userId: String)
@Serializable data class ArticleDetailRoute(val articleId: String, val fromPush: Boolean = false)
```

### Basic NavHost

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = HomeRoute) {
        composable<HomeRoute> {
            HomeScreen(
                onNavigateToArticle = { id ->
                    navController.navigate(ArticleDetailRoute(articleId = id))
                }
            )
        }
        composable<ArticleDetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<ArticleDetailRoute>()
            ArticleDetailScreen(articleId = route.articleId)
        }
    }
}
```

### Navigation Events from ViewModel

```kotlin
@HiltViewModel
class ArticleViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    sealed interface NavEvent {
        data class ToDetail(val articleId: String) : NavEvent
        data object Back : NavEvent
    }

    private val _navEvents = Channel<NavEvent>(Channel.BUFFERED)
    val navEvents = _navEvents.receiveAsFlow()

    fun onArticleClicked(articleId: String) {
        viewModelScope.launch {
            _navEvents.send(NavEvent.ToDetail(articleId))
        }
    }
}
```

### Feature Graphs

```kotlin
fun NavGraphBuilder.articlesGraph(navController: NavController) {
    composable<ArticleListRoute> {
        ArticleListScreen(
            onNavigateToDetail = { id ->
                navController.navigate(ArticleDetailRoute(articleId = id))
            }
        )
    }
    composable<ArticleDetailRoute> { backStackEntry ->
        val route = backStackEntry.toRoute<ArticleDetailRoute>()
        ArticleDetailScreen(articleId = route.articleId, onNavigateBack = { navController.popBackStack() })
    }
}
```

### Navigation Anti-Patterns

- **String routes**: Use `@Serializable` data classes/objects
- **NavController in ViewModel**: ViewModel emits events, Composable handles NavController
- **Business logic in navigation**: ViewModel decides WHERE, Composable implements HOW

---

## 1.6 Error Handling

Repositories map exceptions to domain errors. ViewModels translate to UI state.

### Sealed AppError

```kotlin
sealed class AppError : Exception() {
    data object NetworkUnavailable : AppError() {
        override val message = "No internet connection. Please check your network and try again."
    }
    data object Unauthorized : AppError() {
        override val message = "Your session has expired. Please sign in again."
    }
    data class NotFound(val resource: String) : AppError() {
        override val message = "$resource could not be found."
    }
    data class ServerError(val code: Int) : AppError() {
        override val message = "Server error ($code). Please try again later."
    }
    data class Unknown(override val message: String = "An unexpected error occurred.") : AppError()

    companion object {
        fun from(e: HttpException): AppError = when (e.code()) {
            401 -> Unauthorized
            403 -> Forbidden
            404 -> NotFound("Resource")
            in 500..599 -> ServerError(e.code())
            else -> Unknown(e.message())
        }
    }
}
```

### Result Pattern

```kotlin
// Repository wraps exceptions in Result.failure
override suspend fun fetchUser(id: String): Result<User> = try {
    Result.success(api.getUser(id).toDomain())
} catch (e: HttpException) {
    Result.failure(AppError.from(e))
} catch (e: IOException) {
    Result.failure(AppError.NetworkUnavailable)
}

// ViewModel handles Result
repository.fetchUser(id)
    .onSuccess { _uiState.value = UiState.Success(it) }
    .onFailure { _uiState.value = UiState.Error(it.toUserMessage()) }

// Extension for user-friendly messages
fun Throwable.toUserMessage(): String = when (this) {
    is AppError -> message ?: "Error"
    is IOException -> "No internet connection"
    is HttpException -> AppError.from(this).message ?: "Server error"
    else -> "An unexpected error occurred"
}
```

### Snackbar / One-Time Events for Non-Fatal Errors

```kotlin
private val _events = Channel<UiEvent>(Channel.BUFFERED)
val events = _events.receiveAsFlow()

// In ViewModel: send event
_events.send(UiEvent.ShowSnackbar("Failed to update"))

// In Composable: collect
val snackbarHostState = remember { SnackbarHostState() }
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
        }
    }
}
Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { /* content */ }
```

---

## 1.7 Testing

Interface-based repositories enable testing without network or database calls.

### Testing Framework Hierarchy

| Layer | Framework | When to Use |
|-------|-----------|-------------|
| Unit (ViewModel, Repository) | JUnit5 + Kotlin Coroutines Test | Business logic, state transitions |
| Flow assertions | Turbine | StateFlow / SharedFlow emissions |
| Room DAO | JUnit4 + In-memory Room | Database queries |
| Compose UI | `ComposeTestRule` (AndroidJUnit4) | Component rendering, interactions |

### Fake Repository Pattern

```kotlin
class FakeUserRepository : UserRepository {
    var user: User? = null
    var shouldFail: Boolean = false
    var delay: Long = 0L

    override suspend fun fetchUser(id: String): Result<User> {
        if (delay > 0) kotlinx.coroutines.delay(delay)
        if (shouldFail) return Result.failure(Exception("Fake network error"))
        return user?.let { Result.success(it) }
            ?: Result.failure(Exception("User not found"))
    }
}
```

### ViewModel Test Pattern

```kotlin
@ExtendWith(MainDispatcherExtension::class)
class UserViewModelTest {

    private lateinit var fakeRepository: FakeUserRepository
    private lateinit var viewModel: UserViewModel

    @BeforeEach
    fun setup() {
        fakeRepository = FakeUserRepository()
        viewModel = UserViewModel(repository = fakeRepository)
    }

    @Test
    fun `loadUser emits Success state with user data`() = runTest {
        fakeRepository.user = User(id = "1", name = "Alice", email = "alice@test.com")
        viewModel.loadUser("1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Success)
        assertEquals("Alice", (state as UserUiState.Success).user.name)
    }

    @Test
    fun `loadUser emits Error state when repository fails`() = runTest {
        fakeRepository.shouldFail = true
        viewModel.loadUser("1")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UserUiState.Error)
    }
}
```

### Turbine Flow Testing

```kotlin
@Test
fun `uiState emits Loading then Success`() = runTest {
    viewModel.uiState.test {
        assertEquals(UserUiState.Loading, awaitItem())
        viewModel.loadUser("1")
        assertEquals(UserUiState.Loading, awaitItem())
        val success = awaitItem()
        assertTrue(success is UserUiState.Success)
        cancelAndConsumeRemainingEvents()
    }
}
```

### MainDispatcherExtension (JUnit5)

```kotlin
class MainDispatcherExtension(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : BeforeEachCallback, AfterEachCallback {
    override fun beforeEach(context: ExtensionContext) { Dispatchers.setMain(dispatcher) }
    override fun afterEach(context: ExtensionContext) { Dispatchers.resetMain() }
}
```

### Testing Best Practices

**DO:** Test business logic not implementation, use descriptive backtick names, Arrange-Act-Assert, test edge cases, prefer fakes over mocks.

**DON'T:** Don't test Composable internals directly, don't share state between tests, don't use `Thread.sleep()`, don't test against real network/database.

---

## 1.8 Material Design 3

### App-Level Theme Setup

```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> darkColorScheme()
        else -> lightColorScheme()
    }
    MaterialTheme(colorScheme = colorScheme, typography = AppTypography, shapes = AppShapes, content = content)
}
```

### Color Roles Cheat Sheet

```kotlin
MaterialTheme.colorScheme.primary              // key actions, FABs
MaterialTheme.colorScheme.onPrimary            // text/icon on primary
MaterialTheme.colorScheme.primaryContainer     // filled tonal button background
MaterialTheme.colorScheme.surface              // screen background
MaterialTheme.colorScheme.surfaceVariant       // cards, chips
MaterialTheme.colorScheme.onSurface            // primary text
MaterialTheme.colorScheme.onSurfaceVariant     // secondary text, icons
MaterialTheme.colorScheme.error                // error states
```

### Typography Scale (key roles)

| Role | Size | Usage |
|------|------|-------|
| `headlineLarge` | 32sp | Screen titles |
| `titleLarge` | 22sp | App bar titles |
| `titleMedium` | 16sp | Card titles |
| `bodyLarge` | 16sp | Primary body |
| `bodyMedium` | 14sp | Secondary body |
| `labelLarge` | 14sp | Button labels |
| `labelSmall` | 11sp | Captions |

### Material 3 Rules

**DO:** Use `MaterialTheme.colorScheme` for every color, `MaterialTheme.typography` for all text, `MaterialTheme.shapes` for shapes, dynamic color on Android 12+, `enableEdgeToEdge()` in every Activity.

**DON'T:** Never import `androidx.compose.material` (only `material3`), never hardcode `Color(0xFFABCDEF)` in Composables, never mix M2 and M3, never hardcode font sizes or corner radii.

---

## 1.9 Advanced Patterns

### UseCase Pattern (Domain Layer)

```kotlin
class GetUserFeedUseCase @Inject constructor(
    private val postRepository: PostRepository,
    private val userRepository: UserRepository
) {
    operator fun invoke(userId: String): Flow<List<FeedItem>> {
        return postRepository.observeUserPosts(userId)
            .map { posts -> posts.map { it.toFeedItem() } }
    }
}

// Used in ViewModel
@HiltViewModel
class FeedViewModel @Inject constructor(
    private val getUserFeed: GetUserFeedUseCase
) : ViewModel() {
    fun loadFeed(userId: String) {
        viewModelScope.launch {
            getUserFeed(userId).collect { items ->
                _uiState.value = FeedUiState.Success(items)
            }
        }
    }
}
```

### Shared ViewModel (Activity-Scoped)

```kotlin
@Composable
fun ProfileScreen(
    sessionViewModel: SessionViewModel = hiltViewModel(
        viewModelStoreOwner = LocalContext.current as ComponentActivity
    ),
    featureViewModel: ProfileViewModel = hiltViewModel()
) {
    val user by sessionViewModel.currentUser.collectAsStateWithLifecycle()
}
```

### Optimistic UI

```kotlin
fun onToggleLike(post: Post) {
    val previousState = _uiState.value
    // Optimistic update
    _uiState.update { optimisticUpdate(it, post) }
    viewModelScope.launch {
        repository.toggleLike(post.id)
            .onFailure { _uiState.value = previousState } // rollback
    }
}
```

### Offline-First (Room as Single Source of Truth)

```kotlin
// Repository: observe local, sync from remote
override fun observePosts(): Flow<List<Post>> =
    postDao.observeAll().map { entities -> entities.map { it.toDomain() } }

override suspend fun syncPosts(): Result<Unit> = try {
    val remotePosts = apiService.getPosts()
    postDao.insertAll(remotePosts.map { it.toEntity() })
    Result.success(Unit)
} catch (e: Exception) { Result.failure(e) }

// ViewModel: observe Flow, trigger sync
val posts: StateFlow<List<Post>> = repository.observePosts()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

init { sync() }
```

### State Machine Pattern

```kotlin
sealed interface AuthState {
    data object LoggedOut : AuthState
    data object SigningIn : AuthState
    data class SignedIn(val user: User) : AuthState
    data class Error(val message: String) : AuthState

    val isLoading: Boolean get() = this is SigningIn
    val user: User? get() = (this as? SignedIn)?.user
}
```

---

# Part 2: Code Review

## 2.1 MVVM Pattern Validation

**Trigger:** After writing new Android features, before PR review.

### Validation Checklist

**ViewModel:**

| Check | Required |
|-------|----------|
| `@HiltViewModel` | Yes |
| `@Inject constructor` | Yes |
| Extends `ViewModel()` | Yes |
| Private `MutableStateFlow` | Yes |
| Public `StateFlow` via `asStateFlow()` | Yes |
| Interface-based repository | Yes |
| `viewModelScope` for coroutines | Yes |
| No Compose imports | Yes |
| Sealed UI state | Yes |

**Repository:**

| Check | Required |
|-------|----------|
| Interface defined | Yes |
| `@Inject constructor` on impl | Yes |
| `@Binds` in Hilt module | Yes |
| Returns `Result<T>` | Yes |
| No UI state stored | Yes |
| No `MutableStateFlow` | Yes |

**Composable:**

| Check | Required |
|-------|----------|
| `hiltViewModel()` for injection | Yes |
| `collectAsStateWithLifecycle()` | Yes |
| No direct repository calls | Yes |
| No `MutableStateFlow` mutation | Yes |
| Actions delegate to ViewModel | Yes |

**Model:**

| Check | Required |
|-------|----------|
| `data class` | Yes |
| All properties `val` | Yes |
| No suspend functions | Yes |
| No `MutableStateFlow`/`LiveData` | Yes |
| `@Immutable` annotation | Recommended |

**Navigation:**

| Check | Required |
|-------|----------|
| `@Serializable` route classes | Yes |
| No string-based routes | Yes |
| `toRoute<T>()` for arguments | Yes |
| Nav callbacks as lambdas | Yes |

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Composable calls Repository, ViewModel has Compose imports, `GlobalScope`, manual ViewModel construction | Block PR |
| Warning | `LiveData` instead of `StateFlow`, `collectAsState` not lifecycle-aware, missing `@Immutable`, string nav routes | Address before shipping |
| Info | Missing region comments, `stateIn` optimization, spacing alignment | Optional improvement |

---

## 2.2 Kotlin Coroutines Audit

**Trigger:** PR review for code with coroutines, Flow, async.

### Key Checks

1. **ViewModelScope**: All coroutines in `viewModelScope`, never `GlobalScope`
2. **Dispatchers**: IO for network/DB, Default for CPU, Main for UI
3. **No `runBlocking`** in production code
4. **Job cancellation**: `isActive`/`ensureActive` checks, `searchJob?.cancel()` before new
5. **`collectAsStateWithLifecycle()`**: Not `collectAsState()` in Compose
6. **StateFlow for state, Channel for events**: Never StateFlow for one-shot events
7. **Thread safety**: Mutex or atomic for shared mutable state in repositories
8. **CancellationException**: Always re-throw, never swallow

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | `GlobalScope`, `runBlocking` in prod, unprotected shared mutable state, swallowed CancellationException | Block PR |
| Warning | `collectAsState()` not lifecycle-aware, missing cancellation checks, StateFlow for events | Address before shipping |
| Info | Dispatcher injection for testability | Optional improvement |

---

## 2.3 Android Accessibility Review

**Trigger:** Before completing any Android feature, PR review for UI code.

### Key Checks

1. **TalkBack**: All interactive elements have `contentDescription`
2. **Touch targets**: All interactive elements >= 48dp (use `minimumInteractiveComponentSize()`)
3. **Color contrast**: WCAG AA (4.5:1 body, 3:1 large text), use `MaterialTheme.colorScheme`
4. **Semantics**: `mergeDescendants` for icon+text rows, `stateDescription` for toggles
5. **Custom actions**: Accessible alternatives for swipe/drag gestures
6. **Live regions**: Dynamic content announces changes via `liveRegion`
7. **Headings**: Section headings marked with `heading()` semantics
8. **RTL**: Use `start`/`end` not `left`/`right`, `Icons.AutoMirrored`
9. **Font scaling**: Use `sp` via `MaterialTheme.typography`, no fixed-height text containers

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing TalkBack labels on buttons, touch targets < 48dp, no accessible gesture alternative | Block PR |
| Warning | Missing `stateDescription` on toggles, missing grouping, hardcoded left/right padding | Address before shipping |
| Info | Heading hierarchy, reduce motion | Optional improvement |

---

## 2.4 Material Design 3 Review

**Trigger:** UI components, Compose code, implementing screens.

### Key Checks

1. **Components**: Use M3 components (`Button`, `Card`, `ListItem`), not custom equivalents
2. **Colors**: `MaterialTheme.colorScheme.*`, never hardcoded `Color(0xFF...)` or `Color.White`
3. **Typography**: `MaterialTheme.typography.*`, never hardcoded `fontSize`
4. **Shapes**: `MaterialTheme.shapes.*`, never hardcoded `RoundedCornerShape`
5. **Dynamic color**: `dynamicColorScheme` with API 31+ check and fallback
6. **Dark mode**: All colors adaptive, preview with both light/dark
7. **Elevation**: Prefer `tonalElevation` over `shadowElevation`
8. **Icons**: Outlined for unselected, Filled for selected nav items

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Hardcoded colors breaking dark mode, custom Box replacing M3 components | Block PR |
| Warning | Hardcoded fontSize/fontWeight, hardcoded shapes, missing dynamic color | Address before shipping |
| Info | Non-4dp spacing, shadow elevation over tonal | Optional improvement |

---

## 2.5 Android API Research

**Trigger:** Implementing new features, checking API availability, exploring Jetpack libraries.

### Deprecated API Watchlist (LLMs often generate these incorrectly)

| Deprecated | Modern Replacement |
|---|---|
| `LiveData` | `StateFlow` / `SharedFlow` |
| `AsyncTask` | Coroutines |
| `SharedPreferences` | `DataStore` |
| `onRequestPermissionsResult` | `ActivityResultContracts` |
| String navigation routes | `@Serializable` data classes |
| `Glide` / `Picasso` | `Coil3` |
| `RxJava` | `Flow` |
| `Gson` | `kotlinx.serialization` |

### Reference App

**Now in Android:** github.com/android/nowinandroid

---

# Part 3: Quality Checks

## 3.1 Android Code Quality Checks

**Trigger:** Before commits or PRs, running `/android-check`.

### Commands

| Check | Command | When |
|-------|---------|------|
| ktlint | `./gradlew ktlintCheck` or `ktlintFormat` | Always |
| Detekt | `./gradlew detekt` | Always |
| Android Lint | `./gradlew lint` | Always |
| Build | `./gradlew assembleDebug` | Always |
| Tests | `./gradlew test` | `--test` or `--coverage` |
| Coverage | `./gradlew jacocoTestReport` | `--coverage` |
| Compose | Compose compiler metrics | `--compose` |

### Quick Commands

```bash
/android-check          # Lint + build
/android-check --test   # Lint + build + tests
/android-check --fix    # Auto-fix ktlint violations
/android-check --coverage  # Tests with JaCoCo coverage
/android-check --compose   # Compose compiler stability metrics
```

### Coverage Thresholds (recommended)

- Overall: 70% minimum
- ViewModel: 85% minimum
- Repository: 80% minimum
- UseCase: 90% minimum

---

# Quick Reference

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

    init { loadData() }

    fun loadData() {
        viewModelScope.launch {
            _uiState.value = FeatureUiState.Loading
            repository.fetchData()
                .onSuccess { _uiState.value = FeatureUiState.Success(it) }
                .onFailure { _uiState.value = FeatureUiState.Error(it.message ?: "Error") }
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
interface FeatureRepository {
    suspend fun fetchData(): Result<FeatureData>
    suspend fun saveData(data: FeatureData): Result<Unit>
}

class FeatureRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : FeatureRepository {
    override suspend fun fetchData(): Result<FeatureData> = try {
        Result.success(apiService.getData().toDomain())
    } catch (e: Exception) {
        Result.failure(e)
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
        Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
            when (val state = uiState) {
                is FeatureUiState.Loading -> CircularProgressIndicator()
                is FeatureUiState.Success -> FeatureContent(data = state.data)
                is FeatureUiState.Error -> {
                    AlertDialog(
                        onDismissRequest = viewModel::clearError,
                        confirmButton = { TextButton(onClick = viewModel::clearError) { Text("OK") } },
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
}
```

---

## Decision Trees

### StateFlow vs SharedFlow vs Channel?

```
Emitting current UI state (screens, forms)?
-> StateFlow (MutableStateFlow with asStateFlow())

One-shot events (navigation, snackbars)?
-> Channel<Event>(Channel.BUFFERED) exposed as receiveAsFlow()

Broadcasting to multiple collectors?
-> SharedFlow with replay = 0

Lifecycle-aware collection in Composable?
-> collectAsStateWithLifecycle() (always)
```

### ViewModel Scope?

```
State for one screen?
-> Default: hiltViewModel() scoped to BackStackEntry

State shared across sibling screens (checkout, onboarding)?
-> hiltViewModel(navBackStackEntry) scoped to nav graph

State for entire session (auth, cart)?
-> hiltViewModel(LocalContext.current as ComponentActivity)
```

### When to Use Domain Layer (UseCase)?

```
Same business logic needed by 2+ ViewModels -> YES
Business rule complex enough for isolation -> YES
Logic needs independent testing -> YES
Simple CRUD with no business logic -> SKIP
Single ViewModel owns the logic -> SKIP
```

---

## Layer Summary

| Layer | Type | Role | Rules |
|-------|------|------|-------|
| **Model** | `data class` | Immutable data + computed properties | No async, no mutable state |
| **Repository** | `interface` + `class` impl | Async data access | Returns `Result<T>`, no UI state |
| **ViewModel** | `@HiltViewModel class` | UI state + coordination | No Compose imports, `viewModelScope` only |
| **Composable** | `@Composable fun` | Render UI, delegate actions | Never call repos, never mutate VM |

---

## Key Principles

1. **Unidirectional data flow**: Composables observe state, never mutate ViewModel properties
2. **Single Source of Truth (SSOT)**: Each piece of data has one authoritative source
3. **Interface-based everything**: All components testable in isolation via Hilt `@Binds`
4. **Structured concurrency**: `viewModelScope`, never `GlobalScope`, lifecycle-aware Flow collection
5. **Clear separation**: Each layer has single responsibility -- no cross-layer violations
6. **Material 3 first**: `MaterialTheme.colorScheme`, `MaterialTheme.typography`, dynamic color

---

## Common Scenarios Quick Lookup

| Scenario | Pattern |
|----------|---------|
| Fetch data on screen open | `init { loadData() }` in ViewModel |
| Navigate on event | `Channel` events, `LaunchedEffect` collector |
| Show loading spinner | `UiState.Loading` -> `CircularProgressIndicator()` |
| Handle API error | `Result.failure` -> `UiState.Error` -> `AlertDialog` |
| Search with debounce | `delay(300)` + `Job.cancel()` in ViewModel |
| Infinite scroll | Load more when last item appears, append to list |
| Pull to refresh | `PullToRefreshBox`, call `refresh()` on ViewModel |
| Form validation | Computed `isFormValid` on UI state data class |
| Offline first | Room as SSOT, `Flow` from DAO, sync in background |
| Share content | `Channel` event -> Intent in Composable |

---

## File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Model | `PascalCase.kt` | `User.kt` |
| Repository interface | `{Name}Repository.kt` | `UserRepository.kt` |
| Repository impl | `{Name}RepositoryImpl.kt` | `UserRepositoryImpl.kt` |
| ViewModel | `{Feature}ViewModel.kt` | `UserViewModel.kt` |
| Composable screen | `{Feature}Screen.kt` | `UserScreen.kt` |
| Composable component | `{Name}.kt` | `UserCard.kt` |
| Hilt module | `{Scope}Module.kt` | `RepositoryModule.kt` |
| Room DAO | `{Entity}Dao.kt` | `UserDao.kt` |
| Room entity | `{Name}Entity.kt` | `UserEntity.kt` |
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
│   └── feed/
└── navigation/
    ├── Routes.kt             # @Serializable route definitions
    └── AppNavHost.kt
```
