# Swift to Kotlin/Android Migration Workflow

**Purpose:** Generic patterns and strategies for migrating iOS apps (Swift/SwiftUI) to Android (Kotlin/Compose).

## When to Use This Workflow

- Migrating complete iOS app to Android
- Porting specific features from Swift to Kotlin
- Creating Android equivalent of iOS app
- Understanding platform differences during migration

---

## Migration Strategy

### Phase 1: Architecture Mapping

**Swift MVVM → Kotlin MVVM**

Both platforms use MVVM, but with different implementations:

| iOS (Swift) | Android (Kotlin) |
|-------------|------------------|
| `@Observable` class | `ViewModel` + `StateFlow` |
| `@Published` property | `MutableStateFlow` / `StateFlow` |
| `@State` / `@Binding` | `collectAsStateWithLifecycle()` |
| SwiftUI View | `@Composable` function |
| Combine / async-await | Kotlin Coroutines + Flow |

### Phase 2: UI Layer Translation

**SwiftUI → Jetpack Compose**

| SwiftUI | Jetpack Compose |
|---------|-----------------|
| `struct ContentView: View` | `@Composable fun ContentView()` |
| `var body: some View` | Function body directly |
| `VStack { }` | `Column { }` |
| `HStack { }` | `Row { }` |
| `ZStack { }` | `Box { }` |
| `List { }` | `LazyColumn { }` |
| `ForEach` | `items()` in lazy lists |
| `.padding()` | `Modifier.padding()` |
| `.background(Color.blue)` | `Modifier.background(Color.Blue)` |
| `@State var name = ""` | `var name by remember { mutableStateOf("") }` |
| `@StateObject var vm = VM()` | `val vm: VM = viewModel()` |
| `@EnvironmentObject` | Hilt/Koin DI or pass as parameter |

### Phase 3: Data Layer Translation

**Swift Data Models → Kotlin Data Classes**

**Before (Swift):**
```swift
struct User: Codable {
    let id: String
    let name: String
    let email: String

    var displayName: String {
        name.isEmpty ? email : name
    }
}
```

**After (Kotlin):**
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

### Phase 4: Repository Layer

**Swift Protocols → Kotlin Interfaces**

**Before (Swift):**
```swift
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}

class UserRepositoryImpl: UserRepository {
    func fetchUser(id: String) async throws -> User {
        // API call
    }
}
```

**After (Kotlin):**
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
```

**Key Differences:**
- Swift uses `throws`, Kotlin uses `Result<T>` pattern
- Swift `async` → Kotlin `suspend`
- Kotlin requires explicit error handling

### Phase 5: ViewModel Layer

**Swift Observable → Kotlin ViewModel**

**Before (Swift):**
```swift
@Observable
class UserViewModel {
    var user: User?
    var isLoading = false
    var errorMessage: String?

    private let repository: UserRepository

    init(repository: UserRepository = UserRepositoryImpl()) {
        self.repository = repository
    }

