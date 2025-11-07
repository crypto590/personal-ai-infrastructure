# Controllers (Observable Classes)

**Referenced from**: [SKILL.md](SKILL.md)

**Related**:
- [SERVICES.md](SERVICES.md) - Services that Controllers coordinate
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling in Controllers
- [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md) - Composition and shared Controllers

---

## Overview

Controllers manage UI state and coordinate service calls. They are the glue between Views (presentation) and Services (infrastructure).

**Key characteristics:**
- Always `@Observable @MainActor final class`
- Properties are `private(set)` (read-only from Views)
- Protocol-based service injection for testability
- Track and cancel async tasks properly
- No SwiftUI-specific dependencies (no `@Environment` except for shared controllers)

---

## Basic Controller Pattern

```swift
@Observable
@MainActor
final class UserController {
    // MARK: - Properties
    private(set) var user: User?
    private(set) var isLoading = false

    // MARK: - Dependencies
    private let service: UserServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    // MARK: - Methods
    func loadUser(id: String) async {
        loadTask?.cancel()

        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                user = try await service.fetchUser(id: id)
            } catch {
                if !Task.isCancelled {
                    // Handle error (see ERROR_HANDLING.md)
                }
            }
        }

        await loadTask?.value
    }

    deinit {
        loadTask?.cancel()
    }
}
```

---

## Production Checklist

Every production Controller must have:

### Required Attributes
- ✅ `@Observable` - Makes properties observable by SwiftUI
- ✅ `@MainActor` - Ensures all mutations happen on main thread
- ✅ `final class` - Prevents inheritance, enables optimizations

### Required Property Patterns
- ✅ `private(set)` on all published properties
  - Views can read, but cannot mutate
  - Enforces unidirectional data flow

### Required Dependencies
- ✅ Protocol-based service injection
  - Never depend on concrete service implementations
  - Enables testing with mocks

### Required Task Management
- ✅ Task tracking: `private var loadTask: Task<Void, Never>?`
  - Store reference to ongoing tasks
  - Enables cancellation

- ✅ Cancel previous tasks before starting new ones
  ```swift
  loadTask?.cancel()
  loadTask = Task { ... }
  ```

- ✅ Cancel check: `if !Task.isCancelled`
  - Prevents setting error state after cancellation
  - Avoids unnecessary UI updates

- ✅ Cleanup: `deinit { loadTask?.cancel() }`
  - Prevents memory leaks
  - Stops work when controller is deallocated

### Forbidden Patterns
- ❌ Never use `@Environment` in Controllers (except for shared controllers)
- ❌ Never make properties publicly settable
- ❌ Never depend on concrete service implementations
- ❌ Never skip task cancellation

---

## Task Cancellation Discipline

Task cancellation is critical for memory safety and performance.

### Pattern 1: Cancel and Replace

```swift
private var loadTask: Task<Void, Never>?

func loadData() async {
    // Cancel previous task if still running
    loadTask?.cancel()

    loadTask = Task {
        isLoading = true
        defer { isLoading = false }

        do {
            data = try await service.fetchData()
        } catch {
            // Only set error if task wasn't cancelled
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }

    await loadTask?.value
}
```

**Why this matters:**
- User types in search box → triggers loadData()
- User types again → cancels previous search, starts new one
- Prevents race conditions and wasted work

### Pattern 2: Multiple Tasks

```swift
private var loadTask: Task<Void, Never>?
private var refreshTask: Task<Void, Never>?

func load() async {
    loadTask?.cancel()
    loadTask = Task { /* ... */ }
    await loadTask?.value
}

func refresh() async {
    refreshTask?.cancel()
    refreshTask = Task { /* ... */ }
    await refreshTask?.value
}

deinit {
    loadTask?.cancel()
    refreshTask?.cancel()
}
```

**When to use:**
- Controller has multiple independent async operations
- Each operation can be cancelled independently

### Pattern 3: Check Cancellation Before State Updates

```swift
loadTask = Task {
    isLoading = true
    defer { isLoading = false }

    do {
        let result = try await service.fetch()

        // Check cancellation before setting success state
        if !Task.isCancelled {
            data = result
        }
    } catch {
        // Check cancellation before setting error state
        if !Task.isCancelled {
            errorMessage = error.localizedDescription
        }
    }
}
```

**Why this matters:**
- Prevents setting state after View is dismissed
- Avoids unnecessary UI updates
- Prevents confusing error messages

---

## State Management

### Loading States

```swift
@Observable
@MainActor
final class DataController {
    private(set) var isLoading = false
    private(set) var data: [Item] = []
    private(set) var errorMessage: String?

    func load() async {
        isLoading = true
        errorMessage = nil  // Clear previous error
        defer { isLoading = false }

        do {
            data = try await service.fetchData()
        } catch {
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }
}
```

