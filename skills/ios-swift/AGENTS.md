# iOS & Swift Development - Full Compiled Reference

**This is the compiled reference for agents.** It contains ALL rules, patterns, checklists, and code examples from every section of the ios-swift skill. For the navigable index, see [SKILL.md](SKILL.md).

---

# Part 1: Architecture (MVC)

Modern MVC architecture for Swift/SwiftUI with strict unidirectional data flow.

```
View -> Controller -> Service -> Model
```

**Layer Separation Rules:**

| From | To | Allowed |
|------|----|---------|
| View | Controller | Yes |
| View | Service | NO |
| View | Model | Read only |
| Controller | Service | Yes |
| Controller | Model | Yes |
| Service | Controller | NO |
| Service | Model | Yes |
| Model | Any | NO (pure data) |

**Decision Tree:**

```
What are you building?

Data structure with business logic -> Model (struct)
Async operation (API, database, SDK) -> Service (actor + protocol)
UI state management or service coordination -> Controller (@Observable class)
Display UI or handle user input -> View (SwiftUI, delegates to Controller)
```

---

## 1.1 Controllers (Observable Classes)

Controllers manage UI state and coordinate service calls. They are the glue between Views (presentation) and Services (infrastructure).

**Key characteristics:**
- Always `@Observable @MainActor final class`
- Properties are `private(set)` (read-only from Views)
- Protocol-based service injection for testability
- Track and cancel async tasks properly
- No SwiftUI-specific dependencies (no `@Environment` except for shared controllers)

### Basic Controller Pattern

```swift
@Observable
@MainActor
final class UserController {
    // MARK: - Published State
    private(set) var user: User?
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    // MARK: - Internal State
    private var hasLoadedInitialData = false

    // MARK: - Dependencies
    private let service: UserServiceProtocol

    // MARK: - Tasks
    private var loadTask: Task<Void, Never>?

    // MARK: - Initialization
    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    // MARK: - Public Methods
    func loadUser(id: String) async {
        loadTask?.cancel()

        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                user = try await service.fetchUser(id: id)
            } catch {
                if !Task.isCancelled {
                    errorMessage = error.localizedDescription
                }
            }
        }

        await loadTask?.value
    }

    // MARK: - Private Methods
    private func processData(_ raw: RawModel) -> Model {
        // Transform logic
    }

    // MARK: - Cleanup
    deinit {
        loadTask?.cancel()
    }
}
```

### Required Property Order Within Controllers

1. Published state (`private(set) var` -- properties the View reads)
2. Internal state (`private var` -- non-published tracking state)
3. Dependencies (`private let` -- services, injected values)
4. Tasks (`private var loadTask: Task<Void, Never>?`)
5. Initialization (`init`)
6. Public methods (`func` -- called by Views)
7. Private methods (`private func` -- internal helpers)
8. Cleanup (`deinit`)

### Production Checklist

| Check | Required |
|-------|----------|
| `@Observable` | Yes |
| `@MainActor` | Yes |
| `final class` | Yes |
| `private(set)` on published state | Yes |
| Protocol-based service dependency | Yes |
| Task tracking variable | Yes |
| `deinit` with cancel | Yes |
| Published state before dependencies | Yes |
| Dependencies before init | Yes |
| init before public methods | Yes |
| Public methods before private methods | Yes |
| deinit last | Yes |
| `// MARK:` section comments | Recommended |

### Task Cancellation Discipline

```swift
func load() async {
    loadTask?.cancel()  // Cancel previous

    loadTask = Task {
        isLoading = true
        defer { isLoading = false }

        do {
            data = try await service.fetch()
        } catch {
            if !Task.isCancelled {  // Check before error state
                errorMessage = error.localizedDescription
            }
        }
    }

    await loadTask?.value
}
```

### Multiple Tasks Pattern

