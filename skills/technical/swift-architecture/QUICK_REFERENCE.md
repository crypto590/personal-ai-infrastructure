# Quick Reference Cheat Sheet

Fast lookup guide for common architecture decisions.

## When to Use Each Level

| Scenario | Level | Example |
|----------|-------|---------|
| Toggle, picker, tab selection | 1: @State | Settings screen |
| Form with validation | 2: ViewModel | Sign-up form |
| API call needed | 2: ViewModel | Profile loading |
| Data persistence | 2: ViewModel | Save user preferences |
| Multi-step workflow | 2: ViewModel | Checkout flow |
| Logic shared across screens | 3: Service | Authentication |
| App-wide state | 3: Service | User session |
| External integrations | 3: Service | Location, notifications |

## Code Templates

### Level 1: Simple View

```swift
struct SettingsView: View {
    @State private var isEnabled = false
    
    var body: some View {
        Toggle("Enable", isOn: $isEnabled)
    }
}
```

### Level 2: View + ViewModel

```swift
@Observable
class FeatureViewModel {
    var data: [Item] = []
    var isLoading = false
    var errorMessage: String?
    
    private let service: FeatureService
    
    init(service: FeatureService) {
        self.service = service
    }
    
    func load() async {
        isLoading = true
        do {
            data = try await service.fetch()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}

struct FeatureView: View {
    @State private var viewModel: FeatureViewModel
    
    var body: some View {
        List(viewModel.data) { item in
            Text(item.name)
        }
        .task { await viewModel.load() }
    }
}
```

### Level 3: Service

```swift
@Observable
class AuthenticationService {
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
    
    private let networkService: NetworkServiceProtocol
    
    init(networkService: NetworkServiceProtocol) {
        self.networkService = networkService
    }
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await networkService.post("/auth/login", body: [...])
        currentUser = response.user
    }
}
```

## SOLID Quick Checks

### Single Responsibility
✅ Each class does one thing
❌ A class that handles UI, networking, AND persistence

### Open/Closed
✅ Add new payment methods without changing existing code
❌ Switch statements that grow with new features

### Liskov Substitution
✅ Can swap implementations without breaking behavior
❌ Subclass throws unexpected errors

### Interface Segregation
✅ Small, focused protocols
❌ Protocol with 10+ methods that implementers don't all need

### Dependency Inversion
✅ Inject protocol dependencies
❌ Create concrete dependencies internally

## Common Patterns

### Error Handling

```swift
// Simple: String message
var errorMessage: String?

// Complex: Error state enum
enum State {
    case idle
    case loading
    case loaded([Item])
    case error(Error)
}
```

### Loading States

```swift
var isLoading = false
var isRefreshing = false  // Separate from initial load
```

### Validation

```swift
var emailError: String? {
    guard !email.isEmpty else { return nil }
    return email.contains("@") ? nil : "Invalid email"
}

var isValid: Bool {
    emailError == nil && passwordError == nil
}
```

### Async Operations

```swift
// In ViewModel
func load() async {
    // Async work
}

// In View
.task {
    await viewModel.load()
}
```

### Dependency Injection

```swift
// ✅ Good
init(service: ServiceProtocol) {
    self.service = service
}

// ❌ Bad
init() {
    self.service = ConcreteService()
}
```

## Testing Quick Reference

### Test ViewModels

```swift
func testLoad() async throws {
    let mockService = MockService()
    let viewModel = ViewModel(service: mockService)
    
    await viewModel.load()
    
    XCTAssertEqual(viewModel.data.count, 5)
}
```

### Mock Dependencies

```swift
class MockService: ServiceProtocol {
    var mockData: [Item] = []
    var shouldFail = false
    
    func fetch() async throws -> [Item] {
        if shouldFail { throw TestError() }
        return mockData
    }
}
```

## File Organization

```
YourApp/
├── Views/
│   ├── Feature/
│   │   ├── FeatureView.swift
│   │   └── FeatureViewModel.swift (Level 2)
│   └── SimpleView.swift (Level 1)
├── Services/
│   ├── AuthenticationService.swift
│   ├── NetworkService.swift
│   └── PersistenceService.swift
└── Models/
    └── User.swift
```

## Decision Tree

```
Simple UI state only?
├─ YES → @State in View (Level 1)
└─ NO → Need API, validation, or logic?
    ├─ YES → Add ViewModel (Level 2)
    └─ Logic shared across features?
        ├─ YES → Extract to Service (Level 3)
        └─ NO → Keep in ViewModel
```

## Anti-Patterns

| ❌ Avoid | ✅ Instead |
|---------|----------|
| ViewModels for every view | Only when complexity demands |
| ViewModels importing SwiftUI | Keep framework-independent |
| Massive god ViewModels | Extract to Services |
| Views with business logic | Move to ViewModels |
| Hardcoded dependencies | Inject via initializer |
| Fat protocols (many methods) | Small, focused protocols |

## Common Mistakes

### Premature Optimization
❌ Starting with ViewModels for simple views
✅ Start with @State, add ViewModel when needed

### Over-Engineering
❌ Creating abstractions before you need them
✅ Add layers as complexity emerges

### Tight Coupling
❌ `let service = NetworkService()` inside ViewModel
✅ `init(service: NetworkServiceProtocol)`

### Unclear Responsibilities
❌ One class doing networking, persistence, and UI logic
✅ Separate classes for each concern

## When to Refactor

**Move from Level 1 to Level 2 when:**
- Adding first API call
- Logic exceeds ~30 lines
- Need to test business logic
- State management becomes complex

**Move from Level 2 to Level 3 when:**
- Second feature needs same logic
- Logic is domain-specific (auth, data access)
- Want to share state app-wide

## Transferability

These patterns translate to:

| Platform | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| React | useState | Custom hooks | Context/Redux |
| Flutter | StatefulWidget | ChangeNotifier | Provider/BLoC |
| Android Compose | remember/mutableStateOf | ViewModel | Repository |
| Angular | Component state | Component logic | Services |

## Remember

1. **Start simple** - Don't add architecture until you need it
2. **Let complexity drive decisions** - Refactor when pain emerges
3. **Follow SOLID** - Good design principles apply everywhere
4. **Inject dependencies** - Always testable, always flexible
5. **Protocols over concrete types** - Flexibility and testability
