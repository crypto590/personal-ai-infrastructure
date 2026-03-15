# Advanced Patterns

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [examples.md](examples.md) - Complete feature examples
- [testing.md](testing.md) - Testing advanced patterns

---

## Overview

Advanced patterns for complex features: ViewModel composition, shared state, domain layer use cases, offline-first architecture, pagination, background work, and multi-module design.

---

## ViewModel Composition

Break large ViewModel classes into focused units when a single ViewModel exceeds ~200 lines or manages multiple independent concerns.

### Pattern

```kotlin
// Focused child ViewModel
@HiltViewModel
class ProfilePostsViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    private val _posts = MutableStateFlow<List<Post>>(emptyList())
    val posts: StateFlow<List<Post>> = _posts.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadPosts(userId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            repository.getUserPosts(userId)
                .onSuccess { _posts.value = it }
            _isLoading.value = false
        }
    }
}

// Parent ViewModel composes children via Hilt-assisted injection
@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val postsViewModelFactory: ProfilePostsViewModel.Factory
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    val postsViewModel: ProfilePostsViewModel = postsViewModelFactory.create()

    fun loadProfile(id: String) {
        viewModelScope.launch {
            userRepository.fetchUser(id)
                .onSuccess {
                    _user.value = it
                    postsViewModel.loadPosts(it.id) // coordinate child
                }
        }
    }
}

// Composable uses composed ViewModels
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val user by viewModel.user.collectAsStateWithLifecycle()
    val posts by viewModel.postsViewModel.posts.collectAsStateWithLifecycle()
    val isLoadingPosts by viewModel.postsViewModel.isLoading.collectAsStateWithLifecycle()

    Column {
        user?.let { UserHeader(user = it) }
        if (isLoadingPosts) {
            CircularProgressIndicator()
        } else {
            PostsList(posts = posts)
        }
    }
}
```

### When to Split

- ViewModel exceeds ~200 lines
- Multiple independent async operations (profile data, posts, followers)
- Sections reused in other screens
- Separate ownership makes testing simpler

---

## Shared ViewModels

For state that spans multiple screens: auth session, user preferences, shopping cart.

### Activity-Scoped Shared ViewModel

```kotlin
// Scoped to the Activity lifecycle — survives navigation between screens
@HiltViewModel
class SessionViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    val isAuthenticated: Boolean get() = _currentUser.value != null

    fun setUser(user: User) { _currentUser.value = user }
    fun clearUser() { _currentUser.value = null }
}

// Access in any Composable from the same Activity
@Composable
fun ProfileScreen(
    sessionViewModel: SessionViewModel = hiltViewModel(
        viewModelStoreOwner = LocalContext.current as ComponentActivity
    ),
    featureViewModel: ProfileViewModel = hiltViewModel()
) {
    val user by sessionViewModel.currentUser.collectAsStateWithLifecycle()
    // ...
}
```

### Navigation Graph-Scoped Shared ViewModel

```kotlin
// Scoped to a nav graph — shared only within a nested nav graph
@Composable
fun CheckoutGraph(navController: NavHostController) {
    val checkoutBackStack = remember(navController) {
        navController.getBackStackEntry("checkout_graph")
    }

    NavHost(navController, startDestination = "cart") {
        navigation(startDestination = "cart", route = "checkout_graph") {
            composable("cart") {
                CartScreen(
                    checkoutViewModel = hiltViewModel(checkoutBackStack)
                )
            }
            composable("address") {
                AddressScreen(
                    checkoutViewModel = hiltViewModel(checkoutBackStack)
                )
            }
            composable("payment") {
                PaymentScreen(
                    checkoutViewModel = hiltViewModel(checkoutBackStack)
                )
            }
        }
    }
}
```

---

## UseCase / Interactor Pattern

Use the domain layer when multiple ViewModels need the same business logic, or when ViewModel coordination logic grows complex enough to test independently.

### When to Use Domain Layer

```
Use domain layer when:
- Same business logic needed by 2+ ViewModels
- Business rule is complex enough to merit isolation
- Logic needs to be independently tested

Skip domain layer when:
- Simple CRUD with no business logic
- Single ViewModel owns the logic
- Adding the layer would be pure boilerplate
```

### UseCase Pattern

```kotlin
// domain/GetUserFeedUseCase.kt
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

    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()

    fun loadFeed(userId: String) {
        viewModelScope.launch {
            getUserFeed(userId)
                .catch { _uiState.value = FeedUiState.Error(it.message ?: "Error") }
                .collect { items ->
                    _uiState.value = FeedUiState.Success(items)
                }
        }
    }
}
```