```swift
private var loadTask: Task<Void, Never>?
private var refreshTask: Task<Void, Never>?

deinit {
    loadTask?.cancel()
    refreshTask?.cancel()
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
        guard !query.isEmpty else { results = []; return }

        searchTask = Task {
            try? await Task.sleep(for: .milliseconds(300))
            guard !Task.isCancelled else { return }

            isSearching = true
            defer { isSearching = false }

            do {
                results = try await service.search(query: query)
            } catch {
                if !Task.isCancelled { /* Handle error */ }
            }
        }
    }

    deinit { searchTask?.cancel() }
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
                if !Task.isCancelled { currentPage -= 1 }
            }
        }
        await loadTask?.value
    }
}
```

### Controller Anti-Patterns

- **Public mutable properties:** Always use `private(set)`
- **Not cancelling tasks:** Always `loadTask?.cancel()` before starting new
- **Missing cancellation checks:** Always `if !Task.isCancelled` before error state
- **Concrete service dependencies:** Always use protocols
- **Using @Environment in Controllers:** Controllers never use `@Environment` (Views do)

### When to Split Controllers

Split when: exceeds ~200 lines, manages multiple independent concerns, has multiple distinct async operations.

---

## 1.2 Services (Actors and Structs)

Services are the infrastructure layer. They handle async operations like network calls, database queries, and SDK interactions.

**Key characteristics:**
- Use `actor` for async operations and shared state
- Use `struct` with static methods for pure functions
- Always define a protocol for testability
- No UI or business state (caching is acceptable)
- Return Models, never Controllers
- Never `@MainActor` (background execution only)
- Never `class` (prevents accidental shared mutable state)

### Actor vs Struct Decision Tree

```
Is the service performing async operations?
+-- YES -> Use ACTOR
+-- NO -> Is it a pure function or utility?
    +-- YES -> Use STRUCT with static methods
```

### Protocol-Based Design

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws
}

