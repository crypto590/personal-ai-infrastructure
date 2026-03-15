# Kotlin Coroutines & Concurrency Audit

**Part of:** [kotlin-android](../SKILL.md) > Review

**Trigger:** Before PR review for Kotlin code with coroutines, after implementing repositories with suspend functions, mentions of coroutines/Flow/async/concurrency, reviewing background processing code, checking for potential race conditions, implementing Flow collection in Compose, reviewing ViewModel scope usage.

---

## Audit Checklist

### 1. ViewModelScope Usage

**Check:** Coroutines launched in `viewModelScope`, never `GlobalScope`.

```kotlin
// GOOD - Auto-cancelled when ViewModel cleared
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getUser(id)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message) }
        }
    }
}

// VIOLATION - GlobalScope leaks beyond ViewModel lifecycle
class UserViewModel : ViewModel() {
    fun loadUser(id: String) {
        GlobalScope.launch {  // VIOLATION: not cancelled on ViewModel clear
            // ...
        }
    }
}

// VIOLATION - CoroutineScope not tied to lifecycle
class UserViewModel : ViewModel() {
    private val scope = CoroutineScope(Dispatchers.Main)  // VIOLATION: manual scope

    fun loadUser(id: String) {
        scope.launch { /* ... */ }
    }
    // scope never cancelled
}
```

**Report format:**
```
VIEWMODEL SCOPE: [PASS/FAIL]
- ViewModels using viewModelScope: [count]
- GlobalScope usage: [list files:lines - critical violations]
- Manual CoroutineScope without lifecycle: [list files:lines]
```

### 2. Dispatcher Selection

**Check:** Correct dispatcher for each operation type.

```kotlin
// GOOD - CPU-intensive work on Default
viewModelScope.launch(Dispatchers.Default) {
    val result = processLargeDataset(items)
    withContext(Dispatchers.Main) {
        _uiState.value = UiState.Success(result)
    }
}

// GOOD - IO operations on IO dispatcher
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi,
    private val db: UserDao
) : UserRepository {
    override suspend fun getUser(id: String): Result<User> =
        withContext(Dispatchers.IO) {
            runCatching { api.getUser(id).toDomain() }
        }
}

// BAD - IO on Main blocks UI thread
viewModelScope.launch(Dispatchers.Main) {
    val user = api.getUser(id)  // VIOLATION: network call on Main thread
    _uiState.value = UiState.Success(user)
}

// BAD - CPU work on IO (wasteful, IO has many threads)
withContext(Dispatchers.IO) {
    val sorted = items.sortedBy { it.name }  // Should be Default
}
```

**Dispatcher Guide:**
| Operation | Dispatcher |
|---|---|
| UI updates | `Dispatchers.Main` |
| Network calls, file I/O, DB | `Dispatchers.IO` |
| CPU-intensive computation | `Dispatchers.Default` |
| Unit testing (inject) | `TestCoroutineDispatcher` |

**Report format:**
```
DISPATCHER SELECTION: [PASS/WARN]
- IO operations on IO dispatcher: [count/total]
- CPU operations on Default dispatcher: [count/total]
- Potential Main-thread blocking calls: [list]
- Dispatcher injection for testability: [present/missing]
```

### 3. Structured Concurrency (No runBlocking in Production)

**Check:** No `runBlocking` in production code paths.

```kotlin
// VIOLATION - Blocks thread in production
fun getUserName(id: String): String {
    return runBlocking {  // VIOLATION: blocks calling thread
        repository.getUser(id).getOrNull()?.name ?: ""
    }
}

// GOOD - Suspend function with proper propagation
suspend fun getUserName(id: String): String {
    return repository.getUser(id).getOrNull()?.name ?: ""
}

// ACCEPTABLE - runBlocking only in tests
@Test
fun `test user loading`() = runBlocking {
    // OK in tests
}

// GOOD - runTest for coroutine tests (preferred over runBlocking)
@Test
fun `test user loading`() = runTest {
    advanceUntilIdle()
    // ...
}
```

