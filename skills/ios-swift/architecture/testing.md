# Testing

**Part of:** [ios-swift](../SKILL.md) > Architecture

**Related:**
- [controllers.md](controllers.md) - Controllers to test
- [services.md](services.md) - Service protocols enable testing

---

## Overview

Protocol-based services enable testing without network calls. Test controllers in isolation with mock services. Use Swift Testing as the primary framework.

**Principles (FIRST):**
- **Fast** - Tests run in milliseconds, no network/database
- **Isolated** - Each test creates its own state, no shared dependencies
- **Repeatable** - Same result every time, no environment sensitivity
- **Self-validating** - Pass/fail, no manual inspection
- **Timely** - Written alongside the feature, mirroring production structure

**Critical: Never test SwiftUI views directly.** Test the `@Observable` Controller instead. Mirror production folder structure in your test target.

---

## Swift Testing Framework (Primary)

Swift Testing is the default. Use structs, not classes. Tests are parallel by default.

### Core Rules

- **Structs over classes** - No `XCTestCase`, no `test` prefix
- **`init`/`deinit` for setup/teardown** - Not `setUp()`/`tearDown()` (that is XCTest)
- **`@Suite` is implicit** - Any struct with `@Test` is a suite. Only add `@Suite` when you need traits or a custom display name
- **`#expect` for assertions** - Use `#expect(value == false)` not `#expect(!value)` because `!` defeats macro expansion
- **`#require` for preconditions** - Throws + stops the test on failure. Also unwraps optionals
- **Parallel by default** - `.serialized` trait only works on parameterized tests; adding it to regular tests/suites does nothing

### Basic Pattern

```swift
import Testing

struct UserControllerTests {
    let mockService: MockUserService
    let controller: UserController

    init() {
        mockService = MockUserService()
        controller = UserController(service: mockService)
    }

    @Test("loads user successfully")
    func loadUser() async {
        await mockService.setMockUser(User(id: "1", name: "Alice", email: "alice@test.com"))

        await controller.loadUser(id: "1")

        #expect(controller.user?.name == "Alice")
        #expect(controller.user?.email == "alice@test.com")
        #expect(controller.isLoading == false)
        #expect(controller.errorMessage == nil)
    }

    @Test("handles network error gracefully")
    func loadUserError() async {
        await mockService.setShouldFail(true)

        await controller.loadUser(id: "1")

        #expect(controller.user == nil)
        #expect(controller.isLoading == false)
        #expect(controller.errorMessage != nil)
    }
}
```

### `#require` vs `#expect`

```swift
@Test func userProfileLoads() async {
    await controller.loadUser(id: "123")

    // #require unwraps optionals — test stops if nil
    let user = try #require(controller.user)

    // Now safely use the unwrapped value
    #expect(user.name == "Alice")
    #expect(user.email == "alice@test.com")
}

@Test func preconditionCheck() async throws {
    // #require as a precondition gate — stops test if false
    try #require(controller.isReady, "Controller must be ready before testing")

    await controller.performAction()
    #expect(controller.result != nil)
}
```

### Error Testing

```swift
@Test func throwsSpecificError() async {
    await mockService.setShouldFail(true)

    // Name the specific error — never use Error.self
    #expect(throws: GameError.notInstalled) {
        try await controller.startGame()
    }
}

@Test func doesNotThrow() async {
    // Never.self asserts no error thrown
    #expect(throws: Never.self) {
        try await controller.validateInput("valid@email.com")
    }
}

// Swift 6.1+: #expect(throws:) returns the error for validation
@Test func errorContainsContext() async {
    let error = #expect(throws: APIError.self) {
        try await controller.fetchData()
    }
    #expect(error?.statusCode == 404)
}
```

### Parameterized Tests

```swift
// Single parameter
@Test("validates email format", arguments: [
    "test@example.com",
    "user.name@domain.org",
    "first+last@company.co"
])
func validEmails(email: String) {
    #expect(EmailValidator.isValid(email) == true)
}

// Two collections = Cartesian product (every combination)
@Test("role permissions", arguments: Role.allCases, Permission.allCases)
func permissions(role: Role, permission: Permission) {
    let result = role.hasPermission(permission)
    #expect(result == expectedPermissions[role]?[permission])
}

// Use zip() for pairwise (not Cartesian)
@Test("input/output pairs", arguments: zip(
    ["hello", "world"],
    ["HELLO", "WORLD"]
))
func uppercasing(input: String, expected: String) {
    #expect(input.uppercased() == expected)
}
```