**Pattern:**
- Set `isLoading = true` at start
- Use `defer` to ensure it's set to `false`
- Clear previous errors before loading

### Computed Properties

```swift
@Observable
@MainActor
final class SearchController {
    private(set) var query: String = ""
    private(set) var results: [Item] = []
    private(set) var isLoading = false

    // Computed property for derived state
    var isEmpty: Bool {
        !isLoading && results.isEmpty && !query.isEmpty
    }

    var shouldShowResults: Bool {
        !isLoading && !results.isEmpty
    }

    func updateQuery(_ newQuery: String) {
        query = newQuery
    }
}
```

**When to use computed properties:**
- Derived state based on existing properties
- Avoids storing redundant state
- Automatically updates when dependencies change

### Mutable Private State

```swift
@Observable
@MainActor
final class FormController {
    // Public read-only
    private(set) var isValid = false

    // Private mutable
    private var name: String = ""
    private var email: String = ""

    // Public mutators
    func updateName(_ newName: String) {
        name = newName
        validateForm()
    }

    func updateEmail(_ newEmail: String) {
        email = newEmail
        validateForm()
    }

    private func validateForm() {
        isValid = !name.isEmpty && email.contains("@")
    }
}
```

**Pattern:**
- Keep raw form data private
- Expose only validation state publicly
- Provide explicit mutator methods

---

## Service Coordination

### Single Service

```swift
@Observable
@MainActor
final class ProfileController {
    private(set) var user: User?

    private let userService: UserServiceProtocol

    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }

    func loadProfile(id: String) async {
        do {
            user = try await userService.fetchUser(id: id)
        } catch {
            // Handle error
        }
    }
}
```

### Multiple Services

```swift
@Observable
@MainActor
final class DashboardController {
    private(set) var user: User?
    private(set) var posts: [Post] = []

    private let userService: UserServiceProtocol
    private let postService: PostServiceProtocol

    init(
        userService: UserServiceProtocol = UserService(),
        postService: PostServiceProtocol = PostService()
    ) {
        self.userService = userService
        self.postService = postService
    }

    func load(userId: String) async {
        async let user = userService.fetchUser(id: userId)
        async let posts = postService.fetchPosts(userId: userId)

        do {
            self.user = try await user
            self.posts = try await posts
        } catch {
            // Handle error
        }
    }
}
```

**Pattern:**
- Use `async let` for parallel fetching
- Both requests start simultaneously
- Wait for both with `try await`

### Sequential Dependencies

```swift
func loadUserAndPosts() async {
    do {
        // Load user first
        let user = try await userService.fetchUser(id: "123")
        self.user = user

        // Then load posts using user data
        let posts = try await postService.fetchPosts(userId: user.id)
        self.posts = posts
    } catch {
        // Handle error
    }
}
```

**When to use:**
- Second operation depends on result of first
- Cannot parallelize

---

## Protocol-Based Dependency Injection

### Why Protocols?

```swift
// ❌ BAD: Concrete dependency
final class UserController {
    private let service = UserService()  // Hard to test!
}

// ✅ GOOD: Protocol dependency
final class UserController {
    private let service: UserServiceProtocol

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }
}
```

**Benefits:**
- Testable with mock services
- Swappable implementations
- Clear contracts

### Testing with Protocols

```swift
// Production
let controller = UserController()  // Uses default UserService()

// Testing
let mockService = MockUserService()
let controller = UserController(service: mockService)
```

See [TESTING.md](TESTING.md) for complete testing patterns.

---

## Common Patterns

### Refresh Pattern

```swift
@Observable
@MainActor
final class ListController {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    private(set) var isRefreshing = false

    private var loadTask: Task<Void, Never>?

    func load() async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                items = try await service.fetchItems()
            } catch {
                if !Task.isCancelled {
                    // Handle error
                }
            }
        }
        await loadTask?.value
    }

    func refresh() async {
        loadTask?.cancel()
        loadTask = Task {
            isRefreshing = true
            defer { isRefreshing = false }

            do {
                items = try await service.fetchItems()
            } catch {
                if !Task.isCancelled {
                    // Handle error
                }
            }
        }
        await loadTask?.value
    }
}
```

**Usage in View:**
```swift
List(controller.items) { item in
    Text(item.name)
}
.refreshable {
    await controller.refresh()
}
.task {
    await controller.load()
}
```

### Pagination Pattern