**Report format:**
```
STRUCTURED CONCURRENCY: [PASS/FAIL]
- runBlocking in production code: [list files:lines - violations]
- runBlocking in tests (acceptable): [count]
- Properly propagated suspend functions: [count]
```

### 4. Job Cancellation (isActive / ensureActive)

**Check:** Long-running operations check cancellation state.

```kotlin
// GOOD - Check cancellation before updating state
viewModelScope.launch {
    val result = repository.getItems()
    if (isActive) {  // Guard against cancelled coroutine
        _uiState.value = UiState.Success(result.getOrThrow())
    }
}

// GOOD - ensureActive throws CancellationException
viewModelScope.launch {
    for (item in items) {
        ensureActive()  // Throws if cancelled, propagates correctly
        processItem(item)
    }
}

// BAD - Updates state even after cancellation
viewModelScope.launch {
    val result = repository.getItems()
    // No cancellation check - may update state after ViewModel is gone
    _uiState.value = UiState.Success(result.getOrThrow())
}

// GOOD - Debounced search with Job cancellation
private var searchJob: Job? = null

fun onSearchQueryChanged(query: String) {
    searchJob?.cancel()
    searchJob = viewModelScope.launch {
        delay(300)
        ensureActive()
        repository.search(query)
            .onSuccess { _uiState.value = UiState.Success(it) }
    }
}
```

**Report format:**
```
JOB CANCELLATION: [PASS/WARN]
- Long-running operations with cancellation checks: [count]
- Missing isActive/ensureActive before state updates: [list]
- Debounced operations using Job.cancel(): [count]
- Potential stale state updates: [list]
```

### 5. Flow Collection Lifecycle (collectAsStateWithLifecycle)

**Check:** Flows collected with lifecycle awareness in Compose.

```kotlin
// GOOD - Stops collection when screen is in background
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // ...
}

// BAD - Collects even when screen is backgrounded (battery drain)
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()  // WARNING: not lifecycle-aware
    // ...
}

// GOOD - Flow with lifecycle in non-Compose context
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Only active when at least STARTED
                }
            }
        }
    }
}
```

**Report format:**
```
FLOW COLLECTION: [PASS/WARN]
- Flows collected with collectAsStateWithLifecycle: [count]
- Flows collected with collectAsState (not lifecycle-aware): [list - warnings]
- Flows in Fragments/Activities using repeatOnLifecycle: [count]
- Flows collected without lifecycle awareness: [list]
```

### 6. SharedFlow vs StateFlow

**Check:** Correct Flow type for the use case.

```kotlin
// GOOD - StateFlow for UI state (has initial value, replays last)
private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
val uiState: StateFlow<UiState> = _uiState.asStateFlow()

// GOOD - SharedFlow for one-time events (no replay, multiple collectors)
private val _events = MutableSharedFlow<UiEvent>()
val events: SharedFlow<UiEvent> = _events.asSharedFlow()

fun onButtonClick() {
    viewModelScope.launch {
        _events.emit(UiEvent.ShowSnackbar("Saved successfully"))
    }
}

// GOOD - Channel for one-time UI events (alternative to SharedFlow)
private val _events = Channel<UiEvent>(Channel.BUFFERED)
val events = _events.receiveAsFlow()

// BAD - Using StateFlow for one-time events (collector sees stale event on recomposition)
private val _snackbarMessage = MutableStateFlow<String?>(null)
// This fires again on config change!

// BAD - Using SharedFlow when StateFlow is needed (no initial value, collectors miss initial state)
private val _uiState = MutableSharedFlow<UiState>()  // New collector misses current state!
```

**Report format:**
```
FLOW TYPE: [PASS/WARN]
- StateFlow for UI state: [count]
- SharedFlow for one-time events: [count]
- StateFlow used for events (stale emission risk): [list]
- SharedFlow used for state (missing initial value): [list]
```

### 7. Thread Safety in Repositories

**Check:** Shared mutable state protected with Mutex or atomic operations.