**Parameterized limits:** Max 2 collections. Two collections produce Cartesian product by default.

### Traits

```swift
// .disabled for known broken tests
@Test(.disabled("Server migration in progress"))
func fetchRemoteConfig() async { }

// .bug for tracking
@Test(.bug("https://github.com/org/repo/issues/123", "Flaky on CI"))
func intermittentFailure() async { }

// .timeLimit — ONLY .minutes exists, .seconds does NOT
@Test(.timeLimit(.minutes(1)))
func longRunningOperation() async { }

// .tags for filtering
extension Tag {
    @Tag static var networking: Self
    @Tag static var offline: Self
}

@Test(.tags(.networking))
func fetchUsers() async { }

// @available goes on individual tests, NOT suites
@Test
@available(iOS 26, *)
func liquidGlassEffect() { }
```

### Known Issues

```swift
@Test func featureWithKnownBug() {
    withKnownIssue("Rounding error in currency conversion") {
        let result = convert(amount: 10.0, from: .usd, to: .eur)
        #expect(result == 9.23)
    }
}
```

### Async Confirmation

```swift
// confirmation() for async events — closure MUST complete before returning
@Test func notificationFired() async {
    await confirmation() { confirm in
        NotificationCenter.default.addObserver(
            forName: .userLoggedIn, object: nil, queue: .main
        ) { _ in
            confirm()
        }
        await controller.login(user: "test", password: "pass")
    }
}

// Assert event never happens
@Test func noSpuriousNotification() async {
    await confirmation(expectedCount: 0) { confirm in
        NotificationCenter.default.addObserver(
            forName: .userLoggedOut, object: nil, queue: .main
        ) { _ in
            confirm()  // This should NOT fire
        }
        await controller.refreshToken()
    }
}
```

**Warning:** `confirmation()` requires all code to finish before the closure ends. Completion handlers that fire after the closure returns will not work. Wrap callback APIs with `withCheckedContinuation` first.

### Human-Readable Test Names (Swift 6.1+)

```swift
// Raw identifiers with backticks for descriptive names
@Test func `user profile loads after authentication`() async {
    // ...
}

@Test func `empty cart shows zero total`() {
    // ...
}
```

### Exit Tests (Swift 6.2+)

```swift
@Test func fatalErrorOnInvalidState() async {
    await #expect(processExitsWith: .failure) {
        controller.forceUnwrapNilValue()
    }
}
```

### Attachments (Swift 6.2+)

```swift
@Test func screenshotComparison() async throws {
    let result = try await controller.renderProfile()

    // Attach artifacts to test results (must be Attachable + Codable)
    Attachment.record(result, named: "profile-render-output")

    #expect(result.isValid == true)
}
```

### Source Location for Verification Helpers

```swift
// Custom assertion helpers must propagate source location
func expectUserValid(
    _ user: User?,
    sourceLocation: SourceLocation = #_sourceLocation
) {
    #expect(user != nil, "User should not be nil", sourceLocation: sourceLocation)
    #expect(user?.email.contains("@") == true, sourceLocation: sourceLocation)
}

@Test func userIsValid() async {
    await controller.loadUser(id: "1")
    expectUserValid(controller.user)  // Failures point to THIS line
}
```

### Dependency Injection for Testability

```swift
// Inject URLSession via protocol
protocol URLSessionProtocol: Sendable {
    func data(for request: URLRequest) async throws -> (Data, URLResponse)
}

extension URLSession: URLSessionProtocol {}

// Inject UserDefaults via UUID suiteName
struct UserPreferencesTests {
    let defaults: UserDefaults

    init() {
        defaults = UserDefaults(suiteName: UUID().uuidString)!
    }

    @Test func savesTheme() {
        let prefs = UserPreferences(defaults: defaults)
        prefs.theme = .dark
        #expect(defaults.string(forKey: "theme") == "dark")
    }
}
```

### Range Confirmations (Swift 6.1+)

```swift
@Test func analyticsEventsInRange() async {
    await confirmation(expectedCount: 5...10) { confirm in
        tracker.onEvent = { _ in confirm() }
        await controller.performBatchOperation()
    }
}
```

---

## Mock Service Patterns

### Simple Mock

