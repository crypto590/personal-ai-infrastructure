# ViewModels

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [repositories.md](repositories.md) - Repositories that ViewModels coordinate
- [composables.md](composables.md) - Composables that observe ViewModel state
- [error-handling.md](error-handling.md) - Error handling in ViewModels
- [navigation.md](navigation.md) - Navigation events from ViewModels

---

## Overview

ViewModels manage UI state and coordinate repository calls. They are the bridge between Composables (presentation) and Repositories (data layer).

**Key characteristics:**
- Always `@HiltViewModel` with `@Inject constructor`
- Extends `ViewModel`
- Private `MutableStateFlow`, public `StateFlow` exposure
- Interface-based repository injection for testability
- All coroutines launched in `viewModelScope`
- No Compose-specific imports or dependencies

---

## File Organization

- **One ViewModel per screen, always.** ViewModels are heavy — state management, coroutine lifecycle, cancellation, `onCleared` cleanup. Mixing ViewModels makes files hard to navigate.
- Name the file after the ViewModel: `UserViewModel` → `UserViewModel.kt`
- Place the ViewModel in the same feature folder as its screen, repository, and models (flat, not nested MVC subfolders).
- Sealed UI state classes can live in the same file or a dedicated `UiState.kt` file for the feature.

---

## Basic ViewModel Pattern

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

---

## Production Checklist

Every production ViewModel must have:

### Required Annotations and Class Declaration
- `@HiltViewModel` - Enables Hilt injection into the ViewModel
- `@Inject constructor` - Declares constructor injection
- Extends `ViewModel` - Provides `viewModelScope` and lifecycle awareness

### Required State Patterns
- Private `MutableStateFlow` with public `StateFlow` via `asStateFlow()`
  - Composables can read, but cannot mutate
  - Enforces unidirectional data flow
- Sealed interface or sealed class for UI state
  - Exhaustive `when` in Composables (compile-time safety)
  - Represents every possible screen state

### Required Dependencies
- Interface-based repository injection
  - Never depend on concrete repository implementations
  - Enables unit testing with fake repositories

### Required Coroutine Patterns
- All async work in `viewModelScope.launch { }` or `viewModelScope.async { }`
  - Auto-cancelled when ViewModel is cleared
  - Prevents memory leaks
- Job tracking for cancellable operations (search, filtering)
  - `private var searchJob: Job? = null`
  - Cancel before starting new job

### Required Cleanup
- `onCleared()` for non-coroutine resources (channels, subscriptions)
  - `viewModelScope` coroutines cancel automatically
  - Channels must be closed manually

### Forbidden Patterns
- Never import `androidx.compose.*` in a ViewModel
- Never hold a reference to a `Context` (unless from `SavedStateHandle`)
- Never expose `MutableStateFlow` directly
- Never use `LiveData` in new code
- Never launch coroutines outside `viewModelScope`

---

## State Management

### MutableStateFlow + StateFlow Pattern

```kotlin
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    // Private mutable, public immutable
    private val _uiState = MutableStateFlow<ProductUiState>(ProductUiState.Loading)
    val uiState: StateFlow<ProductUiState> = _uiState.asStateFlow()

    // Additional state streams
    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()
}
```

### Converting Cold Flow to Hot StateFlow with stateIn

Use `stateIn` with `SharingStarted.WhileSubscribed(5_000)` to keep state alive during configuration changes but release after 5 seconds when the UI is gone.

```kotlin
@HiltViewModel
class ArticleViewModel @Inject constructor(
    private val repository: ArticleRepository
) : ViewModel() {

    // Hot StateFlow from a cold repository Flow
    val articles: StateFlow<List<Article>> = repository.getArticles()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = emptyList()
        )

    // Combined state from multiple flows
    val uiState: StateFlow<ArticleUiState> = combine(
        repository.getArticles(),
        repository.getCategories()
    ) { articles, categories ->
        ArticleUiState(articles = articles, categories = categories)
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = ArticleUiState()
    )
}
```

### Computed State with derivedStateOf (in Composable) vs ViewModel

