# Quick Reference

**Referenced from**: [SKILL.md](SKILL.md)

---

## Decision Trees

### What Layer Do I Need?

```
What are you building?

Data structure with business logic
└─> Create Model (struct with computed properties)

Async operation (API, database, SDK)
└─> Create Service (actor or struct protocol)

UI state management or service coordination
└─> Create Controller (@Observable class)

Display UI or handle user input
└─> Create View (SwiftUI, delegates to Controller)
```

### Actor vs Struct for Services?

```
Is the service performing async operations?
├─ YES → Use ACTOR
└─ NO → Is it a pure function or utility?
    └─ YES → Use STRUCT with static methods
```

---

## Code Templates

### Model Template

```swift
struct MyModel: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let createdAt: Date

    var displayName: String {
        // Computed property for business logic
        name.isEmpty ? "Unnamed" : name
    }
}
```

### Service Template (Actor)

```swift
protocol MyServiceProtocol {
    func fetchData(id: String) async throws -> MyModel
}

actor MyService: MyServiceProtocol {
    func fetchData(id: String) async throws -> MyModel {
        // Async implementation
        try await URLSession.shared.data(from: url)
        // ...
    }
}
```

### Service Template (Struct)

```swift
protocol ValidationServiceProtocol {
    static func isValid(_ input: String) -> Bool
}

struct ValidationService: ValidationServiceProtocol {
    static func isValid(_ input: String) -> Bool {
        // Pure function implementation
        !input.isEmpty
    }
}
```

### Controller Template

```swift
@Observable
@MainActor
final class MyController {
    // MARK: - Properties
    private(set) var data: MyModel?
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    // MARK: - Dependencies
    private let service: MyServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: MyServiceProtocol = MyService()) {
        self.service = service
    }

    // MARK: - Methods
    func loadData(id: String) async {
        loadTask?.cancel()

        loadTask = Task {
            isLoading = true
            errorMessage = nil
            defer { isLoading = false }

            do {
                data = try await service.fetchData(id: id)
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }

        await loadTask?.value
    }

    func clearError() {
        errorMessage = nil
    }

    deinit {
        loadTask?.cancel()
    }
}
```

### View Template

```swift
struct MyView: View {
    @State private var controller = MyController()

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView()
            } else if let data = controller.data {
                ContentView(data: data)
            } else {
                Text("No data")
            }
        }
        .task {
            await controller.loadData(id: "123")
        }
        .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
            Button("OK") { controller.clearError() }
        } message: {
            Text(controller.errorMessage ?? "")
        }
    }
}
```

---

## Common Patterns

### Loading State

```swift
// Controller
private(set) var isLoading = false

func load() async {
    isLoading = true
    defer { isLoading = false }
    // ... async work
}

// View
if controller.isLoading {
    ProgressView()
}
```

### Error Handling

```swift
// Controller
private(set) var errorMessage: String?

do {
    // ... async work
} catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}

func clearError() {
    errorMessage = nil
}

// View
.alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
    Button("OK") { controller.clearError() }
} message: {
    Text(controller.errorMessage ?? "")
}
```

### Form Input

```swift
// Controller
private(set) var email = ""

func updateEmail(_ newEmail: String) {
    email = newEmail
    validate()
}

// View
TextField("Email", text: Binding(
    get: { controller.email },
    set: { controller.updateEmail($0) }
))
```

### Navigation

```swift
// Controller
private(set) var navigationDestination: Destination?

enum Destination: Hashable {
    case detail(id: String)
}

func navigate(to destination: Destination) {
    navigationDestination = destination
}

// View
.navigationDestination(for: MyController.Destination.self) { dest in
    switch dest {
    case .detail(let id): DetailView(id: id)
    }
}
.onChange(of: controller.navigationDestination) { _, new in
    if let destination = new {
        path.append(destination)
        controller.clearNavigation()
    }
}
```

### Modal Sheet

```swift
// Controller
private(set) var sheet: Sheet?

enum Sheet: Identifiable {
    case edit(Item)

    var id: String {
        switch self {
        case .edit(let item): return "edit-\(item.id)"
        }
    }
}

func showEdit(_ item: Item) {
    sheet = .edit(item)
}

// View
.sheet(item: $controller.sheet) { sheet in
    switch sheet {
    case .edit(let item): EditView(item: item)
    }
}
```

### Pagination