---

## Event Handling with SharedFlow

Use `SharedFlow` for one-shot events that must not be replayed (navigation, snackbars, dialogs triggered by user action).

```kotlin
@HiltViewModel
class PostDetailViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<PostDetailUiState>(PostDetailUiState.Loading)
    val uiState: StateFlow<PostDetailUiState> = _uiState.asStateFlow()

    // One-shot events using Channel (recommended over SharedFlow for single consumers)
    private val _events = Channel<PostDetailEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun onDeletePost(postId: String) {
        viewModelScope.launch {
            repository.deletePost(postId)
                .onSuccess { _events.send(PostDetailEvent.NavigateBack) }
                .onFailure { _events.send(PostDetailEvent.ShowSnackbar("Failed to delete")) }
        }
    }

    fun onSharePost(post: Post) {
        viewModelScope.launch {
            _events.send(PostDetailEvent.ShareContent(post.title, post.body))
        }
    }
}

sealed interface PostDetailEvent {
    data object NavigateBack : PostDetailEvent
    data class ShowSnackbar(val message: String) : PostDetailEvent
    data class ShareContent(val title: String, val text: String) : PostDetailEvent
}

// Composable handles events
@Composable
fun PostDetailScreen(
    navController: NavController,
    viewModel: PostDetailViewModel = hiltViewModel()
) {
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is PostDetailEvent.NavigateBack -> navController.popBackStack()
                is PostDetailEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
                is PostDetailEvent.ShareContent -> { /* invoke share intent */ }
            }
        }
    }
    // ...
}
```

---

## Offline-First Architecture

Room is the single source of truth. Retrofit fetches and saves to Room. ViewModels observe Room.

```kotlin
// Repository syncs remote → local, exposes local as Flow
class PostRepositoryImpl @Inject constructor(
    private val apiService: ApiService,
    private val postDao: PostDao
) : PostRepository {

    // Observe local database (always current source of truth)
    override fun observePosts(): Flow<List<Post>> {
        return postDao.observeAll().map { entities -> entities.map { it.toDomain() } }
    }

    // Sync from remote and save to local
    override suspend fun syncPosts(): Result<Unit> {
        return try {
            val remotePosts = apiService.getPosts()
            postDao.insertAll(remotePosts.map { it.toEntity() })
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// ViewModel observes Flow, triggers sync on init
@HiltViewModel
class PostListViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    val posts: StateFlow<List<Post>> = repository.observePosts()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init {
        sync()
    }

    fun sync() {
        viewModelScope.launch {
            repository.syncPosts()
        }
    }
}
```

---

## Pagination with Paging 3

Use Paging 3 for large datasets that require efficient pagination with caching and state management.

```kotlin
// PagingSource
class PostPagingSource @Inject constructor(
    private val apiService: ApiService
) : PagingSource<Int, Post>() {

    override fun getRefreshKey(state: PagingState<Int, Post>): Int? {
        return state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchor)?.nextKey?.minus(1)
        }
    }

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, Post> {
        return try {
            val page = params.key ?: 1
            val response = apiService.getPosts(page = page, pageSize = params.loadSize)
            LoadResult.Page(
                data = response.items.map { it.toDomain() },
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.items.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }
}

// Repository
class PostRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) : PostRepository {

    override fun getPostsPager(): Flow<PagingData<Post>> {
        return Pager(
            config = PagingConfig(pageSize = 20, prefetchDistance = 5),
            pagingSourceFactory = { PostPagingSource(apiService) }
        ).flow
    }
}

// ViewModel
@HiltViewModel
class PostListViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    val posts: Flow<PagingData<Post>> = repository.getPostsPager()
        .cachedIn(viewModelScope)
}

// Composable
@Composable
fun PostListScreen(viewModel: PostListViewModel = hiltViewModel()) {
    val pagingItems = viewModel.posts.collectAsLazyPagingItems()

    LazyColumn {
        items(
            count = pagingItems.itemCount,
            key = pagingItems.itemKey { it.id }
        ) { index ->
            val post = pagingItems[index]
            if (post != null) {
                PostCard(post = post, onClick = {})
            }
        }

        when (val loadState = pagingItems.loadState.append) {
            is LoadState.Loading -> {
                item { CircularProgressIndicator(modifier = Modifier.padding(16.dp)) }
            }
            is LoadState.Error -> {
                item {
                    TextButton(onClick = { pagingItems.retry() }) {
                        Text("Retry")
                    }
                }
            }
            else -> Unit
        }
    }
}
```

---

