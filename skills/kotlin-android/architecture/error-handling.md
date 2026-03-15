# Error Handling

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [viewmodels.md](viewmodels.md) - ViewModels handle errors from Repositories
- [repositories.md](repositories.md) - Repositories map exceptions to domain errors

---

## Overview

Repositories map raw exceptions to domain errors. ViewModels catch domain errors and update UI state. Composables display user-friendly error UI.

**Philosophy:**
- Repositories throw (or return `Result.failure`) with domain-level errors
- ViewModels catch and translate errors to UI state (string messages for simple cases)
- Composables display error state — never error logic
- Keep it simple unless complexity is genuinely needed

---

## Basic Pattern

```kotlin
// Repository returns Result<T>
class UserRepositoryImpl @Inject constructor(
    private val api: UserApi
) : UserRepository {
    override suspend fun fetchUser(id: String): Result<User> = try {
        Result.success(api.getUser(id).toDomain())
    } catch (e: Exception) {
        Result.failure(e)
    }
}

// ViewModel handles Result
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
                        message = error.message ?: "Unknown error occurred"
                    )
                }
        }
    }

    fun clearError() {
        if (_uiState.value is UserUiState.Error) {
            _uiState.value = UserUiState.Loading
        }
    }
}

// Composable displays error state
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> CircularProgressIndicator()
        is UserUiState.Success -> UserContent(state.user)
        is UserUiState.Error -> ErrorMessage(
            message = state.message,
            onDismiss = viewModel::clearError,
            onRetry = viewModel::retry
        )
    }
}
```

---

## Sealed Class Error Pattern (AppError)

For better control over user-facing messages, define domain-level errors:

```kotlin
sealed class AppError : Exception() {

    // Network errors
    data object NetworkUnavailable : AppError() {
        override val message = "No internet connection. Please check your network and try again."
    }

    data object RequestTimeout : AppError() {
        override val message = "Request timed out. Please try again."
    }

    // Auth errors
    data object Unauthorized : AppError() {
        override val message = "Your session has expired. Please sign in again."
    }

    data object Forbidden : AppError() {
        override val message = "You don't have permission to do this."
    }

    // Data errors
    data class NotFound(val resource: String) : AppError() {
        override val message = "$resource could not be found."
    }

    data class ServerError(val code: Int) : AppError() {
        override val message = "Server error ($code). Please try again later."
    }

    // Validation errors
    data class ValidationFailed(val field: String, val reason: String) : AppError() {
        override val message = "$field: $reason"
    }

    // Generic fallback
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

---

## Result Wrapper: kotlin.Result vs Custom

### kotlin.Result (preferred for simple cases)

```kotlin
// Repository
override suspend fun fetchProduct(id: String): Result<Product> = runCatching {
    api.getProduct(id).toDomain()
}

// ViewModel
repository.fetchProduct(id)
    .onSuccess { product -> _uiState.value = UiState.Success(product) }
    .onFailure { error -> _uiState.value = UiState.Error(error.toUserMessage()) }

// Extension for user-friendly messages
fun Throwable.toUserMessage(): String = when (this) {
    is AppError -> message ?: "Error"
    is IOException -> "No internet connection"
    is HttpException -> AppError.from(this).message ?: "Server error"
    else -> "An unexpected error occurred"
}
```

### Custom Result for richer error types (when needed)

```kotlin
sealed interface DataResult<out T> {
    data class Success<T>(val data: T) : DataResult<T>
    data class Error(val error: AppError) : DataResult<Nothing>
    data object Loading : DataResult<Nothing>
}

// Usage
when (val result = repository.fetchArticles()) {
    is DataResult.Success -> _uiState.value = UiState.Success(result.data)
    is DataResult.Error -> _uiState.value = UiState.Error(result.error.message ?: "Error")
    DataResult.Loading -> _uiState.value = UiState.Loading
}
```

---

## Repository Error Handling

### Map HTTP and IO Exceptions at the Repository Boundary

```kotlin
class ArticleRepositoryImpl @Inject constructor(
    private val api: ArticleApi,
    private val dao: ArticleDao
) : ArticleRepository {

    override suspend fun fetchArticle(id: String): Result<Article> {
        return try {
            val dto = api.getArticle(id)
            val article = dto.toDomain()
            dao.insertArticle(article.toEntity())
            Result.success(article)
        } catch (e: HttpException) {
            Result.failure(AppError.from(e))
        } catch (e: IOException) {
            // Network unavailable — try cache
            val cached = dao.getArticle(id)
            if (cached != null) {
                Result.success(cached.toDomain())
            } else {
                Result.failure(AppError.NetworkUnavailable)
            }
        } catch (e: Exception) {
            Result.failure(AppError.Unknown(e.message ?: "Unexpected error"))
        }
    }
}
```

---

## ViewModel Error State Management

### Single Error Message

```kotlin
sealed interface ProductUiState {
    data object Loading : ProductUiState
    data class Success(val product: Product) : ProductUiState
    data class Error(val message: String, val canRetry: Boolean = true) : ProductUiState
}

