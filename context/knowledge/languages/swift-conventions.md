# Swift/SwiftUI Conventions

This document defines shared conventions for all Swift and SwiftUI applications in the Athlead monorepo.

## Architecture Overview

### What This Is

This is **MVC (Model-View-Controller)** adapted for modern Swift and SwiftUI.

We're not inventing a new pattern—we're doing MVC correctly with strict conventions that prevent the "Massive View Controller" anti-pattern. The explicit Service layer and Swift concurrency patterns make this architecture powerful, testable, and maintainable.

**What makes this powerful:**
- **Unidirectional data flow**: Views can never directly mutate state
- **Protocol-based services**: Every component is testable in isolation
- **Task cancellation discipline**: Memory-safe async operations by default
- **Clear separation**: Business logic in Models, coordination in Controllers, infrastructure in Services

### Unidirectional Flow

```
View → Controller → Service → Model
```

- **View**: SwiftUI, renders UI, delegates actions to Controller
- **Controller**: Observable class, manages UI state, coordinates services
- **Service**: Actor, stateless async operations, infrastructure layer
- **Model**: Struct, immutable data with business logic

---

## MVC Layer Usage

- **Models/**: Always. Every feature has data structures.
- **Services/**: When performing async operations (API calls, SDK interactions).
- **Controllers/**: When managing UI state or coordinating services.
- **Views/**: Always. Every feature has UI.

**Simplest Feature**: Model + View only.
**Typical Feature**: Model + Service + Controller + View.

---

## Core Layers

### 1. Models (Structs)

Immutable data with computed properties for business logic.

```swift
struct User: Codable, Equatable {
    let id: String
    let name: String
    let email: String

    var displayName: String {
        name.isEmpty ? email : name
    }
}
```

**Rules:**
- Always `struct`, never `class`
- Always `Codable` for API/persistence
- No async operations
- No `@Published` or Observable

### 2. Services (Actors)

Stateless async operations behind protocols.

```swift
protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

actor UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        try await APIClient.shared.get("/users/\(id)")
    }
}

// Example: Struct service for synchronous utilities
protocol ValidationServiceProtocol {
    static func isValidEmail(_ email: String) -> Bool
}

struct ValidationService: ValidationServiceProtocol {
    static func isValidEmail(_ email: String) -> Bool {
        email.contains("@") && email.contains(".")
    }
}
```

**Rules:**
- Use `actor` when: Performing async operations, managing shared state, making network calls
- Use `struct` with static methods when: Pure functions, synchronous utilities, simple data transformations
- Always define protocol for testing
- No UI or business state (caching is acceptable)
- Return Models, never Controllers
- Never `@MainActor` (background execution only)
- ❌ Never use `class` for services (prevents accidental shared mutable state)

### 3. Controllers (Observable Classes)

Manages UI state and coordinates service calls.

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
                    // Handle error
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

**Rules:**
- Always `@Observable @MainActor final class`
- Always `private(set)` on properties
- Always protocol-based service injection
- Always track and cancel tasks in `deinit`
- Always check `Task.isCancelled` before setting error state
- No SwiftUI-specific dependencies (no `@Environment`)

### 4. Views (SwiftUI)

Renders UI and delegates actions to Controller.

```swift
struct UserView: View {
    @State private var controller = UserController()

    var body: some View {
        Group {
            if controller.isLoading {
                ProgressView()
            } else if let user = controller.user {
                Text(user.displayName)
            }
        }
        .task {
            await controller.loadUser(id: "123")
        }
    }
}
```

**Rules:**
- Create Controller with `@State private var`
- Delegate all actions to Controller methods
- Never call Services directly
- Never mutate Controller properties (read-only via `private(set)`)

---

## Production Requirements

Every production feature must have:

**Controller Class:**
- ✅ `@Observable @MainActor final class`
- ✅ `private(set)` on all properties
- ✅ Protocol-based service dependency
- ✅ Task tracking: `private var loadTask: Task<Void, Never>?`
- ✅ Cancel check: `if !Task.isCancelled`
- ✅ Cleanup: `deinit { loadTask?.cancel() }`

**Service:**
- ✅ `actor` for async operations, `struct` with static methods for pure functions
- ✅ Protocol for testing
- ✅ No stored UI/business state
- ✅ Returns structs
- ❌ Never `class`

**Critical Rules:**
- Models: No async code, no `@Published`
- Services: No UI state, background actors only
- Controllers: No `@Environment` dependencies
- Views: Delegate to Controllers, never call Services directly

---

## Error Handling

Controllers handle errors from services and present them to users. Keep it simple and pragmatic.

### Basic Pattern

```swift
@Observable
@MainActor
final class FeatureController {
    private(set) var errorMessage: String?
    private(set) var isLoading = false

    func performAction() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            try await service.doSomething()
        } catch {
            if !Task.isCancelled {
                errorMessage = error.localizedDescription
            }
        }
    }

    func clearError() {
        errorMessage = nil
    }
}

// View displays errors
struct FeatureView: View {
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .alert("Error", isPresented: .constant(controller.errorMessage != nil)) {
                Button("OK") { controller.clearError() }
            } message: {
                Text(controller.errorMessage ?? "")
            }
    }
}
```

### Optional: Custom Error Types

For better control over error messages, define app-specific errors:

```swift
enum AppError: LocalizedError {
    case networkUnavailable
    case authenticationRequired
    case invalidInput(String)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable:
            return "No internet connection. Please try again."
        case .authenticationRequired:
            return "Please sign in to continue."
        case .invalidInput(let field):
            return "\(field) is invalid."
        }
    }
}
```

**Error Handling Rules:**
- ✅ Always check `Task.isCancelled` before setting error state
- ✅ Clear errors before retrying operations
- ✅ Use `localizedDescription` for simple cases
- ✅ Define custom errors when you need specific messaging
- ❌ Don't over-engineer - basic String errors are fine for most cases
- ❌ Don't show technical error details to users

---

## Advanced Patterns

### Controller Composition

Break large Controller classes into focused units.

```swift
// Focused child controllers
@Observable
@MainActor
final class ProfilePostsController {
    private(set) var posts: [Post] = []
    private(set) var isLoading = false

    func loadPosts(userId: String) async { /* ... */ }
}