actor UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        try await APIClient.shared.get("/users/\(id)")
    }

    func updateUser(_ user: User) async throws {
        try await APIClient.shared.put("/users/\(user.id)", body: user)
    }
}
```

### Actor Service Examples

**Network Service:**
```swift
actor NetworkService: NetworkServiceProtocol {
    private let baseURL: URL

    func get<T: Decodable>(_ endpoint: String) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

**Cache Service:**
```swift
actor CacheService: CacheServiceProtocol {
    private var cache: [String: Data] = [:]

    func get<T: Codable>(key: String) -> T? {
        guard let data = cache[key] else { return nil }
        return try? JSONDecoder().decode(T.self, from: data)
    }

    func set<T: Codable>(key: String, value: T) {
        guard let data = try? JSONEncoder().encode(value) else { return }
        cache[key] = data
    }
}
```

### Struct Service Examples

**Validation Service:**
```swift
struct ValidationService: ValidationServiceProtocol {
    static func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }

    static func isValidPassword(_ password: String) -> Bool {
        password.count >= 8 &&
        password.contains(where: { $0.isUppercase }) &&
        password.contains(where: { $0.isLowercase }) &&
        password.contains(where: { $0.isNumber })
    }
}
```

### Service Composition

```swift
actor UserService: UserServiceProtocol {
    private let api: NetworkServiceProtocol
    private let cache: CacheServiceProtocol

    func fetchUser(id: String) async throws -> User {
        if let cached: User = await cache.get(key: "user_\(id)") { return cached }
        let user: User = try await api.get("/users/\(id)")
        await cache.set(key: "user_\(id)", value: user)
        return user
    }
}
```

### Service Rules

**DO:** Always use protocols, return Models, use actors for async, use structs for pure functions, keep services focused.

**DON'T:** Never use class, never store UI state, never use @MainActor, never return/accept Controllers, never import SwiftUI.

### Error Handling in Services

```swift
enum NetworkError: LocalizedError {
    case invalidURL, noData, decodingFailed, httpError(statusCode: Int)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .noData: return "No data received"
        case .decodingFailed: return "Failed to decode response"
        case .httpError(let code): return "HTTP error: \(code)"
        }
    }
}
```

---

## 1.3 Models (Immutable Structs)

Models are immutable data structures with computed properties for business logic.

**Key characteristics:**
- Always `struct`, never `class`
- Always `Codable` for API/persistence
- Always `Equatable` for comparisons
- No async operations
- No `@Published` or Observable
- Business logic in computed properties

### Basic Pattern

```swift
struct User: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    let email: String
    let createdAt: Date

    var displayName: String {
        name.isEmpty ? email : name
    }

    var isNew: Bool {
        Date().timeIntervalSince(createdAt) < 86400
    }
}
```

### Required Property Order Within Models

1. Stored properties (`let` / `var`)
2. Computed properties (`var { get }`)
3. Static methods/properties
4. Custom `init` (if needed beyond memberwise)
5. Nested types (`enum`, `struct`)

### Model Rules

**Always:** Use struct, conform to Codable, conform to Equatable, use computed properties for logic.

**Never:** Use async operations, use @Published or Observable, store mutable UI state.

### Common Patterns

**Nested Types:**
```swift
struct User: Codable, Equatable {
    let id: String
    let address: Address

    struct Address: Codable, Equatable {
        let street: String
        let city: String
        var formatted: String { "\(street), \(city)" }
    }
}
```

**Enums for State:**
```swift
struct Order: Codable, Equatable {
    let status: Status

    enum Status: String, Codable {
        case pending, processing, shipped, delivered, cancelled
        var isActive: Bool { self != .cancelled && self != .delivered }
    }
}
```

**Custom Codable Keys:**
```swift
struct User: Codable, Equatable {
    let emailAddress: String

    enum CodingKeys: String, CodingKey {
        case emailAddress = "email"
    }
}
```

**API Response Wrapper:**
```swift
struct APIResponse<T: Codable>: Codable {
    let data: T
    let meta: Meta

    struct Meta: Codable {
        let page: Int
        let totalPages: Int
        var hasMore: Bool { page < totalPages }
    }
}
```

---

## 1.4 Views (SwiftUI)

Views render UI and delegate actions to Controllers.

**Key characteristics:**
- Create Controller with `@State private var`
- Delegate all actions to Controller methods
- Never call Services directly
- Never mutate Controller properties (read-only via `private(set)`)
- No business logic in Views

### Basic Pattern

```swift
struct UserView: View {
    @State private var controller = UserController()

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView()
            } else if let user = controller.user {
                VStack {
                    Text(user.displayName)
                    Text(user.email)
                }
            } else {
                Text("No user")
            }
        }
        .task {
            await controller.loadUser(id: "123")
        }
    }
}
```

### Required Property Order Within Views

1. `@Environment` / `@EnvironmentObject` properties
2. `@State` / `@Binding` / `@FocusState` properties
3. Regular properties (`let` / `var`)
4. Computed properties
5. `init` (if needed)
6. `body`
7. Helper views (`@ViewBuilder private var`)
8. Helper functions (`private func`)

### View Rules

**DO:** Create Controller with @State, delegate actions to Controller, read Controller state, use .task for initial loading.

**DON'T:** Never mutate Controller properties, never call Services directly, never put business logic in Views.

### View Composition

```swift
// Parent view owns Controller
struct ProfileView: View {
    @State private var controller = ProfileController()

    var body: some View {
        ScrollView {
            if let user = controller.user {
                ProfileHeader(user: user)  // Subview receives data
                ProfileBio(bio: user.bio)
            }
        }
        .task { await controller.load() }
    }
}

// Subviews receive data, not controllers
struct ProfileHeader: View {
    let user: User
    var body: some View {
        VStack {
            AsyncImage(url: user.avatarURL)
            Text(user.displayName)
        }
    }
}
```

### Task Management

```swift
// Preferred: .task modifier (auto-cancels on disappear)
.task { await controller.load() }

// Manual: when you need control
@State private var loadTask: Task<Void, Never>?
.onAppear { loadTask = Task { await controller.load() } }
.onDisappear { loadTask?.cancel() }
```

---

## 1.5 Error Handling

Controllers handle errors from Services and present them to users.

### Basic Pattern

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var errorMessage: String?

    func performAction() async {
        errorMessage = nil  // Clear previous error
        do {
            try await service.doSomething()
        } catch {
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }

    func clearError() { errorMessage = nil }
}
```

### Custom Error Types

```swift
enum AppError: LocalizedError {
    case networkUnavailable
    case authenticationRequired
    case invalidInput(String)
    case serverError(Int)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable: return "No internet connection. Please try again."
        case .authenticationRequired: return "Please sign in to continue."
        case .invalidInput(let field): return "\(field) is invalid."
        case .serverError(let code): return "Server error (\(code)). Please try again later."
        }
    }
}
```

### View Error Patterns

```swift
// Alert
.alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
    Button("OK") { controller.clearError() }
} message: { Text(controller.errorMessage ?? "") }