Prefer deriving additional state inside the ViewModel when it requires business logic:

```kotlin
@HiltViewModel
class CartViewModel @Inject constructor(
    private val repository: CartRepository
) : ViewModel() {

    private val _cartItems = MutableStateFlow<List<CartItem>>(emptyList())

    // Derived state exposed as StateFlow
    val cartSummary: StateFlow<CartSummary> = _cartItems
        .map { items ->
            CartSummary(
                itemCount = items.size,
                subtotal = items.sumOf { it.price * it.quantity },
                isEmpty = items.isEmpty()
            )
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), CartSummary())
}
```

---

## Process Death Handling with SavedStateHandle

Use `SavedStateHandle` to preserve critical ViewModel state across process death. Inject it via Hilt automatically.

```kotlin
@HiltViewModel
class DetailViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val repository: DetailRepository
) : ViewModel() {

    // Retrieve navigation argument (type-safe with Navigation 2.8+)
    private val itemId: String = checkNotNull(savedStateHandle["itemId"])

    // Survives process death - use for user-entered form data
    private val searchQuery = savedStateHandle.getStateFlow("searchQuery", "")

    private val _uiState = MutableStateFlow<DetailUiState>(DetailUiState.Loading)
    val uiState: StateFlow<DetailUiState> = _uiState.asStateFlow()

    init {
        loadDetail(itemId)
    }

    fun updateSearchQuery(query: String) {
        savedStateHandle["searchQuery"] = query
    }
}
```

**What to save in SavedStateHandle:**
- Current item ID or selection
- User-entered form data
- Scroll position (if significant)
- Filter/sort preferences

**What NOT to save:**
- Large data sets (use Room)
- Loaded content (re-fetch on restore)
- Binary data

---

## Job and Coroutine Management

### Pattern 1: Cancel and Replace (search, filtering)

```kotlin
private var searchJob: Job? = null

fun onSearchQueryChanged(query: String) {
    searchJob?.cancel()
    searchJob = viewModelScope.launch {
        delay(300) // debounce 300ms
        _uiState.value = UserListUiState.Loading

        repository.searchUsers(query)
            .onSuccess { users ->
                _uiState.value = UserListUiState.Success(users)
            }
            .onFailure { error ->
                _uiState.value = UserListUiState.Error(error.message ?: "Search failed")
            }
    }
}
```

**Why this matters:**
- User types "hello" → cancels searches for "h", "he", "hel", "hell"
- Only searches for "hello" after 300ms debounce
- Prevents race conditions and wasted API calls

### Pattern 2: Multiple Independent Jobs

```kotlin
@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val statsRepository: StatsRepository
) : ViewModel() {

    private var profileJob: Job? = null
    private var refreshJob: Job? = null

    fun loadProfile(id: String) {
        profileJob?.cancel()
        profileJob = viewModelScope.launch {
            // load profile
        }
    }

    fun refresh() {
        refreshJob?.cancel()
        refreshJob = viewModelScope.launch {
            // refresh data
        }
    }

    override fun onCleared() {
        super.onCleared()
        // viewModelScope coroutines cancel automatically
        // but cancel jobs explicitly for clarity
        profileJob?.cancel()
        refreshJob?.cancel()
    }
}
```

### Pattern 3: Parallel Loading with async

```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        _uiState.value = DashboardUiState.Loading

        try {
            // Launch all three in parallel
            val profileDeferred = async { userRepository.getProfile() }
            val statsDeferred = async { statsRepository.getStats() }
            val feedDeferred = async { feedRepository.getFeed() }

            val profile = profileDeferred.await().getOrThrow()
            val stats = statsDeferred.await().getOrThrow()
            val feed = feedDeferred.await().getOrThrow()

            _uiState.value = DashboardUiState.Success(
                profile = profile,
                stats = stats,
                feed = feed
            )
        } catch (e: Exception) {
            _uiState.value = DashboardUiState.Error(e.message ?: "Load failed")
        }
    }
}
```

---

## Repository Coordination