// Parent composes children
@Observable
@MainActor
final class ProfileController {
    private(set) var user: User?
    let postsController = ProfilePostsController()

    func loadProfile(id: String) async { /* ... */ }
}

// View passes composed controllers to children
struct ProfileView: View {
    @State private var controller = ProfileController()

    var body: some View {
        VStack {
            PostsList(controller: controller.postsController)
        }
    }
}
```

**When to split:** Controller exceeds ~200 lines OR manages multiple independent concerns.

### Shared Controllers

For state spanning multiple features (user context, preferences).

```swift
// 1. Define shared controller with singleton
@Observable
@MainActor
final class AppController {
    static let shared = AppController()

    private(set) var currentUser: User?

    init(currentUser: User? = nil) {
        self.currentUser = currentUser
    }

    func setUser(_ user: User?) {
        self.currentUser = user
    }
}

// 2. Create EnvironmentKey
private struct AppControllerKey: EnvironmentKey {
    static let defaultValue = AppController.shared
}

extension EnvironmentValues {
    var appController: AppController {
        get { self[AppControllerKey.self] }
        set { self[AppControllerKey.self] = newValue }
    }
}

// 3. Inject at app level
@main
struct AthleadApp: App {
    @State private var appController = AppController.shared

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(\.appController, appController)
        }
    }
}

// 4. Access in Views
struct FeatureView: View {
    @Environment(\.appController) private var appController

    var body: some View {
        Text(appController.currentUser?.name ?? "Guest")
    }
}

// 5. Inject into Controller classes
@Observable
@MainActor
final class FeatureController {
    private let appController: AppController

    init(appController: AppController = .shared) {
        self.appController = appController
    }

    var userName: String {
        appController.currentUser?.name ?? "Guest"
    }
}

// 6. Access from Services
actor FeatureService {
    func performAction() async throws -> Result {
        let userId = await MainActor.run {
            AppController.shared.currentUser?.id
        }

        return try await APIClient.shared.post("/action", userId: userId)
    }
}
```

**Shared Controller Rules:**
- ✅ Must be `@Observable @MainActor final class`
- ✅ Must have `static let shared` singleton
- ✅ Must have custom EnvironmentKey
- ✅ Controllers accept via init with `.shared` default
- ✅ Services access via `MainActor.run`
- ❌ Never hardcode `.shared` in Controller properties
- ❌ Never access from Models

### Navigation

Controller owns navigation intent (enum), View owns mechanism (NavigationStack).

```swift
// Controller declares destinations
@Observable
@MainActor
final class FeatureController {
    private(set) var navigationDestination: Destination?

