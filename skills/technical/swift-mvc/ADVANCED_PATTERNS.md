# Advanced Patterns

**Referenced from**: [SKILL.md](SKILL.md), [CONTROLLERS.md](CONTROLLERS.md)

**Related**:
- [CONTROLLERS.md](CONTROLLERS.md) - Basic controller patterns
- [NAVIGATION.md](NAVIGATION.md) - Navigation patterns

---

## Overview

Advanced patterns for complex features: controller composition, shared state, and scaling architecture.

---

## Controller Composition

Break large Controller classes into focused units.

### Pattern

```swift
// Focused child controllers
@Observable
@MainActor
final class ProfilePostsController {
    private(set) var posts: [Post] = []
    private(set) var isLoading = false

    private let service: PostServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: PostServiceProtocol = PostService()) {
        self.service = service
    }

    func loadPosts(userId: String) async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                posts = try await service.fetchPosts(userId: userId)
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

// Parent composes children
@Observable
@MainActor
final class ProfileController {
    private(set) var user: User?
    private(set) var isLoading = false

    // Composed controllers
    let postsController = ProfilePostsController()

    private let userService: UserServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }

    func loadProfile(id: String) async {
        loadTask?.cancel()
        loadTask = Task {
            isLoading = true
            defer { isLoading = false }

            do {
                user = try await userService.fetchUser(id: id)

                // Load posts after user loads
                await postsController.loadPosts(userId: id)
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

// View passes composed controllers to children
struct ProfileView: View {
    @State private var controller = ProfileController()

    var body: some View {
        ScrollView {
            if let user = controller.user {
                ProfileHeader(user: user)
                PostsList(controller: controller.postsController)
            }
        }
        .task {
            await controller.loadProfile(id: "123")
        }
    }
}

struct PostsList: View {
    let controller: ProfilePostsController

    var body: some View {
        if controller.isLoading {
            ProgressView()
        } else {
            ForEach(controller.posts) { post in
                PostRow(post: post)
            }
        }
    }
}
```

### When to Split Controllers

Split a Controller when it:
- **Exceeds ~200 lines**
- **Manages multiple independent concerns**
- **Has multiple distinct async operations**

**Benefits:**
- Smaller, focused controllers
- Easier to test
- Better code organization
- Reusable components

---

## Shared Controllers

For state spanning multiple features (user context, preferences, global settings).

### Full Pattern

```swift
// 1. Define shared controller with singleton
@Observable
@MainActor
final class AppController {
    static let shared = AppController()

    private(set) var currentUser: User?
    private(set) var isAuthenticated = false

    // Private init to enforce singleton
    private init() {}

    // Allow custom init for testing
    init(currentUser: User? = nil) {
        self.currentUser = currentUser
        self.isAuthenticated = currentUser != nil
    }

    func setUser(_ user: User?) {
        self.currentUser = user
        self.isAuthenticated = user != nil
    }

    func signOut() {
        currentUser = nil
        isAuthenticated = false
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
struct MyApp: App {
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
        if let user = appController.currentUser {
            Text("Welcome, \(user.name)")
        } else {
            Text("Please sign in")
        }
    }
}

// 5. Inject into Controller classes
@Observable
@MainActor
final class FeatureController {
    private let appController: AppController
    private let service: FeatureServiceProtocol

    init(
        appController: AppController = .shared,
        service: FeatureServiceProtocol = FeatureService()
    ) {
        self.appController = appController
        self.service = service
    }

    var userName: String {
        appController.currentUser?.name ?? "Guest"
    }

    func performAction() async {
        guard let userId = appController.currentUser?.id else {
            return
        }

        do {
            try await service.doSomething(userId: userId)
        } catch {
            // Handle error
        }
    }
}

// 6. Access from Services (when necessary)
actor FeatureService: FeatureServiceProtocol {
    func performAction() async throws -> Result {
        // Access shared controller from background actor
        let userId = await MainActor.run {
            AppController.shared.currentUser?.id
        }

        guard let userId else {
            throw AppError.authenticationRequired
        }

        return try await APIClient.shared.post("/action", userId: userId)
    }
}
```

### Shared Controller Rules

**✅ DO:**
- Use `@Observable @MainActor final class`
- Provide `static let shared` singleton
- Create custom EnvironmentKey
- Controllers accept via init with `.shared` default
- Services access via `MainActor.run` when needed

**❌ DON'T:**
- Never hardcode `.shared` in Controller properties
- Never access from Models
- Don't overuse - only for truly global state

### Common Shared Controllers

