# Kotlin/Jetpack Compose Conventions

This document defines shared conventions for all Kotlin and Jetpack Compose applications in the Athlead monorepo.

## Architecture Overview

### What This Is

This is **MVVM (Model-View-ViewModel)** adapted for modern Android and Jetpack Compose.

We're using the industry-standard MVVM pattern with strict conventions that prevent common anti-patterns. The explicit Repository layer and Kotlin coroutines/Flow patterns make this architecture powerful, testable, and maintainable.

**What makes this powerful:**
- **Unidirectional data flow**: UI observes state via Flows, never directly mutates
- **Interface-based repositories**: Every component is testable in isolation
- **Structured concurrency**: Memory-safe async operations with proper lifecycle awareness
- **Clear separation**: Data models, UI logic in ViewModels, business logic in Repositories, presentation in Composables

### Unidirectional Flow

```
Composable → ViewModel → Repository → Model
```

- **Composable**: Jetpack Compose UI, renders state, delegates actions to ViewModel
- **ViewModel**: Lifecycle-aware class, manages UI state, coordinates repositories
- **Repository**: Stateless async operations, data access layer
- **Model**: Data class, immutable data structures

---

## MVVM Layer Usage

- **Models/**: Always. Every feature has data structures.
- **Repositories/**: When performing async operations (API calls, database access).
- **ViewModels/**: When managing UI state or coordinating data sources.
- **Composables/**: Always. Every feature has UI.

**Simplest Feature**: Model + Composable only.
**Typical Feature**: Model + Repository + ViewModel + Composable.

---

## Core Layers

### 1. Models (Data Classes)

Immutable data structures with computed properties for business logic.

```kotlin
data class User(
    val id: String,
    val name: String,
    val email: String
) {
    val displayName: String
        get() = name.ifEmpty { email }
}
```

**Rules:**
- Always `data class`, never regular `class`
- Always immutable (`val` properties)
- No suspend functions
- No mutable state or `StateFlow`/`MutableStateFlow`

### 2. Repositories (Interfaces + Implementations)

Stateless async operations behind interfaces.

```kotlin
interface UserRepository {
    suspend fun fetchUser(id: String): Result<User>
}

class UserRepositoryImpl(
    private val apiClient: ApiClient
) : UserRepository {
    override suspend fun fetchUser(id: String): Result<User> {
        return try {
            val user = apiClient.getUser(id)
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Example: Object repository for synchronous utilities
interface ValidationRepository {
    fun isValidEmail(email: String): Boolean
}

object ValidationRepositoryImpl : ValidationRepository {
    override fun isValidEmail(email: String): Boolean {
        return email.contains("@") && email.contains(".")
    }
}
```

**Rules:**
- Use `class` when: Performing async operations, managing dependencies, network/database calls
- Use `object` when: Pure functions, synchronous utilities, simple data transformations
- Always define interface for testing
- No UI or business state (caching via in-memory store is acceptable)
- Return Models, never ViewModels
- Use `Result<T>` for error handling
- ❌ Never use mutable state that ViewModels can directly access

### 3. ViewModels (ViewModel Classes)

Manages UI state and coordinates repository calls.

```kotlin
class UserViewModel(
    private val repository: UserRepository = UserRepositoryImpl(ApiClient())
) : ViewModel() {
    // MARK: - State
    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    // MARK: - Methods
    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading

            repository.fetchUser(id)
                .onSuccess { user ->
                    _uiState.value = UserUiState.Success(user)
                }
                .onFailure { error ->
                    _uiState.value = UserUiState.Error(error.message ?: "Unknown error")
                }
        }
    }
}

// UI State sealed class
sealed interface UserUiState {
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}
```

**Rules:**
- Always extend `ViewModel`
- Always use `StateFlow` for state exposure (use `_mutableState` private + `stateFlow` public)
- Always interface-based repository injection
- Always launch coroutines in `viewModelScope` for automatic cancellation
- Use `sealed interface` for UI state to represent all possible states
- No direct Compose dependencies (no `@Composable` functions)

### 4. Composables (Jetpack Compose)

Renders UI and delegates actions to ViewModel.

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UserUiState.Loading -> {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        is UserUiState.Success -> {
            Text(text = state.user.displayName)
        }
        is UserUiState.Error -> {
            Text(text = "Error: ${state.message}", color = MaterialTheme.colorScheme.error)
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser("123")
    }
}
```

**Rules:**
- Obtain ViewModel using `viewModel()` function
- Collect state using `collectAsStateWithLifecycle()` (requires `lifecycle-runtime-compose`)
- Delegate all actions to ViewModel methods
- Never call Repositories directly
- Never mutate ViewModel state (read-only via `StateFlow`)
- Use `LaunchedEffect` for one-time initialization

---

## Production Requirements

Every production feature must have:

**ViewModel Class:**
- ✅ Extends `ViewModel`
- ✅ Private `MutableStateFlow` with public `StateFlow` exposure
- ✅ Interface-based repository dependency
- ✅ Coroutines launched in `viewModelScope`
- ✅ Sealed UI state classes

**Repository:**
- ✅ `class` for async operations, `object` for pure functions
- ✅ Interface for testing
- ✅ No stored UI/business state
- ✅ Returns `Result<T>` or data classes
- ✅ Proper error handling

**Critical Rules:**
- Models: No async code, no mutable state
- Repositories: No UI state, stateless operations
- ViewModels: No Compose dependencies, lifecycle-aware
- Composables: Delegate to ViewModels, never call Repositories directly

---

## Error Handling

ViewModels handle errors from repositories and present them to users via UI state.

### Basic Pattern

```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}

class FeatureViewModel(
    private val repository: FeatureRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<Data>>(UiState.Loading)
    val uiState: StateFlow<UiState<Data>> = _uiState.asStateFlow()

    fun performAction() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            repository.doSomething()
                .onSuccess { data ->
                    _uiState.value = UiState.Success(data)
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message ?: "Unknown error")
                }
        }
    }

    fun clearError() {
        if (_uiState.value is UiState.Error) {
            _uiState.value = UiState.Loading
        }
    }
}

// Composable displays errors
@Composable
fun FeatureScreen(viewModel: FeatureViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> CircularProgressIndicator()
        is UiState.Success -> Content(data = state.data)
        is UiState.Error -> {
            AlertDialog(
                onDismissRequest = { viewModel.clearError() },
                confirmButton = {
                    TextButton(onClick = { viewModel.clearError() }) {
                        Text("OK")
                    }
                },
                title = { Text("Error") },
                text = { Text(state.message) }
            )
        }
    }
}
```

### Optional: Custom Error Types

For better control over error messages, define app-specific errors:

```kotlin
sealed class AppError : Exception() {
    data object NetworkUnavailable : AppError() {
        override val message = "No internet connection. Please try again."
    }

    data object AuthenticationRequired : AppError() {
        override val message = "Please sign in to continue."
    }

    data class InvalidInput(val field: String) : AppError() {
        override val message = "$field is invalid."
    }
}
```

**Error Handling Rules:**
- ✅ Use sealed UI state to represent all possible states (Loading, Success, Error)
- ✅ Clear errors before retrying operations
- ✅ Use `Result<T>` in repositories for standardized error handling
- ✅ Define custom errors when you need specific messaging
- ❌ Don't over-engineer - basic String errors in UI state are fine for most cases
- ❌ Don't show technical error details to users

---

## Advanced Patterns

### ViewModel Composition

Break large ViewModel classes into focused units.

```kotlin
// Focused child ViewModels
class ProfilePostsViewModel(
    private val repository: PostRepository
) : ViewModel() {
    private val _posts = MutableStateFlow<List<Post>>(emptyList())
    val posts: StateFlow<List<Post>> = _posts.asStateFlow()

    fun loadPosts(userId: String) {
        viewModelScope.launch {
            repository.getUserPosts(userId)
                .onSuccess { _posts.value = it }
        }
    }
}

// Parent composes children
class ProfileViewModel(
    private val userRepository: UserRepository,
    val postsViewModel: ProfilePostsViewModel = ProfilePostsViewModel(PostRepositoryImpl())
) : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadProfile(id: String) {
        viewModelScope.launch {
            userRepository.fetchUser(id)
                .onSuccess { _user.value = it }
        }
    }
}

// Composable uses composed ViewModels
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = viewModel()) {
    val user by viewModel.user.collectAsStateWithLifecycle()
    val posts by viewModel.postsViewModel.posts.collectAsStateWithLifecycle()

    Column {
        user?.let { UserHeader(it) }
        PostsList(posts = posts)
    }
}
```

**When to split:** ViewModel exceeds ~200 lines OR manages multiple independent concerns.

### Shared ViewModels

For state spanning multiple features (user context, preferences).

```kotlin
// 1. Define shared ViewModel
class AppViewModel : ViewModel() {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    fun setUser(user: User?) {
        _currentUser.value = user
    }
}

// 2. Provide at app level via Hilt or manual injection
@HiltViewModel
class AppViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    // Implementation...
}

// 3. Access in Composables
@Composable
fun FeatureScreen(
    appViewModel: AppViewModel = viewModel(LocalContext.current as ComponentActivity),
    featureViewModel: FeatureViewModel = viewModel()
) {
    val currentUser by appViewModel.currentUser.collectAsStateWithLifecycle()

    Text(text = currentUser?.name ?: "Guest")
}

// 4. Inject into other ViewModels via constructor
class FeatureViewModel(
    private val repository: FeatureRepository,
    private val appViewModel: AppViewModel
) : ViewModel() {
    val userName: String
        get() = appViewModel.currentUser.value?.name ?: "Guest"
}
```

**Shared ViewModel Rules:**
- ✅ Must extend `ViewModel`
- ✅ Must be scoped appropriately (Activity-scoped or Navigation-scoped)
- ✅ Use Hilt/Koin for dependency injection when possible
- ✅ Other ViewModels accept via constructor
- ❌ Never hardcode singleton patterns - use DI
- ❌ Never access from Models

### Navigation

ViewModel owns navigation intent (sealed class), Composable owns mechanism (NavController).

```kotlin
// ViewModel declares destinations
class FeatureViewModel : ViewModel() {
    private val _navigationEvent = Channel<NavigationEvent>(Channel.BUFFERED)
    val navigationEvent = _navigationEvent.receiveAsFlow()

    sealed interface NavigationEvent {
        data class ToDetail(val id: String) : NavigationEvent
        data object ToSettings : NavigationEvent
        data object Back : NavigationEvent
    }

    fun navigate(event: NavigationEvent) {
        viewModelScope.launch {
            _navigationEvent.send(event)
        }
    }
}

// Composable implements navigation
@Composable
fun FeatureScreen(
    navController: NavHostController,
    viewModel: FeatureViewModel = viewModel()
) {
    LaunchedEffect(Unit) {
        viewModel.navigationEvent.collect { event ->
            when (event) {
                is FeatureViewModel.NavigationEvent.ToDetail -> {
                    navController.navigate("detail/${event.id}")
                }
                is FeatureViewModel.NavigationEvent.ToSettings -> {
                    navController.navigate("settings")
                }
                is FeatureViewModel.NavigationEvent.Back -> {
                    navController.popBackStack()
                }
            }
        }
    }

    Content(onNavigate = { viewModel.navigate(it) })
}
```

**Modal Presentation (Bottom Sheets, Dialogs):**

```kotlin
// ViewModel declares sheet state
class FeatureViewModel : ViewModel() {
    private val _sheetState = MutableStateFlow<Sheet?>(null)
    val sheetState: StateFlow<Sheet?> = _sheetState.asStateFlow()

    sealed interface Sheet {
        data object Edit : Sheet
        data object Share : Sheet
    }

    fun showSheet(sheet: Sheet) {
        _sheetState.value = sheet
    }

    fun dismissSheet() {
        _sheetState.value = null
    }
}

// Composable renders sheet
@Composable
fun FeatureScreen(viewModel: FeatureViewModel = viewModel()) {
    val sheetState by viewModel.sheetState.collectAsStateWithLifecycle()
    val bottomSheetState = rememberModalBottomSheetState()

    Content()

    sheetState?.let { sheet ->
        ModalBottomSheet(
            onDismissRequest = { viewModel.dismissSheet() },
            sheetState = bottomSheetState
        ) {
            when (sheet) {
                is FeatureViewModel.Sheet.Edit -> EditContent()
                is FeatureViewModel.Sheet.Share -> ShareContent()
            }
        }
    }
}
```

**Navigation Rules:**
- ✅ ViewModel owns navigation intent (sealed class/interface)
- ✅ Composable owns NavController
- ✅ Use `Channel` and `Flow` for one-time navigation events
- ✅ Modal destinations represented as nullable state
- ❌ ViewModel never holds NavController reference
- ❌ Never navigate directly from Composables without ViewModel awareness

---

## Flexibility Guidelines

**When You Can Skip Layers:**
- Simple static content: Model + Composable only (no ViewModel, no Repository)
- Read-only features: Skip Repository if no async operations
- Trivial actions: Skip loading/error states if user won't notice

**When You Can Bend Rules:**
- Prototyping: Skip interfaces for throwaway code
- Internal tools: Direct repository calls from ViewModels if feature is internal-only
- Caching: Repositories can store cache (but not UI/business state)

**Never Compromise:**
- `viewModelScope` for coroutines (prevents memory leaks)
- `StateFlow` immutability (preserves unidirectional data flow)
- Interface-based repositories in production (testability)
- Sealed UI state classes (exhaustive when handling)

---

## Testing

Interface-based repositories enable testing without network calls.

```kotlin
// Mock conforming to interface
class MockUserRepository : UserRepository {
    override suspend fun fetchUser(id: String): Result<User> {
        return Result.success(User(id = "test", name = "Test", email = "test@test.com"))
    }
}

// Test with mock
class UserViewModelTest {
    @Test
    fun `test user loading success`() = runTest {
        val viewModel = UserViewModel(repository = MockUserRepository())
        viewModel.loadUser("123")

        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Success)
        assertEquals("Test", (state as UserUiState.Success).user.name)
    }
}
```

**Why Interfaces Matter:**
- Test ViewModels without network/database
- Verify business logic in isolation
- Fast, deterministic tests

---

## Material Design 3 (Material You)

**Material Design 3** is Android's modern design system, emphasizing dynamic color, improved components, and personalization.

### Basic Usage

Apply Material 3 theming at the app level:

```kotlin
@Composable
fun MyApp() {
    MaterialTheme(
        colorScheme = dynamicColorScheme(),
        typography = Typography,
        shapes = Shapes
    ) {
        // Your app content
        Surface(modifier = Modifier.fillMaxSize()) {
            MainScreen()
        }
    }
}

// Dynamic color (Android 12+)
@Composable
fun dynamicColorScheme(): ColorScheme {
    val context = LocalContext.current
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        dynamicDarkColorScheme(context)
    } else {
        darkColorScheme()
    }
}
```

### Material 3 Components

Use Material 3 components consistently across the app:

```kotlin
// Buttons
Button(onClick = { /* action */ }) {
    Text("Primary Action")
}