## WorkManager for Background Tasks

Use WorkManager for guaranteed background execution (uploads, syncs, cleanup) that must survive process death.

```kotlin
// Define the Worker
class SyncPostsWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    @Inject
    lateinit var repository: PostRepository

    override suspend fun doWork(): Result {
        return try {
            repository.syncPosts()
                .fold(
                    onSuccess = { Result.success() },
                    onFailure = { Result.retry() }
                )
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }

    companion object {
        const val WORK_NAME = "sync_posts"

        fun buildRequest(): PeriodicWorkRequest {
            return PeriodicWorkRequestBuilder<SyncPostsWorker>(15, TimeUnit.MINUTES)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
                .build()
        }
    }
}

// Schedule from ViewModel or Application
class AppViewModel @Inject constructor(
    private val workManager: WorkManager
) : ViewModel() {

    fun scheduleSyncWork() {
        workManager.enqueueUniquePeriodicWork(
            SyncPostsWorker.WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            SyncPostsWorker.buildRequest()
        )
    }

    fun observeSyncStatus(): StateFlow<WorkInfo.State?> {
        return workManager
            .getWorkInfosForUniqueWorkFlow(SyncPostsWorker.WORK_NAME)
            .map { infos -> infos.firstOrNull()?.state }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
    }
}
```

---

## State Machine Pattern

For complex state transitions where invalid states must be prevented by construction.

```kotlin
@HiltViewModel
class AuthViewModel @Inject constructor(
    private val repository: AuthRepository
) : ViewModel() {

    private val _state = MutableStateFlow<AuthState>(AuthState.LoggedOut)
    val state: StateFlow<AuthState> = _state.asStateFlow()

    sealed interface AuthState {
        data object LoggedOut : AuthState
        data object SigningIn : AuthState
        data class SignedIn(val user: User) : AuthState
        data class Error(val message: String) : AuthState

        val isLoading: Boolean get() = this is SigningIn
        val user: User? get() = (this as? SignedIn)?.user
        val errorMessage: String? get() = (this as? Error)?.message
    }

    fun signIn(email: String, password: String) {
        if (_state.value is AuthState.SigningIn) return // guard double-tap
        viewModelScope.launch {
            _state.value = AuthState.SigningIn
            repository.signIn(Credentials(email, password))
                .onSuccess { response ->
                    _state.value = AuthState.SignedIn(response.toUser())
                }
                .onFailure { error ->
                    _state.value = AuthState.Error(error.message ?: "Sign in failed")
                }
        }
    }

    fun signOut() {
        _state.value = AuthState.LoggedOut
    }

    fun clearError() {
        if (_state.value is AuthState.Error) {
            _state.value = AuthState.LoggedOut
        }
    }
}

// View
@Composable
fun AuthScreen(viewModel: AuthViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    when (state) {
        is AuthViewModel.AuthState.LoggedOut -> SignInForm(onSignIn = viewModel::signIn)
        is AuthViewModel.AuthState.SigningIn -> LoadingScreen()
        is AuthViewModel.AuthState.SignedIn -> MainScreen()
        is AuthViewModel.AuthState.Error -> {
            ErrorScreen(
                message = state.errorMessage ?: "",
                onDismiss = viewModel::clearError
            )
        }
    }
}
```

---

## Coordinator / Flow Navigation Pattern

Abstract multi-step navigation flows out of individual screens into a coordinator.

```kotlin
// Onboarding flow coordinator
sealed interface OnboardingStep {
    data object Welcome : OnboardingStep
    data object CreateProfile : OnboardingStep
    data object Permissions : OnboardingStep
    data object Complete : OnboardingStep
}

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _currentStep = MutableStateFlow<OnboardingStep>(OnboardingStep.Welcome)
    val currentStep: StateFlow<OnboardingStep> = _currentStep.asStateFlow()

    fun onNext() {
        _currentStep.value = when (_currentStep.value) {
            is OnboardingStep.Welcome -> OnboardingStep.CreateProfile
            is OnboardingStep.CreateProfile -> OnboardingStep.Permissions
            is OnboardingStep.Permissions -> OnboardingStep.Complete
            is OnboardingStep.Complete -> OnboardingStep.Complete
        }
    }

    fun onBack() {
        _currentStep.value = when (_currentStep.value) {
            is OnboardingStep.Welcome -> OnboardingStep.Welcome
            is OnboardingStep.CreateProfile -> OnboardingStep.Welcome
            is OnboardingStep.Permissions -> OnboardingStep.CreateProfile
            is OnboardingStep.Complete -> OnboardingStep.Permissions
        }
    }
}

@Composable
fun OnboardingFlow(
    onComplete: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val step by viewModel.currentStep.collectAsStateWithLifecycle()

    LaunchedEffect(step) {
        if (step is OnboardingStep.Complete) onComplete()
    }

    AnimatedContent(targetState = step, label = "onboarding_step") { current ->
        when (current) {
            is OnboardingStep.Welcome -> WelcomeStep(onNext = viewModel::onNext)
            is OnboardingStep.CreateProfile -> CreateProfileStep(onNext = viewModel::onNext)
            is OnboardingStep.Permissions -> PermissionsStep(onNext = viewModel::onNext)
            is OnboardingStep.Complete -> Unit
        }
    }
}
```