@HiltViewModel
class ProductViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<ProductUiState>(ProductUiState.Loading)
    val uiState: StateFlow<ProductUiState> = _uiState.asStateFlow()

    fun load(id: String) {
        viewModelScope.launch {
            _uiState.value = ProductUiState.Loading

            repository.fetchProduct(id)
                .onSuccess { _uiState.value = ProductUiState.Success(it) }
                .onFailure { error ->
                    _uiState.value = ProductUiState.Error(
                        message = error.toUserMessage(),
                        canRetry = error is AppError.NetworkUnavailable
                                || error is AppError.RequestTimeout
                    )
                }
        }
    }

    fun retry(id: String) = load(id)
}
```

### Snackbar / One-Time Events for Non-Fatal Errors

```kotlin
sealed interface ProductEvent {
    data class ShowSnackbar(val message: String) : ProductEvent
}

@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val repository: ProductRepository
) : ViewModel() {

    private val _events = Channel<ProductEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun toggleFavorite(product: Product) {
        val previousState = _uiState.value
        // Optimistic update...

        viewModelScope.launch {
            repository.toggleFavorite(product.id)
                .onFailure {
                    _uiState.value = previousState  // Rollback
                    _events.send(ProductEvent.ShowSnackbar("Failed to update favorite"))
                }
        }
    }
}

// Composable
val snackbarHostState = remember { SnackbarHostState() }

LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is ProductEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
        }
    }
}

Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { /* content */ }
```

---

## UI Error Display Patterns

### Full-Screen Error (blocking errors)

```kotlin
@Composable
fun FullScreenError(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Warning,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.error,
            modifier = Modifier.size(64.dp)
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurface
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = onRetry) {
            Text("Try Again")
        }
    }
}
```

### Inline Error (field-level)

```kotlin
@Composable
fun InlineError(message: String, modifier: Modifier = Modifier) {
    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        Icon(
            imageVector = Icons.Default.Error,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.error,
            modifier = Modifier.size(16.dp)
        )
        Text(
            text = message,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.error
        )
    }
}
```

### Alert Dialog Error

```kotlin
@Composable
fun ErrorDialog(
    message: String,
    onDismiss: () -> Unit,
    onRetry: (() -> Unit)? = null
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = { Icon(Icons.Default.ErrorOutline, contentDescription = null) },
        title = { Text("Something went wrong") },
        text = { Text(message) },
        confirmButton = {
            if (onRetry != null) {
                Button(onClick = onRetry) { Text("Retry") }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Dismiss") }
        }
    )
}
```

---

## Retry Pattern

```kotlin
@HiltViewModel
class FeedViewModel @Inject constructor(
    private val repository: FeedRepository
) : ViewModel() {

    private var lastLoadId: String? = null

    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()

    fun load(userId: String) {
        lastLoadId = userId
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading

            repository.getFeed(userId)
                .onSuccess { _uiState.value = FeedUiState.Success(it) }
                .onFailure { _uiState.value = FeedUiState.Error(it.toUserMessage()) }
        }
    }

    fun retry() {
        lastLoadId?.let { load(it) }
    }
}
```

---

## Form Validation Errors

```kotlin
data class SignUpFormState(
    val email: String = "",
    val password: String = "",
    val confirmPassword: String = "",
    val emailError: String? = null,
    val passwordError: String? = null,
    val confirmPasswordError: String? = null,
    val isSubmitting: Boolean = false
) {
    val isValid: Boolean
        get() = emailError == null && passwordError == null && confirmPasswordError == null
                && email.isNotBlank() && password.isNotBlank() && confirmPassword.isNotBlank()
}

@HiltViewModel
class SignUpViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _formState = MutableStateFlow(SignUpFormState())
    val formState: StateFlow<SignUpFormState> = _formState.asStateFlow()

    fun onEmailChanged(email: String) {
        _formState.update { state ->
            state.copy(
                email = email,
                emailError = validateEmail(email)
            )
        }
    }

    fun onPasswordChanged(password: String) {
        _formState.update { state ->
            state.copy(
                password = password,
                passwordError = validatePassword(password),
                confirmPasswordError = validateConfirmPassword(password, state.confirmPassword)
            )
        }
    }

    fun onConfirmPasswordChanged(confirm: String) {
        _formState.update { state ->
            state.copy(
                confirmPassword = confirm,
                confirmPasswordError = validateConfirmPassword(state.password, confirm)
            )
        }
    }

    private fun validateEmail(email: String): String? {
        if (email.isBlank()) return null  // Don't show error until user types
        return if (!Patterns.EMAIL_ADDRESS.matcher(email).matches()) "Invalid email address" else null
    }

    private fun validatePassword(password: String): String? {
        if (password.isBlank()) return null
        return if (password.length < 8) "Password must be at least 8 characters" else null
    }

    private fun validateConfirmPassword(password: String, confirm: String): String? {
        if (confirm.isBlank()) return null
        return if (password != confirm) "Passwords don't match" else null
    }

    fun onSubmit() {
        val state = _formState.value
        if (!state.isValid) return

        viewModelScope.launch {
            _formState.update { it.copy(isSubmitting = true) }

            authRepository.signUp(state.email, state.password)
                .onSuccess { /* navigate to home */ }
                .onFailure { error ->
                    _formState.update {
                        it.copy(
                            isSubmitting = false,
                            emailError = if (error is AppError.ValidationFailed) error.message else null
                        )
                    }
                }
        }
    }
}
```

---

## Global Error Handler

### Coroutine Exception Handler

```kotlin
// App-level exception handler for uncaught coroutine exceptions
@Singleton
class AppCoroutineExceptionHandler @Inject constructor(
    private val analytics: Analytics
) : CoroutineExceptionHandler {

    override val key = CoroutineExceptionHandler

    override fun handleException(context: CoroutineContext, exception: Throwable) {
        Timber.e(exception, "Unhandled coroutine exception")
        analytics.logError(exception)
    }
}