FilledTonalButton(onClick = { /* action */ }) {
    Text("Secondary Action")
}

OutlinedButton(onClick = { /* action */ }) {
    Text("Tertiary Action")
}

// Cards
Card(
    modifier = Modifier.fillMaxWidth(),
    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Card Title", style = MaterialTheme.typography.titleLarge)
        Text("Card content", style = MaterialTheme.typography.bodyMedium)
    }
}

// Top App Bar
TopAppBar(
    title = { Text("Screen Title") },
    navigationIcon = {
        IconButton(onClick = { /* navigate back */ }) {
            Icon(Icons.Default.ArrowBack, contentDescription = "Back")
        }
    },
    colors = TopAppBarDefaults.topAppBarColors(
        containerColor = MaterialTheme.colorScheme.primaryContainer
    )
)
```

### Material 3 Color Roles

```kotlin
// Surface colors
Surface(color = MaterialTheme.colorScheme.surface) { }
Surface(color = MaterialTheme.colorScheme.surfaceVariant) { }

// Container colors (for cards, buttons)
containerColor = MaterialTheme.colorScheme.primaryContainer
containerColor = MaterialTheme.colorScheme.secondaryContainer

// Content colors (text, icons)
contentColor = MaterialTheme.colorScheme.onSurface
contentColor = MaterialTheme.colorScheme.onPrimary
```

### Material 3 Typography

```kotlin
Text(
    text = "Display Large",
    style = MaterialTheme.typography.displayLarge
)