```swift
// App-level state
@Observable
@MainActor
final class AppController {
    static let shared = AppController()
    private(set) var currentUser: User?
    private(set) var theme: Theme = .light
}

// User preferences
@Observable
@MainActor
final class PreferencesController {
    static let shared = PreferencesController()
    private(set) var notificationsEnabled = true
    private(set) var darkModeEnabled = false
}

// Network state
@Observable
@MainActor
final class NetworkController {
    static let shared = NetworkController()
    private(set) var isOnline = true
    private(set) var connectionType: ConnectionType = .wifi
}
```

---

## Coordinator Pattern

For complex navigation flows.

```swift
@Observable
@MainActor
final class OnboardingCoordinator {
    private(set) var currentStep: Step = .welcome
    private(set) var isComplete = false

    enum Step {
        case welcome
        case profile
        case permissions
        case complete
    }

    func next() {
        switch currentStep {
        case .welcome:
            currentStep = .profile
        case .profile:
            currentStep = .permissions
        case .permissions:
            currentStep = .complete
        case .complete:
            isComplete = true
        }
    }

    func back() {
        switch currentStep {
        case .welcome:
            break
        case .profile:
            currentStep = .welcome
        case .permissions:
            currentStep = .profile
        case .complete:
            currentStep = .permissions
        }
    }
}

struct OnboardingFlow: View {
    @State private var coordinator = OnboardingCoordinator()

    var body: some View {
        Group {
            switch coordinator.currentStep {
            case .welcome:
                WelcomeView()
            case .profile:
                ProfileSetupView()
            case .permissions:
                PermissionsView()
            case .complete:
                CompleteView()
            }
        }
        .toolbar {
            if coordinator.currentStep != .welcome {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Back") {
                        coordinator.back()
                    }
                }
            }

            ToolbarItem(placement: .navigationBarTrailing) {
                Button("Next") {
                    coordinator.next()
                }
            }
        }
    }
}
```

---

## Parent-Child Communication

### Child Notifies Parent

```swift
// Child controller
@Observable
@MainActor
final class EditController {
    private(set) var item: Item

    var onSave: ((Item) -> Void)?

    init(item: Item) {
        self.item = item
    }

    func save() {
        onSave?(item)
    }
}

// Parent controller
@Observable
@MainActor
final class ListController {
    private(set) var items: [Item] = []

    func createEditController(for item: Item) -> EditController {
        let editController = EditController(item: item)
        editController.onSave = { [weak self] updatedItem in
            self?.updateItem(updatedItem)
        }
        return editController
    }

    private func updateItem(_ item: Item) {
        if let index = items.firstIndex(where: { $0.id == item.id }) {
            items[index] = item
        }
    }
}
```

---

## State Machine Pattern

For complex state transitions.

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

        var isLoading: Bool {
            if case .signingIn = self { return true }
            return false
        }

        var user: User? {
            if case .signedIn(let user) = self { return user }
            return nil
        }

        var errorMessage: String? {
            if case .error(let message) = self { return message }
            return nil
        }
    }

    func signIn(email: String, password: String) async {
        state = .signingIn

        do {
            let user = try await service.signIn(email: email, password: password)
            state = .signedIn(user)
        } catch {
            if !Task.isCancelled {
                state = .error(error.localizedDescription)
            }
        }
    }

    func signOut() {
        state = .loggedOut
    }
}

// View
switch controller.state {
case .loggedOut:
    SignInForm()
case .signingIn:
    ProgressView()
case .signedIn(let user):
    ProfileView(user: user)
case .error(let message):
    ErrorView(message: message)
}
```

---

## Dependency Container

For complex dependency graphs.

```swift
@Observable
@MainActor
final class DependencyContainer {
    static let shared = DependencyContainer()

    // Services
    let networkService: NetworkServiceProtocol
    let authService: AuthServiceProtocol
    let databaseService: DatabaseServiceProtocol

    // Shared controllers
    let appController: AppController

    init(
        networkService: NetworkServiceProtocol = NetworkService(),
        authService: AuthServiceProtocol = AuthService(),
        databaseService: DatabaseServiceProtocol = DatabaseService(),
        appController: AppController = AppController.shared
    ) {
        self.networkService = networkService
        self.authService = authService
        self.databaseService = databaseService
        self.appController = appController
    }

    // Factory methods
    func makeUserController() -> UserController {
        UserController(
            userService: UserService(network: networkService),
            appController: appController
        )
    }

    func makePostController() -> PostController {
        PostController(
            postService: PostService(network: networkService, database: databaseService)
        )
    }
}

// Usage
struct FeatureView: View {
    @State private var controller = DependencyContainer.shared.makeUserController()
}
```

---

## Related

- [CONTROLLERS.md](CONTROLLERS.md) - Basic controller patterns
- [NAVIGATION.md](NAVIGATION.md) - Navigation patterns
- [TESTING.md](TESTING.md) - Testing composed controllers
- [EXAMPLES.md](EXAMPLES.md) - Real-world examples