### Single Repository

```kotlin
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            _uiState.value = ProfileUiState.Loading

            userRepository.fetchUser(userId)
                .onSuccess { user ->
                    _uiState.value = ProfileUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = ProfileUiState.Error(
                        error.message ?: "Failed to load profile"
                    )
                }
        }
    }
}
```

### Multiple Repositories

```kotlin
@HiltViewModel
class FeedViewModel @Inject constructor(
    private val postRepository: PostRepository,
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()

    fun load(userId: String) {
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading

            try {
                val userDeferred = async { userRepository.fetchUser(userId).getOrThrow() }
                val postsDeferred = async { postRepository.getFeed(userId).getOrThrow() }

                _uiState.value = FeedUiState.Success(
                    user = userDeferred.await(),
                    posts = postsDeferred.await()
                )
            } catch (e: Exception) {
                _uiState.value = FeedUiState.Error(e.message ?: "Failed to load feed")
            }
        }
    }
}
```

### Sequential Dependencies

```kotlin
fun loadUserAndPosts(userId: String) {
    viewModelScope.launch {
        _uiState.value = ProfilePostsUiState.Loading

        // Load user first
        val userResult = userRepository.fetchUser(userId)
        if (userResult.isFailure) {
            _uiState.value = ProfilePostsUiState.Error("Failed to load user")
            return@launch
        }
        val user = userResult.getOrThrow()

        // Then load posts using user data
        postRepository.getPostsByAuthor(user.id)
            .onSuccess { posts ->
                _uiState.value = ProfilePostsUiState.Success(user, posts)
            }
            .onFailure { error ->
                _uiState.value = ProfilePostsUiState.Error(error.message ?: "Failed to load posts")
            }
    }
}
```

---

## Dependency Injection with Hilt

### Why Interface Injection?

```kotlin
// BAD: Concrete dependency
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepositoryImpl  // Hard to test!
) : ViewModel()

// GOOD: Interface dependency
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository  // Testable with fakes
) : ViewModel()
```

### Hilt Module Binds Interface to Implementation

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository

    @Binds
    @Singleton
    abstract fun bindPostRepository(impl: PostRepositoryImpl): PostRepository
}
```

### Testing with Fake Repositories

```kotlin
// In test source set
class FakeUserRepository : UserRepository {
    var shouldFail = false
    var user = User(id = "1", name = "Test User", email = "test@test.com")

    override suspend fun fetchUser(id: String): Result<User> {
        return if (shouldFail) Result.failure(Exception("Network error"))
        else Result.success(user)
    }
}

// Test
class UserViewModelTest {
    @Test
    fun `loadUser success updates state`() = runTest {
        val fakeRepo = FakeUserRepository()
        val viewModel = UserViewModel(repository = fakeRepo)

        viewModel.loadUser("1")
        advanceUntilIdle()

        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Success)
        assertEquals("Test User", (state as UserUiState.Success).user.name)
    }

    @Test
    fun `loadUser failure shows error state`() = runTest {
        val fakeRepo = FakeUserRepository(shouldFail = true)
        val viewModel = UserViewModel(repository = fakeRepo)

        viewModel.loadUser("1")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UserUiState.Error)
    }
}
```

---

## Common Patterns

### Refresh Pattern

```kotlin
@HiltViewModel
class ItemListViewModel @Inject constructor(
    private val repository: ItemRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ItemListUiState>(ItemListUiState.Loading)
    val uiState: StateFlow<ItemListUiState> = _uiState.asStateFlow()

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    init {
        load()
    }

    fun load() {
        viewModelScope.launch {
            _uiState.value = ItemListUiState.Loading

            repository.getItems()
                .onSuccess { items ->
                    _uiState.value = ItemListUiState.Success(items)
                }
                .onFailure { error ->
                    _uiState.value = ItemListUiState.Error(error.message ?: "Load failed")
                }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _isRefreshing.value = true

            repository.getItems()
                .onSuccess { items ->
                    _uiState.value = ItemListUiState.Success(items)
                }
                .onFailure { /* Keep existing state, show snackbar */ }

            _isRefreshing.value = false
        }
    }
}
```

**Usage in Composable:**
```kotlin
val isRefreshing by viewModel.isRefreshing.collectAsStateWithLifecycle()