```swift
// Controller
private(set) var items: [Item] = []
private(set) var hasMore = true
private var currentPage = 0

func loadMore() async {
    guard !isLoadingMore && hasMore else { return }

    currentPage += 1
    let page = try await service.fetchPage(page: currentPage)
    items.append(contentsOf: page.items)
    hasMore = page.hasMore
}

// View
.onAppear {
    if item == controller.items.last && controller.hasMore {
        Task { await controller.loadMore() }
    }
}
```

### Search with Debounce

```swift
// Controller
private(set) var query = ""
private var searchTask: Task<Void, Never>?

func updateQuery(_ newQuery: String) {
    query = newQuery
    performSearch()
}

private func performSearch() {
    searchTask?.cancel()
    guard !query.isEmpty else { return }

    searchTask = Task {
        try? await Task.sleep(for: .milliseconds(300))
        guard !Task.isCancelled else { return }
        // ... perform search
    }
}

// View
TextField("Search", text: Binding(
    get: { controller.query },
    set: { controller.updateQuery($0) }
))
```

---

## Production Checklist

### Controller

- [ ] `@Observable @MainActor final class`
- [ ] All properties are `private(set)`
- [ ] Protocol-based service injection
- [ ] Task tracking: `private var loadTask: Task<Void, Never>?`
- [ ] Cancel check: `if !Task.isCancelled`
- [ ] Cleanup: `deinit { loadTask?.cancel() }`

### Service

- [ ] `actor` for async operations OR `struct` for pure functions
- [ ] Protocol for testing
- [ ] No stored UI/business state
- [ ] Returns structs
- [ ] Never `class`

### Model

- [ ] `struct` (never `class`)
- [ ] `Codable` for API/persistence
- [ ] `Equatable` for comparisons
- [ ] No async operations
- [ ] No `@Published` or Observable

### View

- [ ] Create Controller with `@State private var`
- [ ] Delegate actions to Controller
- [ ] Never call Services directly
- [ ] Never mutate Controller properties

---

## Anti-Patterns

### ❌ Public Mutable Properties

```swift
// ❌ BAD
@Observable
@MainActor
final class MyController {
    var data: String?  // View can mutate!
}

// ✅ GOOD
@Observable
@MainActor
final class MyController {
    private(set) var data: String?
}
```

### ❌ Not Cancelling Tasks

```swift
// ❌ BAD
func load() async {
    loadTask = Task { ... }  // Never cancels previous!
}

// ✅ GOOD
func load() async {
    loadTask?.cancel()
    loadTask = Task { ... }
}
```

### ❌ Missing Cancellation Checks

```swift
// ❌ BAD
} catch {
    errorMessage = error.localizedDescription
}

// ✅ GOOD
} catch {
    if !Task.isCancelled {
        errorMessage = error.localizedDescription
    }
}
```

### ❌ Concrete Dependencies

```swift
// ❌ BAD
final class MyController {
    private let service = MyService()
}

// ✅ GOOD
final class MyController {
    private let service: MyServiceProtocol

    init(service: MyServiceProtocol = MyService()) {
        self.service = service
    }
}
```

### ❌ View Calls Service

```swift
// ❌ BAD
struct MyView: View {
    @State private var service = MyService()

    Button("Load") {
        Task { await service.fetch() }
    }
}

// ✅ GOOD
struct MyView: View {
    @State private var controller = MyController()

    Button("Load") {
        Task { await controller.load() }
    }
}
```

---

## Layer Summary

| Layer | Type | Role | Example |
|-------|------|------|---------|
| **Model** | `struct` | Immutable data + business logic | `User`, `Post` |
| **Service** | `actor` or `struct` | Async operations or utilities | `UserService`, `ValidationService` |
| **Controller** | `@Observable class` | UI state + coordination | `UserController` |
| **View** | SwiftUI `View` | Render UI + delegate actions | `UserView` |

---

## Common Scenarios

| Scenario | Solution |
|----------|----------|
| Need to fetch data from API | Create Service (actor), Controller coordinates, View displays |
| Validate user input | Create ValidationService (struct), Controller calls it |
| Navigate to another screen | Controller declares destination, View implements navigation |
| Show loading indicator | Controller has `isLoading`, View shows ProgressView |
| Handle errors | Service throws, Controller catches, View displays alert |
| Pagination | Controller tracks page, loads more, View detects scroll |
| Search with debounce | Controller debounces, cancels previous, Service searches |

---

## Related

- [SKILL.md](SKILL.md) - Main skill overview
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
- All detail files for comprehensive patterns
