# Testing

**Referenced from**: [SKILL.md](SKILL.md), [SERVICES.md](SERVICES.md), [CONTROLLERS.md](CONTROLLERS.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Controllers to test
- [SERVICES.md](SERVICES.md) - Service protocols enable testing

---

## Overview

Protocol-based services enable testing without network calls. Test controllers in isolation with mock services.

**Benefits:**
- Fast, deterministic tests
- No network/database required
- Verify business logic in isolation
- Test error handling

---

## Basic Pattern

```swift
// Mock service conforming to protocol
actor MockUserService: UserServiceProtocol {
    var shouldFail = false
    var mockUser = User(id: "test", name: "Test User", email: "test@test.com")

    func fetchUser(id: String) async throws -> User {
        if shouldFail {
            throw NetworkError.noData
        }
        return mockUser
    }
}

// Test with mock
func testUserLoading() async {
    let mockService = MockUserService()
    let controller = UserController(service: mockService)

    await controller.loadUser(id: "123")

    XCTAssertEqual(controller.user?.name, "Test User")
    XCTAssertFalse(controller.isLoading)
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
}

// Test
func testPostLoading() async {
    let mockService = MockPostService()
    await mockService.setPosts([
        Post(id: "1", title: "Test Post", body: "Test body", authorId: "user1")
    ])

    let controller = PostController(service: mockService)
    await controller.loadPosts(userId: "user1")

    XCTAssertEqual(controller.posts.count, 1)
    XCTAssertEqual(controller.posts.first?.title, "Test Post")
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
}

// Test
func testWithDelay() async {
    let mockService = MockNetworkService()
    await mockService.setDelay(500)  // 500ms delay

    let start = Date()
    let controller = DataController(service: mockService)
    await controller.loadData()
    let duration = Date().timeIntervalSince(start)

    XCTAssertGreaterThan(duration, 0.5)
}
```

### Call Tracking Mock

```swift
actor MockUserService: UserServiceProtocol {
    var fetchUserCallCount = 0
    var lastFetchedUserId: String?
    var mockUser: User?

    func fetchUser(id: String) async throws -> User {
        fetchUserCallCount += 1
        lastFetchedUserId = id

        guard let user = mockUser else {
            throw NetworkError.noData
        }

        return user
    }

    func reset() {
        fetchUserCallCount = 0
        lastFetchedUserId = nil
        mockUser = nil
    }
}

// Test
func testServiceCalledOnce() async {
    let mockService = MockUserService()
    mockService.mockUser = User(id: "1", name: "Test", email: "test@test.com")

    let controller = UserController(service: mockService)
    await controller.loadUser(id: "123")

    let callCount = await mockService.fetchUserCallCount
    let lastId = await mockService.lastFetchedUserId

    XCTAssertEqual(callCount, 1)
    XCTAssertEqual(lastId, "123")
}
```

---

## Testing Controllers

### Test Success Case

```swift
func testSuccessfulUserLoad() async {
    // Arrange
    let mockService = MockUserService()
    mockService.mockUser = User(id: "1", name: "Alice", email: "alice@test.com")
    let controller = UserController(service: mockService)

    // Act
    await controller.loadUser(id: "1")

    // Assert
    XCTAssertEqual(controller.user?.name, "Alice")
    XCTAssertEqual(controller.user?.email, "alice@test.com")
    XCTAssertFalse(controller.isLoading)
    XCTAssertNil(controller.errorMessage)
}
```

### Test Error Handling

```swift
func testErrorHandling() async {
    // Arrange
    let mockService = MockUserService()
    mockService.shouldFail = true
    let controller = UserController(service: mockService)

    // Act
    await controller.loadUser(id: "1")

    // Assert
    XCTAssertNil(controller.user)
    XCTAssertFalse(controller.isLoading)
    XCTAssertNotNil(controller.errorMessage)
}
```

### Test Loading State

```swift
func testLoadingState() async {
    // Arrange
    let mockService = MockUserService()
    mockService.delayMilliseconds = 500
    let controller = UserController(service: mockService)

    // Act
    let loadTask = Task {
        await controller.loadUser(id: "1")
    }

    // Assert - loading should be true immediately
    try? await Task.sleep(for: .milliseconds(50))
    XCTAssertTrue(controller.isLoading)

    await loadTask.value

    // Assert - loading should be false after completion
    XCTAssertFalse(controller.isLoading)
}
```

### Test Task Cancellation

```swift
func testTaskCancellation() async {
    // Arrange
    let mockService = MockUserService()
    mockService.delayMilliseconds = 500
    let controller = UserController(service: mockService)

    // Act - start first load
    let firstTask = Task {
        await controller.loadUser(id: "1")
    }

    // Start second load before first completes
    try? await Task.sleep(for: .milliseconds(50))
    let secondTask = Task {
        await controller.loadUser(id: "2")
    }

    await firstTask.value
    await secondTask.value

    // Assert - first load was cancelled, second completed
    XCTAssertEqual(mockService.lastFetchedUserId, "2")
}
```

---

## Testing Models

Models are simple structs - test computed properties:

```swift
func testUserDisplayName() {
    let userWithName = User(id: "1", name: "Alice", email: "alice@test.com")
    XCTAssertEqual(userWithName.displayName, "Alice")

    let userWithoutName = User(id: "2", name: "", email: "bob@test.com")
    XCTAssertEqual(userWithoutName.displayName, "bob@test.com")
}

func testOrderTotal() {
    let items = [
        Item(id: "1", price: 10.0),
        Item(id: "2", price: 20.0)
    ]
    let order = Order(items: items, taxRate: 0.1)

    XCTAssertEqual(order.subtotal, 30.0)
    XCTAssertEqual(order.tax, 3.0)
    XCTAssertEqual(order.total, 33.0)
}

func testFormValidation() {
    let validForm = SignUpForm(
        email: "test@test.com",
        password: "password123",
        confirmPassword: "password123"
    )
    XCTAssertTrue(validForm.isValid)

    let invalidEmail = SignUpForm(
        email: "invalid",
        password: "password123",
        confirmPassword: "password123"
    )
    XCTAssertFalse(invalidEmail.isValid)
}
```

---

## Testing Services

Test real services with integration tests (requires network/database):

```swift
func testRealUserService() async throws {
    let service = UserService()

    let user = try await service.fetchUser(id: "real-user-id")

    XCTAssertNotNil(user)
    XCTAssertFalse(user.name.isEmpty)
}
```

**Note:** These are slower and require infrastructure. Mock services for most tests.

---

## Testing Async Operations

### Using Task

```swift
func testAsyncOperation() async {
    let controller = UserController(service: MockUserService())

    await controller.loadUser(id: "123")

    XCTAssertNotNil(controller.user)
}
```

### Using XCTestExpectation

```swift
func testWithExpectation() {
    let expectation = XCTestExpectation(description: "User loaded")
    let controller = UserController(service: MockUserService())

    Task {
        await controller.loadUser(id: "123")
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 1.0)
    XCTAssertNotNil(controller.user)
}
```

---

## Test Organization

### Group Tests by Feature

```swift
final class UserControllerTests: XCTestCase {
    var mockService: MockUserService!
    var controller: UserController!

    override func setUp() {
        super.setUp()
        mockService = MockUserService()
        controller = UserController(service: mockService)
    }

    override func tearDown() {
        mockService = nil
        controller = nil
        super.tearDown()
    }

    func testLoadUser() async {
        // Test implementation
    }

    func testLoadUserError() async {
        // Test implementation
    }

    func testLoadUserCancellation() async {
        // Test implementation
    }
}
```

---

## Snapshot Testing (Optional)

For UI testing with SwiftUI:

```swift
import SnapshotTesting

func testUserViewSnapshot() {
    let mockService = MockUserService()
    mockService.mockUser = User(id: "1", name: "Alice", email: "alice@test.com")

    let view = UserView(controller: UserController(service: mockService))

    assertSnapshot(matching: view, as: .image)
}
```

---

## Best Practices

### ✅ DO

1. **Test business logic, not implementation**
```swift
// ✅ GOOD - Test outcome
XCTAssertEqual(controller.user?.name, "Alice")

// ❌ BAD - Test implementation detail
XCTAssertEqual(mockService.fetchUserCallCount, 1)
```

2. **Use descriptive test names**
```swift
// ✅ GOOD
func testLoadUserSetsUserPropertyOnSuccess() async { }

// ❌ BAD
func testLoadUser() async { }
```

3. **Arrange-Act-Assert pattern**
```swift
func testExample() async {
    // Arrange
    let mockService = MockUserService()
    let controller = UserController(service: mockService)

    // Act
    await controller.loadUser(id: "123")

    // Assert
    XCTAssertNotNil(controller.user)
}
```

4. **Test edge cases**
```swift
func testEmptyList() async { }
func testNetworkError() async { }
func testCancellation() async { }
```

### ❌ DON'T

1. **Don't test framework code**
```swift
// ❌ BAD - Testing SwiftUI
func testButtonExists() {
    // Don't test that SwiftUI renders buttons
}

// ✅ GOOD - Test your logic
func testButtonActionCallsController() {
    // Test that action triggers controller method
}
```

2. **Don't make tests depend on each other**
```swift
// ❌ BAD
var sharedController: UserController!

func test1() {
    sharedController.loadUser()
}

func test2() {
    // Depends on test1 running first!
}

// ✅ GOOD
func test1() {
    let controller = UserController()
    controller.loadUser()
}

func test2() {
    let controller = UserController()
    // Independent test
}
```

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Controllers to test
- [SERVICES.md](SERVICES.md) - Service protocols
- [MODELS.md](MODELS.md) - Model testing
- [EXAMPLES.md](EXAMPLES.md) - Real-world test examples
