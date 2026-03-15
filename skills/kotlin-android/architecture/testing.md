# Testing

**Part of:** [kotlin-android](../SKILL.md) > Architecture

**Related:**
- [examples.md](examples.md) - Full feature examples with tests
- [advanced-patterns.md](advanced-patterns.md) - Patterns that affect testability

---

## Overview

Interface-based repositories enable testing without network or database calls. Test ViewModels in isolation with fake repositories. Use JUnit5 for unit tests, Turbine for Flow testing, and Compose UI Test for UI tests.

**Principles (FIRST):**
- **Fast** - Tests run in milliseconds, no network/database
- **Isolated** - Each test creates its own state, no shared dependencies
- **Repeatable** - Same result every time, no environment sensitivity
- **Self-validating** - Pass/fail with clear assertions
- **Timely** - Written alongside the feature, mirroring production structure

**Critical: Prefer testing ViewModels over testing Composables directly.** The ViewModel contains all business logic. UI tests verify rendering, not correctness.

---

## Testing Framework Hierarchy

| Layer | Framework | When to Use |
|-------|-----------|-------------|
| Unit (ViewModel, Repository) | JUnit5 + Kotlin Coroutines Test | Business logic, state transitions |
| Flow assertions | Turbine | StateFlow / SharedFlow emissions |
| Room DAO | JUnit4 + In-memory Room | Database queries |
| Compose UI | `ComposeTestRule` (AndroidJUnit4) | Component rendering, interactions |
| Screenshot | Roborazzi or Paparazzi | Visual regression |
| Hilt integration | `@HiltAndroidTest` | DI wiring in context |

---

## Gradle Dependencies

```kotlin
// build.gradle.kts (app module)
dependencies {
    // JUnit5
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")

    // Coroutines test (runTest, TestDispatcher)
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")

    // Turbine (Flow testing)
    testImplementation("app.cash.turbine:turbine:1.1.0")

    // MockK (sparingly - prefer fakes)
    testImplementation("io.mockk:mockk:1.13.12")

    // Compose UI Testing
    androidTestImplementation("androidx.compose.ui:ui-test-junit4")
    debugImplementation("androidx.compose.ui:ui-test-manifest")

    // Hilt testing
    androidTestImplementation("com.google.dagger:hilt-android-testing:2.51.1")
    kaptAndroidTest("com.google.dagger:hilt-android-compiler:2.51.1")

    // Room in-memory
    testImplementation("androidx.room:room-testing:2.6.1")

    // Roborazzi (screenshot testing)
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.21.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose-preview-scanner-support:1.21.0")
}

// Enable JUnit5 in unit tests
tasks.withType<Test> {
    useJUnitPlatform()
}
```

---

## Unit Testing ViewModels

### Basic Pattern

```kotlin
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

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

        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Success)
        assertEquals("Alice", (state as UserUiState.Success).user.name)
    }

    @Test
    fun `loadUser emits Error state when repository fails`() = runTest {
        fakeRepository.shouldFail = true

        viewModel.loadUser("1")

        val state = viewModel.uiState.value
        assertTrue(state is UserUiState.Error)
        assertNotNull((state as UserUiState.Error).message)
    }

    @Test
    fun `loadUser sets Loading state before result`() = runTest {
        // Initial state is Loading
        assertEquals(UserUiState.Loading, viewModel.uiState.value)
    }
}
```

### TestDispatcher Setup

```kotlin
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach

class ViewModelWithDispatcherTest {

    private val testDispatcher = UnconfinedTestDispatcher()

    @BeforeEach
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @AfterEach
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `state updates are observable during coroutine execution`() = runTest {
        val fakeRepo = FakeUserRepository()
        fakeRepo.delay = 100L // simulate network delay
        val viewModel = UserViewModel(repository = fakeRepo)

        viewModel.loadUser("1")
        advanceUntilIdle()

        assertTrue(viewModel.uiState.value is UserUiState.Success)
    }
}
```

### JUnit5 Extension for Main Dispatcher

```kotlin
// TestExtensions.kt
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.jupiter.api.extension.AfterEachCallback
import org.junit.jupiter.api.extension.BeforeEachCallback
import org.junit.jupiter.api.extension.ExtensionContext

class MainDispatcherExtension(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : BeforeEachCallback, AfterEachCallback {

    override fun beforeEach(context: ExtensionContext) {
        Dispatchers.setMain(dispatcher)
    }

    override fun afterEach(context: ExtensionContext) {
        Dispatchers.resetMain()
    }
}

// Usage
@ExtendWith(MainDispatcherExtension::class)
class MyViewModelTest {
    @Test
    fun `some test`() = runTest {
        // Main dispatcher is set for you
    }
}
```

