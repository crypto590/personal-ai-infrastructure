# ViewModel Patterns

Detailed patterns for implementing ViewModels in SwiftUI applications.

## Basic ViewModel Structure

```swift
@Observable
class FeatureViewModel {
    // MARK: - Published State
    var items: [Item] = []
    var isLoading = false
    var errorMessage: String?
    
    // MARK: - Dependencies
    private let service: FeatureService
    
    // MARK: - Initialization
    init(service: FeatureService) {
        self.service = service
    }
    
    // MARK: - Public API
    func loadItems() async {
        isLoading = true
        errorMessage = nil
        
        do {
            items = try await service.fetchItems()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func deleteItem(_ item: Item) async throws {
        try await service.delete(item)
        items.removeAll { $0.id == item.id }
    }
}
```

## State Management Patterns

### Loading States

Use clear boolean flags for UI states:

```swift
@Observable
class DataViewModel {
    var data: [Item] = []
    var isLoading = false
    var isRefreshing = false  // Different from initial load
    
    func initialLoad() async {
        guard !isLoading else { return }  // Prevent duplicate loads
        isLoading = true
        await fetchData()
        isLoading = false
    }
    
    func refresh() async {
        guard !isRefreshing else { return }
        isRefreshing = true
        await fetchData()
        isRefreshing = false
    }
}
```

### Error Handling

**Pattern 1: Error message string** (simple cases)
```swift
@Observable
class SimpleViewModel {
    var errorMessage: String?
    
    func performAction() async {
        do {
            try await service.doSomething()
            errorMessage = nil  // Clear on success
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

**Pattern 2: Error state enum** (complex error handling)
```swift
enum LoadingState {
    case idle
    case loading
    case loaded([Item])
    case error(Error)
}

@Observable
class ViewModel {
    var state: LoadingState = .idle
    
    func load() async {
        state = .loading
        do {
            let items = try await service.fetch()
            state = .loaded(items)
        } catch {
            state = .error(error)
        }
    }
}
```

### Validation

Keep validation logic in ViewModels:

```swift
@Observable
class SignUpViewModel {
    var email = ""
    var password = ""
    var confirmPassword = ""
    
    var emailError: String? {
        guard !email.isEmpty else { return nil }
        return email.contains("@") ? nil : "Invalid email"
    }
    
    var passwordError: String? {
        guard !password.isEmpty else { return nil }
        return password.count >= 8 ? nil : "Password must be at least 8 characters"
    }
    
    var confirmPasswordError: String? {
        guard !confirmPassword.isEmpty else { return nil }
        return password == confirmPassword ? nil : "Passwords don't match"
    }
    
    var isValid: Bool {
        emailError == nil && 
        passwordError == nil && 
        confirmPasswordError == nil &&
        !email.isEmpty &&
        !password.isEmpty
    }
}
```

## Coordination Patterns

### Parent-Child ViewModels

When a view contains sub-features:

```swift
@Observable
class DashboardViewModel {
    let profileViewModel: ProfileViewModel
    let notificationsViewModel: NotificationsViewModel
    
    init(
        profileViewModel: ProfileViewModel,
        notificationsViewModel: NotificationsViewModel
    ) {
        self.profileViewModel = profileViewModel
        self.notificationsViewModel = notificationsViewModel
    }
    
    func refreshAll() async {
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.profileViewModel.refresh() }
            group.addTask { await self.notificationsViewModel.refresh() }
        }
    }
}
```

### Navigation State

ViewModels can manage navigation:

```swift
@Observable
class ListViewModel {
    var selectedItem: Item?
    var isPresentingDetail = false
    
    func selectItem(_ item: Item) {
        selectedItem = item
        isPresentingDetail = true
    }
    
    func dismissDetail() {
        isPresentingDetail = false
        selectedItem = nil
    }
}

// In View:
.sheet(isPresented: $viewModel.isPresentingDetail) {
    if let item = viewModel.selectedItem {
        DetailView(item: item)
    }
}
```

## Testing ViewModels

### Mock Dependencies

```swift
class MockAuthService: AuthenticationService {
    var shouldSucceed = true
    var mockUser: User?
    
    override func login(email: String, password: String) async throws -> User {
        if shouldSucceed {
            let user = User(id: "123", email: email)
            mockUser = user
            return user
        } else {
            throw AuthError.invalidCredentials
        }
    }
}