```kotlin
// GOOD - Mutex for shared mutable state
class TokenRepositoryImpl @Inject constructor() : TokenRepository {
    private val mutex = Mutex()
    private var cachedToken: String? = null

    override suspend fun getToken(): String? = mutex.withLock {
        cachedToken
    }

    override suspend fun setToken(token: String) = mutex.withLock {
        cachedToken = token
    }
}

// GOOD - AtomicBoolean for simple flag
class SyncRepositoryImpl @Inject constructor() : SyncRepository {
    private val isSyncing = AtomicBoolean(false)

    override suspend fun sync(): Result<Unit> {
        if (!isSyncing.compareAndSet(false, true)) {
            return Result.failure(IllegalStateException("Sync already in progress"))
        }
        return try {
            performSync()
        } finally {
            isSyncing.set(false)
        }
    }
}

// BAD - Shared mutable state with no synchronization
class CacheRepositoryImpl : CacheRepository {
    private var cache: Map<String, Any> = emptyMap()  // VIOLATION: not thread-safe

    override suspend fun put(key: String, value: Any) {
        cache = cache + (key to value)  // Race condition
    }
}
```

**Report format:**
```
THREAD SAFETY: [PASS/WARN/FAIL]
- Shared mutable state found: [count]
- Protected with Mutex: [count]
- Using atomic operations: [count]
- Unprotected shared mutable state: [list - violations]
```

### 8. Exception Handling

**Check:** Coroutine exceptions handled with SupervisorJob or CoroutineExceptionHandler.

```kotlin
// GOOD - SupervisorJob in custom scope (child failures don't cancel siblings)
class AppSyncManager @Inject constructor() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun startBackgroundSync() {
        scope.launch { syncUsers() }   // Failure here...
        scope.launch { syncPosts() }   // ...does not cancel this
    }
}

// GOOD - CoroutineExceptionHandler for unhandled exceptions
private val exceptionHandler = CoroutineExceptionHandler { _, throwable ->
    _uiState.value = UiState.Error(throwable.message ?: "Unknown error")
    Timber.e(throwable, "Unhandled coroutine exception")
}

viewModelScope.launch(exceptionHandler) {
    repository.doWork()
}

// BAD - Exception in child cancels entire parent scope (not SupervisorJob)
class BadManager {
    private val scope = CoroutineScope(Job() + Dispatchers.IO)  // Regular Job

    fun start() {
        scope.launch { task1() }  // If this throws...
        scope.launch { task2() }  // ...this is also cancelled
    }
}

// GOOD - try/catch for expected failures
viewModelScope.launch {
    try {
        val result = repository.getUser(id)
        _uiState.value = UiState.Success(result)
    } catch (e: NetworkException) {
        _uiState.value = UiState.Error("Network unavailable")
    } catch (e: CancellationException) {
        throw e  // Always re-throw CancellationException
    }
}
```

**Report format:**
```
EXCEPTION HANDLING: [PASS/WARN]
- Custom scopes with SupervisorJob: [count]
- CoroutineExceptionHandler usage: [count]
- CancellationException re-thrown: [count/total]
- Swallowed CancellationExceptions: [list - violations]
- Unhandled exception paths: [list]
```

### 9. Testing Coroutines

**Check:** Tests use `TestDispatcher` and `advanceUntilIdle` for deterministic coroutine testing.

```kotlin
// GOOD - Inject dispatcher for testability
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher
) : ViewModel()

// GOOD - Test with TestDispatcher
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val testDispatcher = StandardTestDispatcher()

    @Test
    fun `loadUser emits success state`() = runTest {
        val viewModel = UserViewModel(fakeRepository, testDispatcher)
        viewModel.loadUser("user-1")
        advanceUntilIdle()
        assertEquals(UiState.Success(testUser), viewModel.uiState.value)
    }
}

// GOOD - MainDispatcherRule for Compose ViewModels
class MainDispatcherRule(
    val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

**Report format:**
```
COROUTINE TESTING: [PASS/WARN]
- ViewModels with injected dispatchers: [count]
- Tests using TestDispatcher: [count]
- Tests using runTest (not runBlocking): [count]
- Tests using runBlocking for coroutines: [list - warnings]
- Missing MainDispatcherRule: [list]
```

### 10. Common Bugs

**Check:** Detect known coroutine pitfalls.

```kotlin
// BUG: Flow not collected lifecycle-aware
// See check #5 above - collectAsState() without lifecycle