// Inject into ViewModels that need global handler
@HiltViewModel
class CriticalViewModel @Inject constructor(
    private val handler: AppCoroutineExceptionHandler,
    private val repository: CriticalRepository
) : ViewModel() {

    fun performCriticalWork() {
        viewModelScope.launch(handler) {
            repository.doWork()
        }
    }
}
```

### supervisorScope for Independent Child Coroutines

```kotlin
fun loadDashboard() {
    viewModelScope.launch {
        _uiState.value = DashboardUiState.Loading

        // supervisorScope: failure of one child doesn't cancel others
        supervisorScope {
            val profileJob = launch {
                userRepository.fetchProfile()
                    .onSuccess { _profile.value = it }
                    .onFailure { Timber.w(it, "Profile load failed") }
            }

            val statsJob = launch {
                statsRepository.fetchStats()
                    .onSuccess { _stats.value = it }
                    .onFailure { Timber.w(it, "Stats load failed") }
            }

            profileJob.join()
            statsJob.join()
        }

        _uiState.value = DashboardUiState.Success
    }
}
```

### Timber Logging Setup

```kotlin
// In Application class
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        } else {
            Timber.plant(CrashReportingTree())
        }
    }
}

class CrashReportingTree : Timber.Tree() {
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        if (priority >= Log.WARN) {
            FirebaseCrashlytics.getInstance().apply {
                tag?.let { setCustomKey("tag", it) }
                t?.let { recordException(it) } ?: run { log(message) }
            }
        }
    }
}
```

---

## Best Practices

### DO

**1. Wrap all repository calls with try-catch**
```kotlin
override suspend fun fetchData(): Result<Data> = try {
    Result.success(api.getData().toDomain())
} catch (e: Exception) {
    Result.failure(e)
}
```

**2. Map technical exceptions to user-friendly messages**
```kotlin
fun Throwable.toUserMessage(): String = when (this) {
    is AppError -> message ?: "Error"
    is IOException -> "No internet connection"
    is HttpException -> "Server error. Please try again."
    else -> "An unexpected error occurred"
}
```

**3. Clear errors before retrying**
```kotlin
fun retry() {
    // Loading state replaces Error state
    _uiState.value = FeatureUiState.Loading
    viewModelScope.launch { /* re-fetch */ }
}
```

**4. Use sealed UI state for exhaustive handling**
```kotlin
// Compose compiler enforces exhaustive when
when (val state = uiState) {
    is UiState.Loading -> LoadingView()
    is UiState.Success -> ContentView(state.data)
    is UiState.Error -> ErrorView(state.message)
}
```

**5. Log errors with Timber before hiding from user**
```kotlin
.onFailure { error ->
    Timber.e(error, "Failed to fetch user")
    _uiState.value = UiState.Error(error.toUserMessage())
}
```

### DON'T

**1. Don't show raw technical errors to users**
```kotlin
// BAD
_uiState.value = UiState.Error(e.toString())  // "IOException: Failed to connect to..."

// GOOD
_uiState.value = UiState.Error("No internet connection. Please try again.")
```

**2. Don't swallow exceptions silently**
```kotlin
// BAD
try {
    api.deleteUser(id)
} catch (e: Exception) {
    // silently ignored!
}

// GOOD
try {
    api.deleteUser(id)
} catch (e: Exception) {
    Timber.e(e, "Delete user failed")
    return Result.failure(e)
}
```

**3. Don't over-engineer error types early**
```kotlin
// Fine for simple features
data class Error(val message: String) : FeatureUiState

// Only add complexity when needed (retryable, error codes, multi-field validation)
data class Error(
    val message: String,
    val canRetry: Boolean,
    val errorCode: String?
) : FeatureUiState
```

**4. Don't use try-catch to control normal flow**
```kotlin
// BAD — exception for non-exceptional case
try {
    val user = userMap[id] ?: throw NoSuchElementException()
    processUser(user)
} catch (e: NoSuchElementException) {
    showEmptyState()
}

// GOOD
val user = userMap[id]
if (user == null) {
    showEmptyState()
} else {
    processUser(user)
}
```

**5. Don't launch coroutines outside viewModelScope for error-safe work**
```kotlin
// BAD — no lifecycle awareness, exception crashes app
GlobalScope.launch {
    repository.fetchData()
}

// GOOD — auto-cancelled, scoped to ViewModel
viewModelScope.launch {
    repository.fetchData()
}
```