---

## Multi-Module Architecture

Organize large apps by feature module to reduce build times and enforce boundaries.

```
app/                          # Shell module — Activity, NavHost, DI graph
├── feature-feed/             # Feed feature module
│   ├── api/                  # Public API (interfaces, routes)
│   └── impl/                 # Implementation (hidden from other modules)
├── feature-profile/
├── feature-search/
├── core-ui/                  # Shared Compose components
├── core-data/                # Shared repositories, Room, Retrofit
├── core-domain/              # Optional: shared use cases
└── core-testing/             # Shared fakes and test utilities
```

### Feature Module Pattern

```kotlin
// feature-feed/api/src/.../FeedRoute.kt
@Serializable
data object FeedRoute

// feature-feed/api/src/.../FeedNavigator.kt
interface FeedNavigator {
    fun NavGraphBuilder.feedGraph(navController: NavController)
}

// feature-feed/impl/src/.../FeedNavigatorImpl.kt
class FeedNavigatorImpl @Inject constructor() : FeedNavigator {
    override fun NavGraphBuilder.feedGraph(navController: NavController) {
        composable<FeedRoute> {
            FeedScreen(onNavigateToPost = { id ->
                navController.navigate(PostDetailRoute(id))
            })
        }
    }
}

// app/NavHost.kt — composes feature graphs
@Composable
fun AppNavHost(
    navController: NavHostController,
    feedNavigator: FeedNavigator,
    profileNavigator: ProfileNavigator
) {
    NavHost(navController, startDestination = FeedRoute) {
        with(feedNavigator) { feedGraph(navController) }
        with(profileNavigator) { profileGraph(navController) }
    }
}
```

---

## Hilt Dependency Container Pattern

Provide implementations cleanly across modules.

```kotlin
// core-data module
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

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

// Scoped to ViewModel
@Module
@InstallIn(ViewModelComponent::class)
object ViewModelModule {

    @Provides
    @ViewModelScoped
    fun provideSavedStateHandle(
        savedStateHandle: SavedStateHandle
    ): SavedStateHandle = savedStateHandle
}
```

---

## Optimistic UI Pattern

Update state immediately for perceived performance, roll back on failure.

```kotlin
@HiltViewModel
class PostDetailViewModel @Inject constructor(
    private val repository: PostRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<PostDetailUiState>(PostDetailUiState.Loading)
    val uiState: StateFlow<PostDetailUiState> = _uiState.asStateFlow()

    private val _events = Channel<PostDetailEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun onToggleLike(post: Post) {
        val previousState = _uiState.value

        // Optimistic update
        _uiState.update { state ->
            if (state is PostDetailUiState.Success) {
                state.copy(post = post.copy(
                    isLiked = !post.isLiked,
                    likeCount = if (post.isLiked) post.likeCount - 1 else post.likeCount + 1
                ))
            } else state
        }

        viewModelScope.launch {
            repository.toggleLike(post.id)
                .onFailure {
                    // Roll back on failure
                    _uiState.value = previousState
                    _events.send(PostDetailEvent.ShowSnackbar("Failed to update like"))
                }
        }
    }
}
```

---

## Clean Architecture (When It Makes Sense)

For large apps with complex business rules shared across multiple surfaces (phone, tablet, wear).

```
Presentation    →    Domain    →    Data
(ViewModel)          (UseCases)     (Repositories)
                     (Entities)
```

**Use Clean Architecture when:**
- App is large (50+ features)
- Multiple deployment targets (phone, tablet, Wear OS, TV)
- Complex business logic that belongs in neither ViewModel nor Repository
- Team wants strict architectural boundaries

**Skip it when:**
- Small/medium app (< 20 screens)
- Simple CRUD with no real business logic
- Solo developer or small team where overhead outweighs benefit

---

*Patterns based on Google's Android Architecture recommendations and production Android applications.*