Text(
    text = "Headline Medium",
    style = MaterialTheme.typography.headlineMedium
)

Text(
    text = "Body Large",
    style = MaterialTheme.typography.bodyLarge
)

Text(
    text = "Label Small",
    style = MaterialTheme.typography.labelSmall
)
```

### Material 3 Rules

**Do:**
- ✅ Use `MaterialTheme` for all theming
- ✅ Use Material 3 components from `androidx.compose.material3`
- ✅ Apply dynamic color on Android 12+
- ✅ Follow Material 3 color roles (primary, secondary, tertiary, surface variants)
- ✅ Use semantic color names (e.g., `onSurface`, `primaryContainer`)

**Don't:**
- ❌ Don't use Material 2 components (`androidx.compose.material`)
- ❌ Don't hardcode colors - use theme colors
- ❌ Don't mix Material 2 and Material 3 in the same app
- ❌ Don't create custom components that don't follow Material 3 guidelines

### Migration from Material 2 to Material 3

**Before (Material 2):**
```kotlin
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme

MaterialTheme {
    Button(onClick = { }) { Text("Click") }
}
```

**After (Material 3):**
```kotlin
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme

MaterialTheme {
    Button(onClick = { }) { Text("Click") }
}
```

**Benefits:**
- Better dynamic theming support
- Improved accessibility
- Modern design language
- Better component consistency

---

## Further Reading

- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html) - Structured concurrency for async operations
- [Jetpack Compose](https://developer.android.com/jetpack/compose) - Modern toolkit for building native UI
- [Android Architecture Guide](https://developer.android.com/topic/architecture) - Guide to app architecture
- [Material Design 3](https://m3.material.io/) - Material You design system