---

## Testing Coroutines

### runTest and advanceUntilIdle

```kotlin
@Test
fun `sequential operations complete in order`() = runTest {
    val viewModel = UserViewModel(repository = fakeRepository)

    viewModel.loadUser("1")
    advanceUntilIdle() // drains all pending coroutines

    assertTrue(viewModel.uiState.value is UserUiState.Success)
}

@Test
fun `delay is respected with advanceTimeBy`() = runTest {
    val scheduler = testScheduler
    val fakeRepo = FakeUserRepository(delay = 300L)
    val viewModel = SearchViewModel(repository = fakeRepo)

    viewModel.onQueryChanged("kotlin")
    // Before debounce fires
    scheduler.advanceTimeBy(200)
    assertTrue(viewModel.uiState.value is SearchUiState.Idle)

    // After debounce fires
    scheduler.advanceTimeBy(200)
    advanceUntilIdle()
    assertTrue(viewModel.uiState.value is SearchUiState.Results)
}

@Test
fun `job cancellation works correctly`() = runTest {
    val fakeRepo = FakeUserRepository(delay = 500L)
    val viewModel = SearchViewModel(repository = fakeRepo)

    viewModel.onQueryChanged("first")
    advanceTimeBy(100)
    viewModel.onQueryChanged("second") // cancels first
    advanceUntilIdle()

    val state = viewModel.uiState.value as SearchUiState.Results
    assertEquals("second", state.query)
}
```

### TestCoroutineScheduler

```kotlin
@Test
fun `multiple concurrent operations complete correctly`() = runTest {
    val viewModel = DashboardViewModel(
        userRepo = FakeUserRepository(),
        postsRepo = FakePostRepository(),
        statsRepo = FakeStatsRepository()
    )

    viewModel.loadDashboard()
    advanceUntilIdle()

    val state = viewModel.uiState.value as DashboardUiState.Success
    assertNotNull(state.user)
    assertNotNull(state.posts)
    assertNotNull(state.stats)
}
```

---

## Testing StateFlow with Turbine

Turbine provides a structured API for asserting Flow emissions in order.

### Basic Flow Testing

```kotlin
import app.cash.turbine.test
import app.cash.turbine.turbineScope

@Test
fun `uiState emits Loading then Success`() = runTest {
    val viewModel = UserViewModel(repository = fakeRepository)
    fakeRepository.user = User(id = "1", name = "Alice", email = "alice@test.com")

    viewModel.uiState.test {
        // Initial emission
        assertEquals(UserUiState.Loading, awaitItem())

        viewModel.loadUser("1")

        // After loading
        assertEquals(UserUiState.Loading, awaitItem()) // re-emits Loading
        val success = awaitItem()
        assertTrue(success is UserUiState.Success)
        cancelAndConsumeRemainingEvents()
    }
}

@Test
fun `uiState emits Error on failure`() = runTest {
    fakeRepository.shouldFail = true
    val viewModel = UserViewModel(repository = fakeRepository)

    viewModel.uiState.test {
        awaitItem() // initial Loading

        viewModel.loadUser("1")

        awaitItem() // Loading again
        val error = awaitItem()
        assertTrue(error is UserUiState.Error)
        cancelAndConsumeRemainingEvents()
    }
}
```

### Testing Multiple Flows Concurrently

```kotlin
@Test
fun `search results update as query changes`() = runTest {
    val viewModel = SearchViewModel(repository = fakeSearchRepository)

    turbineScope {
        val stateTurbine = viewModel.uiState.testIn(backgroundScope)

        assertEquals(SearchUiState.Idle, stateTurbine.awaitItem())

        viewModel.onQueryChanged("android")
        advanceUntilIdle()

        val result = stateTurbine.awaitItem()
        assertTrue(result is SearchUiState.Results)
        stateTurbine.cancel()
    }
}
```

### Testing SharedFlow Events

```kotlin
@Test
fun `sign in success emits NavigateToHome event`() = runTest {
    fakeAuthRepository.authResponse = AuthResponse(token = "token123", userId = "u1")
    val viewModel = SignInViewModel(repository = fakeAuthRepository)

    viewModel.events.test {
        viewModel.signIn("user@test.com", "password")
        advanceUntilIdle()

        val event = awaitItem()
        assertTrue(event is SignInEvent.NavigateToHome)
        cancelAndConsumeRemainingEvents()
    }
}
```