// Inline
if let error = controller.errorMessage {
    HStack { Image(systemName: "exclamationmark.triangle"); Text(error) }
        .foregroundColor(.red).padding()
}
```

### Form Validation

```swift
@Observable
@MainActor
final class SignUpController {
    private(set) var emailError: String?
    private(set) var passwordError: String?
    private(set) var isValid = false

    func updateEmail(_ newEmail: String) {
        email = newEmail
        emailError = ValidationService.isValidEmail(email) ? nil : "Invalid email"
        updateValidity()
    }
}
```

---

## 1.6 Navigation

Controller owns navigation intent (enum), View owns mechanism (NavigationStack).

### Push Navigation

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var navigationDestination: Destination?

    enum Destination: Hashable {
        case detail(id: String)
        case settings
    }

    func navigate(to destination: Destination) { navigationDestination = destination }
    func clearNavigation() { navigationDestination = nil }
}

struct FeatureView: View {
    @State private var controller = FeatureController()
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Content()
                .navigationDestination(for: FeatureController.Destination.self) { dest in
                    switch dest {
                    case .detail(let id): DetailView(id: id)
                    case .settings: SettingsView()
                    }
                }
                .onChange(of: controller.navigationDestination) { _, new in
                    if let destination = new {
                        path.append(destination)
                        controller.clearNavigation()
                    }
                }
        }
    }
}
```

### Modal/Sheet Presentation

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var sheet: Sheet?

    enum Sheet: Identifiable {
        case edit(Item)
        case add

        var id: String {
            switch self {
            case .edit(let item): return "edit-\(item.id)"
            case .add: return "add"
            }
        }
    }

    func showEdit(_ item: Item) { sheet = .edit(item) }
    func showAdd() { sheet = .add }
    func dismissSheet() { sheet = nil }
}
```

### Tab Navigation

```swift
@Observable
@MainActor
final class AppController {
    private(set) var selectedTab: Tab = .home

    enum Tab { case home, search, profile }

    func selectTab(_ tab: Tab) { selectedTab = tab }
}
```

### Deep Linking

```swift
func handle(url: URL) {
    if url.pathComponents.contains("posts"),
       let id = url.pathComponents.last {
        deepLink = .post(id: id)
    }
}
```

### Navigation Rules

- Controller never mutates NavigationPath
- Never store NavigationPath in Controller
- View never decides what to navigate to (delegates to Controller)

---

## 1.7 Advanced Patterns

### Controller Composition

```swift
@Observable
@MainActor
final class ProfileController {
    private(set) var user: User?
    let postsController = ProfilePostsController()

    func loadProfile(id: String) async {
        user = try await userService.fetchUser(id: id)
        await postsController.loadPosts(userId: id)
    }
}
```

### Shared Controllers (Environment)

```swift
@Observable
@MainActor
final class AppController {
    static let shared = AppController()
    private(set) var currentUser: User?
}

private struct AppControllerKey: EnvironmentKey {
    static let defaultValue = AppController.shared
}

extension EnvironmentValues {
    var appController: AppController {
        get { self[AppControllerKey.self] }
        set { self[AppControllerKey.self] = newValue }
    }
}
```

### State Machine Pattern

```swift
@Observable
@MainActor
final class AuthController {
    private(set) var state: State = .loggedOut

    enum State {
        case loggedOut
        case signingIn
        case signedIn(User)
        case error(String)

        var isLoading: Bool { if case .signingIn = self { return true }; return false }
        var user: User? { if case .signedIn(let user) = self { return user }; return nil }
    }
}
```

### Coordinator Pattern

```swift
@Observable
@MainActor
final class OnboardingCoordinator {
    private(set) var currentStep: Step = .welcome
    enum Step { case welcome, profile, permissions, complete }