// BUG: Leaked coroutine scope
class MyActivity : AppCompatActivity() {
    private val scope = CoroutineScope(Dispatchers.Main)  // LEAK: never cancelled
    // Fix: Use lifecycleScope or cancel in onDestroy
}

// BUG: Race condition on shared mutable list
class FeedViewModel : ViewModel() {
    private val items = mutableListOf<Item>()  // VIOLATION: not thread-safe

    fun addItem(item: Item) {
        viewModelScope.launch {
            items.add(item)  // Race condition if called concurrently
        }
    }
    // Fix: Use StateFlow<List<Item>> with value reassignment
}

// BUG: async/await without proper error handling
viewModelScope.launch {
    val deferred = async { repository.getUser(id) }
    // If getUser() throws, exception propagates to launch, not caught here
    val user = deferred.await()
}

// FIX: Wrap async in runCatching or try/catch
viewModelScope.launch {
    val result = runCatching { repository.getUser(id) }
    result.onSuccess { _uiState.value = UiState.Success(it) }
    result.onFailure { _uiState.value = UiState.Error(it.message) }
}

// BUG: suspend function on wrong dispatcher
class UserRepositoryImpl : UserRepository {
    // Room DAOs are already on IO — additional withContext is redundant but harmless
    // Retrofit suspends are NOT automatically IO — withContext(Dispatchers.IO) required
    override suspend fun getRemoteUser(id: String): User {
        return api.getUser(id)  // WARNING: should be in withContext(Dispatchers.IO)
    }
}
```

**Report format:**
```
COMMON BUGS: [PASS/WARN/FAIL]
- Leaked coroutine scopes: [list - violations]
- Mutable shared state without synchronization: [list - violations]
- async/await without error handling: [list - warnings]
- Missing withContext(Dispatchers.IO) on network calls: [list - warnings]
```

---

## Audit Output Format

```markdown
## Kotlin Coroutines Audit: [Feature/File Name]

### Summary
- Overall: [PASS/NEEDS WORK/FAIL]
- Issues found: [count]
- Critical (race conditions, leaked scopes): [count]

### ViewModelScope Usage
[details]

### Dispatcher Selection
[details]

### Structured Concurrency
[details]

### Job Cancellation
[details]

### Flow Collection Lifecycle
[details]

### Flow Type (SharedFlow vs StateFlow)
[details]

### Thread Safety
[details]

### Exception Handling
[details]

### Coroutine Testing
[details]

### Common Bugs
[details]

### Recommendations
1. [ordered by severity]
2. ...

### Migration Steps (if needed)
[Guidance for fixing violations]
```

---

## Severity Levels

| Level | Criteria | Action |
|---|---|---|
| Critical | GlobalScope usage, runBlocking in production, unprotected shared mutable state, CancellationException swallowed, leaked CoroutineScope | Block PR |
| Warning | collectAsState() not lifecycle-aware, missing isActive/ensureActive checks, StateFlow for one-time events, missing SupervisorJob in custom scopes, network call without Dispatchers.IO | Address before shipping |
| Info | Dispatcher injection for testability, runTest over runBlocking in tests | Optional improvement |

---

## Coroutine Testing Quick Reference

```kotlin
// Standard test setup for ViewModel tests
@OptIn(ExperimentalCoroutinesApi::class)
class ViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `my test`() = runTest {
        // Arrange
        val vm = MyViewModel(fakeRepo)

        // Act
        vm.doSomething()
        advanceUntilIdle()  // Runs all pending coroutines

        // Assert
        assertEquals(expected, vm.uiState.value)
    }
}
```
