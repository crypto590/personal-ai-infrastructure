# Architecture Levels - Detailed Guide

Complete guide to the three-level progressive architecture for Swift/SwiftUI applications.

**Referenced from**: [SKILL.md](SKILL.md)

---

## Table of Contents

- [Level 1: Simple Views with @State](#level-1-simple-views-with-state)
- [Level 2: Views with ViewModels](#level-2-views-with-viewmodels)
- [Level 3: Shared Services](#level-3-shared-services)
- [Decision Tree](#decision-tree)
- [File Organization](#file-organization)
- [When to Refactor](#when-to-refactor)
- [Testing Strategy](#testing-strategy)
- [Anti-Patterns](#anti-patterns)

---

## Level 1: Simple Views with @State

**When to use**: View has only local UI state with no business logic

**Pattern**: State lives directly in the SwiftUI view using `@State`

### Example

```swift
struct SettingsView: View {
    @State private var isNotificationsEnabled = false
    @State private var selectedTheme = "Light"
    @State private var fontSize: Double = 14
    
    var body: some View {
        Form {
            Section("Notifications") {
                Toggle("Enable Notifications", isOn: $isNotificationsEnabled)
            }
            
            Section("Appearance") {
                Picker("Theme", selection: $selectedTheme) {
                    Text("Light").tag("Light")
                    Text("Dark").tag("Dark")
                    Text("Auto").tag("Auto")
                }
                
                HStack {
                    Text("Font Size")
                    Slider(value: $fontSize, in: 12...20)
                    Text("\(Int(fontSize))")
                }
            }
        }
    }
}
```

### Characteristics

✅ **Use Level 1 when:**
- No API calls
- No complex validation
- No multi-step workflows
- State is purely UI-related (toggles, selections, input)
- No state shared between screens
- Logic is < 20-30 lines

❌ **Don't use Level 1 when:**
- Making network requests
- Need to test business logic
- Validation is complex
- State needs to be shared
- Logic exceeds ~30 lines

### Common Level 1 Scenarios

- Settings screens with toggles and pickers
- Tab selection
- Simple forms without validation
- Filter/sort UI controls
- Modal presentation state
- Navigation state (for simple navigation)

**Related**: See [EXAMPLES.md](EXAMPLES.md#level-1-simple-filter) for real-world Level 1 examples.

---

## Level 2: Views with ViewModels

**When to use**: Feature needs business logic, API calls, validation, or complex state management

**Pattern**: Separate `@Observable` ViewModel handles logic, View focuses on UI

### Example

```swift
@Observable
class ProfileViewModel {
    var profile: UserProfile?
    var isLoading = false
    var errorMessage: String?
    
    private let authService: AuthenticationService
    
    init(authService: AuthenticationService) {
        self.authService = authService
    }
    
    func loadProfile() async {
        isLoading = true
        errorMessage = nil
        
        do {
            profile = try await authService.fetchUserProfile()
        } catch {
            errorMessage = "Failed to load profile: \(error.localizedDescription)"
        }
        
        isLoading = false
    }
    
    func updateBio(_ newBio: String) async {
        guard var profile = profile else { return }
        
        profile.bio = newBio
        
        do {
            try await authService.updateProfile(profile)
            self.profile = profile
        } catch {
            errorMessage = "Failed to update profile"
        }
    }
}

struct ProfileView: View {
    @State private var viewModel: ProfileViewModel
    @State private var isEditing = false
    
    init(authService: AuthenticationService) {
        self._viewModel = State(initialValue: ProfileViewModel(authService: authService))
    }
    
    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading profile...")
            } else if let profile = viewModel.profile {
                VStack {
                    AsyncImage(url: profile.avatarURL) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        Image(systemName: "person.circle.fill")
                            .resizable()
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())
                    
                    Text(profile.name)
                        .font(.title)
                    
                    Text(profile.bio)
                        .foregroundStyle(.secondary)
                        .padding()
                    
                    Button("Edit Profile") {
                        isEditing = true
                    }
                }
            } else if let error = viewModel.errorMessage {
                VStack {
                    Text(error)
                        .foregroundColor(.red)
                    Button("Retry") {
                        Task { await viewModel.loadProfile() }
                    }
                }
            }
        }
        .task {
            await viewModel.loadProfile()
        }
        .sheet(isPresented: $isEditing) {
            EditProfileView(viewModel: viewModel)
        }
    }
}
```

### Characteristics

✅ **Use Level 2 when:**
- Makes API/network calls
- Contains business logic or validation
- Manages complex state transitions
- Coordinates multiple operations
- Needs testing in isolation
- Logic exceeds ~30 lines

❌ **ViewModels should NOT:**
- Import SwiftUI or UIKit (keep framework-independent)
- Create dependencies internally (always inject)
- Handle UI layout or styling
- Contain navigation logic (unless using coordinator pattern)

### ViewModel Best Practices

1. **Use @Observable**: Modern SwiftUI pattern (iOS 17+)
2. **Inject dependencies**: Always via initializer
3. **Handle all business logic**: Views should just display
4. **Expose simple properties**: Views read/bind to these
5. **Never import SwiftUI**: Keep framework-independent for testing

**Related**: 
- See [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md) for comprehensive ViewModel patterns
- See [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md#dependency-inversion-principle) for dependency injection

---

## Level 3: Shared Services

**When to use**: Logic is needed by multiple ViewModels or across the app

**Pattern**: Extract to a service that ViewModels depend on

### Example

```swift
@Observable
class AuthenticationService {
    var currentUser: User?
    var isAuthenticated: Bool { currentUser != nil }
    
    private let networkService: NetworkServiceProtocol
    private let persistenceService: PersistenceServiceProtocol
    
    init(
        networkService: NetworkServiceProtocol,
        persistenceService: PersistenceServiceProtocol
    ) {
        self.networkService = networkService
        self.persistenceService = persistenceService
    }
    
    func login(email: String, password: String) async throws {
        let response: LoginResponse = try await networkService.post(
            "/auth/login",
            body: ["email": email, "password": password]
        )
        
        currentUser = response.user
        try await persistenceService.save(response.token, forKey: "auth_token")
    }
    
    func logout() async {
        currentUser = nil
        try? await persistenceService.delete(forKey: "auth_token")
    }
    
    func fetchUserProfile() async throws -> UserProfile {
        guard isAuthenticated else {
            throw AuthError.notAuthenticated
        }
        
        return try await networkService.get("/profile")
    }
    
    func updateProfile(_ profile: UserProfile) async throws {
        guard isAuthenticated else {
            throw AuthError.notAuthenticated
        }
        
        try await networkService.put("/profile", body: profile.toDictionary())
    }
}
```

### Common Service Types

- **AuthenticationService**: User auth state and operations
- **NetworkService**: HTTP requests and API communication
- **PersistenceService**: Database/storage operations
- **LocationService**: GPS and location tracking
- **NotificationService**: Push notification handling
- **AnalyticsService**: Event tracking
- **CacheService**: Data caching strategies

### Service Best Practices

1. **Single Responsibility**: Each service handles one domain
2. **Observable when needed**: Use `@Observable` for services with shared state
3. **Accept dependencies**: Via initializer (dependency injection)
4. **Protocol-based**: Define protocol interfaces
5. **Reusable**: Should work across features
6. **Self-contained**: Handle their own error scenarios

**Related**:
- See [SERVICE_LAYER.md](SERVICE_LAYER.md) for comprehensive service patterns
- See [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md#single-responsibility-principle) for SRP examples

---

## Decision Tree

Use this flowchart to determine the appropriate architecture level:

```
┌─────────────────────────────────────────────────────────┐
│ Does the view only display/update simple local state?  │
│ (toggles, pickers, simple forms, no API calls)         │
└──────────────┬──────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       │               │
      YES             NO
       │               │
       │               ▼
       │       ┌───────────────────────────────────────────┐
       │       │ Does it need API calls, validation,       │
       │       │ or complex logic?                         │
       │       └───────────┬───────────────────────────────┘
       │                   │
       │           ┌───────┴───────┐
       │           │               │
       │          YES             NO (unusual)
       │           │               │
       ▼           ▼               ▼
┌──────────┐  ┌────────────┐  ┌──────────┐
│ Level 1  │  │  Level 2   │  │ Level 1  │
│  @State  │  │ ViewModel  │  │ @State   │
│ in View  │  │            │  │ in View  │
└──────────┘  └─────┬──────┘  └──────────┘
                    │
                    ▼
            ┌───────────────────────────────────────┐
            │ Is this logic shared across           │
            │ multiple features?                    │
            └───────────┬───────────────────────────┘
                        │
                ┌───────┴───────┐
                │               │
               YES             NO
                │               │
                ▼               ▼
         ┌─────────────┐  ┌──────────────┐
         │   Level 3   │  │   Level 2    │
         │  Service    │  │  Keep in     │
         │             │  │  ViewModel   │
         └─────────────┘  └──────────────┘
```

### Decision Examples

**Example 1**: Settings toggle
- Simple UI state? → YES
- **Answer**: Level 1 (@State)

**Example 2**: User profile that loads from API
- Simple UI state? → NO
- API calls? → YES
- **Answer**: Level 2 (ViewModel)

**Example 3**: Authentication used across entire app
- Simple UI state? → NO
- API calls? → YES
- Shared logic? → YES
- **Answer**: Level 3 (Service)

**Related**: See [EXAMPLES.md](EXAMPLES.md) for complete feature evolution examples.

---

## File Organization

### Recommended Structure

```
YourApp/
├── App/
│   └── YourAppApp.swift              # App entry point
│
├── Views/
│   ├── ContentView.swift             # Main view
│   ├── Auth/
│   │   ├── LoginView.swift           # Level 2
│   │   └── LoginViewModel.swift
│   ├── Profile/
│   │   ├── ProfileView.swift         # Level 2
│   │   ├── ProfileViewModel.swift
│   │   └── EditProfileView.swift     # Level 1 (form)
│   ├── Settings/
│   │   └── SettingsView.swift        # Level 1
│   └── Dashboard/
│       ├── DashboardView.swift       # Level 2
│       └── DashboardViewModel.swift
│
├── Services/
│   ├── AuthenticationService.swift   # Level 3
│   ├── NetworkService.swift          # Level 3
│   ├── PersistenceService.swift      # Level 3
│   └── LocationService.swift         # Level 3
│
├── Models/
│   ├── User.swift
│   ├── Post.swift
│   └── UserProfile.swift
│
└── Utilities/
    ├── Extensions/
    │   └── View+Extensions.swift
    └── Helpers/
        └── DateFormatter.swift
```

### Naming Conventions

**Views**: `FeatureView.swift`
- Examples: `ProfileView.swift`, `LoginView.swift`, `SettingsView.swift`

**ViewModels**: `FeatureViewModel.swift`
- Examples: `ProfileViewModel.swift`, `LoginViewModel.swift`
- Always match the associated view name

**Services**: `DomainService.swift`
- Examples: `AuthenticationService.swift`, `NetworkService.swift`
- Name reflects the domain/responsibility

**Models**: `EntityName.swift`
- Examples: `User.swift`, `Post.swift`, `Order.swift`
- Use singular form

**Related**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md#file-organization) for quick lookup.

---

## When to Refactor

### Upgrading from Level 1 to Level 2

**Trigger points**:
- You need to make your first API call
- Logic exceeds 20-30 lines
- You want to test the logic in isolation
- State management becomes complex
- Multiple state variables interact in complex ways

**Refactoring process**:
1. Create ViewModel class with `@Observable`
2. Move state variables to ViewModel
3. Move logic functions to ViewModel
4. Inject ViewModel dependencies
5. Update View to use ViewModel

**Example**:
```swift
// Before (Level 1)
struct TodoListView: View {
    @State private var todos = [...]
    @State private var newTodoTitle = ""
    
    func addTodo() {
        // Logic here
    }
}

// After (Level 2)
@Observable
class TodoViewModel {
    var todos = [...]
    var newTodoTitle = ""
    
    func addTodo() {
        // Logic here
    }
}

struct TodoListView: View {
    @State private var viewModel = TodoViewModel()
}
```

### Extracting to Level 3 (Service)

**Trigger points**:
- Second ViewModel needs the same logic
- Logic is domain-specific (auth, networking, persistence)
- Want to share state across the app
- Multiple features need access to the same data

**Refactoring process**:
1. Create Service class with domain-specific name
2. Move shared logic from ViewModels to Service
3. Define protocol interface for Service
4. Inject Service into ViewModels that need it
5. Update ViewModels to use Service

**Example**:
```swift
// Before (duplicated in ViewModels)
class ProfileViewModel {
    func fetchProfile() async throws -> Profile {
        // Auth + network logic
    }
}

class SettingsViewModel {
    func fetchProfile() async throws -> Profile {
        // Same auth + network logic (duplicated!)
    }
}

// After (extracted to Service)
class AuthenticationService {
    func fetchProfile() async throws -> Profile {
        // Auth + network logic (single source)
    }
}

class ProfileViewModel {
    private let authService: AuthenticationService
    
    func fetchProfile() async throws {
        profile = try await authService.fetchProfile()
    }
}
```

**Related**: See [EXAMPLES.md](EXAMPLES.md) for full feature evolution examples.

---

## Testing Strategy

### Level 1: Simple Views

Usually doesn't require unit tests. Use SwiftUI preview or UI testing.

```swift
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
```

### Level 2: ViewModels

Test ViewModels in isolation with mock dependencies.

```swift
func testProfileLoad() async throws {
    // Arrange
    let mockAuth = MockAuthService()
    mockAuth.mockProfile = UserProfile(id: "123", name: "Test User")
    
    let viewModel = ProfileViewModel(authService: mockAuth)
    
    // Act
    await viewModel.loadProfile()
    
    // Assert
    XCTAssertNotNil(viewModel.profile)
    XCTAssertEqual(viewModel.profile?.name, "Test User")
    XCTAssertFalse(viewModel.isLoading)
}

func testProfileLoadError() async throws {
    // Arrange
    let mockAuth = MockAuthService()
    mockAuth.shouldFail = true
    
    let viewModel = ProfileViewModel(authService: mockAuth)
    
    // Act
    await viewModel.loadProfile()
    
    // Assert
    XCTAssertNil(viewModel.profile)
    XCTAssertNotNil(viewModel.errorMessage)
}
```

### Level 3: Services

Test Services with mock dependencies.

```swift
func testLogin() async throws {
    // Arrange
    let mockNetwork = MockNetworkService()
    mockNetwork.mockResponse = LoginResponse(user: User(...), token: "abc123")
    
    let authService = AuthenticationService(
        networkService: mockNetwork,
        persistenceService: MockPersistenceService()
    )
    
    // Act
    try await authService.login(email: "test@example.com", password: "password")
    
    // Assert
    XCTAssertTrue(authService.isAuthenticated)
    XCTAssertNotNil(authService.currentUser)
}
```

**Related**: 
- See [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md#testing-viewmodels) for ViewModel testing patterns
- See [SERVICE_LAYER.md](SERVICE_LAYER.md#testing-services) for Service testing patterns

---

## Anti-Patterns

### ❌ Anti-Pattern 1: ViewModels for Everything

**Bad**: Creating a ViewModel for every single view, even simple ones

```swift
// Unnecessary ViewModel for a simple settings toggle
@Observable
class SettingsViewModel {
    var isNotificationsEnabled = false
}

struct SettingsView: View {
    @State private var viewModel = SettingsViewModel()
    
    var body: some View {
        Toggle("Notifications", isOn: $viewModel.isNotificationsEnabled)
    }
}
```

**Good**: Use @State for simple UI state

```swift
struct SettingsView: View {
    @State private var isNotificationsEnabled = false
    
    var body: some View {
        Toggle("Notifications", isOn: $isNotificationsEnabled)
    }
}
```

### ❌ Anti-Pattern 2: ViewModels Importing SwiftUI

**Bad**: ViewModel that imports SwiftUI

```swift
import SwiftUI  // ❌ ViewModels shouldn't import SwiftUI

@Observable
class ProfileViewModel {
    var profile: UserProfile?
    
    func showAlert() {
        // Trying to show SwiftUI alert from ViewModel
    }
}
```

**Good**: Keep ViewModels framework-independent

```swift
@Observable
class ProfileViewModel {
    var profile: UserProfile?
    var shouldShowAlert = false  // View decides how to show alert
    var alertMessage = ""
}
```

### ❌ Anti-Pattern 3: Massive God ViewModels

**Bad**: One ViewModel doing everything

```swift
@Observable
class AppViewModel {
    // Auth logic
    var currentUser: User?
    func login() { }
    func logout() { }
    
    // Profile logic
    var profile: Profile?
    func loadProfile() { }
    
    // Posts logic
    var posts: [Post] = []
    func loadPosts() { }
    
    // Settings logic
    var settings: Settings?
    func saveSettings() { }
    
    // ...and so on (hundreds of lines)
}
```

**Good**: Extract to focused ViewModels and Services

```swift
// Separate ViewModels
@Observable class ProfileViewModel { }
@Observable class PostsViewModel { }

// Shared Services
class AuthenticationService { }
class SettingsService { }
```

### ❌ Anti-Pattern 4: Business Logic in Views

**Bad**: Complex logic in the View

```swift
struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    
    var body: some View {
        Button("Login") {
            // ❌ Business logic in View
            guard !email.isEmpty, email.contains("@") else { return }
            guard password.count >= 8 else { return }
            
            Task {
                let url = URL(string: "https://api.example.com/login")!
                var request = URLRequest(url: url)
                // ...complex networking code
            }
        }
    }
}
```

**Good**: Logic in ViewModel

```swift
@Observable
class LoginViewModel {
    var email = ""
    var password = ""
    var errorMessage: String?
    
    var isValid: Bool {
        !email.isEmpty && email.contains("@") && password.count >= 8
    }
    
    func login() async {
        // Networking logic here
    }
}
```

### ❌ Anti-Pattern 5: Hardcoded Dependencies

**Bad**: Creating dependencies internally

```swift
@Observable
class ProfileViewModel {
    private let authService = AuthenticationService()  // ❌ Hardcoded
    
    func loadProfile() async {
        // Can't test or swap implementation
    }
}
```

**Good**: Inject dependencies

```swift
@Observable
class ProfileViewModel {
    private let authService: AuthenticationService  // ✅ Injected
    
    init(authService: AuthenticationService) {
        self.authService = authService
    }
}
```

**Related**: See [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md) for more anti-patterns and solutions.

---

## Summary

**Progressive Architecture Approach**:
1. Start with **Level 1** (@State) for simple UI state
2. Move to **Level 2** (ViewModel) when you need business logic or API calls
3. Extract to **Level 3** (Service) when logic is shared across features

**Key Principles**:
- Don't over-engineer simple features
- Let complexity drive architecture decisions
- Always inject dependencies
- Follow SOLID principles at every level
- Refactor when pain points emerge, not preemptively

**When in Doubt**:
- Start simpler than you think you need
- Add complexity only when you feel the pain
- Use the Decision Tree to guide your choices

**Related Resources**:
- [SKILL.md](SKILL.md) - Main skill overview
- [VIEWMODEL_PATTERNS.md](VIEWMODEL_PATTERNS.md) - Detailed ViewModel patterns
- [SERVICE_LAYER.md](SERVICE_LAYER.md) - Service implementation guide
- [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md) - SOLID principles in Swift
- [EXAMPLES.md](EXAMPLES.md) - Real-world feature evolution
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick lookup guide