    func next() { /* advance step */ }
    func back() { /* go back */ }
}
```

### Dependency Container

```swift
@Observable
@MainActor
final class DependencyContainer {
    static let shared = DependencyContainer()

    let networkService: NetworkServiceProtocol
    let authService: AuthServiceProtocol

    func makeUserController() -> UserController {
        UserController(userService: UserService(network: networkService))
    }
}
```

---

## 1.8 Testing

Protocol-based services enable testing without network calls.

### Mock Service Pattern

```swift
actor MockUserService: UserServiceProtocol {
    var shouldFail = false
    var mockUser = User(id: "test", name: "Test User", email: "test@test.com")

    func fetchUser(id: String) async throws -> User {
        if shouldFail { throw NetworkError.noData }
        return mockUser
    }
}
```

### Test Patterns

```swift
// Success
func testSuccessfulUserLoad() async {
    let mockService = MockUserService()
    let controller = UserController(service: mockService)
    await controller.loadUser(id: "1")
    XCTAssertEqual(controller.user?.name, "Test User")
    XCTAssertFalse(controller.isLoading)
}

// Error
func testErrorHandling() async {
    let mockService = MockUserService()
    mockService.shouldFail = true
    let controller = UserController(service: mockService)
    await controller.loadUser(id: "1")
    XCTAssertNil(controller.user)
    XCTAssertNotNil(controller.errorMessage)
}

// Cancellation
func testTaskCancellation() async {
    let mockService = MockUserService()
    mockService.delayMilliseconds = 500
    let controller = UserController(service: mockService)
    // Start first load, then immediately start second
    // Assert second load wins
}
```

### Testing Best Practices

**DO:** Test business logic (not implementation), use descriptive test names, Arrange-Act-Assert pattern, test edge cases.

**DON'T:** Don't test framework code, don't make tests depend on each other.

---

## 1.9 Liquid Glass Design System (iOS 26+)

**Availability:** iOS 26+, iPadOS 26+, macOS Tahoe 26+

### Basic Usage

```swift
// Default glass effect
Text("Hello").padding().glassEffect()

// Custom shape
Text("Hello").padding().glassEffect(in: .rect(cornerRadius: 16.0))

// Tinted and interactive
Text("Hello").padding().glassEffect(.regular.tint(.orange).interactive())
```

### Glass Button Styles

```swift
Button("Sign In") { }.buttonStyle(.glass)
Button("Get Started") { }.buttonStyle(.glassProminent)
```

### Multiple Glass Effects

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable").glassEffect()
        Image(systemName: "eraser.fill").glassEffect()
    }
}
```

### Liquid Glass Rules

**DO:** Use `.glassEffect()` for translucent backgrounds, `.buttonStyle(.glass)` for buttons, `GlassEffectContainer` for multiple effects, `.interactive()` for tappable components.

**DON'T:** Don't create too many containers, don't use tints for decoration, don't implement custom glass effects.

### Migration from Custom Glass

```swift
// Before: .background(.ultraThinMaterial).clipShape(RoundedRectangle(cornerRadius: 12)).shadow(...)
// After:  .glassEffect(in: .rect(cornerRadius: 12))
```

---

# Part 2: Code Review

## 2.1 SwiftUI Pattern Validation

**Trigger:** After writing new SwiftUI features, before PR review for iOS code.

### Validation Checklist

**Controller Class Structure:**

| Check | Required |
|-------|----------|
| `@Observable` | Yes |
| `@MainActor` | Yes |
| `final class` | Yes |
| `private(set)` on published state | Yes |
| Protocol-based service dependency | Yes |
| Task tracking variable | Yes |
| `deinit` with cancel | Yes |
| Property ordering correct | Yes |

**Service Layer:**

| Check | Required |
|-------|----------|
| Protocol defined | Yes |
| `actor` type (for async) | Yes |
| No `@MainActor` | Yes |
| Returns structs | Yes |
| No UI state | Yes |

**View Delegation:**