---

## Fake Repositories (Prefer Over Mocks)

Fakes are simple implementations of repository interfaces for testing. They are more readable, easier to maintain, and more resilient to refactoring than mocks.

### Simple Fake

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

    override suspend fun updateUser(user: User): Result<User> {
        if (shouldFail) return Result.failure(Exception("Update failed"))
        this.user = user
        return Result.success(user)
    }
}
```

### Call-Tracking Fake

```kotlin
class FakeUserRepository : UserRepository {
    var user: User? = null
    var shouldFail: Boolean = false

    var fetchCallCount = 0
    var lastFetchedId: String? = null
    var updateCallCount = 0

    override suspend fun fetchUser(id: String): Result<User> {
        fetchCallCount++
        lastFetchedId = id
        if (shouldFail) return Result.failure(Exception("Error"))
        return user?.let { Result.success(it) }
            ?: Result.failure(Exception("Not found"))
    }

    override suspend fun updateUser(user: User): Result<User> {
        updateCallCount++
        if (shouldFail) return Result.failure(Exception("Error"))
        this.user = user
        return Result.success(user)
    }

    fun reset() {
        fetchCallCount = 0
        lastFetchedId = null
        updateCallCount = 0
        user = null
        shouldFail = false
    }
}

// Test
@Test
fun `repository is called exactly once on loadUser`() = runTest {
    fakeRepository.user = testUser
    viewModel.loadUser("123")
    advanceUntilIdle()

    assertEquals(1, fakeRepository.fetchCallCount)
    assertEquals("123", fakeRepository.lastFetchedId)
}
```

### Fake with Flow Support

```kotlin
class FakePostRepository : PostRepository {
    private val _posts = MutableStateFlow<List<Post>>(emptyList())
    val posts: StateFlow<List<Post>> = _posts.asStateFlow()

    override fun observePosts(): Flow<List<Post>> = _posts.asStateFlow()

    override suspend fun fetchPosts(): Result<List<Post>> {
        return Result.success(_posts.value)
    }

    fun setPosts(posts: List<Post>) {
        _posts.value = posts
    }
}
```

---

## MockK Usage (Sparingly)

Use MockK when you need to verify interactions with third-party classes you can't fake, such as Android system components.

```kotlin
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk

@Test
fun `analytics event is recorded on successful sign in`() = runTest {
    val mockAnalytics = mockk<AnalyticsTracker>(relaxed = true)
    val viewModel = SignInViewModel(
        repository = fakeAuthRepository,
        analytics = mockAnalytics
    )
    fakeAuthRepository.authResponse = AuthResponse(token = "t", userId = "u1")

    viewModel.signIn("user@test.com", "pass")
    advanceUntilIdle()

    coVerify(exactly = 1) { mockAnalytics.track("sign_in_success") }
}

// Stub a suspend function
@Test
fun `network call result is handled`() = runTest {
    val mockApi = mockk<ApiService>()
    coEvery { mockApi.getUser(any()) } returns ApiUser(id = "1", name = "Alice")

    val repo = UserRepositoryImpl(apiService = mockApi)
    val result = repo.fetchUser("1")

    assertTrue(result.isSuccess)
}
```

---

## Testing Room DAOs

Use an in-memory Room database for DAO tests. These are instrumented tests (run on device/emulator).

```kotlin
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import androidx.test.ext.junit.runners.AndroidJUnit4

@RunWith(AndroidJUnit4::class)
class UserDaoTest {

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        userDao = database.userDao()
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun insertAndReadUser() = runTest {
        val user = UserEntity(id = "1", name = "Alice", email = "alice@test.com")
        userDao.insertUser(user)

        val loaded = userDao.getUserById("1")
        assertNotNull(loaded)
        assertEquals("Alice", loaded?.name)
    }

    @Test
    fun deleteUserRemovesFromDatabase() = runTest {
        val user = UserEntity(id = "1", name = "Alice", email = "alice@test.com")
        userDao.insertUser(user)
        userDao.deleteUser(user)

        val loaded = userDao.getUserById("1")
        assertNull(loaded)
    }

