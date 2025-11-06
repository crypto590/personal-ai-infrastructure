---
name: swift-mvc
description: Modern MVC architecture for Swift/SwiftUI with strict unidirectional data flow. Observable Controllers coordinate Services and manage UI state, Services handle async operations, Models contain business logic, Views delegate to Controllers.
---

# Swift MVC Architecture

**Category:** technical

**Brief Description:** Modern MVC (Model-View-Controller) architecture for Swift and SwiftUI applications. Uses @Observable Controllers for UI state coordination, Actor-based Services for async operations, immutable Models for business logic, and SwiftUI Views that delegate actions. Enforces unidirectional data flow and strict layer separation.

---

## When to Use This Skill

Trigger this skill when:
- Building iOS/macOS/watchOS/visionOS apps with SwiftUI
- Designing architecture for new Swift features
- Asking "where should this code live?"
- User mentions ViewModels, Controllers, or architecture
- Organizing Swift/SwiftUI code structure
- Making async/await architectural decisions
- Setting up production-ready Swift patterns
- Reviewing Swift code architecture
- Implementing state management
- Coordinating service calls from UI
- Building testable Swift applications

---

## Core Principle

**Unidirectional data flow with strict layer separation.**

This is MVC done right for modern Swift. Views can never directly mutate state. Controllers coordinate services and manage UI state. Services handle infrastructure. Models contain business logic. Every component is protocol-based and testable in isolation.

---

## Architecture Overview

### Unidirectional Flow

```
View → Controller → Service → Model
```

- **View**: SwiftUI, renders UI, delegates actions to Controller
- **Controller**: Observable class, manages UI state, coordinates services
- **Service**: Actor or struct, stateless async operations, infrastructure layer
- **Model**: Struct, immutable data with business logic

### What Makes This Powerful

- **Unidirectional data flow**: Views can never directly mutate state
- **Protocol-based services**: Every component is testable in isolation
- **Task cancellation discipline**: Memory-safe async operations by default
- **Clear separation**: Business logic in Models, coordination in Controllers, infrastructure in Services

---

## MVC Layer Usage

When building a feature, use these layers:

- **Models/**: Always. Every feature has data structures.
- **Services/**: When performing async operations (API calls, SDK interactions).
- **Controllers/**: When managing UI state or coordinating services.
- **Views/**: Always. Every feature has UI.

**Simplest Feature**: Model + View only.
**Typical Feature**: Model + Service + Controller + View.

---

## Quick Layer Guide

### Models (Structs)
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

**See**: [MODELS.md](MODELS.md) for complete patterns.

### Services (Actors or Structs)
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
```

**See**: [SERVICES.md](SERVICES.md) for actor vs struct decisions and patterns.

### Controllers (Observable Classes)
Manages UI state and coordinates service calls.

```swift
@Observable
@MainActor
final class UserController {
    private(set) var user: User?
    private(set) var isLoading = false

    private let service: UserServiceProtocol
    private var loadTask: Task<Void, Never>?

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

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

**See**: [CONTROLLERS.md](CONTROLLERS.md) for complete controller patterns.

### Views (SwiftUI)
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

**See**: [VIEWS.md](VIEWS.md) for SwiftUI delegation patterns.

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
- Controllers: No `@Environment` dependencies (except for shared controllers)
- Views: Delegate to Controllers, never call Services directly

**See**: [CONTROLLERS.md](CONTROLLERS.md#production-checklist) for complete checklist.

---

## Detailed Documentation

### Core Patterns
- **Controllers**: [CONTROLLERS.md](CONTROLLERS.md)
  - Observable patterns
  - Task cancellation discipline
  - State management
  - Production requirements checklist

- **Services**: [SERVICES.md](SERVICES.md)
  - Actor vs struct decision tree
  - Protocol-based design
  - Async/await patterns
  - Background execution rules

- **Models**: [MODELS.md](MODELS.md)
  - Immutable struct patterns
  - Computed properties for business logic
  - Codable compliance

- **Views**: [VIEWS.md](VIEWS.md)
  - SwiftUI delegation patterns
  - Controller integration
  - Never mutate controller state

### Common Patterns
- **Error Handling**: [ERROR_HANDLING.md](ERROR_HANDLING.md)
  - Controller error patterns
  - Custom error types
  - User-facing messages

- **Navigation**: [NAVIGATION.md](NAVIGATION.md)
  - Controller-owned intent
  - NavigationStack integration
  - Modal presentation

### Advanced Topics
- **Advanced Patterns**: [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md)
  - Controller composition
  - Shared controllers with Environment
  - When to split controllers

- **Testing**: [TESTING.md](TESTING.md)
  - Protocol-based testing
  - Mock services
  - Testing controllers in isolation

- **Liquid Glass**: [LIQUID_GLASS.md](LIQUID_GLASS.md)
  - iOS 26+ design system
  - Glass effect patterns
  - Performance considerations

### Practical Resources
- **Examples**: [EXAMPLES.md](EXAMPLES.md)
  - Real-world feature implementations
  - Complete code examples
  - Common use cases

- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
  - Code templates
  - Decision trees
  - Anti-patterns list

---

## Dependencies

**Related skills:**
- `core/skill-creation` - PAI skill creation methodology
- Future: `swift-testing` (when extracted)
- Future: `swift-concurrency` (when created)

**Required context files:**
- `/Users/coreyyoung/Claude/context/knowledge/languages/swift-conventions.md` - Source conventions (Athlead-specific)
- `/Users/coreyyoung/Claude/context/knowledge/pai/philosophy.md` - PAI philosophy

**Recommended context files:**
- `/Users/coreyyoung/Claude/context/knowledge/languages/swift/` (future) - Swift language specifics
- `/Users/coreyyoung/Claude/context/knowledge/frameworks/swiftui/` (future) - SwiftUI patterns

---

## Quick Reference

| Scenario | Layer | Read |
|----------|-------|------|
| API call needed | Service | [SERVICES.md](SERVICES.md) |
| Coordinate service calls | Controller | [CONTROLLERS.md](CONTROLLERS.md) |
| Display data | View | [VIEWS.md](VIEWS.md) |
| Business logic | Model | [MODELS.md](MODELS.md) |
| Error handling | Controller | [ERROR_HANDLING.md](ERROR_HANDLING.md) |
| Navigation | Controller + View | [NAVIGATION.md](NAVIGATION.md) |
| Shared state | Shared Controller | [ADVANCED_PATTERNS.md](ADVANCED_PATTERNS.md#shared-controllers) |
| Testing | Protocol mocks | [TESTING.md](TESTING.md) |

---

## Decision Tree

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

---

## Notes

**Philosophy**: This skill teaches modern MVC for Swift/SwiftUI with strict conventions that prevent the "Massive View Controller" anti-pattern. The explicit Service layer and Swift concurrency patterns make this architecture powerful, testable, and maintainable.

**Modern Patterns**: Uses Swift 5.9+ @Observable macro, Swift 5.5+ actors, and modern async/await patterns throughout. This is not old-style MVC—it's MVC adapted for modern Swift.

**Source Material**: Based on `/Users/coreyyoung/Claude/context/knowledge/languages/swift-conventions.md`. That file is the single source of truth for Athlead projects. This skill makes those conventions reusable across any Swift project.

**Flexibility**: While this skill encodes strict patterns proven in production, you can adapt terminology or loosen requirements for specific projects via project-specific context files.