| Check | Required |
|-------|----------|
| `@State private var controller` | Yes |
| No direct service calls | Yes |
| No controller property mutation | Yes |
| `.task` for async operations | Recommended |

**Model Compliance:**

| Check | Required |
|-------|----------|
| `struct` type | Yes |
| `Equatable` | Yes |
| No `@Published` | Yes |
| No async code | Yes |
| Stored properties first | Yes |
| Computed after stored | Yes |

**Task Cancellation:**

| Check | Required |
|-------|----------|
| Previous task cancelled | Yes |
| `Task.isCancelled` check | Yes |
| `defer` for loading state | Recommended |
| `await loadTask?.value` | Recommended |

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing @MainActor on Controller, View calls Service, missing task cancellation | Block PR |
| Warning | Missing protocol on Service, class instead of struct for Model | Address before shipping |
| Info | Missing @State on Controller var, could use defer | Optional improvement |

---

## 2.2 Swift Concurrency Audit

**Trigger:** Before PR review for Swift code with async/await, actor isolation, Task usage.

### Audit Checklist

**1. Actor Isolation:** Proper actor usage and isolation boundaries.
- Services as actors for async operations
- No shared mutable state in classes

**2. MainActor Controllers:** Controllers properly MainActor-isolated.
- All Controllers must have `@MainActor`

**3. @concurrent Usage (Swift 6.2):** Heavy computation explicitly marked.
```swift
@concurrent
func processLargeDataset(data: [Item]) async -> Summary {
    // Guaranteed background thread
}
```

**4. Task Cancellation:** Tasks properly tracked and cancelled.
- Track with `private var loadTask: Task<Void, Never>?`
- Cancel previous: `loadTask?.cancel()`
- Check: `if !Task.isCancelled`
- Cleanup: `deinit { loadTask?.cancel() }`

**5. Sendable Conformance:** Types crossing concurrency boundaries are Sendable.
```swift
struct User: Sendable {
    let id: String
    let name: String
}
```

**6. Data Race Detection:** No shared mutable state from multiple contexts.
- Captured mutable variables in Task closures
- Non-isolated access to actor state

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Data races, missing MainActor on controllers | Block PR |
| Warning | Missing task cancellation, heavy work on MainActor | Address before shipping |
| Info | @concurrent opportunities, optimization suggestions | Optional improvement |

### Swift 6.2 Migration Checklist

- Enable strict concurrency checking
- Add `@MainActor` to all controllers
- Mark heavy computation with `@concurrent`
- Verify all Task closures are Sendable
- Check isolated conformances on protocols
- Audit `nonisolated` usage

---

## 2.3 iOS Accessibility Review

**Trigger:** Before completing any iOS feature, PR review for iOS UI code.

### Audit Checklist

**1. VoiceOver Support:** All interactive elements properly labeled.
```swift
Button(action: { }) { Image(systemName: "plus") }
    .accessibilityLabel("Add new item")

HStack { Image(systemName: "star.fill"); Text("4.5") }
    .accessibilityElement(children: .combine)
    .accessibilityLabel("Rating 4.5 stars")
```

**2. Minimum Tap Targets:** All interactive elements >= 44x44pt.
```swift
Image(systemName: "info.circle")
    .frame(width: 20, height: 20)    // Visual size
    .contentShape(Rectangle())
    .frame(width: 44, height: 44)    // Tap target
```

**3. Reduce Transparency:** Glass effects have solid fallbacks.
```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency
.glassEffect(in: .rect(cornerRadius: 12), isEnabled: !reduceTransparency)
```

**4. Reduce Motion:** Animations respect preferences.
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
withAnimation(reduceMotion ? nil : .spring(duration: 0.3)) { isExpanded.toggle() }
```

**5. Increase Contrast:** High contrast mode support.
```swift
@Environment(\.accessibilityContrast) var contrast
Text("Label").foregroundStyle(contrast == .high ? .primary : .secondary)
```

**6. Assistive Access Scene (iOS 26+):**
```swift
@main
struct App: App {
    var body: some Scene {
        WindowGroup { ContentView() }
        AssistiveAccess { SimplifiedContentView() }
    }
}
```

**7. Accessibility Actions:** Complex gestures have alternatives.
```swift
Row()
    .swipeActions { Button("Delete") { delete() } }
    .accessibilityAction(named: "Delete") { delete() }