    @Test
    fun observeUsersEmitsUpdates() = runTest {
        userDao.observeUsers().test {
            assertEquals(emptyList<UserEntity>(), awaitItem())

            val user = UserEntity(id = "1", name = "Alice", email = "alice@test.com")
            userDao.insertUser(user)

            val updated = awaitItem()
            assertEquals(1, updated.size)
            cancelAndConsumeRemainingEvents()
        }
    }
}
```

---

## Compose UI Testing

### Basic Setup

```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import androidx.test.ext.junit.runners.AndroidJUnit4

@RunWith(AndroidJUnit4::class)
class UserProfileScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun userNameIsDisplayed() {
        val user = User(id = "1", name = "Alice", email = "alice@test.com")

        composeTestRule.setContent {
            MaterialTheme {
                UserProfileContent(user = user)
            }
        }

        composeTestRule
            .onNodeWithText("Alice")
            .assertIsDisplayed()
    }

    @Test
    fun loadingStateShowsProgressIndicator() {
        composeTestRule.setContent {
            MaterialTheme {
                UserScreen(uiState = UserUiState.Loading)
            }
        }

        composeTestRule
            .onNodeWithTag("loading_indicator")
            .assertIsDisplayed()
    }

    @Test
    fun errorStateShowsAlertDialog() {
        composeTestRule.setContent {
            MaterialTheme {
                UserScreen(
                    uiState = UserUiState.Error("Something went wrong"),
                    onDismissError = {}
                )
            }
        }

        composeTestRule
            .onNodeWithText("Something went wrong")
            .assertIsDisplayed()
    }
}
```

### Compose Test Matchers

```kotlin
// Find by text
composeTestRule.onNodeWithText("Submit").assertIsDisplayed()
composeTestRule.onNodeWithText("Submit", ignoreCase = true).performClick()

// Find by content description
composeTestRule.onNodeWithContentDescription("Back button").assertIsDisplayed()

// Find by test tag (preferred for non-text nodes)
composeTestRule.onNodeWithTag("user_avatar").assertIsDisplayed()

// Find by role
composeTestRule.onNodeWithRole(Role.Button).assertIsEnabled()

// Hierarchy traversal
composeTestRule.onNodeWithTag("user_list")
    .onChildren()
    .assertCountEquals(3)

// Filter
composeTestRule.onAllNodesWithTag("post_item")
    .filterToOne(hasText("Breaking News"))
    .assertIsDisplayed()

// Assertions
composeTestRule.onNodeWithText("Submit").assertIsEnabled()
composeTestRule.onNodeWithText("Submit").assertIsNotEnabled()
composeTestRule.onNodeWithText("Error message").assertExists()
composeTestRule.onNodeWithText("Old content").assertDoesNotExist()

// Actions
composeTestRule.onNodeWithText("Submit").performClick()
composeTestRule.onNodeWithTag("email_field").performTextInput("user@test.com")
composeTestRule.onNodeWithTag("search_field").performTextClearance()
composeTestRule.onNodeWithTag("post_list").performScrollToIndex(10)
```

### Testing User Interactions

```kotlin
@Test
fun signInFormValidationWorks() {
    var signInCalled = false

    composeTestRule.setContent {
        MaterialTheme {
            SignInForm(
                onSignIn = { email, password -> signInCalled = true }
            )
        }
    }

    // Submit button is disabled initially
    composeTestRule
        .onNodeWithText("Sign In")
        .assertIsNotEnabled()

    // Enter valid email
    composeTestRule
        .onNodeWithTag("email_field")
        .performTextInput("user@test.com")

    // Enter valid password
    composeTestRule
        .onNodeWithTag("password_field")
        .performTextInput("password123")

    // Button becomes enabled
    composeTestRule
        .onNodeWithText("Sign In")
        .assertIsEnabled()
        .performClick()

    assertTrue(signInCalled)
}
```

### Testing with ViewModel

```kotlin
@RunWith(AndroidJUnit4::class)
class UserScreenIntegrationTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun screenLoadsAndDisplaysUser() {
        val fakeRepo = FakeUserRepository()
        fakeRepo.user = User(id = "1", name = "Alice", email = "alice@test.com")
        val viewModel = UserViewModel(repository = fakeRepo)

        composeTestRule.setContent {
            MaterialTheme {
                UserScreen(viewModel = viewModel)
            }
        }

        composeTestRule.waitUntil(timeoutMillis = 5_000) {
            composeTestRule
                .onAllNodesWithText("Alice")
                .fetchSemanticsNodes()
                .isNotEmpty()
        }