    enum Destination: Hashable {
        case detail(id: String)
        case settings
    }

    func navigate(to destination: Destination) {
        navigationDestination = destination
    }

    func clearNavigation() {
        navigationDestination = nil
    }
}

// View implements navigation
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

**Modal Presentation:**

```swift
// Controller declares sheet
@Observable
@MainActor
final class FeatureController {
    private(set) var sheet: Sheet?

    enum Sheet: Identifiable {
        case edit
        case share

        var id: Self { self }
    }

    func showSheet(_ sheet: Sheet) {
        self.sheet = sheet
    }
}

// View renders sheet
struct FeatureView: View {
    @State private var controller = FeatureController()

    var body: some View {
        Content()
            .sheet(item: $controller.sheet) { sheet in
                switch sheet {
                case .edit: EditView()
                case .share: ShareView()
                }
            }
    }
}
```

**Navigation Rules:**
- ✅ Controller owns navigation intent (enum)
- ✅ View owns NavigationStack and NavigationPath
- ✅ Modal destinations must be Identifiable
- ❌ Controller never mutates NavigationPath
- ❌ Never store NavigationPath in Controller

---

## Flexibility Guidelines

**When You Can Skip Layers:**
- Simple static content: Model + View only (no Controller, no Service)
- Read-only features: Skip Service if no async operations
- Trivial actions: Skip loading/error states if user won't notice

**When You Can Bend Rules:**
- Prototyping: Skip protocols for throwaway code
- Internal tools: Direct service calls from Views if feature is internal-only
- Caching: Services can store cache (but not UI/business state)

**Never Compromise:**
- Task cancellation in Controllers (prevents memory leaks)
- `private(set)` on Controller properties (preserves data flow)
- `@MainActor` on Controllers (thread safety)
- Protocol services in production (testability)

---

## Testing

Protocol-based services enable testing without network calls.

```swift
// Mock conforming to protocol
actor MockUserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        User(id: "test", name: "Test", email: "test@test.com")
    }
}

// Test with mock
func testUserLoading() async {
    let controller = UserController(service: MockUserService())
    await controller.loadUser(id: "123")
    XCTAssertEqual(controller.user?.name, "Test")
}
```

**Why Protocols Matter:**
- Test Controllers without network/database
- Verify business logic in isolation
- Fast, deterministic tests

---

## Liquid Glass Design System (iOS 26+)

**Liquid Glass** is Apple's translucent material system that reflects and refracts surroundings while dynamically transforming to bring focus to content. Available in iOS 26+, iPadOS 26+, macOS Tahoe 26+, watchOS 26+, and tvOS 26+.

### Basic Usage

Apply Liquid Glass effects using the `glassEffect()` modifier:

```swift
// Default glass effect (Capsule shape)
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect()

// Custom shape
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(in: .rect(cornerRadius: 16.0))

// Tinted and interactive
Text("Hello, World!")
    .font(.title)
    .padding()
    .glassEffect(.regular.tint(.orange).interactive())
```

### Glass Effect Variants

```swift
// Regular glass (default)
.glassEffect()

// Tinted glass (use sparingly for meaning, not just decoration)
.glassEffect(.regular.tint(.purple.opacity(0.12)))

// Interactive glass (responds to touch/pointer)
.glassEffect(.regular.interactive())

// Combined tint + interactive
.glassEffect(.regular.tint(.blue.opacity(0.1)).interactive())
```

### Custom Shapes

```swift
// Rounded rectangle
.glassEffect(in: .rect(cornerRadius: 12.0))

// Circle
.glassEffect(in: .circle)

// Custom shape
.glassEffect(in: RoundedRectangle(cornerRadius: 20, style: .continuous))
```

### Native Glass Button Styles

For buttons, use native glass button styles instead of custom implementations:

```swift
// Standard glass button
Button("Sign In") {
    // action
}
.buttonStyle(.glass)

// Prominent glass button (for primary actions)
Button("Get Started") {
    // action
}
.buttonStyle(.glassProminent)
```