```swift
@Observable
@MainActor
final class PaginatedListController {
    private(set) var items: [Item] = []
    private(set) var isLoading = false
    private(set) var isLoadingMore = false
    private(set) var hasMore = true

    private var currentPage = 0
    private var loadTask: Task<Void, Never>?

    func load() async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            currentPage = 0
            defer { isLoading = false }

            do {
                let page = try await service.fetchPage(page: currentPage)
                items = page.items
                hasMore = page.hasMore
            } catch {
                if !Task.isCancelled {
                    // Handle error
                }
            }
        }
        await loadTask?.value
    }

    func loadMore() async {
        guard !isLoadingMore && hasMore else { return }

        loadTask?.cancel()
        loadTask = Task {
            isLoadingMore = true
            defer { isLoadingMore = false }

            do {
                currentPage += 1
                let page = try await service.fetchPage(page: currentPage)
                items.append(contentsOf: page.items)
                hasMore = page.hasMore
            } catch {
                if !Task.isCancelled {
                    currentPage -= 1  // Revert on error
                    // Handle error
                }
            }
        }
        await loadTask?.value
    }
}
```

### Search/Debounce Pattern

```swift
@Observable
@MainActor
final class SearchController {
    private(set) var query: String = ""
    private(set) var results: [Item] = []
    private(set) var isSearching = false

    private var searchTask: Task<Void, Never>?

    func updateQuery(_ newQuery: String) {
        query = newQuery
        performSearch()
    }

    private func performSearch() {
        searchTask?.cancel()

        guard !query.isEmpty else {
            results = []
            return
        }

        searchTask = Task {
            // Debounce: wait before searching
            try? await Task.sleep(for: .milliseconds(300))

            guard !Task.isCancelled else { return }

            isSearching = true
            defer { isSearching = false }

            do {
                results = try await service.search(query: query)
            } catch {
                if !Task.isCancelled {
                    // Handle error
                }
            }
        }
    }

    deinit {
        searchTask?.cancel()
    }
}
```

**Why debounce:**
- User types "hello"
- Cancels searches for "h", "he", "hel", "hell"
- Only searches for "hello"
- Reduces API calls

---

## Anti-Patterns

### ❌ Public Mutable Properties

```swift
// ❌ BAD
@Observable
@MainActor
final class UserController {
    var user: User?  // View can mutate this!
}

// ✅ GOOD
@Observable
@MainActor
final class UserController {
    private(set) var user: User?  // View can only read
}
```

### ❌ Not Cancelling Tasks

```swift
// ❌ BAD
func load() async {
    // Never cancels previous task!
    loadTask = Task {
        data = try await service.fetch()
    }
}

// ✅ GOOD
func load() async {
    loadTask?.cancel()  // Cancel previous
    loadTask = Task {
        data = try await service.fetch()
    }
}
```

### ❌ Missing Cancellation Checks

```swift
// ❌ BAD
} catch {
    errorMessage = error.localizedDescription  // Even if cancelled!
}

// ✅ GOOD
} catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}
```

### ❌ Concrete Service Dependencies

```swift
// ❌ BAD
final class UserController {
    private let service = UserService()  // Can't test!
}

// ✅ GOOD
final class UserController {
    private let service: UserServiceProtocol

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }
}
```

### ❌ Using @Environment in Controllers

```swift
// ❌ BAD
@Observable
@MainActor
final class FeatureController {
    @Environment(\.dismiss) var dismiss  // SwiftUI dependency!
}

// ✅ GOOD - Controllers don't use @Environment
// Instead, expose methods and let View handle SwiftUI specifics
@Observable
@MainActor
final class FeatureController {
    private(set) var shouldDismiss = false

    func complete() {
        shouldDismiss = true
    }
}

// View handles dismiss
struct FeatureView: View {
    @Environment(\.dismiss) var dismiss
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .onChange(of: controller.shouldDismiss) { _, shouldDismiss in
                if shouldDismiss {
                    dismiss()
                }
            }
    }
}
```

**Exception**: Shared controllers CAN be injected via @Environment.
See [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md#shared-controllers).

---

## When to Split Controllers

Split a Controller when it:
- Exceeds ~200 lines
- Manages multiple independent concerns
- Has multiple distinct async operations

See [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md#controller-composition) for composition patterns.

---

## Related

- [SERVICES.md](SERVICES.md) - Services that Controllers coordinate
- [VIEWS.md](VIEWS.md) - How Views interact with Controllers
- [ERROR_HANDLING.md](ERROR_HANDLING.md) - Error handling patterns
- [TESTING.md](TESTING.md) - Testing Controllers with mock services
- [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md) - Composition and shared Controllers
- [EXAMPLES.md](EXAMPLES.md) - Real-world Controller examples