        composeTestRule.onNodeWithText("Alice").assertIsDisplayed()
        composeTestRule.onNodeWithText("alice@test.com").assertIsDisplayed()
    }
}
```

---

## Screenshot Testing with Roborazzi

Roborazzi runs on the JVM (no device needed), making screenshot tests fast.

```kotlin
import com.github.takahirom.roborazzi.*
import org.robolectric.annotation.Config

@RunWith(AndroidJUnit4::class)
@Config(sdk = [33])
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class UserCardScreenshotTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun userCardLightMode() {
        composeTestRule.setContent {
            MaterialTheme(colorScheme = lightColorScheme()) {
                UserCard(
                    user = User(id = "1", name = "Alice", email = "alice@test.com"),
                    onClick = {}
                )
            }
        }

        composeTestRule
            .onNodeWithTag("user_card")
            .captureRoboImage()
    }

    @Test
    fun userCardDarkMode() {
        composeTestRule.setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                UserCard(
                    user = User(id = "1", name = "Alice", email = "alice@test.com"),
                    onClick = {}
                )
            }
        }

        composeTestRule
            .onNodeWithTag("user_card")
            .captureRoboImage()
    }
}
```

---

## Navigation Testing

```kotlin
@RunWith(AndroidJUnit4::class)
class NavigationTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun navigatesToDetailOnItemTap() {
        val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

        composeTestRule.setContent {
            MaterialTheme {
                AppNavHost(navController = navController)
            }
        }

        // Tap item on list screen
        composeTestRule
            .onNodeWithTag("post_item_1")
            .performClick()

        // Assert destination
        assertEquals(
            PostDetail(id = "1"),
            navController.currentBackStackEntry?.toRoute<PostDetail>()
        )
    }

    @Test
    fun backButtonPopsBackStack() {
        composeTestRule.setContent {
            MaterialTheme {
                AppNavHost(navController = navController)
            }
        }

        // Navigate to detail
        composeTestRule.onNodeWithTag("post_item_1").performClick()
        assertEquals(2, navController.backQueue.size)

        // Press back
        composeTestRule.onNodeWithContentDescription("Back").performClick()
        assertEquals(1, navController.backQueue.size)
    }
}
```

---

## Hilt Testing

### @HiltAndroidTest Setup

```kotlin
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.UninstallModules
import dagger.hilt.android.testing.BindValue

@HiltAndroidTest
@UninstallModules(RepositoryModule::class)
@RunWith(AndroidJUnit4::class)
class UserScreenHiltTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<HiltTestActivity>()

    @BindValue
    @JvmField
    val fakeUserRepository: UserRepository = FakeUserRepository().apply {
        user = User(id = "1", name = "Alice", email = "alice@test.com")
    }

    @Test
    fun userIsDisplayedOnScreen() {
        composeTestRule.setContent {
            MaterialTheme {
                UserScreen()
            }
        }

        composeTestRule.onNodeWithText("Alice").assertIsDisplayed()
    }
}

// Required activity for Hilt tests
@AndroidEntryPoint
class HiltTestActivity : ComponentActivity()
```

### Test Hilt Module

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class TestRepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(fake: FakeUserRepository): UserRepository
}
```

---

## Parameterized Tests

```kotlin
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.ValueSource

class EmailValidationTest {

    private val validator = EmailValidator()

    @ParameterizedTest
    @ValueSource(strings = ["user@test.com", "first.last@domain.org", "user+tag@company.co"])
    fun `valid emails pass validation`(email: String) {
        assertTrue(validator.isValid(email))
    }

    @ParameterizedTest
    @ValueSource(strings = ["notanemail", "@nodomain", "missing@", ""])
    fun `invalid emails fail validation`(email: String) {
        assertFalse(validator.isValid(email))
    }

    @ParameterizedTest
    @CsvSource(
        "user@test.com, true",
        "notvalid, false",
        "'', false"
    )
    fun `email validation returns expected result`(email: String, expected: Boolean) {
        assertEquals(expected, validator.isValid(email))
    }
}
```

---

## Test Rules and Extensions

```kotlin
// CoroutineTestRule - sets Main dispatcher for all tests in a class
class CoroutineTestRule(
    val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        super.starting(description)
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        super.finished(description)
        Dispatchers.resetMain()
    }
}

// Usage with JUnit4 (for instrumented tests)
@get:Rule
val coroutineTestRule = CoroutineTestRule()

// InstantTaskExecutorRule (for LiveData, if still used)
@get:Rule
val instantTaskExecutorRule = InstantTaskExecutorRule()
```