### Multiple Glass Effects with Containers

Use `GlassEffectContainer` when applying glass effects to multiple views for optimal performance and shape blending:

```swift
GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()

        Image(systemName: "eraser.fill")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
    }
}
```

**Container spacing** controls how glass effects blend together:
- Larger spacing = effects blend sooner during transitions
- When views are closer than spacing, effects merge at rest
- Creates fluid morphing animations as views move

### Unified Glass Effects

Combine multiple views into a single glass shape using `glassEffectUnion`:

```swift
@Namespace private var namespace
let symbolSet = ["cloud.bolt.rain.fill", "sun.rain.fill", "moon.stars.fill", "moon.fill"]

GlassEffectContainer(spacing: 20.0) {
    HStack(spacing: 20.0) {
        ForEach(symbolSet.indices, id: \.self) { item in
            Image(systemName: symbolSet[item])
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectUnion(id: item < 2 ? "1" : "2", namespace: namespace)
        }
    }
}
```

### Morphing Transitions

Coordinate glass effect transitions using `glassEffectID` and `glassEffectTransition`:

```swift
@State private var isExpanded: Bool = false
@Namespace private var namespace

GlassEffectContainer(spacing: 40.0) {
    HStack(spacing: 40.0) {
        Image(systemName: "scribble.variable")
            .frame(width: 80.0, height: 80.0)
            .font(.system(size: 36))
            .glassEffect()
            .glassEffectID("pencil", in: namespace)

        if isExpanded {
            Image(systemName: "eraser.fill")
                .frame(width: 80.0, height: 80.0)
                .font(.system(size: 36))
                .glassEffect()
                .glassEffectID("eraser", in: namespace)
        }
    }
}

Button("Toggle") {
    withAnimation {
        isExpanded.toggle()
    }
}
.buttonStyle(.glass)
```

**Transition Types:**
- **matchedGeometry** (default): For effects within container spacing
- **materialize**: For effects farther apart than container spacing

### Liquid Glass Rules

**Do:**
- ✅ Use `.glassEffect()` for custom components requiring translucent backgrounds
- ✅ Use `.buttonStyle(.glass)` or `.buttonStyle(.glassProminent)` for buttons
- ✅ Use `GlassEffectContainer` when multiple glass effects are near each other
- ✅ Apply tints sparingly to convey meaning (e.g., primary actions, states)
- ✅ Use `.interactive()` for custom tappable components
- ✅ Apply `glassEffect()` after other appearance modifiers

**Don't:**
- ❌ Don't create too many containers on screen (performance impact)
- ❌ Don't use tints for pure decoration
- ❌ Don't apply glass effects to too many views simultaneously
- ❌ Don't implement custom glass effects - use native API
- ❌ Don't add gesture handlers that interfere with `.interactive()`

### Migration from Custom Glass Effects

If you have custom glass implementations (e.g., using `.ultraThinMaterial`), migrate to native Liquid Glass:

**Before (Custom):**
```swift
.background(.ultraThinMaterial)
.clipShape(RoundedRectangle(cornerRadius: 12))
.shadow(color: .black.opacity(0.1), radius: 10)
```

**After (Native):**
```swift
.glassEffect(in: .rect(cornerRadius: 12))
```

**Benefits:**
- Native system performance optimizations
- Automatic adaptation to system theme
- Built-in interactive states
- Morphing and blending animations
- Future-proof as Apple refines the design language

### Performance Considerations

- Limit the number of glass effects on screen simultaneously
- Use `GlassEffectContainer` for clusters of glass views
- Profile with Instruments if experiencing performance issues
- Consider reducing complexity for lower-end devices

### Component Library Pattern

Create reusable glass components for consistency:

```swift
// Shared/Components/GlassCard.swift
struct GlassCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding()
            .glassEffect(in: .rect(cornerRadius: 16))
    }
}

// Usage
GlassCard {
    VStack {
        Text("Title")
        Text("Description")
    }
}
```

---

## Further Reading

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) - Official Apple guide for iOS 26 design system
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html) - Actor-based concurrency patterns
- [Observable Macro](https://developer.apple.com/documentation/observation) - Modern state management in SwiftUI