```swift
actor MockPostService: PostServiceProtocol {
    var mockPosts: [Post] = []

    func fetchPosts(userId: String) async throws -> [Post] {
        return mockPosts
    }

    func setPosts(_ posts: [Post]) {
        mockPosts = posts
    }
}

// Test
@Test func postLoading() async {
    let mockService = MockPostService()
    await mockService.setPosts([
        Post(id: "1", title: "Test Post", body: "Test body", authorId: "user1")
    ])

    let controller = PostController(service: mockService)
    await controller.loadPosts(userId: "user1")

    #expect(controller.posts.count == 1)
    #expect(controller.posts.first?.title == "Test Post")
}
```

### Configurable Mock

```swift
actor MockNetworkService: NetworkServiceProtocol {
    var shouldFail = false
    var errorToThrow: Error = NetworkError.noData
    var delayMilliseconds: Int = 0
    var responseData: [String: Any] = [:]

    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        if delayMilliseconds > 0 {
            try? await Task.sleep(for: .milliseconds(delayMilliseconds))
        }

        if shouldFail {
            throw errorToThrow
        }

        // Return mock data
        let data = try JSONSerialization.data(withJSONObject: responseData)
        return try JSONDecoder().decode(T.self, from: data)
    }

    func setShouldFail(_ fail: Bool) { shouldFail = fail }
    func setError(_ error: Error) { errorToThrow = error }
}
```

### Call Tracking Mock

```swift
actor MockUserService: UserServiceProtocol {
    var fetchUserCallCount = 0
    var lastFetchedUserId: String?
    var mockUser: User?
    var shouldFail = false

    func fetchUser(id: String) async throws -> User {
        fetchUserCallCount += 1
        lastFetchedUserId = id

        if shouldFail { throw NetworkError.noData }
        guard let user = mockUser else { throw NetworkError.noData }
        return user
    }

    func setMockUser(_ user: User) { mockUser = user }
    func setShouldFail(_ fail: Bool) { shouldFail = fail }

    func reset() {
        fetchUserCallCount = 0
        lastFetchedUserId = nil
        mockUser = nil
        shouldFail = false
    }
}

// Test
@Test func serviceCalledOnce() async {
    let mockService = MockUserService()
    await mockService.setMockUser(User(id: "1", name: "Test", email: "test@test.com"))

    let controller = UserController(service: mockService)
    await controller.loadUser(id: "123")

    let callCount = await mockService.fetchUserCallCount
    let lastId = await mockService.lastFetchedUserId

    #expect(callCount == 1)
    #expect(lastId == "123")
}
```

---

## Testing Controllers

### Test Loading State

```swift
@Test func loadingState() async {
    let mockService = MockUserService()
    await mockService.setDelay(500)
    let controller = UserController(service: mockService)

    let loadTask = Task {
        await controller.loadUser(id: "1")
    }

    try? await Task.sleep(for: .milliseconds(50))
    #expect(controller.isLoading == true)

    await loadTask.value
    #expect(controller.isLoading == false)
}
```

### Test Task Cancellation

```swift
@Test func taskCancellation() async {
    let mockService = MockUserService()
    await mockService.setDelay(500)
    let controller = UserController(service: mockService)

    let firstTask = Task {
        await controller.loadUser(id: "1")
    }

    try? await Task.sleep(for: .milliseconds(50))
    let secondTask = Task {
        await controller.loadUser(id: "2")
    }

    await firstTask.value
    await secondTask.value

    let lastId = await mockService.lastFetchedUserId
    #expect(lastId == "2")
}
```

---

## Testing Models

Models are simple structs - test computed properties:

```swift
@Test func userDisplayName() {
    let userWithName = User(id: "1", name: "Alice", email: "alice@test.com")
    #expect(userWithName.displayName == "Alice")

    let userWithoutName = User(id: "2", name: "", email: "bob@test.com")
    #expect(userWithoutName.displayName == "bob@test.com")
}

@Test func orderTotal() {
    let items = [
        Item(id: "1", price: 10.0),
        Item(id: "2", price: 20.0)
    ]
    let order = Order(items: items, taxRate: 0.1)

    #expect(order.subtotal == 30.0)
    #expect(order.tax == 3.0)
    #expect(order.total == 33.0)
}

// Float tolerance
@Test func distanceCalculation() {
    let result = calculateDistance(from: pointA, to: pointB)
    #expect(result.isApproximatelyEqual(to: 5.385, absoluteTolerance: 0.001))
}

@Test func formValidation() {
    let validForm = SignUpForm(
        email: "test@test.com",
        password: "password123",
        confirmPassword: "password123"
    )
    #expect(validForm.isValid == true)

    let invalidEmail = SignUpForm(
        email: "invalid",
        password: "password123",
        confirmPassword: "password123"
    )
    #expect(invalidEmail.isValid == false)
}
```