---

## Test Organization

### Mirror Production Structure

```
app/
└── src/
    ├── main/
    │   └── java/com/myapp/
    │       ├── features/
    │       │   └── user/
    │       │       ├── UserViewModel.kt
    │       │       ├── UserRepository.kt
    │       │       └── UserScreen.kt
    │       └── ...
    ├── test/                          # JVM unit tests
    │   └── java/com/myapp/
    │       └── features/
    │           └── user/
    │               ├── UserViewModelTest.kt
    │               ├── UserRepositoryTest.kt
    │               └── fakes/
    │                   └── FakeUserRepository.kt
    └── androidTest/                   # Instrumented tests
        └── java/com/myapp/
            └── features/
                └── user/
                    ├── UserScreenTest.kt
                    └── UserDaoTest.kt
```

### Group Tests by Behavior

```kotlin
class PostListViewModelTest {

    private lateinit var fakeRepo: FakePostRepository
    private lateinit var viewModel: PostListViewModel

    @BeforeEach
    fun setup() {
        fakeRepo = FakePostRepository()
        viewModel = PostListViewModel(repository = fakeRepo)
    }

    @Nested
    @DisplayName("Initial load")
    inner class InitialLoad {
        @Test
        fun `starts with loading state`() = runTest { /* ... */ }

        @Test
        fun `displays posts on success`() = runTest { /* ... */ }

        @Test
        fun `shows error on failure`() = runTest { /* ... */ }
    }

    @Nested
    @DisplayName("Pagination")
    inner class Pagination {
        @Test
        fun `loadMore appends to existing list`() = runTest { /* ... */ }

        @Test
        fun `loadMore is no-op when all loaded`() = runTest { /* ... */ }
    }

    @Nested
    @DisplayName("Pull to refresh")
    inner class Refresh {
        @Test
        fun `refresh resets list and reloads`() = runTest { /* ... */ }
    }
}
```

---

## Best Practices

### DO

1. **Test business logic, not implementation details**
```kotlin
// GOOD: Test outcome
assertTrue(viewModel.uiState.value is UserUiState.Success)

// BAD: Test internal call count (unless interaction is the feature)
assertEquals(1, fakeRepository.fetchCallCount)
```

2. **Use descriptive test names (backtick format)**
```kotlin
// GOOD
@Test
fun `loadUser emits Success state when repository returns user`() = runTest { }

// BAD
@Test
fun testLoadUser() = runTest { }
```

3. **Arrange-Act-Assert structure**
```kotlin
@Test
fun `sign in updates auth state on success`() = runTest {
    // Arrange
    fakeRepository.authResponse = AuthResponse(token = "abc", userId = "u1")
    val viewModel = SignInViewModel(repository = fakeRepository)

    // Act
    viewModel.signIn("user@test.com", "password123")
    advanceUntilIdle()

    // Assert
    assertTrue(viewModel.uiState.value is SignInUiState.Success)
}
```

4. **Test edge cases explicitly**
```kotlin
@Test fun `empty list shows empty state`() = runTest { }
@Test fun `network error shows retry option`() = runTest { }
@Test fun `second load cancels first`() = runTest { }
@Test fun `loadMore is ignored when already loading`() = runTest { }
```

5. **Prefer fakes over mocks for repositories**
```kotlin
// GOOD: Fake is readable and maintainable
class FakeUserRepository : UserRepository {
    var user: User? = null
    override suspend fun fetchUser(id: String) = user?.let { Result.success(it) }
        ?: Result.failure(Exception("Not found"))
}

// USE SPARINGLY: MockK for interaction verification with third parties
val mockAnalytics = mockk<Analytics>(relaxed = true)
```

### DON'T

1. **Don't test Composable internals** - test ViewModel or use Compose UI Test for rendering
2. **Don't share state between tests** - each test creates its own ViewModel and fakes
3. **Don't use `Thread.sleep()`** - use `advanceUntilIdle()` or `advanceTimeBy()`
4. **Don't test against real network or real database** - always use fakes or in-memory DB
5. **Don't forget `cancelAndConsumeRemainingEvents()`** in Turbine tests
6. **Don't mock data classes** - instantiate them directly
7. **Don't leave `@Ignore`d tests indefinitely** - fix or delete them

---

*Testing patterns based on JUnit5, Kotlin Coroutines Test, Turbine, and Android official testing guidance.*