```

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Missing VoiceOver labels on buttons, tap targets < 44pt | Block PR |
| Warning | Missing Reduce Transparency fallback, no Assistive Access | Address before App Store |
| Info | Optimization opportunities | Optional improvement |

---

## 2.4 Liquid Glass Review

**Trigger:** UI components with glass effects, `.glassEffect()` usage, navigation bars/toolbars.

### Review Checklist

**0. Surface Appropriateness (Most Critical):**

| Surface Type | Glass OK? | Examples |
|--------------|-----------|----------|
| Navigation bars | YES | TabView, NavigationStack bars |
| Tab bars | YES | System TabView |
| Toolbars | YES | Floating action buttons |
| Sidebars | YES | iPad sidebar navigation |
| HUD overlays | YES | Volume indicators |
| **Content cards** | **NO** | Player cards, list items |
| **Reading areas** | **NO** | Long-form text |
| **Dense data** | **NO** | Tables, grids |
| **Forms/inputs** | **NO** | Text fields, pickers |

```swift
// BAD - content card with glass
VStack { /* player info */ }.glassEffect()  // VIOLATION

// GOOD - content card with solid background
VStack { /* player info */ }
    .background(Color.appCard)
    .clipShape(RoundedRectangle(cornerRadius: 12))
```

**1. Single Glass Layer Rule:** No glass on glass.

**2. Contrast Compliance:** WCAG AA (4.5:1 body, 3:1 large text). Use `.foregroundStyle(.primary)`.

**3. Performance:** Max 3-5 glass effects on simple UI, 8-10 on complex. Use `GlassEffectContainer`.

**4. Accessibility Fallbacks:** Handle Reduce Transparency.

**5. API Usage:** Native `.glassEffect()`, not `.background(.ultraThinMaterial)`.

### Severity Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Critical | Glass on content surfaces, glass on glass, missing accessibility | Block PR |
| Warning | Performance concerns, custom implementations | Address before shipping |
| Info | Style suggestions, optimization | Optional improvement |

---

## 2.5 Apple API Research

**Trigger:** Implementing new iOS features, exploring unfamiliar Apple frameworks, checking API availability.

### Research Process

1. **Identify Domain:** UI/UX, Data, Media, System, Hardware, Services, AI/ML
2. **Check Documentation Sources:**
   - Xcode Documentation (most accurate for API signatures)
   - Apple Developer Documentation (comprehensive guides)
   - Human Interface Guidelines (design patterns)
   - WWDC Sessions (deep dives)
3. **Verify API Availability:**
```swift
@available(iOS 26.0, *)
func useNewFeature() { }