func testLoginSuccess() async throws {
    let mockAuth = MockAuthService()
    mockAuth.shouldSucceed = true
    
    let viewModel = LoginViewModel(authService: mockAuth)
    viewModel.email = "test@example.com"
    viewModel.password = "password123"
    
    await viewModel.login()
    
    XCTAssertNil(viewModel.errorMessage)
    XCTAssertNotNil(mockAuth.mockUser)
}
```

### Testing Async Operations

```swift
func testDataLoading() async throws {
    let mockService = MockDataService()
    mockService.mockData = [Item(id: "1", name: "Test")]
    
    let viewModel = DataViewModel(service: mockService)
    
    await viewModel.loadData()
    
    XCTAssertEqual(viewModel.items.count, 1)
    XCTAssertFalse(viewModel.isLoading)
    XCTAssertNil(viewModel.errorMessage)
}
```

## Common Patterns

### Debounced Search

```swift
@Observable
class SearchViewModel {
    var searchText = "" {
        didSet {
            searchTask?.cancel()
            searchTask = Task {
                try? await Task.sleep(nanoseconds: 300_000_000)  // 300ms debounce
                await performSearch()
            }
        }
    }
    var results: [Item] = []
    
    private var searchTask: Task<Void, Never>?
    
    private func performSearch() async {
        guard !searchText.isEmpty else {
            results = []
            return
        }
        
        do {
            results = try await service.search(query: searchText)
        } catch {
            results = []
        }
    }
}
```

### Pagination

```swift
@Observable
class PaginatedViewModel {
    var items: [Item] = []
    var isLoading = false
    var hasMorePages = true
    
    private var currentPage = 0
    private let pageSize = 20
    
    func loadNextPage() async {
        guard !isLoading, hasMorePages else { return }
        
        isLoading = true
        do {
            let newItems = try await service.fetchPage(currentPage, size: pageSize)
            items.append(contentsOf: newItems)
            currentPage += 1
            hasMorePages = newItems.count == pageSize
        } catch {
            // Handle error
        }
        isLoading = false
    }
    
    func refresh() async {
        currentPage = 0
        items = []
        hasMorePages = true
        await loadNextPage()
    }
}
```

### Optimistic Updates

```swift
@Observable
class TodoViewModel {
    var todos: [Todo] = []
    
    func toggleComplete(_ todo: Todo) async {
        // Optimistic update
        if let index = todos.firstIndex(where: { $0.id == todo.id }) {
            todos[index].isComplete.toggle()
        }
        
        // Sync with backend
        do {
            try await service.updateTodo(todo)
        } catch {
            // Rollback on failure
            if let index = todos.firstIndex(where: { $0.id == todo.id }) {
                todos[index].isComplete.toggle()
            }
            // Show error
        }
    }
}
```

## ViewModel Lifecycle

### Initialization

```swift
@Observable
class ViewModel {
    var data: [Item] = []
    
    private let service: DataService
    
    init(service: DataService) {
        self.service = service
    }
    
    // Don't do async work in init - call from .task modifier instead
}

// In View:
struct ContentView: View {
    @State private var viewModel: ViewModel
    
    var body: some View {
        // ...
    }
    .task {
        await viewModel.loadInitialData()  // Load data when view appears
    }
}
```

### Cleanup

```swift
@Observable
class StreamingViewModel {
    var messages: [Message] = []
    
    private var streamTask: Task<Void, Never>?
    
    func startListening() {
        streamTask = Task {
            for await message in service.messageStream() {
                messages.append(message)
            }
        }
    }
    
    func stopListening() {
        streamTask?.cancel()
        streamTask = nil
    }
}

// In View:
.onDisappear {
    viewModel.stopListening()
}
```

## Best Practices Summary

1. **Keep ViewModels UI-framework independent** - No SwiftUI imports
2. **Inject all dependencies** - Don't create them internally
3. **Use @Observable** - Modern SwiftUI state management
4. **Handle all business logic** - Keep views focused on UI
5. **Expose simple properties** - Views should just read/bind
6. **Test in isolation** - Mock dependencies for unit tests
7. **One ViewModel per feature** - Don't create massive god objects
8. **Clear loading states** - Use explicit boolean flags
9. **Graceful error handling** - Always provide user-facing error messages
10. **Clean async patterns** - Use Swift's async/await properly