---

## Test Organization

### Group Tests by Feature

```swift
struct UserControllerTests {
    let mockService: MockUserService
    let controller: UserController

    init() {
        mockService = MockUserService()
        controller = UserController(service: mockService)
    }

    @Test func loadUser() async { }
    @Test func loadUserError() async { }
    @Test func loadUserCancellation() async { }
}
```

### Nested Suites for Sub-Features

```swift
struct ProfileTests {
    @Suite("Avatar Management")
    struct AvatarTests {
        @Test func uploadAvatar() async { }
        @Test func deleteAvatar() async { }
    }

    @Suite("Settings")
    struct SettingsTests {
        @Test func updateNotifications() async { }
        @Test func changePassword() async { }
    }
}
```

---

## Best Practices

### DO

1. **Test business logic, not implementation**
```swift
// GOOD - Test outcome
#expect(controller.user?.name == "Alice")

// BAD - Test implementation detail
#expect(await mockService.fetchUserCallCount == 1)
```

2. **Use descriptive test names**
```swift
// GOOD - human-readable string or backtick name
@Test("sets user property on successful load")
func loadUserSuccess() async { }

@Test func `loading user sets user property on success`() async { }

// BAD
@Test func testLoadUser() async { }
```

3. **Arrange-Act-Assert pattern**
```swift
@Test func example() async {
    // Arrange
    let mockService = MockUserService()
    let controller = UserController(service: mockService)

    // Act
    await controller.loadUser(id: "123")

    // Assert
    #expect(controller.user != nil)
}
```

4. **Test edge cases**
```swift
@Test func emptyList() async { }
@Test func networkError() async { }
@Test func cancellation() async { }
```

### DON'T

1. **Don't test SwiftUI views directly** - test Controllers
2. **Don't make tests depend on each other** - each test creates its own state
3. **Don't use `test` prefix** - Swift Testing discovers `@Test`, not name prefixes
4. **Don't add `@Suite` to every struct** - it is implicit for types containing `@Test`
5. **Don't use `!` in `#expect`** - write `#expect(value == false)` instead of `#expect(!value)`
6. **Don't use `.serialized` on non-parameterized tests** - it has no effect
7. **Don't use `.seconds()` with `.timeLimit`** - only `.minutes()` exists

---

## XCTest Legacy / Migration Guide

XCTest is still required for **UI tests** (XCUITest). Do NOT migrate UI tests to Swift Testing. For unit tests, migrate to Swift Testing following this order:

### Migration Order

1. **Structure first** - Convert `XCTestCase` classes to structs, `setUp`/`tearDown` to `init`/`deinit`
2. **Parameterized tests** - Convert repeated test methods to `@Test(arguments:)`
3. **Preconditions** - Replace `XCTUnwrap` and guard assertions with `#require`
4. **Traits** - Replace `XCTSkipIf`/`XCTSkipUnless` with `.disabled` or `.enabled` traits

### XCTest Equivalents

| XCTest | Swift Testing |
|--------|---------------|
| `XCTestCase` class | Plain struct |
| `func testFoo()` | `@Test func foo()` |
| `setUp()` / `tearDown()` | `init()` / `deinit` |
| `XCTAssert(expr)` | `#expect(expr)` |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` |
| `XCTAssertNil(expr)` | `#expect(expr == nil)` |
| `XCTAssertNotNil(expr)` | `#expect(expr != nil)` |
| `XCTAssertTrue(expr)` | `#expect(expr == true)` |
| `XCTAssertFalse(expr)` | `#expect(expr == false)` |
| `XCTAssertThrowsError` | `#expect(throws: SomeError.self) { }` |
| `XCTUnwrap(expr)` | `try #require(expr)` |
| `XCTSkipIf(cond)` | `@Test(.enabled(if: !cond))` |
| `XCTFail("msg")` | `Issue.record("msg")` |
| `XCTAssertEqual(a, b, accuracy:)` | `a.isApproximatelyEqual(to: b, absoluteTolerance:)` |

### XCTest Pattern (for UI tests only)

```swift
// UI tests MUST remain in XCTest
final class UserFlowUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        app.launch()
    }

    override func tearDown() {
        app = nil
        super.tearDown()
    }

    func testLoginFlow() {
        app.textFields["Email"].tap()
        app.textFields["Email"].typeText("test@test.com")
        // ...
    }
}
```

---

*Swift Testing patterns inspired by Paul Hudson's Swift Testing Pro and Apple's Testing framework documentation.*