    func loadUser(id: String) async {
        isLoading = true
        do {
            user = try await repository.fetchUser(id: id)
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}
```

**After (Kotlin):**
```kotlin
class UserViewModel(
    private val repository: UserRepository = UserRepositoryImpl()
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
                    _uiState.value = UserUiState.Error(error.message ?: "Unknown error")
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

**Key Differences:**
- Kotlin uses sealed UI state pattern (more explicit)
- `viewModelScope` automatically cancels coroutines
- StateFlow vs multiple published properties
- Kotlin requires extending `ViewModel` base class

### Phase 6: View Layer

**SwiftUI View → Composable**

**Before (Swift):**
```swift
struct UserScreen: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                Text(user.displayName)
            } else if let error = viewModel.errorMessage {
                Text(error)
                    .foregroundColor(.red)
            }
        }
        .task {
            await viewModel.loadUser(id: "123")
        }
    }
}
```

**After (Kotlin):**
```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column {
        when (val state = uiState) {
            is UserUiState.Loading -> {
                CircularProgressIndicator()
            }
            is UserUiState.Success -> {
                Text(text = state.user.displayName)
            }
            is UserUiState.Error -> {
                Text(
                    text = state.message,
                    color = MaterialTheme.colorScheme.error
                )
            }
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser("123")
    }
}
```

**Key Differences:**
- Kotlin uses `when` for exhaustive state handling
- `collectAsStateWithLifecycle()` vs `@StateObject`
- `LaunchedEffect` vs `.task`
- Material theme colors vs SwiftUI colors

---

## Language Syntax Mapping

### Common Swift → Kotlin Patterns

| Swift | Kotlin |
|-------|--------|
| `let constant = value` | `val constant = value` |
| `var variable = value` | `var variable = value` |
| `func name(param: Type) -> ReturnType` | `fun name(param: Type): ReturnType` |
| `if let unwrapped = optional` | `optional?.let { unwrapped -> }` |
| `guard let value = optional else { return }` | `val value = optional ?: return` |
| `[Type]` (Array) | `List<Type>` |
| `[Key: Value]` (Dictionary) | `Map<Key, Value>` |
| `enum Case { case a, b }` | `enum class Case { A, B }` |
| `struct` | `data class` |
| `class` | `class` |
| `protocol` | `interface` |
| `extension` | `extension function` |
| `String?` (Optional) | `String?` (Nullable) |
| `try? await call()` | `runCatching { call() }` |
| `async throws` | `suspend` + `Result<T>` |
| `.map { }` | `.map { }` |
| `.filter { }` | `.filter { }` |
| `.isEmpty` | `.isEmpty()` |
| `.count` | `.size` |

### Optionals vs Nullables

**Swift:**
```swift
var name: String? = nil
if let unwrappedName = name {
    print(unwrappedName)
}
```

**Kotlin:**
```kotlin
var name: String? = null
name?.let { unwrappedName ->
    println(unwrappedName)
}
// Or simpler:
println(name ?: "default")
```

### Collections

**Swift:**
```swift
let numbers = [1, 2, 3, 4, 5]
let doubled = numbers.map { $0 * 2 }
let evens = numbers.filter { $0 % 2 == 0 }
```

**Kotlin:**
```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }
val evens = numbers.filter { it % 2 == 0 }
```

### Closures vs Lambdas

**Swift:**
```swift
func performAction(completion: (Result<String, Error>) -> Void) {
    completion(.success("Done"))
}

performAction { result in
    switch result {
    case .success(let value): print(value)
    case .failure(let error): print(error)
    }
}
```

**Kotlin:**
```kotlin
fun performAction(completion: (Result<String>) -> Unit) {
    completion(Result.success("Done"))
}

performAction { result ->
    result
        .onSuccess { value -> println(value) }
        .onFailure { error -> println(error) }
}
```

---

## Platform-Specific Differences

### Lifecycle Management

**iOS (Swift):**
- Views automatically manage lifecycle
- `onAppear` / `onDisappear` modifiers
- Combine subscriptions need manual cancellation

**Android (Kotlin):**
- `ViewModel` survives configuration changes
- `viewModelScope` auto-cancels on ViewModel clear
- `collectAsStateWithLifecycle()` handles lifecycle automatically
- Use `LaunchedEffect` / `DisposableEffect` for side effects

### Dependency Injection

**iOS:** Typically manual or using `@EnvironmentObject`

**Android:** Use Hilt or Koin for DI:
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()
```

### Navigation

**iOS (SwiftUI):**
```swift
NavigationStack {
    NavigationLink("Details", value: item)
}
```

**Android (Compose):**
```kotlin
val navController = rememberNavController()
NavHost(navController, startDestination = "home") {
    composable("home") { HomeScreen(navController) }
    composable("details/{id}") { DetailScreen() }
}
```

### Theming

**iOS:** Uses `Color`, `Font` from SwiftUI

**Android:** Material 3 with `MaterialTheme`:
```kotlin
MaterialTheme(
    colorScheme = dynamicColorScheme(),
    typography = Typography
) {
    // App content
}
```

---

## Migration Checklist

### Pre-Migration

- [ ] Audit iOS codebase architecture
- [ ] Identify platform-specific features (e.g., HealthKit → Health Connect)
- [ ] List all third-party dependencies
- [ ] Document API integrations
- [ ] Map iOS features to Android equivalents

### During Migration

- [ ] Set up Android project structure
- [ ] Implement MVVM with Kotlin conventions
- [ ] Migrate data models (Swift structs → Kotlin data classes)
- [ ] Convert repositories (protocols → interfaces)
- [ ] Translate ViewModels (Observable → ViewModel + StateFlow)
- [ ] Rebuild UI (SwiftUI → Jetpack Compose)
- [ ] Implement navigation (NavigationStack → NavHost)
- [ ] Set up dependency injection (Hilt/Koin)
- [ ] Apply Material 3 theming

### Post-Migration

- [ ] Test all features on Android devices
- [ ] Verify edge cases and error handling
- [ ] Performance testing
- [ ] Accessibility audit
- [ ] Code review against Kotlin conventions
- [ ] Update documentation

---

## Common Pitfalls

### 1. State Management Confusion

**Pitfall:** Trying to use multiple `@Published`-like properties instead of sealed state.

**Solution:** Use sealed UI state classes for all possible states (Loading, Success, Error).

### 2. Missing Lifecycle Awareness

**Pitfall:** Not using `viewModelScope` or `collectAsStateWithLifecycle()`.

**Solution:** Always launch coroutines in `viewModelScope` and collect state with lifecycle awareness.

### 3. Direct Repository Access

**Pitfall:** Calling repositories directly from Composables (like Swift views might call services).

**Solution:** Always go through ViewModel layer.

### 4. Ignoring Material Design

**Pitfall:** Trying to replicate iOS design exactly.

**Solution:** Embrace Material 3 design system for native Android feel.

### 5. Error Handling Differences

**Pitfall:** Using Swift's `throws` pattern directly.

**Solution:** Use Kotlin's `Result<T>` pattern for consistent error handling.

---

## Best Practices

1. **Don't Port Blindly:** Adapt to Android conventions, don't just translate
2. **Embrace Material 3:** Use native design system, not iOS look-alike
3. **Use Kotlin Idioms:** Leverage Kotlin features (data classes, sealed classes, extension functions)
4. **Follow MVVM Strictly:** Kotlin conventions are stricter than Swift for good reason
5. **Test with Interfaces:** Interface-based repositories enable better testing
6. **Think Lifecycle:** Android lifecycle is different, respect it
7. **Use Jetpack Libraries:** Don't reinvent what Jetpack provides

---

## Platform Feature Mapping

| iOS Feature | Android Equivalent |
|-------------|-------------------|
| HealthKit | Health Connect |
| CloudKit | Firebase / Room + Cloud sync |
| Core Data | Room Database |
| UserDefaults | DataStore (prefer over SharedPreferences) |
| Keychain | EncryptedSharedPreferences / Keystore |
| StoreKit | Google Play Billing |
| Push Notifications | Firebase Cloud Messaging |
| Sign in with Apple | Google Sign-In / Firebase Auth |
| SwiftData | Room Database |
| PhotosPicker | Photo Picker (Jetpack) |

---

## Reference Resources

**Kotlin Conventions:**
`read /Users/coreyyoung/Claude/context/knowledge/languages/kotlin-conventions.md`

**Compose Documentation:**
- https://developer.android.com/jetpack/compose
- https://developer.android.com/jetpack/compose/mental-model

**Migration Guides:**
- https://developer.android.com/jetpack/compose/interop/adding
- https://kotlinlang.org/docs/home.html

---

## Quick Reference: Side-by-Side Example

**Complete Feature: User Profile**

### iOS (Swift + SwiftUI)

```swift
// Model
struct User: Codable {
    let id: String
    let name: String
}

// Repository
protocol UserRepository {
    func fetchUser(id: String) async throws -> User
}

// ViewModel
@Observable
class UserViewModel {
    var user: User?
    var isLoading = false

    func loadUser(id: String) async {
        isLoading = true
        user = try? await repository.fetchUser(id: id)
        isLoading = false
    }
}

// View
struct UserScreen: View {
    @StateObject var viewModel = UserViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                Text(user.name)
            }
        }
        .task { await viewModel.loadUser(id: "123") }
    }
}
```

### Android (Kotlin + Compose)

```kotlin
// Model
data class User(
    val id: String,
    val name: String
)

// Repository
interface UserRepository {
    suspend fun fetchUser(id: String): Result<User>
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            repository.fetchUser(id)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message) }
        }
    }
}

sealed interface UiState {
    data object Loading : UiState
    data class Success(val user: User) : UiState
    data class Error(val message: String?) : UiState
}

// Composable
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column {
        when (val state = uiState) {
            is UiState.Loading -> CircularProgressIndicator()
            is UiState.Success -> Text(state.user.name)
            is UiState.Error -> Text("Error: ${state.message}")
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser("123")
    }
}
```

**Key Observations:**
- Kotlin requires more boilerplate (sealed state, StateFlow patterns)
- Kotlin is more explicit (better for large codebases)
- Both follow MVVM but with platform-specific implementations
- Android has stricter separation of concerns

---

This workflow is generic and reusable across any Swift → Kotlin migration project.