if #available(iOS 26, *) { /* new API */ } else { /* fallback */ }
```

### Research Output Format

```markdown
## Apple API Research: [Topic]
### Recommended Approach
### Primary API
**Framework:** [name]  **Availability:** iOS [version]+
### Implementation Pattern
### Alternative Approaches
### Caveats
### Resources
```

---

# Part 3: Quality Checks

## 3.1 iOS Code Quality Checks

**Trigger:** Before commits or PRs, running `/ios-check`.

### Workflow

1. Detect iOS project
2. Check SwiftLint config (create from template if missing)
3. Run checks in order: SwiftLint -> Build -> Tests -> Coverage
4. Report results

### Commands

| Check | Command | When |
|-------|---------|------|
| SwiftLint | `swiftlint` or `swiftlint --fix` | Always |
| Build | `mcp__xcodebuildmcp__build_sim` | Always |
| Tests | `mcp__xcodebuildmcp__test_sim` | `--test` or `--coverage` |
| Coverage | Parse xcresult | `--coverage` |

### SwiftLint Config

Key settings:
- Line length: 120 warning / 200 error
- File length: 500 warning / 1000 error
- Allows short names (i, j, x, y) in loops
- Disables rules conflicting with SwiftUI: `trailing_comma`, `multiple_closures_with_trailing_closure`, `redundant_optional_initialization`
- Opt-in rules: `empty_count`, `empty_string`, `first_where`, `force_unwrapping`

### Quick Commands

```bash
/ios-check          # Lint + build
/ios-check --test   # Lint + build + tests
/ios-check --fix    # Auto-fix lint violations
/ios-check --coverage  # Tests with coverage
```

---

# Part 4: Workflows

## 4.1 Swift to Kotlin/Android Migration

**Trigger:** Migrating iOS app to Android, porting features Swift to Kotlin.

### Architecture Mapping

| iOS (Swift) | Android (Kotlin) |
|-------------|------------------|
| `@Observable` class | `ViewModel` + `StateFlow` |
| `@Published` property | `MutableStateFlow` / `StateFlow` |
| `@State` / `@Binding` | `collectAsStateWithLifecycle()` |
| SwiftUI View | `@Composable` function |
| Combine / async-await | Kotlin Coroutines + Flow |

### UI Translation

| SwiftUI | Jetpack Compose |
|---------|-----------------|
| `VStack` | `Column` |
| `HStack` | `Row` |
| `ZStack` | `Box` |
| `List` | `LazyColumn` |
| `NavigationLink` | `navController.navigate()` with `@Serializable` routes |
| `@State var` | `remember { mutableStateOf() }` |
| `.task` | `LaunchedEffect` |

### Language Syntax Mapping

| Swift | Kotlin |
|-------|--------|
| `let` | `val` |
| `var` | `var` |
| `func -> ReturnType` | `fun : ReturnType` |
| `if let` | `?.let { }` |
| `guard let else return` | `?: return` |
| `[Type]` | `List<Type>` |
| `[Key: Value]` | `Map<Key, Value>` |
| `struct` | `data class` |
| `protocol` | `interface` |
| `async throws` | `suspend` + `Result<T>` |

### Platform Feature Mapping

| iOS Feature | Android Equivalent |
|-------------|-------------------|
| HealthKit | Health Connect |
| CloudKit | Firebase / Room + Cloud sync |
| Core Data / SwiftData | Room Database |
| UserDefaults | DataStore |
| Keychain | EncryptedSharedPreferences |
| StoreKit | Google Play Billing |
| Push Notifications | Firebase Cloud Messaging |

### Best Practices

1. Don't port blindly - adapt to Android conventions
2. Embrace Material 3 design system
3. Use Kotlin idioms (data classes, sealed classes, extension functions)
4. Follow MVVM strictly
5. Test with interfaces
6. Respect Android lifecycle
7. Use Jetpack libraries

---

# Quick Reference

## Code Templates

### Model
```swift
struct MyModel: Codable, Equatable, Identifiable {
    let id: String
    let name: String
    var displayName: String { name.isEmpty ? "Unnamed" : name }
}
```

### Service (Actor)
```swift
protocol MyServiceProtocol {
    func fetchData(id: String) async throws -> MyModel
}
actor MyService: MyServiceProtocol {
    func fetchData(id: String) async throws -> MyModel { /* ... */ }
}
```

### Controller
```swift
@Observable
@MainActor
final class MyController {
    private(set) var data: MyModel?
    private(set) var isLoading = false
    private(set) var errorMessage: String?
    private let service: MyServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: MyServiceProtocol = MyService()) { self.service = service }

    func load(id: String) async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            defer { isLoading = false }
            do { data = try await service.fetchData(id: id) }
            catch { if !Task.isCancelled { errorMessage = error.localizedDescription } }
        }
        await loadTask?.value
    }

    deinit { loadTask?.cancel() }
}
```

### View
```swift
struct MyView: View {
    @State private var controller = MyController()

    var body: some View {
        Group {
            if controller.isLoading { ProgressView() }
            else if let data = controller.data { Text(data.name) }
        }
        .task { await controller.load(id: "123") }
    }
}
```

### Mock Service
```swift
actor MockMyService: MyServiceProtocol {
    var shouldFail = false
    var mockData = MyModel(id: "test", name: "Test")

    func fetchData(id: String) async throws -> MyModel {
        if shouldFail { throw NetworkError.noData }
        return mockData
    }
}
```