PullToRefreshBox(
    isRefreshing = isRefreshing,
    onRefresh = { viewModel.refresh() }
) {
    LazyColumn { /* content */ }
}
```

### Pagination with Paging 3

```kotlin
@HiltViewModel
class NewsViewModel @Inject constructor(
    private val repository: NewsRepository
) : ViewModel() {

    val news: Flow<PagingData<Article>> = repository.getNewsPager()
        .flow
        .cachedIn(viewModelScope)  // Cache in viewModelScope for config changes
}

// Repository
class NewsRepositoryImpl @Inject constructor(
    private val api: NewsApi
) : NewsRepository {

    override fun getNewsPager(): Pager<Int, Article> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5),
        pagingSourceFactory = { NewsPagingSource(api) }
    )
}

// PagingSource
class NewsPagingSource(
    private val api: NewsApi
) : PagingSource<Int, Article>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Article> {
        val page = params.key ?: 1
        return try {
            val response = api.getArticles(page = page, pageSize = params.loadSize)
            LoadResult.Page(
                data = response.articles,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.articles.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, Article>): Int? =
        state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchor)?.nextKey?.minus(1)
        }
}
```

**Usage in Composable:**
```kotlin
val news = viewModel.news.collectAsLazyPagingItems()

LazyColumn {
    items(news.itemCount) { index ->
        news[index]?.let { article -> ArticleCard(article) }
    }
    news.apply {
        when {
            loadState.refresh is LoadState.Loading -> item { LoadingIndicator() }
            loadState.append is LoadState.Loading -> item { LoadingIndicator() }
            loadState.refresh is LoadState.Error -> item { ErrorRetry { retry() } }
        }
    }
}
```

### Search with Debounce

```kotlin
@HiltViewModel
class SearchViewModel @Inject constructor(
    private val repository: SearchRepository
) : ViewModel() {

    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    private val _results = MutableStateFlow<SearchUiState>(SearchUiState.Idle)
    val results: StateFlow<SearchUiState> = _results.asStateFlow()

    init {
        // Collect query changes with debounce
        viewModelScope.launch {
            _query
                .debounce(300)
                .distinctUntilChanged()
                .collect { query ->
                    if (query.isBlank()) {
                        _results.value = SearchUiState.Idle
                    } else {
                        performSearch(query)
                    }
                }
        }
    }

    fun onQueryChanged(query: String) {
        _query.value = query
    }

    private suspend fun performSearch(query: String) {
        _results.value = SearchUiState.Loading

        repository.search(query)
            .onSuccess { results ->
                _results.value = if (results.isEmpty()) {
                    SearchUiState.Empty
                } else {
                    SearchUiState.Results(results)
                }
            }
            .onFailure { error ->
                _results.value = SearchUiState.Error(error.message ?: "Search failed")
            }
    }
}

sealed interface SearchUiState {
    data object Idle : SearchUiState
    data object Loading : SearchUiState
    data object Empty : SearchUiState
    data class Results(val items: List<SearchResult>) : SearchUiState
    data class Error(val message: String) : SearchUiState
}
```

### Optimistic Updates

```kotlin
@HiltViewModel
class PostViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<PostListUiState>(PostListUiState.Loading)
    val uiState: StateFlow<PostListUiState> = _uiState.asStateFlow()

    private val _events = Channel<PostEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun toggleLike(post: Post) {
        val currentState = _uiState.value
        if (currentState !is PostListUiState.Success) return

        // Optimistic update
        val updatedPost = post.copy(
            isLiked = !post.isLiked,
            likeCount = if (post.isLiked) post.likeCount - 1 else post.likeCount + 1
        )
        _uiState.value = currentState.copy(
            posts = currentState.posts.map { if (it.id == post.id) updatedPost else it }
        )

        viewModelScope.launch {
            repository.toggleLike(post.id)
                .onFailure {
                    // Rollback on failure
                    _uiState.value = currentState
                    _events.send(PostEvent.ShowSnackbar("Failed to update like"))
                }
        }
    }
}

sealed interface PostEvent {
    data class ShowSnackbar(val message: String) : PostEvent
    data class NavigateToDetail(val postId: String) : PostEvent
}
```

---

## Anti-Patterns

### Exposing MutableStateFlow

```kotlin
// BAD
class UserViewModel : ViewModel() {
    val uiState = MutableStateFlow<UiState>(UiState.Loading)  // Composable can mutate!
}

// GOOD
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
}
```

### No Job Cancellation

```kotlin
// BAD
fun search(query: String) {
    viewModelScope.launch {
        // Previous search never cancelled!
        val results = repository.search(query)
        _uiState.value = UiState.Success(results)
    }
}

// GOOD
private var searchJob: Job? = null

fun search(query: String) {
    searchJob?.cancel()
    searchJob = viewModelScope.launch {
        val results = repository.search(query)
        _uiState.value = UiState.Success(results)
    }
}
```

### Using LiveData in New Code

```kotlin
// BAD (old pattern, avoid in new code)
class UserViewModel : ViewModel() {
    val user = MutableLiveData<User>()
}

// GOOD (modern pattern)
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()
}
```

### God ViewModel

```kotlin
// BAD: One ViewModel managing too many concerns
class AppViewModel : ViewModel() {
    // User management
    fun loadUser() { }
    fun updateUser() { }

    // Post management
    fun loadPosts() { }
    fun createPost() { }
    fun deletePost() { }

    // Notification management
    fun loadNotifications() { }
    fun markAsRead() { }
}

// GOOD: Split into focused ViewModels
class UserViewModel : ViewModel() { /* user operations */ }
class PostViewModel : ViewModel() { /* post operations */ }
class NotificationViewModel : ViewModel() { /* notification operations */ }
```

### Concrete Repository Dependency

```kotlin
// BAD
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepositoryImpl  // Cannot test!
) : ViewModel()

// GOOD
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository  // Interface - testable
) : ViewModel()
```

### Holding Context Reference

```kotlin
// BAD
@HiltViewModel
class FileViewModel @Inject constructor(
    private val context: Context  // Memory leak!
) : ViewModel()

// GOOD - use @ApplicationContext if Context is truly needed
@HiltViewModel
class FileViewModel @Inject constructor(
    @ApplicationContext private val context: Context
) : ViewModel()
```

---

## When to Split ViewModels

Split a ViewModel when it:
- Exceeds ~200 lines of meaningful logic
- Manages multiple independent concerns
- Has three or more independent async operations
- Contains state that could be independently testable

**Split approach — child ViewModels for focused concerns:**

```kotlin
// Child ViewModel
@HiltViewModel
class ProfileStatsViewModel @Inject constructor(
    private val statsRepository: StatsRepository
) : ViewModel() {

    private val _stats = MutableStateFlow<StatsUiState>(StatsUiState.Loading)
    val stats: StateFlow<StatsUiState> = _stats.asStateFlow()

    fun loadStats(userId: String) {
        viewModelScope.launch {
            statsRepository.getStats(userId)
                .onSuccess { _stats.value = StatsUiState.Success(it) }
                .onFailure { _stats.value = StatsUiState.Error(it.message ?: "Error") }
        }
    }
}

// Parent ViewModel coordinates
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            userRepository.fetchUser(id)
                .onSuccess { _user.value = it }
        }
    }
}
```

**In Composable, obtain both with `hiltViewModel()`:**
```kotlin
@Composable
fun ProfileScreen(
    profileViewModel: ProfileViewModel = hiltViewModel(),
    statsViewModel: ProfileStatsViewModel = hiltViewModel()
) {
    val user by profileViewModel.user.collectAsStateWithLifecycle()
    val stats by statsViewModel.stats.collectAsStateWithLifecycle()
    // ...
}
```
